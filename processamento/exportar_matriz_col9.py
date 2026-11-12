"""Exporta uma matriz densa 29×29 para CSV, incluindo células zero. Sem banco."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def extrair(resultados,municipio,ano,mascara='par'):
    pasta=resultados/'municipios'/str(municipio)
    ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
    with np.load(pasta/ck['npz'],allow_pickle=False) as z:
        if mascara=='tripla':
            if municipio!=2102325 or ano not in (2001,2002): raise ValueError('Máscara tripla disponível somente para Buriticupu 2001/2002.')
            i=ano-2001; pixels=z['tripla_pixels'][i]; areas=z['tripla_area_ha'][i]
        else:
            pos=np.flatnonzero(z['anos'][:-1]==ano)
            if len(pos)!=1: raise ValueError('Ano não encontrado nos resultados.')
            i=int(pos[0]); pixels=z['pixels'][i]; areas=z['area_ha'][i]
        classes=z['classes']
        grade=pd.MultiIndex.from_product([classes,classes],names=['classe_origem','classe_destino']).to_frame(index=False)
        grade['pixels']=pixels.ravel(); grade['area_ha']=areas.ravel()
    grade['CD_MUN']=municipio; grade['ano_origem']=ano; grade['ano_destino']=ano+1; grade['mascara']=mascara
    return grade


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resultados',type=Path,required=True); p.add_argument('--municipio',type=int,required=True)
    p.add_argument('--ano-origem',type=int,required=True); p.add_argument('--mascara',choices=['par','tripla'],default='par')
    p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args(); tabela=extrair(a.resultados,a.municipio,a.ano_origem,a.mascara)
    a.saida.parent.mkdir(parents=True,exist_ok=True)
    tabela.to_csv(a.saida,sep=';',mode='x',index=False,encoding='utf-8-sig')
    print(f'{len(tabela)} células, incluindo zeros; nenhuma saída anterior substituída.')
