"""Desmatamento PRODES por município e bioma.

Para cada parte de município dentro de um bioma (interseção calculada no PostGIS),
soma a área de cada classe do raster PRODES Brasil (~10 m). A área de cada pixel é
calculada no elipsoide GRS80 pela latitude da sua linha, pois o raster está em
coordenadas geográficas.

Grava também historico/prodes_area_classe_municipio.csv (modo CSV do app).

Uso:  python processamento/prodes.py
"""
import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import shapely
from rasterio.features import geometry_mask
from rasterio.windows import Window, from_bounds

import config
from banco import aplicar_migracoes, conectar, registrar_carga

# Elipsoide GRS80 (SIRGAS 2000)
SEMIEIXO_MAIOR_M = 6378137.0
ACHATAMENTO = 1 / 298.257222101
EXCENTRICIDADE = np.sqrt(ACHATAMENTO * (2 - ACHATAMENTO))
SEMIEIXO_MENOR_M = SEMIEIXO_MAIOR_M * (1 - ACHATAMENTO)
SEM_DADO = 255
LINHAS_POR_BLOCO = 256           # limita a memória ao ler municípios grandes a 10 m


def ler_legenda():
    """Classes do PRODES a partir do estilo QGIS (.qml) distribuído com o raster."""
    qml = config.PRODES_RASTER.with_suffix(".qml")
    classes = []
    for entrada in ET.parse(qml).iter("paletteEntry"):
        valor = int(entrada.get("value"))
        rotulo = entrada.get("label").split(" ", 1)[1].strip()
        ano = re.fullmatch(r"[dr](\d{4})", rotulo)
        if rotulo.startswith("d") and ano:
            tipo = "desmatamento"
        elif rotulo.startswith("r") and ano:
            tipo = "residuo"
        elif valor == 91:
            tipo = "hidrografia"
        elif valor == 100:
            tipo = "vegetacao_nativa"
        else:
            raise ValueError(f"Classe PRODES não prevista: {valor} {rotulo}")
        classes.append((valor, rotulo, tipo, int(ano.group(1)) if ano else None))
    return classes


def _q(latitude_rad):
    """Função auxiliar da área de uma faixa de latitude no elipsoide."""
    seno = np.sin(latitude_rad)
    return seno / (1 - EXCENTRICIDADE**2 * seno**2) + np.arctanh(EXCENTRICIDADE * seno) / EXCENTRICIDADE


def area_pixel_m2(lat_topo_graus, altura_graus, largura_graus):
    """Área exata, no elipsoide, de pixels geográficos: b²/2 · Δλ · |q(φ1) − q(φ2)|."""
    phi1 = np.radians(lat_topo_graus)
    phi2 = np.radians(lat_topo_graus + altura_graus)
    return SEMIEIXO_MENOR_M**2 / 2 * np.radians(largura_graus) * np.abs(_q(phi1) - _q(phi2))


def area_por_classe(parte):
    """Área (ha) de cada classe dentro de uma geometria. Roda em processo separado."""
    cd_mun, cd_bioma, wkb = parte
    geometria = shapely.from_wkb(wkb)
    areas = np.zeros(256)
    with rasterio.open(config.PRODES_RASTER) as raster:
        janela = from_bounds(*geometria.bounds, transform=raster.transform)
        janela = janela.round_offsets().round_lengths().intersection(Window(0, 0, raster.width, raster.height))
        for inicio in range(0, int(janela.height), LINHAS_POR_BLOCO):
            bloco = Window(janela.col_off, janela.row_off + inicio, janela.width,
                           min(LINHAS_POR_BLOCO, janela.height - inicio))
            dados = raster.read(1, window=bloco)
            t = raster.window_transform(bloco)
            dentro = geometry_mask([geometria], out_shape=dados.shape, transform=t, invert=True)
            linhas = np.nonzero(dentro)[0]
            contagem = np.bincount(linhas * 256 + dados[dentro], minlength=dados.shape[0] * 256)
            contagem = contagem.reshape(dados.shape[0], 256)
            # Área de um pixel em cada linha (varia com a latitude)
            area_linha = area_pixel_m2(t.f + np.arange(dados.shape[0]) * t.e, t.e, t.a)
            areas += (contagem * area_linha[:, None]).sum(axis=0)
    areas[SEM_DADO] = 0  # fora do Brasil no raster (pequenas diferenças de limite)
    return cd_mun, cd_bioma, {int(c): areas[c] / 1e4 for c in np.nonzero(areas)[0]}


def carregar_biomas(conexao):
    biomas = gpd.read_file(config.BIOMAS_SHP).to_crs("EPSG:4674")
    with conexao.transaction():
        carga_id = registrar_carga(conexao, "IBGE - Biomas do Brasil 1:250.000", config.BIOMAS_SHP,
                                   len(biomas), versao="2019",
                                   referencia="https://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/vetores/")
        conexao.cursor().executemany(
            """
            INSERT INTO ref.bioma (cd_bioma, nome, geom, carga_id)
            VALUES (%s, %s, ST_Multi(ST_GeomFromWKB(%s, 4674)), %s)
            ON CONFLICT (cd_bioma) DO UPDATE SET nome = EXCLUDED.nome, geom = EXCLUDED.geom, carga_id = EXCLUDED.carga_id
            """,
            [(int(b.CD_Bioma), b.Bioma, b.geometry.wkb, carga_id) for b in biomas.itertuples()],
        )
    print(f"{len(biomas)} biomas carregados em ref.bioma")


def partes_municipio_bioma(conexao):
    """Interseção município x bioma, com o bioma subdividido para acelerar o recorte."""
    return conexao.execute(
        """
        WITH bioma_parte AS (SELECT cd_bioma, ST_Subdivide(geom, 512) AS geom FROM ref.bioma)
        SELECT m.cd_mun, p.cd_bioma,
               ST_AsBinary(ST_Union(ST_CollectionExtract(ST_Intersection(m.geom, p.geom), 3)))
        FROM ref.municipio m
        JOIN bioma_parte p ON ST_Intersects(m.geom, p.geom)
        GROUP BY m.cd_mun, p.cd_bioma
        """
    ).fetchall()


def carregar_no_banco(conexao):
    carregar_biomas(conexao)
    partes = [(cd_mun, cd_bioma, bytes(wkb)) for cd_mun, cd_bioma, wkb in partes_municipio_bioma(conexao)]
    print(f"{len(partes)} partes município x bioma; calculando áreas por classe...")

    processos = min(6, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=processos) as executor:
        resultados = list(executor.map(area_por_classe, partes, chunksize=4))
    linhas = [(cd_mun, cd_bioma, classe, area)
              for cd_mun, cd_bioma, areas in resultados for classe, area in areas.items()]

    legenda = ler_legenda()
    with conexao.transaction():
        carga_id = registrar_carga(conexao, "INPE PRODES Brasil - desmatamento por ano PRODES",
                                   config.PRODES_RASTER, len(linhas), versao=config.PRODES_VERSAO,
                                   referencia="https://terrabrasilis.dpi.inpe.br/downloads/")
        conexao.cursor().executemany(
            """
            INSERT INTO prodes.classe (classe_id, rotulo, tipo, ano, carga_id) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (classe_id) DO UPDATE SET
                rotulo = EXCLUDED.rotulo, tipo = EXCLUDED.tipo, ano = EXCLUDED.ano, carga_id = EXCLUDED.carga_id
            """,
            [(*classe, carga_id) for classe in legenda],
        )
        conexao.execute("DELETE FROM prodes.area_classe")
        with conexao.cursor().copy(
            "COPY prodes.area_classe (cd_mun, cd_bioma, classe_id, area_ha, carga_id) FROM STDIN"
        ) as copia:
            for cd_mun, cd_bioma, classe, area in linhas:
                copia.write_row((cd_mun, cd_bioma, classe, area, carga_id))
    conexao.execute("ANALYZE ref.bioma, prodes.classe, prodes.area_classe")
    print(f"{len(linhas)} linhas carregadas em prodes.area_classe (carga {carga_id})")


def exportar_csv(conexao):
    """Grava a área por classe da área de estudo para o modo CSV do app."""
    cursor = conexao.execute(
        'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", bioma,'
        " classe_id, rotulo, tipo, ano, area_ha"
        " FROM prodes.vw_area_classe_municipio ORDER BY cd_mun, bioma, classe_id"
    )
    tabela = pd.DataFrame(cursor.fetchall(), columns=[c.name for c in cursor.description])
    tabela["ano"] = tabela["ano"].astype("Int64")
    tabela.to_csv(config.PRODES_CSV, sep=";", decimal=",", float_format="%.4f", index=False, encoding="utf-8")
    print(f"{len(tabela)} linhas gravadas em {config.PRODES_CSV}")


if __name__ == "__main__":
    with conectar() as conexao:
        aplicar_migracoes(conexao)
        carregar_no_banco(conexao)
        exportar_csv(conexao)
