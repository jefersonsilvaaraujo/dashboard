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

# Lista opcional com os municípios da área de estudo (CSV com a coluna CD_MUN).
# Se o arquivo não existir, todos os municípios do shapefile são usados.
AREA_ESTUDO_CSV = DADOS_DIR / "municipios_base" / "area_estudo.csv"

# Saídas (versionadas, lidas pelo app)
MUNICIPIOS_CSV = PROJETO_DIR / "coordenadas" / "municipios_coord.csv"
COBERTURA_CSV = PROJETO_DIR / "historico" / "estatisticas_coverage_historico.csv"
LEGENDA_CSV = PROJETO_DIR / "historico" / "legenda_mapbiomas.csv"
