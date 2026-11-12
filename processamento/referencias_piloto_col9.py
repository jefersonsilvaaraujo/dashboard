"""Referências cegas do piloto: cenas georreferenciadas, QA do footprint e lacunas explícitas."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import urllib.parse

import numpy as np
import pandas as pd
from affine import Affine
from PIL import Image,ImageDraw
from pyproj import Transformer
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha,csv_novo
from processamento.referencias_tematica_col9 import obter_json,assinar,ler_chip,token_container,EARTH,PC


def validar_ano(ano):
    if not 1985<=ano<=2023: raise ValueError('Referências limitadas a 1985–2023; 2024 reservado.')


def consulta(lon,lat,ano,landsat,janela):
    validar_ano(ano)
    inicio,fim=('01-01','12-31') if landsat else (('11-01','12-31') if janela=='fim_ano' else ('05-01','10-31'))
    params={'collections':'landsat-c2-l2' if landsat else 'sentinel-2-l2a',
        'intersects':json.dumps({'type':'Point','coordinates':[lon,lat]}),
        'datetime':f'{ano}-{inicio}T00:00:00Z/{ano}-{fim}T23:59:59Z',
        'limit':24,'query':json.dumps({'eo:cloud_cover':{'lt':60}})}
    if landsat: params['sortby']='+eo:cloud_cover'
    url=(PC if landsat else EARTH)+'?'+urllib.parse.urlencode(params)
    d=obter_json(url)
    itens=sorted(d.get('features',[]),key=(lambda x:x['properties']['datetime']) if janela=='fim_ano'
                 else (lambda x:x['properties'].get('eo:cloud_cover',100)),reverse=janela=='fim_ano')
    return url,d,itens


def qualidade_footprint(item,cantos,landsat):
    href=item['assets']['qa_pixel' if landsat else 'scl']['href']
    with rasterio.open(assinar(href) if landsat else href) as s:
        proj=Transformer.from_crs(4326,s.crs,always_xy=True)
        pol=[proj.transform(x,y) for x,y in cantos]; x,y=zip(*pol)
        i0,j0=s.index(min(x),max(y)); i1,j1=s.index(max(x),min(y))
        janela=Window(min(j0,j1)-1,min(i0,i1)-1,abs(j1-j0)+3,abs(i1-i0)+3)
        a=s.read(1,window=janela,boundless=True,fill_value=0)
        mascara=s.read_masks(1,window=janela,boundless=True)>0
        tr=s.window_transform(janela)
        dentro=geometry_mask([{'type':'Polygon','coordinates':[pol+[pol[0]]]}],out_shape=a.shape,
            transform=tr,invert=True,all_touched=True)
        bons=(a & sum(1<<i for i in (0,1,2,3,4,5)))==0 if landsat else np.isin(a,[4,5,6])
        bons &= mascara
        n=int(dentro.sum()); frac=float(bons[dentro].mean()) if n else 0
    return {'n_celulas_QA_footprint':n,'fracao_QA_adequada_footprint':frac,
        'criterio':'Todas as células QA que tocam o footprint sem flags ruins; não é acurácia temática.'}


def prancha(imagens,cantos,pasta):
    placas=[]
    for e,rgb in imagens:
        im=Image.fromarray(np.moveaxis(rgb,0,2)); tr=Affine(*e['transform']); inv=~tr
        proj=Transformer.from_crs(4326,e['crs'],always_xy=True)
        pol=[inv*proj.transform(x,y) for x,y in cantos]
        cx=sum(x for x,y in pol)/4; cy=sum(y for x,y in pol)/4
        ctx=im.resize((360,360),Image.Resampling.NEAREST)
        ImageDraw.Draw(ctx).polygon([(360*x/im.width,360*y/im.height) for x,y in pol],outline='yellow',width=1)
        raio=max(5,round(100/e['resolucao_m'])); x0,y0=int(cx)-raio,int(cy)-raio
        zoom=im.crop((x0,y0,x0+2*raio,y0+2*raio)).resize((360,360),Image.Resampling.NEAREST)
        ImageDraw.Draw(zoom).polygon([((x-x0)*360/(2*raio),(y-y0)*360/(2*raio)) for x,y in pol],outline='yellow',width=2)
        p=Image.new('RGB',(376,780),'white'); draw=ImageDraw.Draw(p)
        draw.text((6,6),f"{e['data_imagem'][:10]} | {e['sensor']} | {e['resolucao_m']:g} m",fill='black')
        p.paste(ctx,(8,30)); p.paste(zoom,(8,402)); draw.text((6,765),'Amarelo: pixel avaliado; abaixo: zoom',fill='black')
        placas.append(p)
    if not placas:
        p=Image.new('RGB',(752,300),'white'); draw=ImageDraw.Draw(p)
        draw.text((20,40),'Sem recorte adequado nas consultas documentadas.',fill='black')
        draw.text((20,70),'Manter o caso. Registrar inconclusivo; solicitar complemento.',fill='black')
    else:
        p=Image.new('RGB',(376*len(placas),780),'white')
        for i,placa in enumerate(placas): p.paste(placa,(376*i,0))
    p.save(pasta/'prancha.png')


def processar(r,tr_mb,saida,fingerprint):
    pasta=saida/r['caso']; pronto=pasta/'concluido.json'
    if pronto.exists():
        d=json.loads(pronto.read_text(encoding='utf-8'))
        if d['fingerprint']!=fingerprint: raise ValueError('Protocolo mudou; escolher novo lote.')
        for n,h in d['sha256'].items():
            if sha(pasta/n)!=h: raise ValueError('Recorte anterior divergente.')
        return d['resumo']
    if pasta.exists(): raise FileExistsError('Tentativa parcial preservada: '+str(pasta))
    pasta.mkdir(parents=True)
    col,lin=int(r['coluna_raster']),int(r['linha_raster'])
    cantos=[tr_mb*(col,lin),tr_mb*(col+1,lin),tr_mb*(col+1,lin+1),tr_mb*(col,lin+1)]
    poligono={'type':'Feature','properties':{'caso':r['caso']},'geometry':{'type':'Polygon','coordinates':[cantos+[cantos[0]]]}}
    (pasta/'pixel.geojson').write_text(json.dumps(poligono),encoding='utf-8')
    evid=[]; imagens=[]
    with rasterio.Env(GDAL_HTTP_TIMEOUT='25',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_CACHEMAX=128*1024*1024):
        for ano in (int(r['ano_origem']),int(r['ano_destino'])):
            for janela in (['principal','fim_ano'] if ano>=2020 else ['principal']):
                e={'caso':r['caso'],'ano':ano,'janela':janela,'situacao':'sem_recorte_adequado_nesta_busca','tentativas':[]}
                fontes=[False,True] if ano>=2016 and janela=='principal' else [ano<2016]
                for landsat in fontes:
                    try:
                        url,cat,itens=consulta(r['longitude'],r['latitude'],ano,landsat,janela)
                        nome=f'catalogo_{ano}_{janela}_{"landsat" if landsat else "sentinel"}.json'
                        (pasta/nome).write_text(json.dumps(cat,ensure_ascii=False),encoding='utf-8')
                        e.setdefault('consultas',[]).append({'url':url,'catalogo':nome,'sha256':sha(pasta/nome),
                            'n_retornados':len(itens),'limite_tentativas':6})
                        for item in itens[:6]:
                            try:
                                q=qualidade_footprint(item,cantos,landsat)
                                if q['fracao_QA_adequada_footprint']<1:
                                    e['tentativas'].append({'cena':item['id'],'motivo':'QA_footprint_parcial',**q}); continue
                                raw,rgb,meta=ler_chip(item,r['longitude'],r['latitude'],landsat)
                                if meta['qa_centro_inadequada']:
                                    e['tentativas'].append({'cena':item['id'],'motivo':'QA_centro'}); continue
                                nome=f'imagem_{ano}_{janela}.tif'; tr=Affine(*meta['transform'])
                                with rasterio.open(pasta/nome,'w',driver='GTiff',height=raw.shape[1],width=raw.shape[2],
                                    count=3,dtype=raw.dtype,crs=meta['crs'],transform=tr,compress='deflate') as dst:
                                    dst.write(raw); dst.update_tags(cena=item['id'],data_imagem=item['properties']['datetime'],
                                        representacao='DN reflectância Landsat (escala0.0000275 offset-0.2)' if landsat else 'TCI Sentinel2 uint8')
                                e.update({'situacao':'disponivel_para_interpretacao','sensor':'Landsat' if landsat else 'Sentinel-2',
                                    'cena':item['id'],'data_imagem':item['properties']['datetime'],'raster':nome,
                                    'rgb_visualizacao':'Landsat DN*0.0000275-0.2, escala0..0.3; Sentinel TCI8bits',**meta,**q})
                                imagens.append((e.copy(),rgb)); break
                            except Exception as ex:
                                e['tentativas'].append({'cena':item['id'],'erro_tipo':type(ex).__name__,'http_status':getattr(ex,'code',None)})
                        if e['situacao']=='disponivel_para_interpretacao': break
                    except Exception as ex: e['tentativas'].append({'erro_tipo':type(ex).__name__,'http_status':getattr(ex,'code',None)})
                evid.append(e)
    meta={'caso':r['caso'],'longitude':r['longitude'],'latitude':r['latitude'],
        'ano_t':int(r['ano_origem']),'ano_t1':int(r['ano_destino']),
        'consulta_utc':datetime.now(timezone.utc).isoformat(),'evidencias':evid,
        'limites':'QA nominal não garante ausência de névoa/sombra ou qualidade temática; não usar cores como rótulo automático.'}
    (pasta/'metadados.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    imagens.sort(key=lambda x:x[0]['data_imagem']); prancha(imagens,cantos,pasta)
    anos_ok=sorted({e['ano'] for e in evid if e['situacao']=='disponivel_para_interpretacao'})
    resumo={'caso':r['caso'],'ano_t':int(r['ano_origem']),'ano_t1':int(r['ano_destino']),
        'anos_com_recorte':','.join(map(str,anos_ok)),
        'n_recortes':len(imagens),'par_com_recortes':set(anos_ok)=={int(r['ano_origem']),int(r['ano_destino'])}}
    registro={'fingerprint':fingerprint,'resumo':resumo,'sha256':{p.name:sha(p) for p in pasta.iterdir() if p.is_file()}}
    with pronto.open('x',encoding='utf-8') as f: json.dump(registro,f,indent=2)
    return resumo


def executar(piloto,manifesto,workers):
    saida=piloto/'referencias_cegas'; saida.mkdir(exist_ok=True)
    entrada=piloto/'gestao_restrita/vinculo_piloto_amostra_original.csv'
    p=pd.read_csv(entrada,sep=';',encoding='utf-8-sig')
    if len(p)!=120 or not p.desenho.eq('probabilistica').all(): raise ValueError('Piloto não corresponde ao protocolo.')
    m=json.loads(manifesto.read_text(encoding='utf-8')); tr=Affine(*m['rasters']['1985']['grade']['transform'])
    protocolo={'codigo_sha256':sha(Path(__file__)),'helper_sha256':sha(PROJETO/'processamento/referencias_tematica_col9.py'),
        'entrada_sha256':sha(entrada),'manifesto_sha256':sha(manifesto),'sem_2024':True,
        'limites':'24 cenas por consulta, até6 tentadas; RGB e QA; S2principal→Landsat se necessário; não busca exaustiva.'}
    fingerprint=__import__('hashlib').sha256(json.dumps(protocolo,sort_keys=True).encode()).hexdigest()
    registro=piloto/'gestao_restrita/protocolo_aquisicao.json'
    if registro.exists():
        if json.loads(registro.read_text(encoding='utf-8'))['fingerprint']!=fingerprint: raise ValueError('Protocolo alterado.')
    else:
        with registro.open('x',encoding='utf-8') as f: json.dump({'fingerprint':fingerprint,**protocolo},f,indent=2)
    # Uma assinatura pública por contêiner, em memória; evita muitas chamadas SAS.
    try: token_container('landsateuwest','landsat-c2')
    except Exception: pass  # cada caso registrará seu resultado real, sem substituição.
    linhas=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fs=[pool.submit(processar,r,tr,saida,fingerprint) for r in p.to_dict('records')]
        for i,f in enumerate(as_completed(fs),1):
            r=f.result(); linhas.append(r); print(f"{i}/120 {r['caso']} recortes={r['n_recortes']}",flush=True)
    arq=piloto/'gestao_restrita/cobertura_referencias.csv'
    if not arq.exists(): csv_novo(pd.DataFrame(linhas).sort_values('caso'),arq)
    print('Pares com recortes:',sum(x['par_com_recortes'] for x in linhas),'de 120; sem rótulos.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--piloto',type=Path,required=True)
    p.add_argument('--manifesto',type=Path,required=True); p.add_argument('--workers',type=int,choices=(1,2,3),default=3)
    a=p.parse_args(); executar(a.piloto,a.manifesto,a.workers)
