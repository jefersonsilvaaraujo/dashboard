"""Identidade e integridade das séries; não executa consultas ou cargas."""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ContratoSerie:
    id: str
    colecao: str
    inicio: int
    fim: int
    municipios: int
    linhas: int
    ufs: frozenset[str]
    cobertura: str
    territorio: str


COL9 = ContratoSerie(
    'col9_255_1985_2023', '9', 1985, 2023, 255, 113364,
    frozenset({'MA', 'MT', 'PA', 'RO', 'TO'}),
    'mapbiomas.vw_cobertura_col9_255', 'ref.vw_municipios_col9_255',
)
LEGADO = ContratoSerie(
    'legado_10_1', '10.1', 1985, 2024, 268, 126212,
    COL9.ufs, 'mapbiomas.vw_cobertura_municipio', 'ref.vw_municipio',
)
SERIES = {s.id: s for s in (COL9, LEGADO)}
COLUNAS_COL9 = ('CD_MUN', 'NM_MUN', 'SIGLA_UF', 'ano', 'classe_cobertura',
                'pixels', 'area_ha', 'perc_ocupacao')


def validar_cobertura(base, municipios, contrato=COL9):
    """Verifica dados completos antes dos filtros; cadastro confere a identidade IBGE."""
    faltam = set(COLUNAS_COL9) - set(base.columns)
    if faltam:
        raise ValueError(f'Colunas de cobertura ausentes: {sorted(faltam)}')
    if not {'CD_MUN', 'NM_MUN', 'SIGLA_UF'} <= set(municipios.columns):
        raise ValueError('Cadastro territorial sem código, nome ou UF.')
    if municipios[['CD_MUN', 'NM_MUN', 'SIGLA_UF']].isna().any().any():
        raise ValueError('Cadastro territorial contém valores ausentes.')
    if len(municipios) != contrato.municipios or not municipios['CD_MUN'].is_unique:
        raise ValueError('Quantidade ou unicidade do cadastro territorial inválida.')
    if len(base) != contrato.linhas or base[list(COLUNAS_COL9)].isna().any().any():
        raise ValueError('Quantidade de registros ou preenchimento da cobertura inválido.')
    for coluna in ('CD_MUN', 'ano', 'classe_cobertura', 'pixels', 'area_ha', 'perc_ocupacao'):
        valores = pd.to_numeric(base[coluna], errors='raise')
        if not np.isfinite(valores.to_numpy(dtype=float)).all():
            raise ValueError(f'{coluna}: valor não finito.')
        if coluna in ('CD_MUN', 'ano', 'classe_cobertura', 'pixels') and (valores % 1 != 0).any():
            raise ValueError(f'{coluna}: esperado número inteiro.')
    if set(base['CD_MUN']) != set(municipios['CD_MUN']):
        raise ValueError('Códigos da cobertura divergem do cadastro territorial.')
    if set(base['SIGLA_UF']) != contrato.ufs or set(municipios['SIGLA_UF']) != contrato.ufs:
        raise ValueError('UFs divergentes do contrato.')
    if set(base['ano']) != set(range(contrato.inicio, contrato.fim + 1)):
        raise ValueError('Anos divergentes do contrato.')
    if base.duplicated(['CD_MUN', 'ano', 'classe_cobertura']).any():
        raise ValueError('Chave município–ano–classe duplicada.')
    pares = base[['CD_MUN', 'ano']].drop_duplicates()
    if len(pares) != contrato.municipios * (contrato.fim - contrato.inicio + 1):
        raise ValueError('Há município sem cobertura em algum ano.')
    cadastro = municipios.set_index('CD_MUN')
    for coluna in ('NM_MUN', 'SIGLA_UF'):
        if not base[coluna].eq(base['CD_MUN'].map(cadastro[coluna])).all():
            raise ValueError(f'{coluna} diverge do cadastro por código IBGE.')
    if ((base['area_ha'] <= 0) | (base['pixels'] <= 0) |
            ~base['perc_ocupacao'].between(0, 100) |
            ~base['classe_cobertura'].between(1, 255)).any():
        raise ValueError('Área, pixels, percentual ou código de classe fora do domínio.')
