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


def carregar_geometrias():
    """Polígonos dos municípios da área de estudo (SIRGAS 2000)."""
    gdf = gpd.read_file(config.SHAPEFILE_MUNICIPIOS).to_crs("EPSG:4674")
    gdf["CD_MUN"] = gdf["CD_MUN"].astype(int)

    if config.AREA_ESTUDO_CSV.exists():
        area_estudo = pd.read_csv(config.AREA_ESTUDO_CSV)
        gdf = gdf[gdf["CD_MUN"].isin(area_estudo["CD_MUN"].astype(int))]

    return gdf


def carregar_municipios():
    """Municípios da área de estudo com área oficial e centroide."""
    gdf = carregar_geometrias()

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


if __name__ == "__main__":
    municipios = carregar_municipios()
    municipios.to_csv(config.MUNICIPIOS_CSV, index=False)
    print(f"{len(municipios)} municípios gravados em {config.MUNICIPIOS_CSV}")
