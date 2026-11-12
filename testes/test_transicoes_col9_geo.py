"""Contratos científicos das transições; executar no ambiente geoespacial."""
import numpy as np
import pytest

pytest.importorskip('rasterio')
pytest.importorskip('geopandas')
from rasterio.transform import Affine
from processamento.transicoes_col9 import (CLASSES,N,LUT,contar_transicoes,metricas,percentual,
                                            aplicar_patch,area_linhas)
from processamento.manifesto_transicoes_col9 import conferir_grade


def test_matriz_comum_conserva_pixels_areas_e_demais_categorias():
    a=np.array([3,3,4,0,27,15,29,3],dtype=np.uint8)
    b=np.array([15,25,4,15,3,3,15,0],dtype=np.uint8)
    pesos=np.arange(1,9,dtype=float)/10
    c,h=contar_transicoes(LUT[a],LUT[b],pesos)
    assert c.shape==(29,29) and h.shape==(29,29)
    assert c.sum()==5 and h.sum()==pytest.approx(1.9)
    assert c[np.flatnonzero(CLASSES==27),:].sum()==0
    assert c[:,np.flatnonzero(CLASSES==27)].sum()==0
    st=LUT[a]>=0
    ec=np.bincount(LUT[a][st],minlength=N)
    ea=np.bincount(LUT[a][st],weights=pesos[st],minlength=N)
    r=metricas(c,h,ec,ea)
    assert r['area_convertida_ha']==pytest.approx(.1)
    assert r['vn_inicial_elegivel_ha']==pytest.approx(.6)
    assert r['vn_inicial_observada_ha']==pytest.approx(1.4)
    assert r['elegibilidade_vn_pct']==pytest.approx(100*.6/1.4)
    assert r['taxa_conversao_pct']==pytest.approx(100*.1/.6)
    assert r['taxa_mais25_pct']==pytest.approx(50)
    assert r['taxa_mais29_32_pct']==pytest.approx(100*.8/1.3)
    assert r['taxa_mais29_32_25_pct']==pytest.approx(100*1./1.3)
    assert not any('alvo' in k or k in ('tau','A_min') for k in r)


def test_marginais_reproduzem_classes_na_mascara_comum():
    rng=np.random.default_rng(817)
    codigos=np.array([0,3,4,15,25,27,29,32,33],dtype=np.uint8)
    a=rng.choice(codigos,1000); b=rng.choice(codigos,1000); pesos=rng.uniform(.08,.09,1000)
    comum=(LUT[a]>=0)&(LUT[b]>=0)
    c,h=contar_transicoes(LUT[a],LUT[b],pesos)
    np.testing.assert_array_equal(c.sum(axis=1),np.bincount(LUT[a][comum],minlength=N))
    np.testing.assert_array_equal(c.sum(axis=0),np.bincount(LUT[b][comum],minlength=N))
    np.testing.assert_allclose(h.sum(axis=1),np.bincount(LUT[a][comum],weights=pesos[comum],minlength=N))
    np.testing.assert_allclose(h.sum(axis=0),np.bincount(LUT[b][comum],weights=pesos[comum],minlength=N))


def test_mascara_tripla_exclui_pixel_valido_em_apenas_dois_anos():
    valores=np.array([[3,3,0,3],[15,15,3,0],[15,0,15,15]],dtype=np.uint8)
    indices=LUT[valores]; comum=(indices>=0).all(axis=0)
    for i in (0,1):
        par,_=contar_transicoes(indices[i],indices[i+1],np.ones(4))
        tripla,_=contar_transicoes(indices[i],indices[i+1],np.ones(4),comum)
        assert par.sum()==2
        assert tripla.sum()==1


def test_sem_vegetacao_inicial_taxa_e_elegibilidade_sao_indefinidas():
    a=LUT[np.array([15,33],dtype=np.uint8)]; b=LUT[np.array([3,15],dtype=np.uint8)]
    c,h=contar_transicoes(a,b,np.ones(2))
    ec=np.bincount(a,minlength=N); ea=ec.astype(float)
    r=metricas(c,h,ec,ea)
    assert r['area_convertida_ha']==0
    assert r['taxa_conversao_pct'] is None and r['elegibilidade_vn_pct'] is None


def test_sem_mascara_comum_matriz_zerada_nao_significa_alvo_negativo():
    c,h=contar_transicoes(np.array([-1,0]),np.array([0,-1]),np.ones(2))
    r=metricas(c,h,np.zeros(N,dtype=int),np.zeros(N))
    assert c.sum()==0 and h.sum()==0
    assert r['taxa_conversao_pct'] is None


def test_particionar_em_blocos_preserva_matriz():
    a=LUT[np.array([3,3,15,29,33,0,27],dtype=np.uint8)]
    b=LUT[np.array([15,25,3,15,33,3,3],dtype=np.uint8)]
    w=np.linspace(.08,.09,7)
    inteiro_c,inteiro_a=contar_transicoes(a,b,w)
    partes=[contar_transicoes(a[s],b[s],w[s]) for s in (slice(0,3),slice(3,None))]
    np.testing.assert_array_equal(inteiro_c,sum(x[0] for x in partes))
    np.testing.assert_allclose(inteiro_a,sum(x[1] for x in partes),rtol=0,atol=1e-15)


def test_complemento_so_zero_e_audita_divergencias_sem_modificar_original():
    original=np.array([[3,0,0],[27,15,0]],dtype=np.uint8)
    patch=np.array([[4,15,15],[3,15,27]],dtype=np.uint8)
    dentro=np.array([[True,True,False],[True,True,True]])
    novo,preenchidos,div=aplicar_patch(original,patch,dentro)
    assert novo.tolist()==[[3,15,0],[27,15,0]]
    assert preenchidos.sum()==1 and div==1
    assert original[0,1]==0


def test_area_pixel_varia_com_latitude_sem_usar_constante_009ha():
    a=area_linhas(Affine(.0002694945852358564,0,-50,0,-.0002694945852358564,-2),2)
    b=area_linhas(Affine(.0002694945852358564,0,-50,0,-.0002694945852358564,-16),2)
    assert (.07<a).all() and (a<.1).all()
    assert a[0]>b[0] and a[0]!=.09


def test_grade_deslocada_nao_e_reamostrada_silenciosamente():
    g={'crs':'EPSG:4326','transform':[.01,0,-50,0,-.01,-2],
       'largura':20,'altura':20,'bandas':1,'dtype':'uint8','nodata':0}
    conferir_grade(g,g.copy())
    outro={**g,'transform':[.01,0,-49.995,0,-.01,-2]}
    with pytest.raises(ValueError,match='Grade'):
        conferir_grade(g,outro)


def test_percentual_corrige_apenas_ruido_numerico_nos_limites():
    assert percentual(.6,.60000000000001)==100
    assert percentual(100.04,100)==100.04
    assert percentual(1,0) is None
