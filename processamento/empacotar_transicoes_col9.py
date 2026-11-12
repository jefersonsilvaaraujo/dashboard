"""Checkpoint portátil com hashes: código, referências e resultados, sem rasters/banco."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

PROJETO=Path(__file__).resolve().parents[1]


def empacotar(resultados,saida):
    resultados=resultados.resolve()
    if not (resultados/'concluido.json').is_file():
        raise ValueError('Execução científica ainda não concluída.')
    if saida.exists() or saida.with_suffix('.sha256').exists():
        raise FileExistsError('Checkpoint anterior preservado; escolher novo nome.')
    final=json.loads((resultados/'concluido.json').read_text(encoding='utf-8'))
    for nome,h in final['artefatos'].items():
        if hashlib.sha256((resultados/nome).read_bytes()).hexdigest()!=h:
            raise ValueError(f'Artefato consolidado divergente: {nome}')
    checkpoints=list((resultados/'municipios').glob('*/concluido.json'))
    if len(checkpoints)!=final['municipios']:
        raise ValueError('Quantidade de checkpoints municipais divergente.')
    arquivos=set()
    for p in resultados.rglob('*'):
        if p.is_file() and 'municipios' not in p.relative_to(resultados).parts:
            arquivos.add(p)
    for ck in checkpoints:
        info=json.loads(ck.read_text(encoding='utf-8')); arquivos.add(ck)
        for nome,h in info['artefatos'].items():
            p=ck.parent/nome
            if hashlib.sha256(p.read_bytes()).hexdigest()!=h:
                raise ValueError(f'Checkpoint municipal divergente: {p}')
            arquivos.add(p)
    # Lista restrita: não inclui .env, credenciais, banco nem dados brutos.
    for padrao in (
        'processamento/*transicoes_col9.py','processamento/exportar_matriz_col9.py',
        'testes/test_transicoes_col9_geo.py','testes/test_exportar_matriz_col9.py',
        'referencias/*','docs/PROTOCOLO_TRANSICOES_COL9.md',
        'docs/RELATORIO_EXPLORATORIO_TRANSICOES_COL9.md',
        'docs/RELATORIO_IMPLANTACAO_COL9_20261111.md',
        'docs/RELATORIO_ETAPA_TRANSICOES_COL9.md',
        'docs/evidencias/transicoes_*20261111*',
    ):
        arquivos.update(p for p in PROJETO.glob(padrao) if p.is_file())
    manifesto={'criado_em_utc':datetime.now(timezone.utc).isoformat(),
        'conteudo':'Código, referências e resultados novos; rasters originais e banco externos.',
        'sem_alvo_binario':True,'sha256':{}}
    saida.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(saida,'x',compression=ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(arquivos):
            nome=p.relative_to(PROJETO).as_posix()
            conteudo=p.read_bytes()
            manifesto['sha256'][nome]=hashlib.sha256(conteudo).hexdigest()
            z.writestr(nome,conteudo)
        z.writestr('MANIFESTO_CHECKPOINT.json',json.dumps(manifesto,ensure_ascii=False,indent=2))
    # Ler novamente o ZIP confirma integridade CRC e hashes do conteúdo empacotado.
    with ZipFile(saida) as z:
        if z.testzip() is not None: raise ValueError('CRC do ZIP divergente.')
        for nome,h in manifesto['sha256'].items():
            if hashlib.sha256(z.read(nome)).hexdigest()!=h:
                raise ValueError(f'Hash no ZIP divergente: {nome}')
    h=hashlib.sha256(saida.read_bytes()).hexdigest()
    with saida.with_suffix('.sha256').open('x',encoding='utf-8') as f:
        f.write(f'{h}  {saida.name}\n')
    print(json.dumps({'zip':str(saida),'arquivos':len(arquivos),'bytes':saida.stat().st_size,
                      'sha256':h,'crc_e_hashes_verificados':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resultados',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args(); empacotar(a.resultados,a.saida)
