"""Fecha entrega A/B/C com hashes e ZIP novo. Não escreve no acervo consolidado."""
import argparse
from datetime import datetime,timezone
import importlib.metadata
import json
from pathlib import Path
import sys
from zipfile import ZipFile,ZIP_DEFLATED

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import sha,conferir_acervo

PROJETO=Path(__file__).resolve().parents[1]


def executar(base,resultados,zip_saida):
    registro=base/'manifesto_checkpoint.json'
    if registro.exists() or zip_saida.exists() or zip_saida.with_suffix('.sha256').exists():
        raise FileExistsError('Checkpoint existente preservado; escolher novos nomes.')
    conferir_acervo(resultados)
    m=json.loads((PROJETO/'referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    dados=Path(m['base_dados'])
    for chave in ('territorio','consolidado','complemento'):
        if sha(dados/m[chave]['arquivo'])!=m[chave]['sha256']: raise ValueError('Fonte externa alterada.')
    for _,r in m['rasters'].items():
        s=(dados/r['arquivo']).stat()
        if (s.st_size,s.st_mtime_ns)!=(r['bytes'],r['mtime_ns']): raise ValueError('Raster original alterado.')
    arquivos={p.resolve() for p in base.rglob('*') if p.is_file()}
    scripts=['cenarios_validacao_col9','amostra_tematica_col9','inventariar_referencias_locais_col9',
        'referencias_tematica_col9','referencias_fim_ano_col9','pranchas_pixel_validacao_col9',
        'diagnostico_picos_col9','respostas_tematica_col9','relatorios_validacao_cientifica_col9',
        'fechar_checkpoint_validacao_col9']
    arquivos.update((PROJETO/'processamento'/f'{n}.py').resolve() for n in scripts)
    for p in ['modelagem/contrato_matriz_col9.py','testes/test_validacao_cientifica_col9.py',
        'testes/test_amostragem_tematica_col9_geo.py','docs/RELATORIO_VALIDACAO_TEMATICA_COL9.md',
        'docs/RELATORIO_COMPARACAO_LIMIARES_COL9.md','docs/ESPECIFICACAO_MATRIZ_TREINAMENTO_COL9.md',
        'docs/ENTREGA_VALIDACAO_CIENTIFICA_COL9.md','docs/PROTOCOLO_TRANSICOES_COL9.md']:
        arquivos.add((PROJETO/p).resolve())
    arquivos.update(p.resolve() for p in (PROJETO/'referencias').glob('*') if p.is_file())
    arquivos.update(p.resolve() for p in (PROJETO/'docs/evidencias').glob('validacao_*')
                    if p.is_file() and 'fechamento' not in p.name)
    manifesto={'criado_em_utc':datetime.now(timezone.utc).isoformat(),
        'status':'A: referência probabilística pendente; B/C executados sem homologação do alvo.',
        'consolidado_anterior_sha256':sha(resultados/'concluido.json'),
        'sem_treinamento':True,'sem_rotulo_homologado':True,'ambiente':{n:importlib.metadata.version(n)
            for n in ['numpy','pandas','rasterio','geopandas','shapely','pyproj','Pillow']},
        'nao_incluidos':'Rasters e matrizes consolidadas anteriores externos, PostgreSQL, credenciais, contêineres.',
        'codigo_fechamento_sha256':sha(Path(__file__)),
        'sha256':{p.relative_to(PROJETO).as_posix():sha(p) for p in sorted(arquivos)}}
    with registro.open('x',encoding='utf-8') as f: json.dump(manifesto,f,ensure_ascii=False,indent=2)
    arquivos.add(registro.resolve()); zip_saida.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(zip_saida,'x',ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(arquivos): z.write(p,p.relative_to(PROJETO).as_posix())
    with ZipFile(zip_saida) as z:
        if z.testzip() is not None: raise ValueError('ZIP falhou na verificação CRC.')
        import hashlib
        for nome,h in manifesto['sha256'].items():
            if hashlib.sha256(z.read(nome)).hexdigest()!=h: raise ValueError('Conteúdo empacotado divergente.')
    digest=sha(zip_saida)
    with zip_saida.with_suffix('.sha256').open('x',encoding='utf-8') as f: f.write(f'{digest}  {zip_saida.name}\n')
    print(json.dumps({'zip':str(zip_saida),'bytes':zip_saida.stat().st_size,'arquivos':len(arquivos),
        'sha256':digest,'crc_e_hashes_verificados':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('base','resultados','zip-saida'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); executar(a.base,a.resultados,a.zip_saida)
