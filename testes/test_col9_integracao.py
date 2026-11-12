"""Integração somente leitura. Usa a mesma configuração dos testes legados."""
from pathlib import Path
import hashlib
import os

import pandas as pd
import pytest
from sqlalchemy import text
from streamlit.testing.v1 import AppTest

import dados
import dados_col9
from contratos_series import COL9, validar_cobertura
from testes.test_paridade import banco  # fixture existente, usuário de leitura

PAGINA = Path(__file__).resolve().parents[1] / 'pages' / '01_Colecao_9_255.py'


def test_contrato_real_e_permissoes(banco, monkeypatch):
    monkeypatch.setattr(dados, 'USA_BANCO', True)
    dados_col9.carregar.clear()
    base, legenda = dados_col9.carregar()
    with banco.connect() as conexao:
        municipios = pd.read_sql(text('SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", '
                                      'sigla_uf AS "SIGLA_UF" FROM ref.vw_municipios_col9_255'), conexao)
        validar_cobertura(base, municipios)
        assert conexao.execute(text('SHOW default_transaction_read_only')).scalar() == 'on'
        for objeto in (COL9.cobertura, COL9.territorio):
            permissoes = conexao.execute(text(
                "SELECT has_table_privilege(current_user,:objeto,'SELECT'),"
                "has_table_privilege(current_user,:objeto,'INSERT,UPDATE,DELETE,TRUNCATE')"
            ), {'objeto': objeto}).one()
            assert permissoes == (True, False)
        assert conexao.execute(text(
            'SELECT bool_and(round(area_ha::float8::numeric,4)=area_ha) '
            'AND bool_and(round(perc_ocupacao::float8::numeric,4)=perc_ocupacao) '
            'FROM mapbiomas.vw_cobertura_col9_255')).scalar()
    assert set(base.classe_cobertura) <= set(legenda.classe_cobertura)
    assert len(base) == 113364


def test_pagina_col9_filtros_e_ausencia_de_resultados(banco, monkeypatch):
    monkeypatch.setattr(dados, 'USA_BANCO', True)
    at = AppTest.from_file(str(PAGINA), default_timeout=120).run()
    assert not at.exception and not at.error
    assert at.metric[0].value == '255'
    at.sidebar.multiselect[1].select(2101772).run()
    assert not at.exception and at.metric[0].value == '1'
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert any('Nenhum registro' in i.value for i in at.info)


def test_pagina_nao_exibe_excecao_de_conexao(monkeypatch):
    def falhar(*args, **kwargs):
        raise Exception('detalhe interno que não pode chegar à interface')
    monkeypatch.setattr(dados_col9, 'carregar', falhar)
    at = AppTest.from_file(str(PAGINA)).run()
    assert not at.exception
    assert len(at.error) == 1
    assert 'detalhe interno' not in at.error[0].value


def test_paridade_com_consolidado_col9(banco, monkeypatch):
    arquivo = Path(os.environ.get('MESTRADO_DADOS', PAGINA.parents[2])) / 'cobertura_col9_255_1985_2023_consolidada.csv'
    if not arquivo.exists():
        pytest.skip('Consolidado Col9 externo indisponível para paridade.')
    esperado = dados_col9.proveniencia()['arquivos']['consolidado']['sha256']
    assert hashlib.sha256(arquivo.read_bytes()).hexdigest() == esperado
    csv = pd.read_csv(arquivo, sep=';', encoding='utf-8-sig')
    monkeypatch.setattr(dados, 'USA_BANCO', True)
    base, _ = dados_col9.carregar()
    chaves = ['CD_MUN', 'ano', 'classe_cobertura']
    csv = csv.sort_values(chaves).reset_index(drop=True)
    base = base.sort_values(chaves).reset_index(drop=True)
    pd.testing.assert_frame_equal(base[csv.columns], csv, check_dtype=False, atol=0.00005, rtol=0)
