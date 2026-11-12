"""Auditoria técnica offline do piloto; não estima acurácia nem responde às fichas."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import shape

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import sha,csv_novo
from processamento.pacote_avaliadores_col9 import verificar_metadados


def executar(piloto,saida):
    if saida.exists(): raise FileExistsError('Auditoria anterior preservada.')
    linhas=[]
    for pasta in sorted((piloto/'referencias_cegas').iterdir()):
        if not pasta.is_dir(): continue
        ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
        for n,h in ck['sha256'].items():
            if sha(pasta/n)!=h: raise ValueError('Checkpoint de cena divergente.')
        m=json.loads((pasta/'metadados.json').read_text(encoding='utf-8')); verificar_metadados(m)
        pixel=json.loads((pasta/'pixel.geojson').read_text(encoding='utf-8'))['geometry']; geom=shape(pixel)
        for e in m['evidencias']:
            if e['situacao']!='disponivel_para_interpretacao': continue
            itens=[]
            for c in e['consultas']:
                itens+=json.loads((pasta/c['catalogo']).read_text(encoding='utf-8')).get('features',[])
            item=next(x for x in itens if x['id']==e['cena'])
            cobre=shape(item['geometry']).covers(geom)
            with rasterio.open(pasta/e['raster']) as s:
                proj=Transformer.from_crs(4326,s.crs,always_xy=True)
                coords=[proj.transform(x,y) for x,y in pixel['coordinates'][0]]
                mask=geometry_mask([{'type':'Polygon','coordinates':[coords]}],out_shape=s.shape,
                    transform=s.transform,invert=True,all_touched=True)
                a=s.read(); zero=bool(np.all(a==0,axis=0)[mask].any())
                xmin,ymin,xmax,ymax=shape({'type':'Polygon','coordinates':[coords]}).bounds
                cabe=xmin>=s.bounds.left and xmax<=s.bounds.right and ymin>=s.bounds.bottom and ymax<=s.bounds.top
            linhas.append({'caso':m['caso'],'ano':e['ano'],'janela':e['janela'],'cena':e['cena'],
                'cena_cobre_footprint':cobre,'recorte_contem_footprint':cabe,'RGB_zero_no_footprint':zero,
                'fracao_QA_adequada':e['fracao_QA_adequada_footprint']})
    d=pd.DataFrame(linhas); csv_novo(d,saida)
    print(json.dumps({'recortes':len(d),'casos':int(d.caso.nunique()),
        'cena_nao_cobre_footprint':int((~d.cena_cobre_footprint).sum()),
        'recorte_nao_contem_footprint':int((~d.recorte_contem_footprint).sum()),
        'com_RGB_zero_no_footprint':int(d.RGB_zero_no_footprint.sum()),'sem_acuracia':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--piloto',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.piloto,a.saida)
