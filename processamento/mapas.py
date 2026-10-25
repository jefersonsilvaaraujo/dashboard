"""Mapas de uso e cobertura da área de estudo e de cada município.

A partir dos rasters anuais do MapBiomas Coleção 10, gera para cada ano de
config.ANOS_MAPAS:

- o mapa da região de estudo (PNG + world file .pgw), sempre com a mesma
  extensão e o mesmo tamanho, usado no app com o marcador do município;
- um mapa por município (mapas_municipios/<CD_MUN>_<ano>.png), recortado
  pelo limite municipal e com fundo transparente.

Uso:  python processamento/mapas.py
"""
import math

import numpy as np
import pandas as pd
import rasterio
from PIL import Image, ImageDraw
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds

import config
from municipios import carregar_geometrias

LARGURA_REGIAO = 1400        # pixels do mapa da região
TAMANHO_MUNICIPIO = 500      # maior lado, em pixels, do mapa de cada município
INDICE_CONTORNO = 254        # índice da paleta usado para desenhar os limites
COR_CONTORNO = (51, 51, 51)


def montar_paleta():
    """Paleta indexada pelo código da classe; índice 0 fica transparente."""
    paleta = np.full((256, 3), 200, dtype=np.uint8)
    legenda = pd.read_csv(config.LEGENDA_CSV)
    for classe, cor in zip(legenda["classe_cobertura"], legenda["cor_rgb"]):
        paleta[classe] = [int(cor[i:i + 2], 16) for i in (1, 3, 5)]
    paleta[INDICE_CONTORNO] = COR_CONTORNO
    return paleta.flatten().tolist()


def ler_janela(raster, limites, largura_max):
    """Lê o raster no retângulo pedido, reduzindo pela moda se passar de largura_max."""
    janela = from_bounds(*limites, transform=raster.transform).round_offsets().round_lengths()
    escala = max(janela.width, janela.height) / largura_max
    escala = max(escala, 1.0)
    largura = math.ceil(janela.width / escala)
    altura = math.ceil(janela.height / escala)
    dados = raster.read(1, window=janela, out_shape=(altura, largura), resampling=Resampling.mode)
    transformacao = raster.window_transform(janela) * rasterio.Affine.scale(
        janela.width / largura, janela.height / altura
    )
    return dados, transformacao


def aneis(geometria):
    """Contornos externos de um Polygon ou MultiPolygon."""
    poligonos = getattr(geometria, "geoms", [geometria])
    return [p.exterior.coords for p in poligonos]


def desenhar_limites(imagem, geometrias, transformacao, espessura):
    inversa = ~transformacao
    desenho = ImageDraw.Draw(imagem)
    for geometria in geometrias:
        for anel in aneis(geometria):
            pontos = [inversa * (x, y) for x, y in anel]
            desenho.line(pontos, fill=INDICE_CONTORNO, width=espessura)


def para_imagem(dados, transformacao, geometrias, paleta, espessura):
    """Pinta as classes, apaga o que está fora dos polígonos e desenha os limites."""
    fora = geometry_mask(geometrias, out_shape=dados.shape, transform=transformacao)
    dados = np.where(fora, 0, dados).astype(np.uint8)
    imagem = Image.fromarray(dados, mode="P")
    imagem.putpalette(paleta)
    desenhar_limites(imagem, geometrias, transformacao, espessura)
    return imagem


def gravar_world_file(caminho_png, transformacao):
    """World file (.pgw) com as coordenadas do centro do pixel superior esquerdo."""
    a, _, c, _, e, f = transformacao[:6]
    linhas = [a, 0.0, 0.0, e, c + a / 2, f + e / 2]
    caminho_png.with_suffix(".pgw").write_text("\n".join(f"{v:.14f}" for v in linhas) + "\n")


def gerar_mapas():
    municipios = carregar_geometrias().to_crs("EPSG:4326")  # mesmo SRC dos rasters
    paleta = montar_paleta()

    # Extensão comum a todos os anos: a área de estudo com 2% de margem
    xmin, ymin, xmax, ymax = municipios.total_bounds
    margem = 0.02 * max(xmax - xmin, ymax - ymin)
    limites_regiao = (xmin - margem, ymin - margem, xmax + margem, ymax + margem)

    # Contornos simplificados para o mapa da região (o detalhe original não aparece nessa escala)
    contornos_regiao = municipios.geometry.simplify(0.002).tolist()

    config.MAPAS_MUNICIPIOS_DIR.mkdir(exist_ok=True)
    for antigo in config.MAPAS_MUNICIPIOS_DIR.glob("*.png"):
        antigo.unlink()

    for ano in config.ANOS_MAPAS:
        caminho_raster = str(config.MAPBIOMAS_RASTER).format(ano=ano)
        with rasterio.open(caminho_raster) as raster:
            dados, transformacao = ler_janela(raster, limites_regiao, LARGURA_REGIAO)
            imagem = para_imagem(dados, transformacao, contornos_regiao, paleta, espessura=1)
            destino = config.MAPA_REGIAO_PNG.with_name(config.MAPA_REGIAO_PNG.name.format(ano=ano))
            imagem.save(destino, transparency=0, optimize=True)
            gravar_world_file(destino, transformacao)
            print(f"{ano}: mapa da região {imagem.size} gravado em {destino}")

            for mun in municipios.itertuples():
                x0, y0, x1, y1 = mun.geometry.bounds
                folga = 0.02 * max(x1 - x0, y1 - y0)
                limites = (x0 - folga, y0 - folga, x1 + folga, y1 + folga)
                dados, transformacao = ler_janela(raster, limites, TAMANHO_MUNICIPIO)
                imagem = para_imagem(dados, transformacao, [mun.geometry], paleta, espessura=2)
                imagem.save(config.MAPAS_MUNICIPIOS_DIR / f"{mun.CD_MUN}_{ano}.png",
                            transparency=0, optimize=True)
            print(f"{ano}: {len(municipios)} mapas municipais gravados em {config.MAPAS_MUNICIPIOS_DIR}")


if __name__ == "__main__":
    gerar_mapas()
