"""Confere igualdade exata WKB NDR entre banco e GeoPackage do checkpoint.

Recebe exportação somente leitura de CD_MUN/hash_geometria. Não conecta no banco.
"""
import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import MultiPolygon

PROJETO = Path(__file__).resolve().parents[1]


def verificar(gpkg, hashes_banco, saida):
    fonte = json.loads((PROJETO/'referencias/fontes_col9.json').read_text(encoding='utf-8'))['territorio']
    if hashlib.sha256(gpkg.read_bytes()).hexdigest() != fonte['sha256']:
        raise ValueError('Hash do GeoPackage não coincide com o checkpoint.')
    g = gpd.read_file(gpkg)
    if len(g)!=255 or g.CD_MUN.nunique()!=255 or g.crs.to_epsg()!=4674:
        raise ValueError('Cadastro diferente dos 255 em EPSG:4674.')
    geometrias = {}
    for r in g.itertuples():
        geom = MultiPolygon([r.geometry]) if r.geometry.geom_type=='Polygon' else r.geometry
        geometrias[str(int(r.CD_MUN))] = hashlib.sha256(geom.wkb).hexdigest()
    banco = {str(int(r['CD_MUN'])):r['hash_geometria'] for r in json.loads(hashes_banco.read_text(encoding='utf-8'))}
    if banco != geometrias:
        raise ValueError('Banco e GeoPackage não têm geometrias idênticas; não homologar mapas.')
    contrato = {'territorio':fonte, 'crs':'EPSG:4674', 'municipios':255,
                'metodo':'SHA-256 de WKB NDR da geometria original MultiPolygon, sem SRID embutido',
                'geometrias_sha256_wkb_ndr':geometrias}
    if saida.exists():
        if json.loads(saida.read_text(encoding='utf-8')) != contrato:
            raise ValueError('Contrato existente diverge; preservado para investigação.')
    else:
        with saida.open('x',encoding='utf-8') as f:
            json.dump(contrato,f,ensure_ascii=False,indent=2)
    print('255/255 geometrias idênticas entre banco e GeoPackage. Contrato preservado/versionado.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gpkg',type=Path,required=True)
    p.add_argument('--hashes-banco',type=Path,required=True)
    p.add_argument('--saida',type=Path,default=PROJETO/'referencias/territorio_col9_hashes.json')
    a=p.parse_args()
    verificar(a.gpkg,a.hashes_banco,a.saida)
