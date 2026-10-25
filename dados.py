"""Acesso aos dados do painel.

Com as variáveis do PostgreSQL definidas (PGHOST etc., como no docker-compose),
os dados vêm do banco. Sem elas, vêm dos CSVs gerados em processamento/, o que
permite rodar o painel sem Docker. Os dois caminhos devolvem as mesmas colunas.
"""
import os

import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USA_BANCO = bool(os.environ.get("PGHOST"))
CACHE_SEGUNDOS = 3600  # dados mudam só quando o processamento é executado


def _csv(*partes):
    return os.path.join(BASE_DIR, *partes)


@st.cache_resource
def _engine():
    # Importado aqui para o modo CSV funcionar sem SQLAlchemy/psycopg instalados
    from sqlalchemy import create_engine

    # Sem parâmetros na URL: o psycopg lê PGHOST, PGPORT, PGDATABASE, PGUSER e PGPASSWORD
    return create_engine("postgresql+psycopg://", pool_pre_ping=True, pool_size=2, max_overflow=2)


def _consultar(sql, parametros=None):
    from sqlalchemy import text

    with _engine().connect() as conexao:
        return pd.read_sql(text(sql), conexao, params=parametros)


@st.cache_data(ttl=CACHE_SEGUNDOS, show_spinner="Carregando dados de cobertura...")
def carregar_cobertura():
    """Área por município, ano e classe (colunas CD_MUN, NM_MUN, SIGLA_UF, ano,
    classe_cobertura, area_ha, perc_ocupacao)."""
    if USA_BANCO:
        return _consultar(
            'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", ano,'
            " classe_cobertura, area_ha, perc_ocupacao"
            " FROM mapbiomas.vw_cobertura_municipio ORDER BY cd_mun, ano, classe_cobertura"
        )
    return pd.read_csv(_csv("historico", "estatisticas_coverage_historico.csv"), sep=";", decimal=",")


@st.cache_data(ttl=CACHE_SEGUNDOS, show_spinner=False)
def carregar_legenda():
    """Classes MapBiomas (classe_cobertura, nome_classe, cor_rgb, grupo, tipo)."""
    if USA_BANCO:
        return _consultar(
            "SELECT classe_id AS classe_cobertura, nome AS nome_classe, cor AS cor_rgb, grupo, tipo"
            " FROM mapbiomas.classe ORDER BY classe_id"
        )
    return pd.read_csv(_csv("historico", "legenda_mapbiomas.csv"))


@st.cache_data(ttl=CACHE_SEGUNDOS, show_spinner=False)
def carregar_focos_mensais():
    """Focos de calor por município, ano e mês (só meses com focos), com médias de
    FRP, chuva, dias sem chuva e risco de fogo quando disponíveis."""
    if USA_BANCO:
        return _consultar(
            'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", ano, mes, focos,'
            " focos_com_frp, frp_medio, frp_maximo, precipitacao_media, dias_sem_chuva_medio, risco_fogo_medio"
            " FROM queimadas.vw_focos_municipio_mes ORDER BY cd_mun, ano, mes"
        )
    return pd.read_csv(_csv("historico", "focos_municipio_mensal.csv"), sep=";", decimal=",")


@st.cache_data(ttl=CACHE_SEGUNDOS, show_spinner="Carregando focos...")
def carregar_focos_pontos(ano, cd_mun=None):
    """Localização dos focos de um ano (de um município ou de toda a área de estudo).

    Só disponível com o banco; no modo CSV devolve None.
    """
    if not USA_BANCO:
        return None
    sql = (
        "SELECT ST_Y(f.geom) AS latitude, ST_X(f.geom) AS longitude,"
        " (f.data_hora AT TIME ZONE 'UTC')::date AS data, a.frp"
        " FROM queimadas.foco f"
        " JOIN ref.municipio m USING (cd_mun)"
        " LEFT JOIN queimadas.foco_atributo a USING (foco_id)"
        " WHERE m.area_estudo"
        "   AND f.data_hora >= make_timestamptz(:ano, 1, 1, 0, 0, 0, 'UTC')"
        "   AND f.data_hora <  make_timestamptz(:ano + 1, 1, 1, 0, 0, 0, 'UTC')"
    )
    parametros = {"ano": int(ano)}
    if cd_mun is not None:  # usa o índice (cd_mun, data_hora); sem município, o BRIN de data_hora
        sql += " AND f.cd_mun = :cd_mun"
        parametros["cd_mun"] = int(cd_mun)
    return _consultar(sql, parametros)


@st.cache_data(ttl=CACHE_SEGUNDOS, show_spinner=False)
def carregar_municipios():
    """Municípios da área de estudo (CD_MUN, nome_municipio, SIGLA_UF, AREA_KM2, latitude, longitude)."""
    if USA_BANCO:
        return _consultar(
            'SELECT cd_mun AS "CD_MUN", nome AS nome_municipio, sigla_uf AS "SIGLA_UF",'
            ' area_km2::float8 AS "AREA_KM2", latitude, longitude FROM ref.vw_municipio ORDER BY cd_mun'
        )
    return pd.read_csv(_csv("coordenadas", "municipios_coord.csv"))
