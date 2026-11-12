"""Base de municípios da área de estudo.

Lê o shapefile dos municípios e grava coordenadas/municipios_coord.csv, usado
pelo app para posicionar o marcador nos mapas. O código IBGE (CD_MUN) é a chave
de ligação entre todas as fontes de dados.

Uso:  python processamento/municipios.py
"""
import unicodedata
import warnings

import geopandas as gpd
import pandas as pd

import config


def normalizar_nome(nome):
    """Remove acentos, apóstrofos e hífens para casar nomes entre fontes."""
    texto = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    return " ".join(texto.upper().replace("'", "").replace("-", " ").split())


def codigos_area_estudo(gdf):
    """Códigos IBGE da área de estudo: a lista opcional, ou todos do shapefile."""
    if config.AREA_ESTUDO_CSV.exists():
        return set(pd.read_csv(config.AREA_ESTUDO_CSV)["CD_MUN"].astype(int))
    return set(gdf["CD_MUN"])


def carregar_geometrias(apenas_area_estudo=True):
    """Polígonos dos municípios (SIRGAS 2000)."""
    gdf = gpd.read_file(config.SHAPEFILE_MUNICIPIOS).to_crs("EPSG:4674")
    gdf["CD_MUN"] = gdf["CD_MUN"].astype(int)

    if apenas_area_estudo:
        gdf = gdf[gdf["CD_MUN"].isin(codigos_area_estudo(gdf))]

    return gdf


def carregar_municipios(apenas_area_estudo=True):
    """Municípios com área oficial e centroide."""
    gdf = carregar_geometrias(apenas_area_estudo)

    # Centroide em coordenadas geográficas, como na versão original do arquivo
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        centroides = gdf.geometry.centroid

    return pd.DataFrame({
        "CD_MUN": gdf["CD_MUN"].values,
        "nome_municipio": gdf["NM_MUN"].values,
        "SIGLA_UF": gdf["SIGLA_UF"].values,
        "AREA_KM2": gdf["AREA_KM2"].values,
        "latitude": centroides.y.values,
        "longitude": centroides.x.values,
    })


def carregar_no_banco(conexao):
    """Insere ou atualiza todos os municípios do shapefile em ref.municipio.

    Todos entram no banco; a lista da área de estudo só liga/desliga area_estudo,
    sem apagar dados ligados ao município.
    """
    from banco import registrar_carga

    gdf = carregar_geometrias(apenas_area_estudo=False)
    area_estudo = codigos_area_estudo(gdf)

    with conexao.transaction():
        carga_id = registrar_carga(conexao, "Limites municipais da área de estudo (IBGE)",
                                   config.SHAPEFILE_MUNICIPIOS, len(gdf))
        linhas = [
            (int(m.CD_MUN), m.NM_MUN, int(m.CD_MUN) // 100000, float(m.AREA_KM2),
             int(m.CD_MUN) in area_estudo, m.geometry.wkb, carga_id)
            for m in gdf.itertuples()
        ]
        conexao.cursor().executemany(
            """
            INSERT INTO ref.municipio (cd_mun, nome, cd_uf, area_km2, area_estudo, geom, carga_id)
            VALUES (%s, %s, %s, %s, %s, ST_Multi(ST_GeomFromWKB(%s, 4674)), %s)
            ON CONFLICT (cd_mun) DO UPDATE SET
                nome = EXCLUDED.nome, cd_uf = EXCLUDED.cd_uf, area_km2 = EXCLUDED.area_km2,
                area_estudo = EXCLUDED.area_estudo, geom = EXCLUDED.geom, carga_id = EXCLUDED.carga_id
            """,
            linhas,
        )
        # Municípios que saíram do shapefile permanecem (podem ter dados ligados), fora da área de estudo
        conexao.execute("UPDATE ref.municipio SET area_estudo = false WHERE NOT (cd_mun = ANY(%s))",
                        ([int(cd) for cd in gdf["CD_MUN"]],))
        # Derivados dos municípios: limite externo da área de estudo e pares de vizinhos
        conexao.execute("REFRESH MATERIALIZED VIEW ref.mv_area_estudo_contorno")
        conexao.execute("REFRESH MATERIALIZED VIEW ref.mv_municipio_vizinho")
    print(f"{len(gdf)} municípios carregados em ref.municipio ({len(area_estudo)} na área de estudo)")


if __name__ == "__main__":
    municipios = carregar_municipios()
    municipios.to_csv(config.MUNICIPIOS_CSV, index=False)
    print(f"{len(municipios)} municípios gravados em {config.MUNICIPIOS_CSV}")
