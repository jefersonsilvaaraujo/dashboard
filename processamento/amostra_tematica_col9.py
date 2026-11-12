"""Amostragem probabilística em dois estágios e inspeção dirigida, sem referência inventada."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window,from_bounds
from shapely import from_wkb

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import VN,UA,sha,csv_novo
from processamento.transicoes_col9 import aplicar_patch,ler_patch,area_linhas

SEMENTE=20261111
PRIORIDADES=[5103809,2109908,5107107,5105507,2102325]


def rng_chave(chave):
    n=int.from_bytes(hashlib.sha256(f'{SEMENTE}|{chave}'.encode()).digest()[:8],'little')
    return np.random.default_rng(n)


def periodo(ano):
    if ano<=1999: return '1986_1999'
    if ano<=2009: return '2000_2009'
    if ano<=2019: return '2010_2019'
    if ano<=2021: return '2020_2021'
    return str(ano)


def desenhar(q,est,n_por_estrato=2):
    if n_por_estrato<2: raise ValueError('Exigir dois conglomerados por estrato não censitário.')
    f=q.merge(est,on=['CD_MUN','ano_origem'],validate='one_to_one').sort_values(['CD_MUN','ano_origem'])
    f['periodo']=f.ano_destino.map(periodo)
    f['magnitude']=np.where(f.taxa_conversao_pct.lt(.5),'R_menor_0_5',np.where(f.taxa_conversao_pct.lt(2),'R_0_5_a_2','R_2_ou_mais'))
    f['estabilidade']=np.where(f.estabilidade_classe_pct.ge(95),'classe_igual_ge95','classe_igual_lt95')
    f['estrato']=f[['SIGLA_UF','periodo','magnitude','estabilidade']].agg('|'.join,axis=1)
    selecionados=[]; estratos=[]
    for nome,g in f.groupby('estrato',sort=True):
        n=min(n_por_estrato,len(g)); pos=rng_chave(nome).choice(len(g),size=n,replace=False)
        s=g.iloc[np.sort(pos)].copy(); s['N_psu_estrato']=len(g); s['n_psu_estrato']=n; s['pi_psu']=n/len(g)
        s['desenho']='probabilistica'; selecionados.append(s)
        estratos.append({'estrato':nome,'N_psu':len(g),'n_psu':n,'pi_psu':n/len(g)})
    probabilistica=pd.concat(selecionados,ignore_index=True)
    dirigidas=f[f.CD_MUN.isin(PRIORIDADES)&f.ano_origem.isin([2018,2019,2020,2021,2022])].copy()
    especiais=f[(f.CD_MUN.eq(5105507)&f.ano_origem.isin([1985,1986,1987]))|
                 (f.CD_MUN.eq(2102325)&f.ano_origem.isin([1999,2000,2001,2002,2003]))]
    dirigidas=pd.concat([dirigidas,especiais]).drop_duplicates(['CD_MUN','ano_origem']).copy()
    dirigidas['desenho']='dirigida'; dirigidas['pi_psu']=np.nan
    return f,probabilistica,dirigidas,pd.DataFrame(estratos)


def grupos_pixels(a,b,valido):
    n=np.isin(a,VN); u=np.isin(b,UA)
    return {'VN_UA':valido&n&u,'VN_outros':valido&n&~u,
            'outras_origens_UA':valido&~n&u,'outras_origens_outros':valido&~n&~u}


def selecionar_pixels(a,b,valido,n,chave):
    amostra=[]; info=[]
    for k,mask in grupos_pixels(a,b,valido).items():
        indices=np.flatnonzero(mask); total=len(indices); tamanho=min(n,total)
        info.append({'estrato_pixel':k,'N_pixels':total,'n_pixels':tamanho})
        if not total: continue
        escolhidos=rng_chave(f'{chave}|{k}').choice(total,size=tamanho,replace=False)
        for idx in indices[np.sort(escolhidos)]:
            linha,coluna=divmod(int(idx),a.shape[1])
            amostra.append({'linha_local':linha,'coluna_local':coluna,'estrato_pixel':k,
                'N_pixels_estrato':total,'n_pixels_estrato':tamanho,'pi_pixel_condicional':tamanho/total})
    return amostra,info


def processar(tarefa):
    cd,t,wkb,desenho,pi,estrato,manifesto,n,contagem_esperada,conv_esperada=tarefa
    m=json.loads(Path(manifesto).read_text(encoding='utf-8')); base=Path(m['base_dados']); geom=from_wkb(wkb)
    with rasterio.Env(GDAL_CACHEMAX=512*1024*1024):
        with rasterio.open(base/m['rasters'][str(t)]['arquivo']) as src:
            w=from_bounds(*geom.bounds,src.transform)
            x0=max(0,int(np.floor(w.col_off))); y0=max(0,int(np.floor(w.row_off)))
            x1=min(src.width,int(np.ceil(w.col_off+w.width))); y1=min(src.height,int(np.ceil(w.row_off+w.height)))
            janela=Window(x0,y0,x1-x0,y1-y0); tr=src.window_transform(janela)
            dentro=geometry_mask([geom],out_shape=(y1-y0,x1-x0),transform=tr,invert=True,all_touched=False)
            pesos=area_linhas(tr,y1-y0)
        anos=[t,t+1]; arrays=[]; validos=[]
        def ler(ano):
            with rasterio.open(base/m['rasters'][str(ano)]['arquivo']) as s:
                a=s.read(1,window=janela); v=s.read_masks(1,window=janela)>0
                if cd in m['complemento']['municipios'] and ano!=2002:
                    with rasterio.open(base/m['complemento']['arquivo']) as p:
                        banda=list(p.descriptions).index(f'classification_{ano}')+1
                        patch=ler_patch(p,banda,janela,m['complemento']['offset_col_linha'])
                    a,_,div=aplicar_patch(a,patch,dentro)
                    if div: raise ValueError('Complemento divergente.')
                    # NoData do arquivo original não invalida os zeros recuperados.
                    v|=(patch!=0)&(patch!=27)&dentro
                return a,dentro&v&(a!=0)&(a!=27)
        for ano in anos:
            a,v=ler(ano); arrays.append(a); validos.append(v)
        a,b=arrays; valido=validos[0]&validos[1]
        grupos=grupos_pixels(a,b,valido)
        if int(valido.sum())!=contagem_esperada or int(grupos['VN_UA'].sum())!=conv_esperada:
            raise ValueError(f'{cd}/{t}: amostra não reproduz o suporte consolidado.')
        amostra,info=selecionar_pixels(a,b,valido,n,f'{desenho}|{cd}|{t}')
        for r in amostra:
            lin,col=r.pop('linha_local'),r.pop('coluna_local')
            lon,lat=rasterio.transform.xy(tr,lin,col)
            p=r['pi_pixel_condicional']*pi if desenho=='probabilistica' else np.nan
            r.update({'id':f'{desenho[:1]}_{cd}_{t}_{y0+lin}_{x0+col}',
                'CD_MUN':cd,'ano_origem':t,'ano_destino':t+1,'desenho':desenho,'estrato_psu':estrato,
                'pi_psu':pi,'pi_inclusao':p,'linha_raster':y0+lin,'coluna_raster':x0+col,
                'longitude':lon,'latitude':lat,'area_pixel_ha':float(pesos[lin]),
                'peso_expansao_ha':float(pesos[lin])/p if p>0 else np.nan,
                'classe_t':int(a[lin,col]),'classe_t1':int(b[lin,col])})
        # Contexto local anterior/posterior: apenas diagnóstico, nunca preditor.
        for ano,coluna in [(t-1,'classe_t_menos1'),(t+2,'classe_t_mais2')]:
            if 1985<=ano<=2023:
                with rasterio.open(base/m['rasters'][str(ano)]['arquivo']) as s:
                    for r in amostra:
                        j=Window(r['coluna_raster'],r['linha_raster'],1,1)
                        v=int(s.read(1,window=j)[0,0])
                        if v==0 and cd in m['complemento']['municipios'] and ano!=2002:
                            with rasterio.open(base/m['complemento']['arquivo']) as psrc:
                                banda=list(psrc.descriptions).index(f'classification_{ano}')+1
                                v=int(ler_patch(psrc,banda,j,m['complemento']['offset_col_linha'])[0,0])
                        r[coluna]=v if v not in (0,27,s.nodata) else None
            else:
                for r in amostra: r[coluna]=None
        for r in amostra:
            r['origem_persiste_desde_t_menos1']=None if r['classe_t_menos1'] is None else r['classe_t_menos1']==r['classe_t']
            r['destino_persiste_em_t_mais2']=None if r['classe_t_mais2'] is None else r['classe_t_mais2']==r['classe_t1']
        for r in info: r.update({'CD_MUN':cd,'ano_origem':t,'desenho':desenho})
        return amostra,info


def executar(resultados,limiares,manifesto,saida,workers=2):
    if saida.exists(): raise FileExistsError('Amostra anterior preservada.')
    q=pd.read_csv(resultados/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    est=pd.read_csv(limiares/'estabilidade_municipio_par.csv',sep=';',encoding='utf-8-sig')
    frame,prob,dirig,estratos=desenhar(q,est)
    saida.mkdir(parents=True)
    for nome,d in [('universo',frame),('psu_probabilisticas',prob),('psu_dirigidas',dirig),('estratos',estratos)]: csv_novo(d,saida/f'{nome}.csv')
    protocolo={'semente':SEMENTE,'n_psu_por_estrato':2,'n_pixels_por_subestrato':4,
        'periodos':['1986_1999','2000_2009','2010_2019','2020_2021','2022','2023'],
        'regiao':'UF: MA,MT,PA,RO,TO','magnitude':'R<0.5; 0.5<=R<2; R>=2 (desenho, não alvo)',
        'estabilidade':'diagonal/área comum >=95% ou <95% (códigos, não acurácia)',
        'pixel_estratos':['VN_UA','VN_outros','outras_origens_UA','outras_origens_outros'],
        'pi':'n_h/N_h × n_hjk/N_hjk; SRS sem reposição em ambos os estágios',
        'unidade_inferencia':'área-pixel-par em suporte comum, 255 municípios, 38 pares',
        'sem_precisao_pre_garantida':'piloto estratificado; IC requer desenho por conglomerados e respostas independentes',
        'codigo_sha256':sha(Path(__file__)),'manifesto_rasters_sha256':sha(manifesto),
        'resultados_sha256':sha(resultados/'concluido.json'),'n_psu_probabilisticas':len(prob),'n_psu_dirigidas':len(dirig)}
    (saida/'protocolo_pre_sorteio_pixels.json').write_text(json.dumps(protocolo,ensure_ascii=False,indent=2),encoding='utf-8')
    m=json.loads(manifesto.read_text(encoding='utf-8')); g=gpd.read_file(Path(m['base_dados'])/m['territorio']['arquivo']).set_index('CD_MUN')
    geoms={int(cd):row.geometry.wkb for cd,row in g.iterrows()}
    tarefas=[]
    for df in (prob,dirig):
        for r in df.itertuples():
            tarefas.append((int(r.CD_MUN),int(r.ano_origem),geoms[int(r.CD_MUN)],r.desenho,float(r.pi_psu),
                r.estrato,str(manifesto.resolve()),4,int(r.pixels_comuns),int(r.pixels_convertidos)))
    linhas=[]; info=[]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        fs=[pool.submit(processar,t) for t in tarefas]
        for i,f in enumerate(as_completed(fs),1):
            a,b=f.result(); linhas+=a; info+=b; print(f'{i}/{len(tarefas)} unidades amostradas',flush=True)
    pontos=pd.DataFrame(linhas).sort_values('id')
    csv_novo(pontos,saida/'pontos_com_contexto_mapeado.csv')
    csv_novo(pd.DataFrame(info).sort_values(['desenho','CD_MUN','ano_origem','estrato_pixel']),saida/'subestratos_pixels.csv')
    # Ficha cega não revela classes MapBiomas, magnitude ou cenário ao intérprete.
    cego=pontos[['id','longitude','latitude','ano_origem','ano_destino']].copy()
    for col in ['referencia_t','referencia_t1','data_imagem_t','data_imagem_t1','fonte','interprete','evidencia_arquivo','justificativa']:
        cego[col]=''
    cego['situacao']='pendente_referencia'; csv_novo(cego,saida/'fichas_cegas.csv')
    registro={'pontos':len(pontos),'probabilisticos':int(pontos.desenho.eq('probabilistica').sum()),
        'dirigidos':int(pontos.desenho.eq('dirigida').sum()),'sem_acuracia_estimada':True,
        'arquivos_sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}}
    (saida/'concluido_amostragem.json').write_text(json.dumps(registro,indent=2),encoding='utf-8')
    print(json.dumps(registro,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('resultados','limiares','manifesto','saida'): p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--workers',type=int,choices=(1,2),default=2)
    a=p.parse_args(); executar(a.resultados,a.limiares,a.manifesto,a.saida,a.workers)
