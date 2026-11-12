"""Delimita o pixel Col9 exato nas imagens de referência já salvas. Sem acesso à rede."""
import argparse
import html
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from PIL import Image,ImageDraw
from affine import Affine
from pyproj import Transformer

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import sha


def executar(base,manifesto,saida):
    if saida.exists(): raise FileExistsError('Pranchas anteriores preservadas.')
    saida.mkdir(parents=True)
    m=json.loads(manifesto.read_text(encoding='utf-8'))
    tr_mb=Affine(*m['rasters']['1985']['grade']['transform'])
    pontos=pd.read_csv(base/'amostragem/pontos_com_contexto_mapeado.csv',sep=';').set_index('id')
    links=[]
    for lote in ('referencias_v2','referencias_fim_ano','referencias_historicas_v3'):
        for p in sorted((base/lote).glob('*/evidencias.json')):
            identificador=p.parent.name; pt=pontos.loc[identificador]
            d=json.loads(p.read_text(encoding='utf-8')); evid=d['evidencias'] if isinstance(d,dict) else d
            placas=[]
            for e in evid:
                if e['situacao']!='recorte_para_interpretacao': continue
                with np.load(p.parent/f"chip_{e['ano']}.npz",allow_pickle=False) as z: raw=z['bandas']
                rgb=raw if e['resolucao_m']==10 else np.clip((raw.astype(float)*.0000275-.2)/.3*255,0,255).astype('uint8')
                im=Image.fromarray(np.moveaxis(rgb,0,2))
                referencia=Affine(*e['transform']); inv=~referencia
                proj=Transformer.from_crs(4326,e['crs'],always_xy=True)
                col,lin=int(pt.coluna_raster),int(pt.linha_raster)
                corners=[tr_mb*(col,lin),tr_mb*(col+1,lin),tr_mb*(col+1,lin+1),tr_mb*(col,lin+1)]
                polygon=[inv*proj.transform(x,y) for x,y in corners]
                cx=sum(x for x,y in polygon)/4; cy=sum(y for x,y in polygon)/4
                contexto=im.resize((384,384),Image.Resampling.NEAREST)
                sx,sy=384/im.width,384/im.height
                ImageDraw.Draw(contexto).polygon([(x*sx,y*sy) for x,y in polygon],outline='yellow',width=1)
                raio=max(5,round(100/e['resolucao_m']))
                x0,y0=int(cx)-raio,int(cy)-raio; lado=2*raio
                zoom=im.crop((x0,y0,x0+lado,y0+lado)).resize((384,384),Image.Resampling.NEAREST)
                ImageDraw.Draw(zoom).polygon([((x-x0)*384/lado,(y-y0)*384/lado) for x,y in polygon],outline='yellow',width=2)
                placa=Image.new('RGB',(400,820),'white'); dr=ImageDraw.Draw(placa)
                data=e.get('data_imagem',e.get('data',''))[:10]
                dr.text((8,6),f"{data} | {e['resolucao_m']:g} m",fill='black')
                placa.paste(contexto,(8,30)); placa.paste(zoom,(8,425))
                dr.text((8,807),'Amarelo: footprint Col9; inferior: zoom',fill='black'); placas.append(placa)
            if not placas: continue
            painel=Image.new('RGB',(len(placas)*400,820),'white')
            for i,placa in enumerate(placas): painel.paste(placa,(400*i,0))
            arq=saida/f'{identificador}_{lote}.png'; painel.save(arq)
            links.append((identificador,lote,arq.name))
    texto='<!doctype html><meta charset="utf-8"><title>Referências temáticas Col9</title><style>body{font-family:sans-serif;max-width:1600px;margin:auto}img{max-width:100%}</style><h1>Pranchas de referência — pixel Col9 delimitado</h1><p>Sem classes do mapa ou cenários revelados. Amarelo: footprint da grade Col9, transformado para o CRS da cena; não corrige erro de registro. Imagens só para interpretação, sem rótulos homologados.</p>'
    for ident,lote,nome in links: texto+=f'<h2>{html.escape(ident)} — {lote}</h2><a href="{nome}"><img loading="lazy" src="{nome}"></a>'
    (saida/'indice.html').write_text(texto,encoding='utf-8')
    (saida/'manifesto.json').write_text(json.dumps({'codigo_sha256':sha(Path(__file__)),
        'metodo':'Quatro cantos da célula original Col9, projeção always_xy para CRS da cena e inversa da transformada do recorte. Sem reclassificar pixels.',
        'limite':'Footprint exato da grade nominal; não certifica registro entre sensores ou representação temática.',
        'sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},indent=2),encoding='utf-8')
    print(f'{len(links)} pranchas com footprint, sem alterar recortes originais.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('base','manifesto','saida'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); executar(a.base,a.manifesto,a.saida)
