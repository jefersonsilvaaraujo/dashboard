"""Caminhos usados pelos scripts de processamento.

Os dados brutos (planilhas, rasters, focos) ficam fora do repositório. Por padrão
são procurados na pasta-mãe do projeto (ex.: D:\\mestrado). Para outro local,
defina a variável de ambiente MESTRADO_DADOS.
"""
import os
from pathlib import Path

PROJETO_DIR = Path(__file__).resolve().parent.parent
DADOS_DIR = Path(os.environ.get("MESTRADO_DADOS", PROJETO_DIR.parent))

# Entradas (não versionadas)
SHAPEFILE_MUNICIPIOS = DADOS_DIR / "municipios_base" / "50km_todosMun.shp"
MAPBIOMAS_XLSX = (
    DADOS_DIR / "mapbiomas_col10"
    / "MAPBIOMAS_BRAZIL-COVERAGE_STATISTICS-COL.10.1-MUNICIPALITIES_STATES_BIOMES.xlsx"
)
MAPBIOMAS_ABA = "COVERAGE_10.1"
MAPBIOMAS_ABA_LEGENDA = "LEGEND_CODE"

# Rasters anuais de cobertura do MapBiomas Coleção 10 (Brasil inteiro, ~750 MB/ano)
# https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/lulc/coverage/
MAPBIOMAS_RASTER = DADOS_DIR / "mapbiomas_col10" / "rasters" / "brazil_coverage_{ano}.tif"
ANOS_MAPAS = (1985, 2024)

# Focos de calor do INPE, satélite de referência, um zip por ano (2003 em diante)
# https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/
FOCOS_DIR = DADOS_DIR / "queimadas_inpe" / "focos_br_ref_2003_2025"
FOCOS_SATELITE = "AQUA_M-T"
# Shapefiles anuais do BDQueimadas, com FRP, chuva, dias sem chuva e risco de fogo
FOCOS_ATRIBUTOS_DIR = DADOS_DIR / "queimadas_inpe"

# Lista opcional com os municípios da área de estudo (CSV com a coluna CD_MUN).
# Se o arquivo não existir, todos os municípios do shapefile são usados.
AREA_ESTUDO_CSV = DADOS_DIR / "municipios_base" / "area_estudo.csv"

# Saídas (versionadas, lidas pelo app)
MUNICIPIOS_CSV = PROJETO_DIR / "coordenadas" / "municipios_coord.csv"
COBERTURA_CSV = PROJETO_DIR / "historico" / "estatisticas_coverage_historico.csv"
LEGENDA_CSV = PROJETO_DIR / "historico" / "legenda_mapbiomas.csv"
FOCOS_MENSAIS_CSV = PROJETO_DIR / "historico" / "focos_municipio_mensal.csv"
MAPA_REGIAO_PNG = PROJETO_DIR / "municipios_shapefile" / "municipios_{ano}.png"
MAPAS_MUNICIPIOS_DIR = PROJETO_DIR / "mapas_municipios"
