import json
import hashlib

import numpy as np
import pandas as pd
import pytest

from analise_col9 import (METODOLOGIA, MAPA_CATEGORIAS, classificar, indicadores,
                         serie_classes, medias_decadas, comparar_anos, auditar_areas)
from dados_col9 import carregar_legenda, carregar_mapas_regionais, proveniencia
from visualizacao_col9 import mapa_municipal


def cobertura(linhas):
    return pd.DataFrame(linhas, columns=['CD_MUN', 'ano', 'classe_cobertura', 'area_ha'])


@pytest.fixture
def base():
    return cobertura([(1,2023,3,20.),(1,2023,15,50.),(1,2023,25,10.),
                      (1,2023,33,10.),(1,2023,29,5.),(1,2023,32,5.),(1,2023,27,900.),
                      (2,2023,3,900.),(2,2023,15,50.),(2,2023,33,50.)])


def test_politica_aprovada_particiona_legenda_sem_alterar_oficial():
    legenda = carregar_legenda()
    assert METODOLOGIA['status'] == 'aprovada_pelo_pesquisador'
    assert set(legenda.classe_cobertura) == set(MAPA_CATEGORIAS) - {0}
    assert legenda.set_index('classe_cobertura').loc[29, 'grupo'] == 'Vegetação Herbácea e Arbustiva'
    bruto = cobertura([(1,2023,29,10.)])
    novo = classificar(bruto)
    assert novo.categoria_operacional.iloc[0] == 'Ambientes naturais específicos'
    assert 'categoria_operacional' not in bruto


def test_razao_entre_somas_e_sensibilidades(base):
    r = indicadores(base).iloc[0]
    assert r.area_classificada_ha == 1100
    assert r.nao_observado_ha == 900
    assert r.vegetacao_nativa_pct == pytest.approx(100*920/1100)
    assert r.vegetacao_nativa_ampliada_pct == pytest.approx(100*930/1100)
    assert r.usos_antropicos_pct == pytest.approx(100*100/1100)
    assert r.usos_antropicos_com25_pct == pytest.approx(100*110/1100)
    assert r.vegetacao_nativa_pct != pytest.approx((20+90)/2)


def test_filtro_classe_nao_reduz_denominador(base):
    s = serie_classes(base, [15]).iloc[0]
    assert s.area_classificada_ha == 1100
    assert s.participacao_pct == pytest.approx(100*100/1100)
    assert set(serie_classes(base).classe_cobertura) == {3,15,25,29,32,33}


def test_nao_observado_nao_vira_zero_ou_alvo():
    bruto = cobertura([(1,1985,27,100.),(1,2023,3,60.),(1,2023,15,40.)])
    r = indicadores(bruto).iloc[0]
    assert np.isnan(r.vegetacao_nativa_pct)
    s = serie_classes(bruto,[15])
    assert np.isnan(s[s.ano.eq(1985)].area_ha.iloc[0])
    assert not any(c.startswith('alvo') for c in r.index)


def test_ausencia_de_classe_observada_vira_zero_no_calculo_de_media():
    bruto = cobertura([(1,1985,15,10.),(1,1986,3,20.)])
    d = medias_decadas(bruto,[15]).iloc[0]
    assert d.media_anual_area_ha == 5
    assert d.anos_observados == 2 and d.periodo_incompleto


def test_decadas_incompletas_e_media_anual():
    bruto = cobertura([(1,a,3,float(a-1900)) for a in range(1985,2024)])
    d = medias_decadas(bruto).set_index('decada')
    assert d.anos_observados.to_dict() == {1980:5,1990:10,2000:10,2010:10,2020:4}
    assert d.loc[2020,'media_anual_area_ha'] == 121.5
    assert not bool(d.loc[1990,'periodo_incompleto'])


def test_variacao_liquida_e_base_zero():
    bruto = cobertura([(1,1985,3,100.),(1,2023,3,60.),(1,2023,15,40.)])
    c = comparar_anos(bruto,1985,2023).set_index('classe_cobertura')
    assert c.loc[3,'variacao_liquida_ha'] == -40
    assert c.loc[3,'variacao_relativa_pct'] == -40
    assert c.loc[15,'area_inicial_ha'] == 0
    assert np.isnan(c.loc[15,'variacao_relativa_pct'])
    with pytest.raises(ValueError):
        comparar_anos(bruto,2023,1985)


def test_agua_aquicultura_mosaico_e_silvicultura():
    bruto = cobertura([(1,2023,c,10.) for c in (3,9,21,31,33,25)])
    r = indicadores(bruto).iloc[0]
    assert r.usos_antropicos_ha == 30
    assert r.agua_ha == 10 and r.indeterminada_ha == 10
    assert r.vegetacao_nativa_ha == 10


def test_auditoria_mede_diferencas_sem_imputar_nodata(base):
    territorio = pd.DataFrame({'CD_MUN':[1,2], 'NM_MUN':['A','B'],'SIGLA_UF':['MA','MT'],
                               'area_cadastrada_ha':[110.,1100.],
                               'area_geodesica_wgs84_ha':[100.,1000.],
                               'area_geodesica_grs80_ha':[100.,1000.]})
    a = auditar_areas(base,territorio).set_index('CD_MUN')
    assert a.loc[1,'diferenca_classificada_cadastrada_ha'] == -10
    assert a.loc[1,'diferenca_classificada_geodesica_wgs84_ha'] == 0
    assert 'não atribuída' in a.loc[1,'causa_diferenca']
    with pytest.raises(ValueError):
        auditar_areas(base,territorio.iloc[:1])


def test_codigo_desconhecido_ou_chave_duplicada_nao_produz_indicador():
    with pytest.raises(ValueError):
        indicadores(cobertura([(1,2023,7,10.)]))
    with pytest.raises(ValueError):
        indicadores(cobertura([(1,2023,3,10.),(1,2023,3,10.)]))


def test_mapa_preserva_mesmo_conjunto_de_codigos(base):
    poligono = json.dumps({'type':'Polygon','coordinates':[[[0,0],[0,1],[1,1],[1,0],[0,0]]]})
    territorio = pd.DataFrame({'CD_MUN':[1,2],'NM_MUN':['A','B'],'SIGLA_UF':['MA','MT'],'geojson':[poligono,poligono]})
    valores = indicadores(base,('CD_MUN',))
    fig = mapa_municipal(valores,territorio,'vegetacao_nativa_pct','Col9')
    assert set(fig.data[0].locations) == {'1','2'}
    assert len(fig.data[0].geojson['features']) == 2
    with pytest.raises(ValueError):
        mapa_municipal(valores,territorio.iloc[:1],'vegetacao_nativa_pct','Col9')


def test_imagens_recusam_colecao_incorreta_e_hash_adulterado(tmp_path):
    fonte = proveniencia()['arquivos']['territorio']
    arquivo = tmp_path/'teste.png'
    arquivo.write_bytes(b'imagem de teste')
    m = {'colecao':'9','municipios':255,'territorio':fonte,
         'mapas':{str(a):{'arquivo':arquivo.name,'sha256':hashlib.sha256(arquivo.read_bytes()).hexdigest()} for a in (1985,2023)}}
    (tmp_path/'manifesto.json').write_text(json.dumps(m),encoding='utf-8')
    assert carregar_mapas_regionais(tmp_path)['colecao']=='9'
    arquivo.write_bytes(b'adulterada')
    with pytest.raises(ValueError,match='Hash'):
        carregar_mapas_regionais(tmp_path)
    m['colecao']='10.1'
    (tmp_path/'manifesto.json').write_text(json.dumps(m),encoding='utf-8')
    with pytest.raises(ValueError,match='coleção'):
        carregar_mapas_regionais(tmp_path)
