"""Indicadores descritivos D1–D4. Não define alvos de modelagem nem grava dados."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

METODOLOGIA = json.loads((Path(__file__).parent / 'referencias' / 'metodologia_col9.json').read_text(encoding='utf-8'))
CATEGORIAS = {
    'vegetacao_nativa': 'Vegetação nativa operacional',
    'natural_especifica': 'Ambientes naturais específicos',
    'usos_antropicos': 'Usos antrópicos mapeados',
    'agua': 'Superfície de água',
    'indeterminada': 'Classe 25 — origem indeterminada',
    'nao_observado': 'Não observado',
}
MAPA_CATEGORIAS = {c: nome for nome in CATEGORIAS for c in METODOLOGIA[nome]}
OBSERVADOS = set(MAPA_CATEGORIAS) - set(METODOLOGIA['nao_observado'])


def _verificar(base):
    if not {'CD_MUN', 'ano', 'classe_cobertura', 'area_ha'} <= set(base):
        raise ValueError('Cobertura sem colunas canônicas.')
    if base.duplicated(['CD_MUN', 'ano', 'classe_cobertura']).any():
        raise ValueError('Cobertura contém chave duplicada.')
    if base[['CD_MUN', 'ano', 'classe_cobertura', 'area_ha']].isna().any().any():
        raise ValueError('Cobertura contém valores ausentes.')
    if not set(base.classe_cobertura) <= set(MAPA_CATEGORIAS):
        raise ValueError('Classe sem definição na metodologia Col9.')
    if not np.isfinite(base.area_ha.astype(float)).all() or (base.area_ha < 0).any():
        raise ValueError('Área inválida.')


def _percentual(numerador, denominador):
    return 100 * numerador / denominador.where(denominador > 0)


def classificar(base):
    _verificar(base)
    resultado = base.copy()
    resultado['categoria_operacional'] = resultado.classe_cobertura.map(MAPA_CATEGORIAS).map(CATEGORIAS)
    resultado['versao_metodologia'] = METODOLOGIA['versao']
    return resultado


def indicadores(base, por=('ano',)):
    """Requer base territorial/temporal validada, antes do filtro de classes.

    Categorias ausentes viram zero apenas nos grupos observados da base. Grupos
    sem área classificada recebem percentuais NA. Não inventa município–ano.
    """
    _verificar(base)
    por = list(por)
    resultado = base.groupby(por, as_index=False, observed=True).agg(registros=('area_ha', 'size'))
    for categoria in CATEGORIAS:
        parcelas = base[base.classe_cobertura.isin(METODOLOGIA[categoria])]
        soma = parcelas.groupby(por, as_index=False, observed=True).area_ha.sum().rename(columns={'area_ha': f'{categoria}_ha'})
        resultado = resultado.merge(soma, on=por, how='left', validate='one_to_one')
        resultado[f'{categoria}_ha'] = resultado[f'{categoria}_ha'].fillna(0)
    resultado['area_classificada_ha'] = resultado[[f'{c}_ha' for c in CATEGORIAS if c != 'nao_observado']].sum(axis=1)
    extra = base[base.classe_cobertura.isin(METODOLOGIA['sensibilidade_vegetacao'])].groupby(por, as_index=False, observed=True).area_ha.sum().rename(columns={'area_ha': 'sensibilidade_vegetacao_ha'})
    resultado = resultado.merge(extra, on=por, how='left', validate='one_to_one')
    resultado['sensibilidade_vegetacao_ha'] = resultado.sensibilidade_vegetacao_ha.fillna(0)
    denominador = resultado.area_classificada_ha
    resultado['vegetacao_nativa_pct'] = _percentual(resultado.vegetacao_nativa_ha, denominador)
    resultado['vegetacao_nativa_ampliada_pct'] = _percentual(resultado.vegetacao_nativa_ha + resultado.sensibilidade_vegetacao_ha, denominador)
    resultado['usos_antropicos_pct'] = _percentual(resultado.usos_antropicos_ha, denominador)
    resultado['usos_antropicos_com25_pct'] = _percentual(resultado.usos_antropicos_ha + resultado.indeterminada_ha, denominador)
    return resultado.sort_values(por).reset_index(drop=True)


def serie_classes(base, codigos=None):
    """Área e participação por classe; denominador sempre vem da base completa."""
    _verificar(base)
    anos = sorted(base.ano.unique())
    codigos = sorted(set(base.classe_cobertura) & OBSERVADOS) if codigos is None else sorted(set(codigos) & OBSERVADOS)
    grade = pd.MultiIndex.from_product([anos, codigos], names=['ano', 'classe_cobertura'])
    soma = base[base.classe_cobertura.isin(OBSERVADOS)].groupby(['ano', 'classe_cobertura']).area_ha.sum()
    resultado = soma.reindex(grade, fill_value=0).rename('area_ha').reset_index()
    totais = indicadores(base)[['ano', 'area_classificada_ha']]
    resultado = resultado.merge(totais, on='ano', validate='many_to_one')
    resultado['area_ha'] = resultado.area_ha.where(resultado.area_classificada_ha > 0)
    resultado['participacao_pct'] = _percentual(resultado.area_ha, resultado.area_classificada_ha)
    return resultado


def medias_decadas(base, codigos=None):
    anual = serie_classes(base, codigos)
    anual['decada'] = anual.ano // 10 * 10
    medias = anual.groupby(['decada', 'classe_cobertura'], as_index=False).agg(
        media_anual_area_ha=('area_ha', 'mean'), anos_observados=('area_ha', 'count'),
        primeiro_ano=('ano', 'min'), ultimo_ano=('ano', 'max'))
    medias['periodo_incompleto'] = medias.anos_observados.ne(10)
    medias['periodo'] = medias.primeiro_ano.astype(str) + '–' + medias.ultimo_ano.astype(str)
    return medias


def comparar_anos(base, inicial, final, codigos=None):
    if inicial >= final or not {inicial, final} <= set(base.ano):
        raise ValueError('Escolha dois anos observados, em ordem crescente.')
    serie = serie_classes(base[base.ano.isin([inicial, final])], codigos)
    tabela = serie.pivot(index='classe_cobertura', columns='ano', values='area_ha').rename(columns={inicial: 'area_inicial_ha', final: 'area_final_ha'}).reset_index()
    tabela.columns.name = None
    tabela['variacao_liquida_ha'] = tabela.area_final_ha - tabela.area_inicial_ha
    tabela['variacao_relativa_pct'] = _percentual(tabela.variacao_liquida_ha, tabela.area_inicial_ha)
    tabela['ano_inicial'], tabela['ano_final'] = inicial, final
    return tabela


def auditar_areas(base, territorio):
    """Confronta somas raster e duas medidas do MESMO limite original (não simplificado).

    Diferenças são medidas de consistência e não são rotuladas como NoData.
    Não altera perc_ocupacao nem os denominadores originais.
    """
    if not territorio.CD_MUN.is_unique or set(base.CD_MUN) != set(territorio.CD_MUN):
        raise ValueError('Território e cobertura não têm a mesma seleção de códigos.')
    areas = ['area_cadastrada_ha', 'area_geodesica_wgs84_ha', 'area_geodesica_grs80_ha']
    if territorio[areas].isna().any().any() or (territorio[areas] <= 0).any().any():
        raise ValueError('Áreas territoriais ausentes ou inválidas.')
    tabela = indicadores(base, ('CD_MUN', 'ano')).merge(
        territorio[['CD_MUN', 'NM_MUN', 'SIGLA_UF', *areas]], on='CD_MUN', validate='many_to_one')
    for referencia in ('cadastrada', 'geodesica_wgs84', 'geodesica_grs80'):
        tabela[f'diferenca_classificada_{referencia}_ha'] = tabela.area_classificada_ha - tabela[f'area_{referencia}_ha']
        tabela[f'razao_classificada_{referencia}_pct'] = _percentual(tabela.area_classificada_ha, tabela[f'area_{referencia}_ha'])
    tabela['desvio_cadastro_geodesica_pct'] = _percentual(tabela.area_cadastrada_ha - tabela.area_geodesica_wgs84_ha, tabela.area_geodesica_wgs84_ha)
    tabela['causa_diferenca'] = 'não atribuída; auditar método de área, máscara e recorte'
    return tabela
