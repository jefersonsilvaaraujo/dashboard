"""Complementa a inspeção dirigida com cenas novembro/dezembro, sem substituir o lote seco."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
import sys
import urllib.parse

import numpy as np
import pandas as pd
from PIL import Image,ImageDraw
import rasterio
from pyproj import Transformer
from rasterio.windows import Window

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.referencias_tematica_col9 import obter_json,ler_chip,EARTH
from processamento.cenarios_validacao_col9 import sha,csv_novo


def ponto(r,saida):
    pasta=saida/r['id']; pasta.mkdir(); linhas=[]; imagens=[]
    for ano in (r['ano_origem'],r['ano_destino']):
        params={'collections':'sentinel-2-l2a','intersects':json.dumps({'type':'Point','coordinates':[r['longitude'],r['latitude']]}),
            'datetime':f'{ano}-11-01T00:00:00Z/{ano}-12-31T23:59:59Z','limit':100}
        registro={'id':r['id'],'ano':ano,'situacao':'sem_cena_central_adequada','tentativas':[]}
        try:
            d=obter_json(EARTH+'?'+urllib.parse.urlencode(params))
            (pasta/f'catalogo_{ano}.json').write_text(json.dumps(d),encoding='utf-8')
            for z in sorted(d.get('features',[]),key=lambda x:x['properties']['datetime'],reverse=True)[:30]:
                try:
                    with rasterio.open(z['assets']['scl']['href']) as s:
                        x,y=Transformer.from_crs(4326,s.crs,always_xy=True).transform(r['longitude'],r['latitude'])
                        lin,col=s.index(x,y); v=int(s.read(1,window=Window(col,lin,1,1))[0,0])
                    if v not in (4,5,6):
                        registro['tentativas'].append({'item':z['id'],'QA':v}); continue
                    raw,rgb,q=ler_chip(z,r['longitude'],r['latitude'],False)
                    with (pasta/f'chip_{ano}.npz').open('xb') as f: np.savez_compressed(f,bandas=raw)
                    registro.update({'situacao':'recorte_para_interpretacao','item':z['id'],'data':z['properties']['datetime'],**q})
                    im=Image.fromarray(np.moveaxis(rgb,0,2)).resize((384,384),Image.Resampling.NEAREST)
                    ImageDraw.Draw(im).rectangle((187,187,197,197),outline='white',width=1)
                    im.save(pasta/f'visual_{ano}.png'); imagens.append((im,registro['data'][:10])); break
                except Exception as e: registro['tentativas'].append({'item':z['id'],'erro_tipo':type(e).__name__})
        except Exception as e: registro.update({'situacao':'consulta_indisponivel','erro_tipo':type(e).__name__})
        linhas.append(registro)
    if imagens:
        p=Image.new('RGB',(384*len(imagens),420),'white'); dr=ImageDraw.Draw(p)
        for i,(im,data) in enumerate(imagens): p.paste(im,(384*i,30)); dr.text((384*i+5,5),data,fill='black')
        p.save(pasta/'painel_fim_ano.png')
    (pasta/'evidencias.json').write_text(json.dumps(linhas,ensure_ascii=False,indent=2),encoding='utf-8')
    return [{k:v for k,v in x.items() if k!='tentativas'} for x in linhas]


def executar(referencias,saida):
    if saida.exists(): raise FileExistsError('Lote anterior preservado.')
    p=pd.read_csv(referencias/'selecao_dirigida_referencias.csv',sep=';')
    p=p[p.ano_origem.isin([2021,2022])]
    saida.mkdir(parents=True); linhas=[]
    regs=json.loads(p.to_json(orient='records',double_precision=15))
    with rasterio.Env(GDAL_HTTP_TIMEOUT='25',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with ThreadPoolExecutor(max_workers=3) as pool:
            fs=[pool.submit(ponto,r,saida) for r in regs]
            for i,f in enumerate(as_completed(fs),1): linhas+=f.result(); print(f'{i}/{len(fs)} complementos de fim de ano',flush=True)
    csv_novo(pd.DataFrame(linhas),saida/'inventario.csv')
    (saida/'manifesto.json').write_text(json.dumps({'codigo_sha256':sha(Path(__file__)),
        'metodo':'Até 100 cenas retornadas, até 30 mais recentes tentadas; QA central SCL 4/5/6; nenhum rótulo',
        'sha256':{str(p.relative_to(saida)):sha(p) for p in saida.rglob('*') if p.is_file()}},indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--referencias',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.referencias,a.saida)
