"""Probabilidades, pesos, controles de omissão e reprodutibilidade do sorteio."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip('rasterio'); pytest.importorskip('geopandas')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.amostra_tematica_col9 import desenhar,selecionar_pixels


def test_sorteio_psu_reprodutivel_sem_reposicao_e_pesos_corretos():
    q=pd.DataFrame({'CD_MUN':list(range(8))*2,'ano_origem':[2021]*8+[2022]*8,
        'ano_destino':[2022]*8+[2023]*8,'SIGLA_UF':['MA']*16,'taxa_conversao_pct':[3]*16})
    e=q[['CD_MUN','ano_origem']].copy(); e['estabilidade_classe_pct']=90
    f,p,d,h=desenhar(q,e); f2,p2,_,_=desenhar(q.sample(frac=1,random_state=9),e)
    pd.testing.assert_frame_equal(p,p2)
    assert p.pi_psu.eq(.25).all() and len(p)==4 and not p.duplicated(['CD_MUN','ano_origem']).any()
    assert (p.groupby('estrato').pi_psu.apply(lambda x:sum(1/x))==8).all()
    assert h.N_psu.sum()==len(f)


def test_censo_estrato_unitario_e_proibicao_n1_amostral():
    q=pd.DataFrame({'CD_MUN':[1],'ano_origem':[2022],'ano_destino':[2023],'SIGLA_UF':['RO'],'taxa_conversao_pct':[.1]})
    e=q[['CD_MUN','ano_origem']].copy(); e['estabilidade_classe_pct']=100
    assert desenhar(q,e)[1].pi_psu.eq(1).all()
    with pytest.raises(ValueError): desenhar(q,e,n_por_estrato=1)


def test_pixel_amostra_inclui_nao_conversao_e_outras_origens():
    a=np.array([[3,3,15,15],[3,3,15,15]],dtype='uint8')
    b=np.array([[15,3,15,3],[15,3,15,3]],dtype='uint8'); v=np.ones_like(a,dtype=bool)
    p,info=selecionar_pixels(a,b,v,1,'toy')
    assert len(p)==4 and {x['pi_pixel_condicional'] for x in p}=={.5}
    assert len({(x['linha_local'],x['coluna_local']) for x in p})==4
    assert {x['estrato_pixel'] for x in p}=={'VN_UA','VN_outros','outras_origens_UA','outras_origens_outros'}
    assert sum(x['N_pixels'] for x in info)==8
    assert p==selecionar_pixels(a,b,v,1,'toy')[0]


def test_pixels_invalidos_nao_se_tornam_controle():
    a=np.array([[3,0,27]],dtype='uint8'); b=np.array([[15,15,3]],dtype='uint8')
    p,_=selecionar_pixels(a,b,np.array([[True,False,False]]),4,'x')
    assert len(p)==1 and p[0]['pi_pixel_condicional']==1
