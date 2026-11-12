"""Consulta STAC e recorta imagens públicas para inspeção dirigida, sem gerar rótulos."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from functools import lru_cache
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
from PIL import Image,ImageDraw
from pyproj import Transformer
import rasterio
from rasterio.windows import Window

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import sha,csv_novo

EARTH='https://earth-search.aws.element84.com/v1/search'
PC='https://planetarycomputer.microsoft.com/api/stac/v1/search'


def obter_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'DefesaMestrado-validacao-cientifica/1.0'})
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req,timeout=35) as f: return json.load(f)
        except HTTPError as e:
            if e.code not in (429,500,502,503,504) or tentativa==2: raise
            time.sleep(1+tentativa)


@lru_cache(maxsize=1024)
def token_container(conta,container):
    return obter_json(f'https://planetarycomputer.microsoft.com/api/sas/v1/token/{conta}/{container}')['token']


def assinar(h):
    p=urllib.parse.urlparse(h)
    if not p.netloc.endswith('.blob.core.windows.net'): return h
    conta=p.netloc.split('.')[0]; container=p.path.strip('/').split('/')[0]
    return h+'?'+token_container(conta,container)


def consulta(lon,lat,ano,landsat=False):
    params={'collections':'landsat-c2-l2' if landsat else 'sentinel-2-l2a',
        'intersects':json.dumps({'type':'Point','coordinates':[lon,lat]}),
        'datetime':f'{ano}-01-01T00:00:00Z/{ano}-12-31T23:59:59Z' if landsat else f'{ano}-05-01T00:00:00Z/{ano}-10-31T23:59:59Z',
        'limit':8,'query':json.dumps({'eo:cloud_cover':{'lt':30}})}
    if landsat: params['sortby']='+eo:cloud_cover'
    url=(PC if landsat else EARTH)+'?'+urllib.parse.urlencode(params)
    d=obter_json(url)
    d['features']=sorted(d.get('features',[]),key=lambda z:(z['properties'].get('eo:cloud_cover',100),z['id']))
    return url,d


def ler_chip(item,lon,lat,landsat):
    chave='red' if landsat else 'visual'; href=item['assets'][chave]['href']
    def href_leitura(h):
        # Assinatura pública de leitura permanece apenas em memória, nunca no manifesto.
        return assinar(h) if landsat else h
    with rasterio.open(href_leitura(href)) as s:
        x,y=Transformer.from_crs(4326,s.crs,always_xy=True).transform(lon,lat)
        lin,col=s.index(x,y); metade=32 if landsat else 64
        win=Window(col-metade,lin-metade,2*metade,2*metade)
        tr=s.window_transform(win); crs=s.crs
        a=s.read(1 if landsat else [1,2,3],window=win,boundless=True,fill_value=0)
        if landsat:
            bandas=[a]
            for k in ('green','blue'):
                with rasterio.open(href_leitura(item['assets'][k]['href'])) as b: bandas.append(b.read(1,window=win,boundless=True,fill_value=0))
            raw=np.stack(bandas); reflectancia=raw.astype(float)*.0000275-.2
            rgb=np.clip(reflectancia/.3*255,0,255).astype('uint8')
        else: raw=a; rgb=a.astype('uint8')
    qa_key='qa_pixel' if landsat else 'scl'
    with rasterio.open(href_leitura(item['assets'][qa_key]['href'])) as qs:
        qx,qy=Transformer.from_crs(4326,qs.crs,always_xy=True).transform(lon,lat)
        qlin,qcol=qs.index(qx,qy); v=int(qs.read(1,window=Window(qcol,qlin,1,1))[0,0])
    ruim=bool(v & ((1<<0)|(1<<1)|(1<<3)|(1<<4)|(1<<5))) if landsat else v not in (4,5,6)
    return raw,rgb,{'crs':str(crs),'transform':list(tr)[:6],'qa_centro':v,'qa_centro_inadequada':ruim,
        'resolucao_m':float(abs(tr.a)),'largura_m':float(abs(tr.a)*rgb.shape[2]),'href_sem_token':href}


def executar_ponto(r,saida):
    pasta=saida/r['id']; pasta.mkdir()
    anos=sorted(set(a for a in (r['ano_origem']-1,r['ano_origem'],r['ano_destino'],r['ano_destino']+1) if 1985<=a<=2023))
    evidencias=[]; paineis=[]
    for ano in anos:
        meta={'ano':ano,'id_ponto':r['id'],'longitude':r['longitude'],'latitude':r['latitude']}
        try:
            landsat=ano<2016
            url,catalogo=consulta(r['longitude'],r['latitude'],ano,landsat)
            arquivo=pasta/f'catalogo_{ano}.json'; arquivo.write_text(json.dumps(catalogo,ensure_ascii=False),encoding='utf-8')
            meta.update({'consulta':url,'catalogo_sha256':sha(arquivo),'n_candidatos_consultados':len(catalogo.get('features',[])),
                'fonte':'Landsat/USGS via Planetary Computer' if landsat else 'Sentinel-2/ESA via Earth Search'})
            erros=[]; escolhido=None
            for item in catalogo.get('features',[])[:3]:
                try:
                    raw,rgb,qual=ler_chip(item,r['longitude'],r['latitude'],landsat)
                    if qual['qa_centro_inadequada']: erros.append({'item':item['id'],'motivo':'QA central inadequada','QA':qual['qa_centro']}); continue
                    escolhido=(item,raw,rgb,qual); break
                except Exception as e:
                    # Não registrar URLs de exceções GDAL que possam conter SAS.
                    erros.append({'item':item['id'],'motivo':type(e).__name__,'http_status':getattr(e,'code',None)})
            meta['tentativas']=erros
            if escolhido is None:
                meta['situacao']='sem_recorte_adequado_nesta_consulta'
            else:
                item,raw,rgb,qual=escolhido
                p=pasta/f'chip_{ano}.npz'
                with p.open('xb') as f: np.savez_compressed(f,bandas=raw)
                meta.update({'situacao':'recorte_para_interpretacao','item':item['id'],
                    'data_imagem':item['properties']['datetime'],'nuvens_cena_pct':item['properties'].get('eo:cloud_cover'),
                    'chip_sha256':sha(p),**qual})
                im=Image.fromarray(np.moveaxis(rgb,0,2)).resize((384,384),Image.Resampling.NEAREST)
                dr=ImageDraw.Draw(im); dr.rectangle((187,187,197,197),outline='white',width=1)
                im.save(pasta/f'visual_{ano}.png')
                paineis.append((ano,im,meta['data_imagem'][:10],qual['resolucao_m']))
        except Exception as e: meta.update({'situacao':'consulta_indisponivel','erro_tipo':type(e).__name__,'http_status':getattr(e,'code',None)})
        evidencias.append(meta)
    if paineis:
        painel=Image.new('RGB',(384*len(paineis),445),'white'); dr=ImageDraw.Draw(painel)
        for i,(ano,im,data,res) in enumerate(paineis):
            painel.paste(im,(i*384,45)); dr.text((i*384+6,8),f'{ano} | {data} | {res:g} m',fill='black')
        dr.text((5,430),f"{r['id']} | marcador central: localizacao; nao delimita o pixel MapBiomas",fill='black')
        painel.save(pasta/'painel_referencia.png')
    registro={'ponto':r,'consulta_em_utc':datetime.now(timezone.utc).isoformat(),'evidencias':evidencias,
              'sem_rotulo_independente':True,'dependencia':'Sentinel: sensor distinto; Landsat: mesmo tipo de sensor do MapBiomas, interpretação ainda pendente'}
    (pasta/'evidencias.json').write_text(json.dumps(registro,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    return [{'id':r['id'],'CD_MUN':r['CD_MUN'],'ano_origem':r['ano_origem'],**{k:v for k,v in e.items() if k not in ('tentativas','consulta')}} for e in evidencias]


def executar(amostra,saida,historicos=False):
    if saida.exists(): raise FileExistsError('Referências anteriores preservadas.')
    p=pd.read_csv(amostra/'pontos_com_contexto_mapeado.csv',sep=';',encoding='utf-8-sig')
    d=p[p.desenho.eq('dirigida')]; selecao=[]
    for (_,t),g in d[d.ano_origem.isin([2019,2021,2022])].groupby(['CD_MUN','ano_origem']):
        conv=g[g.estrato_pixel.eq('VN_UA')].sort_values(['classe_t','id'])
        selecao.append(conv.iloc[0])
        if t==2022: selecao.append(g[g.estrato_pixel.eq('VN_outros')].sort_values('id').iloc[0])
    for cd,t in [(2102325,2001),(2102325,2002),(5105507,1985),(5105507,1986)]:
        selecao.append(d[d.CD_MUN.eq(cd)&d.ano_origem.eq(t)&d.estrato_pixel.eq('VN_UA')].sort_values('id').iloc[0])
    pontos=pd.DataFrame(selecao).drop_duplicates('id')
    if historicos: pontos=pontos[pontos.ano_origem.lt(2016)]
    saida.mkdir(parents=True)
    csv_novo(pontos,saida/'selecao_dirigida_referencias.csv')
    todos=[]
    # Env GDAL é estabelecido no thread principal; leituras independentes por arquivo.
    with rasterio.Env(GDAL_HTTP_TIMEOUT='30',GDAL_HTTP_MAX_RETRY='1',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with ThreadPoolExecutor(max_workers=1 if historicos else 3) as pool:
            registros=json.loads(pontos.to_json(orient='records',double_precision=15))
            fs=[pool.submit(executar_ponto,r,saida) for r in registros]
            for i,f in enumerate(as_completed(fs),1):
                todos+=f.result(); print(f'{i}/{len(fs)} dossiês públicos registrados',flush=True)
    csv_novo(pd.DataFrame(todos).sort_values(['id','ano']),saida/'inventario_evidencias.csv')
    manifesto={'codigo_sha256':sha(Path(__file__)),'desenho':'inspeção dirigida; não usar para acurácia representativa',
        'janela':'Sentinel maio a outubro; Landsat janeiro a dezembro; nuvens de cena <30%; até 8 cenas candidatas, até 3 tentadas; não busca exaustiva',
        'historicos_somente':historicos,
        'QA':'Sentinel SCL centro em 4/5/6; Landsat QA_PIXEL sem fill/dilated/cloud/shadow/snow',
        'limitacoes':'QA central não garante toda a janela limpa; data de cena não coincide necessariamente com estado anual; nenhum rótulo automático',
        'arquivos_sha256':{str(p.relative_to(saida)):sha(p) for p in saida.rglob('*') if p.is_file()}}
    (saida/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')
    print(pd.DataFrame(todos).situacao.value_counts().to_string(),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--amostra',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); p.add_argument('--historicos',action='store_true')
    a=p.parse_args(); executar(a.amostra,a.saida,a.historicos)
