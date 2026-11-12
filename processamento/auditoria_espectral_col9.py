"""Confronto espectral automatizado de casos dirigidos anteriores, sem interpretação.

Reutiliza exatamente as cenas selecionadas no checkpoint anterior; não procura
cenas que concordem com a conversão. NDVI não fornece rótulo de uso da terra.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

from affine import Affine
import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio
from rasterio.windows import Window,from_bounds
from shapely.geometry import Polygon,box,mapping
from shapely import transform as transformar

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha,csv_novo
from processamento.referencias_tematica_col9 import assinar


def projetar(fn,geom):
    return transformar(geom,fn,interleaved=False)


def deduplicar_tarefas(tarefas):
    unicos={};repetidos=[]
    for t in tarefas:
        chave=(t[0]['id'],int(t[1]['ano']))
        if chave in unicos:
            anterior=unicos[chave]
            if anterior[2]['id']!=t[2]['id']:
                raise ValueError('Mais de uma cena distinta para ponto/ano: seleção explícita necessária.')
            repetidos.append({'id':chave[0],'ano':chave[1],'cena':t[2]['id'],
                'catalogo_usado':str(anterior[3]),'catalogo_repetido':str(t[3])})
        else:unicos[chave]=t
    return list(unicos.values()),repetidos


def calibrar(dados,asset,landsat):
    bandas=asset.get('raster:bands',[])
    b=bandas[0] if bandas else {}
    if 'scale' not in b or 'offset' not in b:
        if not landsat:raise ValueError('Calibração Sentinel não documentada no asset.')
        escala,offset=.0000275,-.2
        origem='USGS Collection2 L2: fator0.0000275, offset-0.2'
    else:
        escala,offset=float(b['scale']),float(b['offset']);origem='raster:bands do asset STAC arquivado'
    return dados.astype(float)*escala+offset,{'scale':escala,'offset':offset,'origem':origem}


def extrair(tarefa,saida,transform):
    p,e,item,catalogo=tarefa;idp=p['id'];ano=int(e['ano'])
    if not 1985<=ano<=2023:raise ValueError('Ano não autorizado.')
    out={'id':idp,'CD_MUN':p['CD_MUN'],'ano':ano,'ano_t':p['ano_origem'],'ano_t1':p['ano_destino'],
         'classe_t':p['classe_t'],'classe_t1':p['classe_t1'],'cena':item['id'],
         'data_imagem':e['data_imagem'],'catalogo_sha256':sha(catalogo),
         'desenho':'dirigido_preexistente_sem_inferencia','tipo_evidencia':'proxy_espectral_sem_rotulo_tematico'}
    landsat='landsat' in item.get('collection','').lower() or item['id'].startswith(('LT','LE','LC'))
    out['sensor']='Landsat' if landsat else 'Sentinel-2'
    prefix=saida/(idp+'_'+str(ano));assets=item['assets']
    keynir='nir08' if landsat else 'nir'
    urls={k:assets[k]['href'] for k in ['red',keynir,'qa_pixel' if landsat else 'scl']}
    def abrir(k):return rasterio.open(assinar(urls[k]) if landsat else urls[k])
    row,col=p['linha_raster'],p['coluna_raster']
    geo=Polygon([transform*(col,row),transform*(col+1,row),transform*(col+1,row+1),transform*(col,row+1)])
    with rasterio.Env(GDAL_HTTP_TIMEOUT=25,GDAL_HTTP_MAX_RETRY=1,GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with abrir('red') as s:
            trans=Transformer.from_crs(4326,s.crs,always_xy=True)
            pol=projetar(trans.transform,geo)
            w=from_bounds(*pol.bounds,s.transform)
            r0,c0=int(np.floor(w.row_off)),int(np.floor(w.col_off))
            r1,c1=int(np.ceil(w.row_off+w.height)),int(np.ceil(w.col_off+w.width))
            win=Window(c0,r0,c1-c0,r1-r0)
            rawr=s.read(1,window=win,boundless=True,fill_value=0);tr=s.window_transform(win);crs=s.crs
            weights=np.array([[pol.intersection(box(*(tr*(c,r+1)),*(tr*(c+1,r)))).area
                              for c in range(rawr.shape[1])] for r in range(rawr.shape[0])])
        with abrir(keynir) as s:
            if s.crs!=crs or s.transform!=Affine(tr.a,tr.b,tr.c-c0*tr.a,tr.d,tr.e,tr.f-r0*tr.e):
                # grade é comparada independentemente da representação reconstruída
                if s.window_transform(win)!=tr:raise ValueError('Grades red/nir divergentes.')
            rawn=s.read(1,window=win,boundless=True,fill_value=0)
        qkey='qa_pixel' if landsat else 'scl'
        with abrir(qkey) as s:
            polq=projetar(Transformer.from_crs(crs,s.crs,always_xy=True).transform,pol)
            w=from_bounds(*polq.bounds,s.transform)
            qr,qc=int(np.floor(w.row_off)),int(np.floor(w.col_off))
            qh=int(np.ceil(w.row_off+w.height))-qr;qw=int(np.ceil(w.col_off+w.width))-qc
            qwin=Window(qc,qr,qw,qh);qa=s.read(1,window=qwin,boundless=True,fill_value=0)
            qtr=s.window_transform(qwin)
            qwgt=np.array([[polq.intersection(box(*(qtr*(c,r+1)),*(qtr*(c+1,r)))).area
                           for c in range(qa.shape[1])] for r in range(qa.shape[0])])
            bom=(((qa & sum(1<<b for b in (0,1,2,3,4,5)))==0)&(qa>0)) if landsat else np.isin(qa,[4,5,6])
            qa_frac=float(qwgt[bom].sum()/qwgt.sum())
        rr,calr=calibrar(rawr,assets['red'],landsat);nn,caln=calibrar(rawn,assets[keynir],landsat)
        ok=(rawr>0)&(rawn>0)&(weights>0)&(rr>=0)&(nn>=0)&((nn+rr)>0)
        ndvi=np.divide(nn-rr,nn+rr,out=np.full(rr.shape,np.nan),where=ok)
        valido=float(weights[ok].sum()/weights.sum())
        valor=float(np.sum(ndvi[ok]*weights[ok])/weights[ok].sum()) if ok.any() else None
    np.savez_compressed(str(prefix)+'_dados.npz',red_DN=rawr,nir_DN=rawn,QA=qa,
                        pesos_intersecao_m2=weights,QA_pesos_m2=qwgt,NDVI=ndvi)
    meta={'item':item,'URLs_sem_assinatura':urls,'crs':str(crs),'transform':list(tr)[:6],
          'transform_QA':list(qtr)[:6],'pixel_col9_projetado':mapping(pol),
          'calibracao_red':calr,'calibracao_nir':caln,'saturacao':'QA_RADSAT não lido: limitação remanescente.',
          'dados_sha256':sha(Path(str(prefix)+'_dados.npz'))}
    Path(str(prefix)+'_fonte.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    out.update(situacao='calculado',NDVI_medio_footprint=valor,fracao_reflectancia_valida=valido,
               fracao_QA_adequada=qa_frac,QA_footprint_completo=qa_frac>=1-1e-9,
               fonte_json=Path(str(prefix)+'_fonte.json').name,
               evidencias='Proxy de vigor/estrutura/sazonalidade; nunca confirma manejo ou origem nativa por si só.')
    return out


def executar(checkpoint,saida):
    if saida.exists():raise FileExistsError('Saída anterior preservada.')
    saida.mkdir(parents=True)
    mani=json.loads((PROJETO/'referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    tr=Affine(*mani['rasters']['1985']['grade']['transform'])
    tarefas=[]
    for nome in ['referencias_v2','referencias_historicas_v3']:
        for p in sorted((checkpoint/nome).glob('*/evidencias.json')):
            d=json.loads(p.read_text(encoding='utf-8'))
            for e in d['evidencias']:
                if not e.get('item'):continue
                cat=p.parent/f"catalogo_{e['ano']}.json"
                if sha(cat)!=e['catalogo_sha256']:raise ValueError('Catálogo anterior divergiu.')
                itens=json.loads(cat.read_text(encoding='utf-8')).get('features',[])
                it=next(i for i in itens if i['id']==e['item'])
                tarefas.append((d['ponto'],e,it,cat))
    tarefas,repetidos=deduplicar_tarefas(tarefas)
    out=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(extrair,t,saida,tr):t for t in tarefas}
        for f in as_completed(futures):
            t=futures[f]
            try:r=f.result()
            except Exception as exc:
                # Não registrar mensagens de bibliotecas que possam conter SAS temporário.
                r={'id':t[0]['id'],'CD_MUN':t[0]['CD_MUN'],'ano':t[1]['ano'],
                   'ano_t':t[0]['ano_origem'],'ano_t1':t[0]['ano_destino'],'situacao':'inconclusivo_falha_consulta',
                   'tipo_erro':type(exc).__name__,'sem_rotulo_tematico':True}
            out.append(r);print(f"Espectral {len(out)}/{len(tarefas)} {r['ano']}: {r['situacao']}",flush=True)
    d=pd.DataFrame(out).sort_values(['id','ano']);csv_novo(d,saida/'NDVI_cenas.csv')
    pares=[]
    for idp,g in d.groupby('id'):
        t=int(g.ano_t.iloc[0]);g=g.set_index('ano');r={'id':idp,'CD_MUN':int(g.CD_MUN.iloc[0]),'ano_t':t,'ano_t1':t+1}
        if t not in g.index or t+1 not in g.index:
            r['situacao']='inconclusivo_cena_ausente'
        else:
            a,b=g.loc[t],g.loc[t+1]
            if a.situacao!='calculado' or b.situacao!='calculado':r['situacao']='inconclusivo_falha_consulta'
            else:
                da,db=pd.Timestamp(a.data_imagem),pd.Timestamp(b.data_imagem)
                dias=abs(da.dayofyear-db.dayofyear);dias=min(dias,366-dias)
                r.update(distancia_sazonal_dias=dias,NDVI_t=a.NDVI_medio_footprint,NDVI_t1=b.NDVI_medio_footprint,
                         delta_NDVI=b.NDVI_medio_footprint-a.NDVI_medio_footprint)
                r['situacao']='proxy_comparavel_sem_adjudicacao' if (
                    dias<=45 and a.sensor==b.sensor and a.QA_footprint_completo and b.QA_footprint_completo
                    and a.fracao_reflectancia_valida>=.999 and b.fracao_reflectancia_valida>=.999
                    ) else 'inconclusivo_sazonalidade_QA_suporte_ou_sensor'
        r['limite']='DeltaNDVI não identifica uso antrópico, corte ou relevância ambiental; amostra dirigida.'
        pares.append(r)
    csv_novo(pd.DataFrame(pares),saida/'NDVI_pares.csv')
    (saida/'manifesto_espectral.json').write_text(json.dumps({'executado_utc':datetime.now(timezone.utc).isoformat(),
        'n_cenas_previas':len(tarefas),'sem_nova_interpretacao_humana':True,'sem_rotulo_automatico_de_conversao':True,
        'mesmas_cenas_repetidas_em_catalogos':repetidos,
        'selecao':'Mesmas cenas escolhidas e arquivadas no checkpoint anterior, sem otimização de concordância.',
        'protocolo':'NDVI com reflectância calibrada por asset; média ponderada pela interseção do pixel Col9. QA de todo footprint; comparação sazonal≤45dias e mesma família de sensor. Limite QA_RADSAT e atmosfera residual.',
        'arquivos':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True);a=p.parse_args();executar(a.checkpoint,a.saida)
