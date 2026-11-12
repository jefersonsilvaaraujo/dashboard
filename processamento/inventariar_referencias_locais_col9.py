"""Inventaria cabeçalhos e índices ZIP, sem extrair nem alterar o acervo indicado."""
import argparse
from collections import Counter
import json
from pathlib import Path
import zipfile

import rasterio


def executar(base,saida):
    if saida.exists(): raise FileExistsError('Inventário anterior preservado.')
    registros=[]
    for p in sorted(base.rglob('*')):
        if not p.is_file(): continue
        d={'arquivo':str(p),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns}
        if p.name.startswith('._'):
            d['tipo']='metadado_AppleDouble_nao_e_imagem_ou_zip'
            registros.append(d)
            continue
        try:
            if p.suffix.lower()=='.zip':
                with zipfile.ZipFile(p) as z:
                    d['conteudo']=[{'nome':n.filename,'bytes':n.file_size,'CRC32':n.CRC} for n in z.infolist() if not n.is_dir()]
            elif p.suffix.lower() in ('.tif','.tiff','.jp2'):
                with rasterio.open(p) as s:
                    d.update({'bandas':s.count,'dtype':s.dtypes,'crs':str(s.crs),'dimensoes':[s.width,s.height],
                              'resolucao':s.res,'descricoes':s.descriptions})
        except (zipfile.BadZipFile,rasterio.errors.RasterioIOError,OSError) as e:
            d['erro_inventario']=type(e).__name__
        registros.append(d)
    entradas=[n['nome'] for d in registros for n in d.get('conteudo',[])]
    resumo={'n_arquivos':len(registros),'n_metadados_AppleDouble':sum('tipo' in d for d in registros),
        'n_zips':sum(Path(d['arquivo']).suffix.lower()=='.zip' and 'tipo' not in d for d in registros),
        'n_erros':sum('erro_inventario' in d for d in registros),'n_entradas_zip':len(entradas),
        'extensoes_zip':dict(Counter(Path(n).suffix.lower() for n in entradas)),
        'tipos_raster':dict(Counter(str((d['bandas'],d['dtype'])) for d in registros if 'bandas' in d))}
    with saida.open('x',encoding='utf-8') as f:
        json.dump({'raiz':str(base),'somente_leitura':True,'resumo':resumo,'arquivos':registros},f,ensure_ascii=False,indent=2)
    print(json.dumps(resumo,ensure_ascii=False,indent=2))
    print('Conteúdo ZIP fora de coverage:',[n for n in entradas if 'coverage' not in n.lower()][:40])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--base',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.base,a.saida)
