"""Manifesto imutável dos 39 rasters aprovados; nenhuma escrita nas fontes."""
import argparse
import hashlib
import json
from pathlib import Path

import rasterio

PROJETO = Path(__file__).resolve().parents[1]
ANOS = tuple(range(1985, 2024))
NOMES = {a: f'municipios_coverage_{a}-{2025-a:03d}.tif' for a in ANOS}
NOMES.update({2002:'municipios_coverage_2002_COL9_validado.tif',
              2016:'municipios_coverage_2016-008.tif',2017:'municipios_coverage_2017-009.tif'})


def sha256(arquivo):
    h = hashlib.sha256()
    with Path(arquivo).open('rb') as f:
        for bloco in iter(lambda:f.read(16*1024*1024),b''):
            h.update(bloco)
    return h.hexdigest()


def grade(src):
    return {'crs':src.crs.to_string() if src.crs else None,
            'transform':list(src.transform)[:6], 'largura':src.width,'altura':src.height,
            'bandas':src.count,'dtype':src.dtypes[0],'nodata':src.nodata,
            'blocos':[list(b) for b in src.block_shapes]}


def conferir_grade(a,b):
    for campo in ('crs','transform','largura','altura','bandas','dtype'):
        if a[campo]!=b[campo]:
            raise ValueError(f'Grade divergente: {campo}')
    if a['crs']!='EPSG:4326' or a['bandas']!=1 or a['dtype']!='uint8':
        raise ValueError('Esperado raster anual uint8, EPSG:4326, banda única.')


def preparar(base,saida):
    if saida.exists():
        raise FileExistsError('Manifesto já existe; preservado. Use-o ou escolha outro destino.')
    fontes=json.loads((PROJETO/'referencias/fontes_col9.json').read_text(encoding='utf-8'))
    gpkg=base/'correcao_territorial_255/resultado_20261107_192346/municipios_255_ibge_2025.gpkg'
    consolidado=base/fontes['consolidado']['arquivo']
    if sha256(gpkg)!=fontes['territorio']['sha256'] or sha256(consolidado)!=fontes['consolidado']['sha256']:
        raise ValueError('Território ou consolidado divergem do checkpoint aprovado.')
    validacao=base/'validacao_final_2002_colecao9.json'
    v=json.loads(validacao.read_text(encoding='utf-8'))
    if not v['grade_compativel'] or v['resultados']['c9']['concordancia_pct']!=100:
        raise ValueError('Registro de validação amostral de 2002 inesperado.')
    manifesto={'versao':'transicoes_col9_v1','colecao':'9','periodo':[1985,2023],
        'base_dados':str(base.resolve()),'territorio':{'arquivo':str(gpkg.relative_to(base)), 'sha256':sha256(gpkg)},
        'consolidado':{'arquivo':consolidado.name,'sha256':sha256(consolidado)},
        'origem':'Acervo local Col9 aprovado pelo pesquisador; 2002 recomposto de tiles Col9 e validado por amostras GEE.',
        'limite_proveniencia':'A aprovação e as amostras históricas não equivalem à validação temática de todos os pixels dos 39 anos.',
        'validacao_2002':{'arquivo':validacao.name,'sha256':sha256(validacao),'resultado_c9':v['resultados']['c9']},
        'rasters':{}}
    referencia=None
    for ano in ANOS:
        caminho=base/'Mapas-Estudo'/NOMES[ano]
        with rasterio.open(caminho) as src:
            g=grade(src)
            if referencia is None: referencia=g
            conferir_grade(referencia,g)
        print(f'Manifesto {ano}: SHA-256 {caminho.name}',flush=True)
        st=caminho.stat()
        manifesto['rasters'][str(ano)]={'arquivo':str(caminho.relative_to(base)), 'sha256':sha256(caminho),
            'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'grade':g}
    alias=base/'Mapas-Estudo/municipios_coverage_2002-023.tif'
    if sha256(alias)!=manifesto['rasters']['2002']['sha256']:
        raise ValueError('Raster 2002 usado no consolidado não é idêntico ao validado.')
    manifesto['alias_2002']={'arquivo':str(alias.relative_to(base)),'sha256':sha256(alias),'identico_ao_validado':True}
    patch=base/'Mapas-Estudo/mapbiomas_col9_recuperacao_3municipios_MA.tif'
    with rasterio.open(patch) as p:
        descricoes=[f'classification_{a}' for a in ANOS if a!=2002]
        if list(p.descriptions)!=descricoes or p.count!=38 or p.dtypes!=('uint8',)*38:
            raise ValueError('Complemento MA diferente das 38 bandas aprovadas.')
        a=referencia['transform']; b=list(p.transform)[:6]
        if p.crs.to_string()!=referencia['crs'] or [a[0],a[1],a[3],a[4]]!=[b[0],b[1],b[3],b[4]]:
            raise ValueError('Complemento MA fora da resolução/orientação da grade.')
        desloc=[(b[2]-a[2])/a[0],(b[5]-a[5])/a[4]]
        if any(abs(x-round(x))>0.001 for x in desloc): raise ValueError('Complemento deslocado em subpixel.')
        manifesto['complemento']={'arquivo':str(patch.relative_to(base)),'sha256':sha256(patch),
            'bytes':patch.stat().st_size,'mtime_ns':patch.stat().st_mtime_ns,
            'grade':grade(p),'descricoes':descricoes,'offset_col_linha':[round(x) for x in desloc],
            'municipios':[2101772,2108504,2112274],
            'regra':'Preencher exclusivamente zeros nos três municípios; não modificar rasters; não aplicar a 2002.'}
    saida.parent.mkdir(parents=True,exist_ok=True)
    with saida.open('x',encoding='utf-8') as f: json.dump(manifesto,f,ensure_ascii=False,indent=2)
    print(f'Manifesto concluído: {saida}',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args(); preparar(a.base,a.saida)
