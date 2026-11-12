"""Matrizes anuais Col9 por município. Somente leitura das fontes, sem banco/alvo.

Saídas novas por município permitem retomar execução sem substituir resultados.
Zero, 27 e NoData são excluídos; somente a máscara comum participa das matrizes.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import ExitStack
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
from multiprocessing.util import Finalize
import json
from pathlib import Path
import sys
import time
import uuid

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window, from_bounds
from shapely import from_wkb
from shapely.geometry import MultiPolygon
from shapely.geometry.polygon import orient

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.manifesto_transicoes_col9 import sha256, grade, conferir_grade

POLITICA=json.loads((PROJETO/'referencias/metodologia_col9.json').read_text(encoding='utf-8'))
CLASSES=np.array(sorted(pd.read_csv(PROJETO/'referencias/legenda_col9.csv').classe_cobertura),dtype=np.uint8)
N=len(CLASSES)
LUT=np.full(256,-1,dtype=np.int16)
for i,c in enumerate(CLASSES):
    if c!=27: LUT[c]=i
CONHECIDOS=np.zeros(256,dtype=bool); CONHECIDOS[CLASSES]=True; CONHECIDOS[0]=True
GEOD=Geod(ellps='WGS84')
ESTADO={}


def percentual(n,d):
    if d<=0: return None
    valor=100*float(n)/float(d)
    # Elimina somente ruído de soma em torno dos limites exatos, sem truncar
    # razões raster/polígono genuinamente maiores que 100%.
    if abs(valor-100)<1e-9: return 100.0
    if abs(valor)<1e-12: return 0.0
    return valor


def contar_transicoes(a,b,pesos,comum=None):
    """Vetores de índices canônicos; -1 é inválido. Retorna matriz densa 29×29."""
    if a.shape!=b.shape or a.shape!=pesos.shape:
        raise ValueError('Vetores de transição incompatíveis.')
    valido=(a>=0)&(b>=0)
    if comum is not None: valido &= comum
    if ((a[valido]>=N)|(b[valido]>=N)).any(): raise ValueError('Índice de classe inválido.')
    pares=a[valido].astype(np.int32)*N+b[valido]
    pixels=np.bincount(pares,minlength=N*N).reshape(N,N)
    areas=np.bincount(pares,weights=pesos[valido],minlength=N*N).reshape(N,N)
    return pixels,areas


def selecionar(codigos):
    return np.flatnonzero(np.isin(CLASSES,codigos))


def metricas(pixels,areas,estoque_pixels,estoque_areas):
    vn=selecionar(POLITICA['vegetacao_nativa']); ua=selecionar(POLITICA['usos_antropicos'])
    c25=selecionar([25]); c29=selecionar([29]); c32=selecionar([32])
    den=float(areas[vn,:].sum()); conv=float(areas[np.ix_(vn,ua)].sum())
    r={'area_convertida_ha':conv,'vn_inicial_elegivel_ha':den,
       'taxa_conversao_pct':percentual(conv,den),
       'pixels_convertidos':int(pixels[np.ix_(vn,ua)].sum()),
       'pixels_vn_elegiveis':int(pixels[vn,:].sum()),
       'vn_inicial_observada_ha':float(estoque_areas[vn].sum()),
       'elegibilidade_vn_pct':percentual(den,estoque_areas[vn].sum()),
       'elegibilidade_vn_pixels_pct':percentual(pixels[vn,:].sum(),estoque_pixels[vn].sum()),
       'conversao_potencial_para25_ha':float(areas[np.ix_(vn,c25)].sum()),
       'conversao_origem29_ha':float(areas[np.ix_(c29,ua)].sum()),
       'conversao_origem32_ha':float(areas[np.ix_(c32,ua)].sum())}
    for nome,origens,destinos in (
        ('mais25',vn,np.r_[ua,c25]),('mais29',np.r_[vn,c29],ua),
        ('mais32',np.r_[vn,c32],ua),('mais29_32',np.r_[vn,c29,c32],ua),
        ('mais29_32_25',np.r_[vn,c29,c32],np.r_[ua,c25])):
        d=float(areas[origens,:].sum()); c=float(areas[np.ix_(origens,destinos)].sum())
        r[f'area_convertida_{nome}_ha']=c
        r[f'vn_elegivel_{nome}_ha']=d
        r[f'taxa_{nome}_pct']=percentual(c,d)
    if conv>den+1e-6 or (pixels<0).any() or (areas<0).any():
        raise ValueError('Matriz viola conservação ou domínio.')
    return r


def area_linhas(transform,altura):
    x,y=transform.c,transform.f
    return np.array([abs(GEOD.polygon_area_perimeter(
        [x,x+transform.a,x+transform.a,x],
        [y+i*transform.e,y+i*transform.e,y+(i+1)*transform.e,y+(i+1)*transform.e])[0])/10000
        for i in range(altura)])


def ler_patch(src,banda,janela,offset):
    col=int(janela.col_off)-offset[0]; lin=int(janela.row_off)-offset[1]
    h,w=int(janela.height),int(janela.width)
    x0,y0=max(0,col),max(0,lin); x1,y1=min(src.width,col+w),min(src.height,lin+h)
    resultado=np.zeros((h,w),dtype=np.uint8)
    if x1>x0 and y1>y0:
        resultado[y0-lin:y1-lin,x0-col:x1-col]=src.read(banda,window=Window(x0,y0,x1-x0,y1-y0))
    return resultado


def aplicar_patch(original,patch,dentro):
    copia=original.copy()
    preencher=dentro&(original==0)&(patch!=0)&(patch!=27)
    divergencias=dentro&(original!=0)&(original!=27)&(patch!=0)&(patch!=27)&(original!=patch)
    copia[preencher]=patch[preencher]
    return copia,preencher,int(divergencias.sum())


def iniciar(manifesto,anos,cache_mb):
    global ESTADO
    pilha=ExitStack(); pilha.enter_context(rasterio.Env(GDAL_CACHEMAX=cache_mb*1024*1024))
    base=Path(manifesto['base_dados'])
    fontes=[pilha.enter_context(rasterio.open(base/manifesto['rasters'][str(a)]['arquivo'])) for a in anos]
    patch=pilha.enter_context(rasterio.open(base/manifesto['complemento']['arquivo']))
    estoque=pd.read_csv(base/manifesto['consolidado']['arquivo'],sep=';',encoding='utf-8-sig')
    ESTADO={'pilha':pilha,'fontes':fontes,'patch':patch,'manifesto':manifesto,'anos':anos,
            'areas_linhas':area_linhas(fontes[0].transform,fontes[0].height), 'estoque':estoque}
    Finalize(None,pilha.close,exitpriority=20)


def _escrever_csv(caminho,linhas):
    if not linhas: return
    with caminho.open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(linhas[0])); w.writeheader(); w.writerows(linhas)


def processar_municipio(tarefa):
    cd,nome,uf,wkb,destino,fingerprint,bloco=tarefa
    inicio=time.monotonic(); pasta=Path(destino)/'municipios'/str(cd)
    pronto=pasta/'concluido.json'
    if pronto.exists():
        anterior=json.loads(pronto.read_text(encoding='utf-8'))
        if anterior['fingerprint']!=fingerprint: raise ValueError('Checkpoint de outro protocolo; não substituir.')
        for arq,h in anterior['artefatos'].items():
            if sha256(pasta/arq)!=h: raise ValueError('Checkpoint corrompido; preservado para investigação.')
        return cd,'retomado',anterior.get('segundos',0)
    fontes=ESTADO['fontes']; anos=ESTADO['anos']; patch=ESTADO['patch']; mani=ESTADO['manifesto']
    geom=from_wkb(wkb); win=from_bounds(*geom.bounds,fontes[0].transform)
    x0=max(0,int(np.floor(win.col_off))); y0=max(0,int(np.floor(win.row_off)))
    x1=min(fontes[0].width,int(np.ceil(win.col_off+win.width)))
    y1=min(fontes[0].height,int(np.ceil(win.row_off+win.height)))
    if x1<=x0 or y1<=y0: raise ValueError(f'{cd}: polígono fora da grade.')
    k=len(anos); cont=np.zeros((k-1,N,N),dtype=np.int64); area=np.zeros_like(cont,dtype=np.float64)
    est_c=np.zeros((k,N),dtype=np.int64); est_a=np.zeros((k,N),dtype=np.float64)
    rec_c=np.zeros(k,dtype=np.int64); rec_a=np.zeros(k); div=np.zeros(k,dtype=np.int64)
    bruto_c=np.zeros(k,dtype=np.int64)
    grade_pixels=0; grade_ha=0.
    trip_c=np.zeros((2,N,N),dtype=np.int64); trip_a=np.zeros((2,N,N))
    triplo=cd==2102325 and {2001,2002,2003}<=set(anos)
    idx3=[anos.index(a) for a in (2001,2002,2003)] if triplo else []
    for linha in range(y0,y1,bloco):
        for coluna in range(x0,x1,bloco):
            janela=Window(coluna,linha,min(bloco,x1-coluna),min(bloco,y1-linha))
            shape=(int(janela.height),int(janela.width))
            dentro=geometry_mask([geom],shape,fontes[0].window_transform(janela),invert=True)
            npix=int(dentro.sum())
            if not npix: continue
            pesos=np.broadcast_to(ESTADO['areas_linhas'][linha:linha+shape[0],None],shape)[dentro]
            grade_pixels+=npix; grade_ha+=float(pesos.sum())
            indices=np.empty((k,npix),dtype=np.int16)
            for i,(ano,src) in enumerate(zip(anos,fontes)):
                dados=src.read(1,window=janela)
                bruto=dados[dentro]
                validos=(LUT[bruto]>=0)
                if src.nodata is not None: validos &= bruto!=src.nodata
                bruto_c[i]+=int(validos.sum())
                if cd in mani['complemento']['municipios'] and ano!=2002:
                    banda=mani['complemento']['descricoes'].index(f'classification_{ano}')+1
                    novos=ler_patch(patch,banda,janela,mani['complemento']['offset_col_linha'])
                    dados,preenchidos,divergencias=aplicar_patch(dados,novos,dentro)
                    rec_c[i]+=int(preenchidos.sum()); rec_a[i]+=float(pesos[preenchidos[dentro]].sum()); div[i]+=divergencias
                valores=dados[dentro]
                desconhecidos=~CONHECIDOS[valores]
                if src.nodata is not None: desconhecidos &= valores!=src.nodata
                if desconhecidos.any(): raise ValueError(f'{cd}/{ano}: códigos desconhecidos {np.unique(valores[desconhecidos])}')
                cod=LUT[valores].copy()
                if src.nodata is not None: cod[valores==src.nodata]=-1
                indices[i]=cod; v=cod>=0
                est_c[i]+=np.bincount(cod[v],minlength=N)
                est_a[i]+=np.bincount(cod[v],weights=pesos[v],minlength=N)
            for i in range(k-1):
                c,a=contar_transicoes(indices[i],indices[i+1],pesos); cont[i]+=c; area[i]+=a
            if triplo:
                comum=(indices[idx3]>=0).all(axis=0)
                for i in range(2):
                    c,a=contar_transicoes(indices[idx3[i]],indices[idx3[i+1]],pesos,comum)
                    trip_c[i]+=c; trip_a[i]+=a
    # Verificação independente: todos os estoques anuais contra o consolidado aprovado.
    referencia=ESTADO['estoque']; referencia=referencia[referencia.CD_MUN.eq(cd)&referencia.ano.isin(anos)]
    ref_c=np.zeros_like(est_c); ref_a=np.zeros_like(est_a)
    for r in referencia.itertuples():
        i=anos.index(int(r.ano)); j=int(np.flatnonzero(CLASSES==r.classe_cobertura)[0])
        ref_c[i,j]=r.pixels; ref_a[i,j]=r.area_ha
    erro_px=int(np.abs(est_c-ref_c).max()); erro_ha=float(np.abs(est_a-ref_a).max())
    if erro_px or erro_ha>0.0001:
        raise ValueError(f'{cd}: estoques não conferem com CSV: pixels={erro_px}, área={erro_ha}')
    partes=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
    area_geom=sum(abs(GEOD.geometry_area_perimeter(orient(p,sign=1.0))[0]) for p in partes)/10000
    linhas=[]
    for i,ano in enumerate(anos[:-1]):
        pc=int(cont[i].sum()); ac=float(area[i].sum()); vi=int(est_c[i].sum()); vf=int(est_c[i+1].sum())
        ai=float(est_a[i].sum()); af=float(est_a[i+1].sum())
        if pc>min(vi,vf) or pc<0 or ac>min(ai,af)+0.0001:
            raise ValueError('Máscara comum viola os estoques observados.')
        r={'CD_MUN':cd,'NM_MUN':nome,'SIGLA_UF':uf,'ano_origem':ano,'ano_destino':anos[i+1],
           'pixels_grade_municipio':grade_pixels,'area_grade_municipio_ha':grade_ha,'area_geodesica_poligono_ha':area_geom,
           'pixels_validos_inicial':vi,'pixels_validos_final':vf,'pixels_comuns':pc,
           'pixels_so_inicial':vi-pc,'pixels_so_final':vf-pc,'pixels_invalidos_ambos':grade_pixels-vi-vf+pc,
           'pixels_excluidos':grade_pixels-pc,'area_valida_inicial_ha':ai,'area_valida_final_ha':af,
           'area_comum_ha':ac,'area_so_inicial_ha':ai-ac,'area_so_final_ha':af-ac,
           'cobertura_comum_pixels_pct':percentual(pc,grade_pixels),'cobertura_comum_area_grade_pct':percentual(ac,grade_ha),
           'razao_comum_poligono_pct':percentual(ac,area_geom),
           'pixels_complementados_inicial':int(rec_c[i]),'pixels_complementados_final':int(rec_c[i+1]),
           'pixels_validos_brutos_inicial':int(bruto_c[i]),'pixels_validos_brutos_final':int(bruto_c[i+1]),
           **metricas(cont[i],area[i],est_c[i],est_a[i])}
        linhas.append(r)
    if (div>0).any(): raise ValueError('Complemento diverge de pixels classificados; investigar sem sobrescrever.')
    trip_linhas=[]
    if triplo:
        for i in range(2):
            j=idx3[i]
            trip_linhas.append({'CD_MUN':cd,'ano_origem':anos[j],'ano_destino':anos[j+1],
                'mascara':'comum_2001_2002_2003','pixels_comuns':int(trip_c[i].sum()),
                'area_comum_ha':float(trip_a[i].sum()),**metricas(trip_c[i],trip_a[i],est_c[j],est_a[j])})
    tentativa=pasta/('tentativa_'+uuid.uuid4().hex[:12]); tentativa.mkdir(parents=True)
    npz=tentativa/'matrizes_completas.npz'
    with npz.open('xb') as f:
        np.savez_compressed(f,classes=CLASSES,anos=np.array(anos),pixels=cont,area_ha=area,
                            estoque_pixels=est_c,estoque_area_ha=est_a,
                            tripla_pixels=trip_c,tripla_area_ha=trip_a,
                            complementados_pixels=rec_c,complementados_area_ha=rec_a)
    _escrever_csv(tentativa/'metricas_qualidade.csv',linhas)
    _escrever_csv(tentativa/'buriticupu_tripla.csv',trip_linhas)
    artifacts={str(p.relative_to(pasta)):sha256(p) for p in tentativa.iterdir() if p.is_file()}
    checkpoint={'CD_MUN':cd,'fingerprint':fingerprint,'artefatos':artifacts,
        'npz':str(npz.relative_to(pasta)), 'metricas':str((tentativa/'metricas_qualidade.csv').relative_to(pasta)),
        'tripla':str((tentativa/'buriticupu_tripla.csv').relative_to(pasta)) if triplo else None,
        'erro_estoques_pixels':erro_px,'erro_estoques_area_ha':erro_ha,'segundos':time.monotonic()-inicio,
        'area_grade_ha':grade_ha,'area_geodesica_ha':area_geom}
    with pronto.open('x',encoding='utf-8') as f: json.dump(checkpoint,f,ensure_ascii=False,indent=2)
    return cd,'calculado',checkpoint['segundos']


def consolidar(saida,codigos,anos,execucao):
    if (saida/'concluido.json').exists():
        print('Execução já consolidada; resultados preservados.',flush=True); return
    todas=[]; trip=[]; estoques=[]; mats_c=[]; mats_a=[]
    for cd in codigos:
        pasta=saida/'municipios'/str(cd); ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
        todas.append(pd.read_csv(pasta/ck['metricas'],encoding='utf-8-sig'))
        if ck['tripla']: trip.append(pd.read_csv(pasta/ck['tripla'],encoding='utf-8-sig'))
        estoques.append({'CD_MUN':cd,'erro_pixels':ck['erro_estoques_pixels'],'erro_area_ha':ck['erro_estoques_area_ha']})
        with np.load(pasta/ck['npz'],allow_pickle=False) as m:
            mats_c.append(m['pixels']); mats_a.append(m['area_ha'])
    qa=pd.concat(todas,ignore_index=True).sort_values(['CD_MUN','ano_origem'])
    qa.to_csv(saida/'metricas_municipio_ano.csv',mode='x',index=False,encoding='utf-8-sig')
    pd.DataFrame(estoques).to_csv(saida/'validacao_estoques.csv',mode='x',index=False,encoding='utf-8-sig')
    if trip: pd.concat(trip,ignore_index=True).to_csv(saida/'buriticupu_mascara_tripla.csv',mode='x',index=False,encoding='utf-8-sig')
    with (saida/'matrizes_completas_255.npz').open('xb') as f:
        np.savez_compressed(f,CD_MUN=np.array(codigos),anos=np.array(anos),classes=CLASSES,
                            pixels=np.stack(mats_c),area_ha=np.stack(mats_a))
    arquivos={p.name:sha256(p) for p in saida.iterdir() if p.is_file() and p.name!='concluido.json'}
    final={'concluido_em_utc':datetime.now(timezone.utc).isoformat(),'municipios':len(codigos),
           'pares':len(qa),'anos':anos,'sem_alvo_binario':True,'sem_limiares_definitivos':True,
           'classes_matriz':CLASSES.tolist(),'celulas_zero':'armazenadas nas matrizes densas; classe 27 excluída da máscara e mantida como linha/coluna zero',
           'artefatos':arquivos,'execucao':execucao}
    with (saida/'concluido.json').open('x',encoding='utf-8') as f: json.dump(final,f,ensure_ascii=False,indent=2)
    print(f'Concluído: {len(codigos)} municípios, {len(qa)} pares, sem alvo binário.',flush=True)


def executar(args):
    m=json.loads(args.manifesto.read_text(encoding='utf-8')); base=Path(m['base_dados'])
    anos=sorted(args.anos or list(range(1985,2024)))
    if len(anos)<2 or anos!=list(range(min(anos),max(anos)+1)) or not set(anos)<=set(range(1985,2024)):
        raise ValueError('Anos devem formar uma sequência anual consecutiva da Col9.')
    for ano in anos:
        info=m['rasters'][str(ano)]; caminho=base/info['arquivo']; st=caminho.stat()
        if st.st_size!=info['bytes'] or st.st_mtime_ns!=info['mtime_ns']:
            raise ValueError(f'Fonte {ano} alterada desde o manifesto.')
        if args.verificar_hashes:
            print(f'Verificando hash {ano}',flush=True)
            if sha256(caminho)!=info['sha256']: raise ValueError('Hash de raster divergente.')
        with rasterio.open(caminho) as src: conferir_grade(m['rasters'][str(anos[0])]['grade'],grade(src))
    gpkg=base/m['territorio']['arquivo']; csv_base=base/m['consolidado']['arquivo']; patch=base/m['complemento']['arquivo']
    for arq,h in ((gpkg,m['territorio']['sha256']),(csv_base,m['consolidado']['sha256']),(patch,m['complemento']['sha256'])):
        if sha256(arq)!=h: raise ValueError('Território/consolidado/complemento alterado.')
    g=gpd.read_file(gpkg)
    geometrias=json.loads((PROJETO/'referencias/territorio_col9_hashes.json').read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    for r in g.itertuples():
        geom=MultiPolygon([r.geometry]) if r.geometry.geom_type=='Polygon' else r.geometry
        if hashlib.sha256(geom.wkb).hexdigest()!=geometrias[str(int(r.CD_MUN))]: raise ValueError('Geometria fora do contrato.')
    if args.municipios:
        if not set(args.municipios)<=set(g.CD_MUN.astype(int)): raise ValueError('Município fora dos 255.')
        g=g[g.CD_MUN.astype(int).isin(args.municipios)]
    g=g.sort_values('CD_MUN'); codigos=g.CD_MUN.astype(int).tolist()
    execucao={'manifesto_sha256':sha256(args.manifesto),'codigo_sha256':sha256(Path(__file__)),
        'metodologia_sha256':sha256(PROJETO/'referencias/metodologia_col9.json'),'anos':anos,'municipios':codigos,
        'bloco':args.bloco,'regra_municipio':'centro do pixel, máscara independente por município',
        'area':'WGS84 geodésica por linha; sem reamostragem','nao_observado':[0,27],
        'tolerancia_paridade_estoques_ha':0.0001,
        'versoes':{n:importlib.metadata.version(n) for n in ('numpy','pandas','rasterio','geopandas','shapely','pyproj')}}
    fingerprint=hashlib.sha256(json.dumps(execucao,sort_keys=True).encode()).hexdigest()
    if args.saida.exists():
        if not args.retomar: raise FileExistsError('Saída já existe; use --retomar para validar checkpoints, sem sobrescrever.')
        antigo=json.loads((args.saida/'execucao.json').read_text(encoding='utf-8'))
        if antigo['fingerprint']!=fingerprint: raise ValueError('Protocolo mudou; escolher outra pasta de resultados.')
    else:
        args.saida.mkdir(parents=True)
        with (args.saida/'execucao.json').open('x',encoding='utf-8') as f: json.dump({'fingerprint':fingerprint,**execucao},f,ensure_ascii=False,indent=2)
    tarefas=[(int(r.CD_MUN),r.NM_MUN,r.SIGLA_UF,r.geometry.wkb,str(args.saida),fingerprint,args.bloco) for r in g.itertuples()]
    with ProcessPoolExecutor(max_workers=args.workers,initializer=iniciar,initargs=(m,anos,args.cache_mb)) as pool:
        futuros=[pool.submit(processar_municipio,t) for t in tarefas]
        for i,f in enumerate(as_completed(futuros),1):
            cd,status,segundos=f.result(); print(f'{i}/{len(tarefas)} {cd} {status} {segundos:.1f}s',flush=True)
    # Verificação de imutabilidade rápida ao final; hashes completos estão no manifesto.
    for ano in anos:
        info=m['rasters'][str(ano)]; st=(base/info['arquivo']).stat()
        if (st.st_size,st.st_mtime_ns)!=(info['bytes'],info['mtime_ns']): raise ValueError('Fonte alterada durante o cálculo.')
    consolidar(args.saida,codigos,anos,execucao)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifesto',type=Path,required=True); p.add_argument('--saida',type=Path,required=True)
    p.add_argument('--anos',nargs='+',type=int); p.add_argument('--municipios',nargs='+',type=int)
    p.add_argument('--workers',type=int,default=2); p.add_argument('--bloco',type=int,default=512)
    p.add_argument('--cache-mb',type=int,default=256); p.add_argument('--retomar',action='store_true')
    p.add_argument('--verificar-hashes',action='store_true')
    a=p.parse_args()
    if not 1<=a.workers<=4 or not 128<=a.bloco<=2048 or not 64<=a.cache_mb<=2048: p.error('Parâmetros de recursos fora dos limites.')
    executar(a)
