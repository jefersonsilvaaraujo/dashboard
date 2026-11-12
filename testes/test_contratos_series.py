from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from contratos_series import COL9, LEGADO, validar_cobertura
from dados_col9 import carregar, carregar_legenda, proveniencia


@pytest.fixture
def amostra():
    municipios = pd.DataFrame({'CD_MUN': [2101772, 5101837],
                              'NM_MUN': ['Bela Vista do Maranhão', 'Boa Esperança do Norte'],
                              'SIGLA_UF': ['MA', 'MT']})
    linhas = []
    for m in municipios.itertuples():
        for ano in (1985, 1986):
            for classe in (3, 15):
                linhas.append([m.CD_MUN, m.NM_MUN, m.SIGLA_UF, ano, classe, 10, 0.9, 50.0])
    base = pd.DataFrame(linhas, columns=['CD_MUN', 'NM_MUN', 'SIGLA_UF', 'ano',
                                       'classe_cobertura', 'pixels', 'area_ha', 'perc_ocupacao'])
    contrato = replace(COL9, fim=1986, municipios=2, linhas=8, ufs=frozenset({'MA', 'MT'}))
    return base, municipios, contrato


def test_aceita_serie_completa(amostra):
    validar_cobertura(*amostra)


@pytest.mark.parametrize('defeito', ['duplicacao', 'ano', 'troca_codigo', 'lacuna',
                                    'uf', 'nome', 'nulo', 'area', 'pixels', 'percentual',
                                    'infinito', 'classe_zero', 'pixels_fracionarios'])
def test_recusa_corrupcao_sem_depender_so_de_contagens(amostra, defeito):
    base, municipios, contrato = amostra
    if defeito == 'duplicacao':
        base.iloc[0] = base.iloc[1]
    elif defeito == 'ano':
        base.loc[0, 'ano'] = 2024
    elif defeito == 'troca_codigo':
        base.loc[base.CD_MUN == 2101772, 'CD_MUN'] = 2108504
    elif defeito == 'lacuna':
        # Mesma contagem, anos e municípios; falta apenas um par município–ano.
        base.loc[(base.CD_MUN == 2101772) & (base.ano == 1986), 'ano'] = 1985
        base.loc[2:3, 'classe_cobertura'] = [4, 5]
    elif defeito == 'uf':
        base.loc[0, 'SIGLA_UF'] = 'PA'
    elif defeito == 'nome':
        base.loc[0, 'NM_MUN'] = 'Homônimo'
    elif defeito == 'nulo':
        base.loc[0, 'area_ha'] = np.nan
    elif defeito == 'area':
        base.loc[0, 'area_ha'] = -1
    elif defeito == 'pixels':
        base.loc[0, 'pixels'] = 0
    elif defeito == 'percentual':
        base.loc[0, 'perc_ocupacao'] = 101
    elif defeito == 'infinito':
        base.loc[0, 'area_ha'] = np.inf
    elif defeito == 'classe_zero':
        base.loc[0, 'classe_cobertura'] = 0
    else:
        base['pixels'] = base['pixels'].astype(float)
        base.loc[0, 'pixels'] = 1.5
    with pytest.raises(ValueError):
        validar_cobertura(base, municipios, contrato)


def test_serie_legada_nao_pode_entrar_no_modulo_col9():
    with pytest.raises(ValueError, match='somente'):
        carregar(LEGADO.id)


def test_legenda_tem_identidade_e_cor_independentes():
    legenda = carregar_legenda().set_index('classe_cobertura')
    assert len(legenda) == 29
    assert legenda.loc[6, 'cor_rgb'] == '#007785'
    assert 'tipo' not in legenda.columns
    assert proveniencia()['legenda']['colecao'] == '9'
    assert proveniencia()['serie'] == COL9.id
