"""Consultas Col9 independentes do legado; nenhuma migração ou fallback para CSV."""
import json
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

import dados
from contratos_series import COL9, validar_cobertura

REFERENCIAS = Path(__file__).resolve().parent / 'referencias'


def carregar_legenda():
    legenda = pd.read_csv(REFERENCIAS / 'legenda_col9.csv')
    if not legenda['classe_cobertura'].is_unique:
        raise ValueError('Legenda Col9 contém códigos duplicados.')
    return legenda


def proveniencia():
    return {
        'serie': COL9.id, 'colecao': COL9.colecao,
        'periodo': [COL9.inicio, COL9.fim], 'municipios': COL9.municipios,
        'cobertura': COL9.cobertura, 'territorio': COL9.territorio,
        'limites': 'IBGE 2025 / EPSG:4674',
        'legenda': json.loads((REFERENCIAS / 'legenda_col9.json').read_text(encoding='utf-8')),
        'arquivos': json.loads((REFERENCIAS / 'fontes_col9.json').read_text(encoding='utf-8')),
        'metodologia': json.loads((REFERENCIAS / 'metodologia_col9.json').read_text(encoding='utf-8')),
        'ressalva_2002': 'Buriticupu: diferença de máscara; transições exigem pixels válidos nos dois anos.',
        'fontes_complementares': 'PRODES e queimadas ainda não harmonizados para os 255.',
    }


@st.cache_data(ttl=1800, show_spinner='Consultando a Coleção 9 no PostgreSQL...')
def carregar(serie_id=COL9.id):
    # Nomes SQL não vêm da interface. Validar identidade antes de consultar.
    if serie_id != COL9.id:
        raise ValueError('Este módulo aceita somente col9_255_1985_2023.')
    if not dados.USA_BANCO:
        raise RuntimeError('A Coleção 9 requer PostgreSQL (PGHOST).')
    base = dados._consultar(
        'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", '
        'ano, classe_cobertura, pixels, area_ha::float8 AS area_ha, '
        'perc_ocupacao::float8 AS perc_ocupacao '
        'FROM mapbiomas.vw_cobertura_col9_255 '
        'ORDER BY cd_mun, ano, classe_cobertura'
    )
    municipios = dados._consultar(
        'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF" '
        'FROM ref.vw_municipios_col9_255 ORDER BY cd_mun'
    )
    validar_cobertura(base, municipios)
    legenda = carregar_legenda()
    if not set(base['classe_cobertura']) <= set(legenda['classe_cobertura']):
        raise ValueError('Há classes ausentes da legenda oficial versionada da Coleção 9.')
    return base, legenda


@st.cache_data(ttl=1800, show_spinner='Consultando o território Col9...')
def carregar_territorio():
    if not dados.USA_BANCO:
        raise RuntimeError('O território Col9 requer PostgreSQL.')
    territorio = dados._consultar(
        'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", '
        'area_geom_km2::float8 * 100 AS area_cadastrada_ha, '
        'ST_Area(ST_Transform(geom,4326)::geography,true)/10000 AS area_geodesica_wgs84_ha, '
        'ST_Area(geom::geography,true)/10000 AS area_geodesica_grs80_ha, '
        'ST_SRID(geom) AS srid, ST_IsValid(geom) AS geometria_valida, '
        'ST_IsEmpty(geom) AS geometria_vazia, '
        "encode(sha256(ST_AsBinary(geom,'NDR')),'hex') AS hash_geometria, "
        'ST_AsGeoJSON(ST_Transform(ST_SimplifyPreserveTopology(geom,:tolerancia),4326)) AS geojson '
        'FROM ref.vw_municipios_col9_255 ORDER BY cd_mun', {'tolerancia': 0.002}
    )
    if (len(territorio) != COL9.municipios or not territorio.CD_MUN.is_unique or
            not territorio.srid.eq(4674).all() or not territorio.geometria_valida.all() or
            territorio.geometria_vazia.any()):
        raise ValueError('Cadastro Col9 com contagem, SRID ou geometria inválida.')
    arquivo_hashes = REFERENCIAS / 'territorio_col9_hashes.json'
    if not arquivo_hashes.exists():
        raise ValueError('Contrato territorial Col9 ausente no checkout.')
    esperado = json.loads(arquivo_hashes.read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    atual = {str(int(r.CD_MUN)): r.hash_geometria for r in territorio.itertuples()}
    if atual != esperado:
        raise ValueError('As geometrias do banco divergem da delimitação Col9 versionada.')
    return territorio


def carregar_mapas_regionais(pasta=None):
    pasta = Path(pasta) if pasta is not None else Path(__file__).parent / 'mapas_col9'
    if not (pasta / 'manifesto.json').exists():
        return None
    manifesto = json.loads((pasta / 'manifesto.json').read_text(encoding='utf-8'))
    if (manifesto.get('colecao') != '9' or manifesto.get('municipios') != 255 or
            set(manifesto.get('mapas', {})) != {'1985', '2023'} or
            manifesto.get('territorio',{}).get('sha256') != proveniencia()['arquivos']['territorio']['sha256']):
        raise ValueError('Mapas não correspondem à coleção, anos ou território Col9 aprovados.')
    for info in manifesto['mapas'].values():
        arquivo = pasta / info['arquivo']
        if arquivo.resolve().parent != pasta.resolve() or hashlib.sha256(arquivo.read_bytes()).hexdigest() != info['sha256']:
            raise ValueError('Hash ou caminho de imagem Col9 divergente do manifesto.')
    return manifesto
