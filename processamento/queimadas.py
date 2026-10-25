"""Focos de calor do INPE (satélite de referência) por município.

- Focos: um zip anual com todos os focos do Brasil (config.FOCOS_DIR).
- Atributos: shapefiles anuais do BDQueimadas com FRP, chuva, dias sem chuva e
  risco de fogo, ligados aos focos por data/hora e coordenadas.

O município de cada foco é definido no banco pelo polígono que contém o ponto.
Grava também historico/focos_municipio_mensal.csv (modo CSV do app).

Uso:  python processamento/queimadas.py
"""
import re
import zipfile

import numpy as np
import pandas as pd
import pyogrio

import config
from banco import aplicar_migracoes, conectar, registrar_carga

ATRIBUTOS = ["frp", "precipitacao", "dias_sem_chuva", "risco_fogo"]


def arquivos_focos():
    return sorted(config.FOCOS_DIR.glob("focos_br_ref_*.zip"))


def ano_do_arquivo(caminho):
    return int(re.search(r"(\d{4})", caminho.name).group(1))


def dentro(dados, limites, x="lon", y="lat"):
    xmin, ymin, xmax, ymax = limites
    return dados[dados[x].between(xmin, xmax) & dados[y].between(ymin, ymax)]


def ler_focos(limites):
    """Focos de todos os anos dentro do retângulo da área de estudo, em ordem de data."""
    partes = []
    for arquivo in arquivos_focos():
        with zipfile.ZipFile(arquivo) as compactado:
            dados = pd.read_csv(compactado.open(compactado.namelist()[0]),
                                usecols=["id_bdq", "foco_id", "lat", "lon", "data_pas", "bioma"])
        partes.append(dentro(dados, limites))
    focos = pd.concat(partes, ignore_index=True)
    focos["data_hora"] = pd.to_datetime(focos["data_pas"], utc=True)  # o INPE publica em UTC
    return focos.drop(columns="data_pas").sort_values("data_hora", kind="stable").reset_index(drop=True)


def arquivos_atributos(anos):
    """Shapefiles anuais do BDQueimadas para os anos que têm focos."""
    encontrados = []
    for shp in config.FOCOS_ATRIBUTOS_DIR.glob("focos_qmd_inpe_*/focos_qmd_inpe_*.shp"):
        if shp.name.startswith("._"):  # metadados do macOS
            continue
        if int(shp.name[15:19]) in anos:
            encontrados.append(shp)
    return sorted(encontrados)


def ler_atributos(shapefiles, limites):
    """Atributos dos focos, com a limpeza de valores inválidos."""
    partes = []
    for shp in shapefiles:
        dados = pyogrio.read_dataframe(
            shp, read_geometry=False,
            columns=["DataHora", "Latitude", "Longitude", "FRP", "Precipitac", "DiaSemChuv", "RiscoFogo"],
        )
        if dados.empty:
            continue
        # Nos anos antigos as colunas vêm como texto; vazio vira NaN
        numeros = {c: pd.to_numeric(dados[c].astype(str).str.strip(), errors="coerce")
                   for c in ["Latitude", "Longitude", "FRP", "Precipitac", "DiaSemChuv", "RiscoFogo"]}
        partes.append(dentro(pd.DataFrame({
            "data_hora": pd.to_datetime(dados["DataHora"], format="%Y/%m/%d %H:%M:%S", utc=True),
            "lat": numeros["Latitude"],
            "lon": numeros["Longitude"],
            "frp": numeros["FRP"],
            "precipitacao": numeros["Precipitac"],
            "dias_sem_chuva": numeros["DiaSemChuv"],
            "risco_fogo": numeros["RiscoFogo"],
        }), limites))
    atributos = pd.concat(partes, ignore_index=True).replace(-999, np.nan)  # -999 = sem dado

    # Valores fora da faixa física da variável são tratados como ausentes
    atributos.loc[atributos["frp"] < 0, "frp"] = np.nan
    atributos.loc[atributos["precipitacao"] < 0, "precipitacao"] = np.nan
    atributos.loc[~atributos["dias_sem_chuva"].between(0, 120), "dias_sem_chuva"] = np.nan  # o INPE limita a 120
    atributos.loc[~atributos["risco_fogo"].between(0, 1), "risco_fogo"] = np.nan
    return atributos.dropna(subset=ATRIBUTOS, how="all")


def ligar_atributos(focos, atributos):
    """Liga atributos aos focos por data/hora e coordenadas (3 casas decimais).

    Focos com a mesma data/hora e coordenadas são pareados pela ordem de ocorrência.
    """
    chave = ["data_hora", "lat3", "lon3"]
    pares = []
    for dados in (focos, atributos):
        dados = dados.assign(lat3=dados["lat"].round(3), lon3=dados["lon"].round(3))
        dados["ordem"] = dados.groupby(chave).cumcount()
        pares.append(dados)
    ligados = pares[0][["foco_id"] + chave + ["ordem"]].merge(
        pares[1][chave + ["ordem"] + ATRIBUTOS], on=chave + ["ordem"]
    )
    return ligados[["foco_id"] + ATRIBUTOS]


def sem_nan(valor):
    return None if pd.isna(valor) else valor


def carregar_no_banco(conexao):
    """Substitui focos e atributos e recalcula o agregado mensal numa única transação."""
    limites = conexao.execute(
        "SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e)"
        " FROM (SELECT ST_Extent(geom) AS e FROM ref.municipio) x"
    ).fetchone()
    focos = ler_focos(limites)
    anos = {ano_do_arquivo(a) for a in arquivos_focos()}
    shapefiles = arquivos_atributos(anos)
    atributos = ligar_atributos(focos, ler_atributos(shapefiles, limites))
    print(f"{len(focos)} focos no retângulo da área de estudo; {len(atributos)} com atributos")

    with conexao.transaction():
        carga_focos = registrar_carga(
            conexao, "INPE BDQueimadas - focos de calor do satélite de referência",
            arquivos_focos(), 0, versao=config.FOCOS_SATELITE,
            referencia="https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/",
        )
        carga_atributos = registrar_carga(
            conexao, "INPE BDQueimadas - atributos dos focos (FRP, chuva, dias sem chuva, risco de fogo)",
            [s.with_suffix(".dbf") for s in shapefiles], 0, versao=config.FOCOS_SATELITE,
            referencia="https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/",
        )

        conexao.execute(
            "CREATE TEMP TABLE foco_bruto (foco_id uuid, id_bdq bigint, data_hora timestamptz,"
            " bioma text, lon float8, lat float8) ON COMMIT DROP"
        )
        with conexao.cursor().copy("COPY foco_bruto FROM STDIN") as copia:
            for f in focos.itertuples(index=False):
                copia.write_row((f.foco_id, int(f.id_bdq), f.data_hora, f.bioma, float(f.lon), float(f.lat)))

        # Polígonos subdivididos: o teste ponto-no-polígono fica rápido mesmo em municípios
        # com dezenas de milhares de vértices
        conexao.execute(
            "CREATE TEMP TABLE municipio_parte ON COMMIT DROP AS"
            " SELECT cd_mun, ST_Subdivide(geom, 256) AS geom FROM ref.municipio"
        )
        conexao.execute("CREATE INDEX ON municipio_parte USING gist (geom)")
        conexao.execute("ANALYZE foco_bruto, municipio_parte")

        conexao.execute("DELETE FROM queimadas.foco_atributo")
        conexao.execute("DELETE FROM queimadas.foco")
        inseridos = conexao.execute(
            """
            INSERT INTO queimadas.foco (foco_id, id_bdq, data_hora, satelite, bioma, cd_mun, geom, carga_id)
            SELECT foco_id, id_bdq, data_hora, %(satelite)s, bioma, cd_mun, ponto, %(carga)s
            FROM (
                -- Um ponto na divisa entre partes (ou entre municípios) casa com mais de uma;
                -- fica uma só, escolhida de forma determinística
                SELECT DISTINCT ON (b.foco_id) b.foco_id, b.id_bdq, b.data_hora, b.bioma, p.cd_mun, b.ponto
                FROM (SELECT *, ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 4674) AS ponto
                      FROM foco_bruto) b
                JOIN municipio_parte p ON ST_Intersects(p.geom, b.ponto)
                ORDER BY b.foco_id, p.cd_mun
            ) unicos
            ORDER BY data_hora  -- ordem física por data, base do índice BRIN
            """,
            {"satelite": config.FOCOS_SATELITE, "carga": carga_focos},
        ).rowcount

        conexao.execute(
            "CREATE TEMP TABLE atributo_bruto (foco_id uuid, frp real, precipitacao real,"
            " dias_sem_chuva smallint, risco_fogo real) ON COMMIT DROP"
        )
        with conexao.cursor().copy("COPY atributo_bruto FROM STDIN") as copia:
            for a in atributos.itertuples(index=False):
                dias = None if pd.isna(a.dias_sem_chuva) else int(a.dias_sem_chuva)
                copia.write_row((a.foco_id, sem_nan(a.frp), sem_nan(a.precipitacao), dias, sem_nan(a.risco_fogo)))
        com_atributos = conexao.execute(
            "INSERT INTO queimadas.foco_atributo (foco_id, frp, precipitacao, dias_sem_chuva, risco_fogo, carga_id)"
            " SELECT a.foco_id, a.frp, a.precipitacao, a.dias_sem_chuva, a.risco_fogo, %s"
            " FROM atributo_bruto a JOIN queimadas.foco f USING (foco_id)",
            (carga_atributos,),
        ).rowcount

        conexao.execute("UPDATE ref.carga SET registros = %s WHERE carga_id = %s", (inseridos, carga_focos))
        conexao.execute("UPDATE ref.carga SET registros = %s WHERE carga_id = %s", (com_atributos, carga_atributos))
        conexao.execute("REFRESH MATERIALIZED VIEW queimadas.mv_focos_municipio_mes")

    conexao.execute("VACUUM ANALYZE queimadas.foco")
    conexao.execute("VACUUM ANALYZE queimadas.foco_atributo")
    conexao.execute("ANALYZE queimadas.mv_focos_municipio_mes")
    print(f"{inseridos} focos carregados em queimadas.foco ({com_atributos} com atributos)")


def exportar_csv(conexao):
    """Grava o agregado mensal da área de estudo para o modo CSV do app."""
    cursor = conexao.execute(
        'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", ano, mes, focos,'
        " focos_com_frp, frp_medio, frp_maximo, precipitacao_media, dias_sem_chuva_medio, risco_fogo_medio"
        " FROM queimadas.vw_focos_municipio_mes ORDER BY cd_mun, ano, mes"
    )
    mensal = pd.DataFrame(cursor.fetchall(), columns=[c.name for c in cursor.description])
    mensal.to_csv(config.FOCOS_MENSAIS_CSV, sep=";", decimal=",", float_format="%.4f",
                  index=False, encoding="utf-8")
    print(f"{len(mensal)} linhas gravadas em {config.FOCOS_MENSAIS_CSV}")


if __name__ == "__main__":
    with conectar() as conexao:
        aplicar_migracoes(conexao)
        carregar_no_banco(conexao)
        exportar_csv(conexao)
