"""Integração descritiva; sem cargas, migrações ou construção de variável-alvo."""
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import dados
import dados_col9
from analise_col9 import auditar_areas, indicadores
from testes.test_paridade import banco

PAGINA = Path(__file__).resolve().parents[1]/'pages/01_Colecao_9_255.py'


def test_auditoria_real_tem_9945_pares_e_razoes_reproduziveis(banco,monkeypatch):
    monkeypatch.setattr(dados,'USA_BANCO',True)
    base,_ = dados_col9.carregar()
    territorio = dados_col9.carregar_territorio()
    a = auditar_areas(base,territorio)
    assert len(a) == 255*39
    assert not a.duplicated(['CD_MUN','ano']).any()
    assert territorio.srid.eq(4674).all() and territorio.geometria_valida.all()
    assert (a.area_classificada_ha > 0).all()
    assert a.causa_diferenca.str.contains('não atribuída').all()
    por_mun = indicadores(base,('CD_MUN','ano'))
    regional = indicadores(base)
    for ano in (1985,2002,2023):
        m = por_mun[por_mun.ano.eq(ano)]
        r = regional[regional.ano.eq(ano)].iloc[0]
        assert r.vegetacao_nativa_pct == pytest.approx(100*m.vegetacao_nativa_ha.sum()/m.area_classificada_ha.sum())
        assert r.usos_antropicos_com25_pct >= r.usos_antropicos_pct
        assert r.vegetacao_nativa_ampliada_pct >= r.vegetacao_nativa_pct


def test_pagina_classe_isolada_mantem_indicadores_e_territorio(banco,monkeypatch):
    monkeypatch.setattr(dados,'USA_BANCO',True)
    at = AppTest.from_file(str(PAGINA),default_timeout=120).run()
    assert not at.exception and not at.error
    metricas = [m.value for m in at.metric]
    assert len(at.tabs)==5 and len(at.get('plotly_chart'))>=7
    at.sidebar.multiselect[2].select(15).run()
    assert not at.exception
    assert [m.value for m in at.metric][4:] == metricas[4:]
    at.sidebar.slider[0].set_value((2023,2023)).run()
    assert not at.exception
    assert any('pelo menos dois anos' in i.value for i in at.info)
    at.sidebar.multiselect[1].select(2102325).run()
    assert not at.exception and at.metric[0].value=='1'
