"""Pré-visualizações Col9 1985/2023 com máscara dos 255 e complemento do MA.

Somente desenho por vizinho mais próximo. Não produz estatísticas, não altera
rasters e não executa ETL/banco. Geometrias originais definem a máscara visual.
"""
import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from PIL import Image
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling

PROJETO = Path(__file__).resolve().parents[1]
ALVOS = {2101772, 2108504, 2112274}


def aplicar_complemento(original, complemento, dentro_alvos):
    if original.shape != complemento.shape or original.shape != dentro_alvos.shape:
        raise ValueError('Grades de desenho incompatíveis.')
    resultado = original.copy()
    preenchidos = dentro_alvos & (original == 0) & (complemento > 0) & (complemento != 27)
    resultado[preenchidos] = complemento[preenchidos]
    return resultado, int(preenchidos.sum())


def sha256(arquivo):
    h = hashlib.sha256()
    with arquivo.open('rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def gerar(base, saida, largura=1400):
    if saida.exists():
        raise FileExistsError('Diretório de mapas já existe; escolher outro, sem sobrescrever o checkpoint.')
    gpkg = base / 'correcao_territorial_255/resultado_20261107_192346/municipios_255_ibge_2025.gpkg'
    municipios = gpd.read_file(gpkg)
    esperado = json.loads((PROJETO / 'referencias/fontes_col9.json').read_text(encoding='utf-8'))
    if sha256(gpkg) != esperado['territorio']['sha256'] or len(municipios) != 255 or municipios.CD_MUN.nunique() != 255:
        raise ValueError('Território diferente do checkpoint Col9 aprovado.')
    municipios = municipios.to_crs(4326)
    xmin, ymin, xmax, ymax = municipios.total_bounds
    altura = round(largura * (ymax - ymin) / (xmax - xmin))
    transform = from_bounds(xmin, ymin, xmax, ymax, largura, altura)
    shape = (altura, largura)
    dentro = geometry_mask(municipios.geometry, shape, transform, invert=True)
    dentro_alvos = geometry_mask(municipios[municipios.CD_MUN.astype(int).isin(ALVOS)].geometry, shape, transform, invert=True)
    legenda = pd.read_csv(PROJETO / 'referencias/legenda_col9.csv')
    paleta = np.full((256, 4), 0, dtype=np.uint8)
    for r in legenda.itertuples():
        paleta[r.classe_cobertura] = [int(r.cor_rgb[i:i+2],16) for i in (1,3,5)] + [255]
    paleta[27] = [220, 220, 220, 255]
    saida.mkdir(parents=True)
    manifesto = {'colecao': '9', 'territorio': esperado['territorio'], 'municipios': 255,
                 'crs_desenho': 'EPSG:4326', 'bounds': [float(v) for v in (xmin,ymin,xmax,ymax)],
                 'metodo': 'vizinho mais proximo; mascara 255; complemento apenas zeros nos tres municipios MA; somente visualizacao',
                 'advertencia': 'Imagem reduzida; cores nao sao RGB de origem; nao usar para estatisticas ou transicoes.', 'mapas': {}}
    patch_path = base / 'Mapas-Estudo/mapbiomas_col9_recuperacao_3municipios_MA.tif'
    with rasterio.Env(GDAL_CACHEMAX=64*1024*1024), rasterio.open(patch_path) as patch:
        descricoes = tuple(f'classification_{ano}' for ano in range(1985,2024) if ano != 2002)
        if patch.count != 38 or patch.descriptions != descricoes:
            raise ValueError('Bandas do complemento divergentes do checkpoint.')
        patch_hash = sha256(patch_path)
        for ano, nome in ((1985, 'municipios_coverage_1985-040.tif'), (2023, 'municipios_coverage_2023-002.tif')):
            origem = base / 'Mapas-Estudo' / nome
            print(f'{ano}: lendo somente para pré-visualização...', flush=True)
            with rasterio.open(origem) as src:
                if src.count != 1 or src.crs != patch.crs or src.dtypes[0] != 'uint8':
                    raise ValueError('Raster anual com estrutura inesperada.')
                a, b = src.transform, patch.transform
                if not np.allclose([a.a,a.e,a.b,a.d],[b.a,b.e,0,0],rtol=0,atol=1e-12):
                    raise ValueError('Complemento não está na resolução e orientação da grade original.')
                desloc = [(b.c-a.c)/a.a, (b.f-a.f)/a.e]
                if any(abs(v-round(v))>0.001 for v in desloc):
                    raise ValueError('Complemento com deslocamento subpixel.')
                original = np.zeros(shape, dtype=np.uint8)
                complemento = np.zeros(shape, dtype=np.uint8)
                for fonte, destino in ((rasterio.band(src,1), original),
                                       (rasterio.band(patch,descricoes.index(f'classification_{ano}')+1), complemento)):
                    reproject(fonte, destino, dst_transform=transform, dst_crs='EPSG:4326',
                              resampling=Resampling.nearest, warp_mem_limit=64, num_threads=2)
                resultado, recuperados = aplicar_complemento(original, complemento, dentro_alvos)
                resultado[~dentro] = 0
                desconhecidos = set(np.unique(resultado)) - {0, *legenda.classe_cobertura.tolist()}
                if desconhecidos:
                    raise ValueError(f'Classes não previstas na paleta Col9: {desconhecidos}')
                destino = saida / f'colecao9_255_{ano}.png'
                Image.fromarray(paleta[resultado]).save(destino)
                print(f'{ano}: calculando hash de origem para proveniência...', flush=True)
                manifesto['mapas'][str(ano)] = {'arquivo': destino.name, 'sha256': sha256(destino),
                    'raster': origem.name, 'sha256_raster': sha256(origem),
                    'complemento': patch_path.name, 'sha256_complemento': patch_hash,
                    'pixels_recuperados_no_desenho': recuperados, 'largura': largura, 'altura': altura}
    (saida / 'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Mapas Col9 novos gerados; originais preservados.', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,default=PROJETO.parent)
    p.add_argument('--saida',type=Path,default=PROJETO/'mapas_col9')
    p.add_argument('--largura',type=int,default=1400)
    a = p.parse_args()
    if not 200 <= a.largura <= 3000:
        p.error('Largura deve ficar entre 200 e 3000 pixels.')
    gerar(a.base,a.saida,a.largura)
