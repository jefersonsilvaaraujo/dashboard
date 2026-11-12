"""Checkpoint de gestão do piloto. Inclui vínculo restrito: não enviar aos avaliadores."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile,ZIP_DEFLATED

import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha,conferir_acervo
from processamento.pacote_avaliadores_col9 import verificar_ficha_cega


def executar(piloto,checkpoint_anterior,resultados,zip_saida):
    pronto=piloto/'manifesto_gestao.json'
    if pronto.exists() or zip_saida.exists() or zip_saida.with_suffix('.sha256').exists():
        raise FileExistsError('Checkpoint anterior preservado; escolher nova saída.')
    antigo=json.loads((checkpoint_anterior/'manifesto_checkpoint.json').read_text(encoding='utf-8'))
    for nome,h in antigo['sha256'].items():
        if sha(PROJETO/nome)!=h: raise ValueError('Arquivo de checkpoint anterior alterado: '+nome)
    conferir_acervo(resultados)
    m=json.loads((PROJETO/'referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    base=Path(m['base_dados'])
    for _,r in m['rasters'].items():
        s=(base/r['arquivo']).stat()
        if (s.st_size,s.st_mtime_ns)!=(r['bytes'],r['mtime_ns']): raise ValueError('Raster alterado.')
    for chave in ('territorio','consolidado','complemento'):
        if sha(base/m[chave]['arquivo'])!=m[chave]['sha256']: raise ValueError('Fonte alterada.')
    for nome,h in {'app.py':'a71cf9d8ccf45aa52c08cc734093208952b736d49fdbea9842d0d3cdfc1fbc87',
        'dados.py':'e7fe3009b1a4b5978499bfe891272c3455e11b0e215f91070f2a9a06d9ba8fba'}.items():
        if sha(PROJETO/nome)!=h: raise ValueError('Legado alterado.')
    recibos=json.loads((piloto/'pacotes_v2/recibo_entrega.json').read_text(encoding='utf-8'))
    casos=set(pd.read_csv(piloto/'gestao_restrita/vinculo_piloto_amostra_original.csv',sep=';').caso)
    for recibo in recibos:
        p=piloto/'pacotes_v2'/recibo['zip']
        if sha(p)!=recibo['sha256']: raise ValueError('Pacote divergente.')
        with ZipFile(p) as z:
            if z.testzip() is not None: raise ValueError('CRC do pacote inválido.')
            ficha=pd.read_csv(io.BytesIO(z.read('ficha_independente.csv')),sep=';',keep_default_na=False)
            verificar_ficha_cega(ficha)
            if set(ficha.caso)!=casos or not ficha.avaliador.eq(recibo['avaliador']).all(): raise ValueError('Avaliador/casos divergentes.')
            if not ficha.estado_t.eq('').all() or not ficha.estado_t1.eq('').all(): raise ValueError('Respostas preenchidas indevidamente.')
            for n in z.namelist():
                if 'gestao_restrita' in n: raise ValueError('Gestão exposta.')
                if n.endswith(('.csv','.json','.html','.md')):
                    texto=z.read(n).decode('utf-8-sig')
                    if re.search(r'p_\d{7}_\d{4}_\d+_\d+',texto): raise ValueError('ID original exposto.')
                    if re.search(r'"(?:classe_t|classe_t1|estrato_psu|estrato_pixel|peso_expansao_ha)"',texto):
                        raise ValueError('Atributo do mapa/desenho exposto.')
            pm=json.loads(z.read('manifesto.json'))
            for nome,h in pm['sha256'].items():
                if hashlib.sha256(z.read(nome)).hexdigest()!=h: raise ValueError('Hash interno divergente.')
    arquivos=set()
    for pasta in ('gestao_restrita','referencias_cegas','modelagem_retrospectiva'):
        arquivos.update(p.resolve() for p in (piloto/pasta).rglob('*') if p.is_file())
    arquivos.update(p.resolve() for p in (piloto/'pacotes_v2').iterdir() if p.is_file())
    novos=['processamento/piloto_interpretacao_col9.py','processamento/referencias_piloto_col9.py',
        'processamento/pacote_avaliadores_col9.py','processamento/auditar_piloto_col9.py','processamento/fechar_piloto_col9.py',
        'modelagem/protocolo_retrospectivo_col9.py','testes/test_piloto_retrospectivo_col9.py',
        'testes/test_referencias_piloto_col9_geo.py','docs/PROTOCOLO_PILOTO_TEMATICO_COL9.md',
        'docs/INSTRUCOES_AVALIADORES_PILOTO_COL9.md','docs/NOTA_CONVERSAO_RELEVANTE_COL9.md',
        'docs/PROTOCOLO_MODELAGEM_RETROSPECTIVA_COL9.md','docs/PENDENCIAS_DECISOES_PILOTO_COL9.md',
        'referencias/decisoes_pesquisador_col9_piloto_v1.json']
    for nome in novos:
        p=PROJETO/nome
        if p.suffix=='.py': compile(p.read_text(encoding='utf-8'),str(p),'exec')
        arquivos.add(p.resolve())
    for nome in ('processamento/cenarios_validacao_col9.py','processamento/referencias_tematica_col9.py',
                 'modelagem/contrato_matriz_col9.py','referencias/manifesto_rasters_transicoes_col9.json'):
        arquivos.add((PROJETO/nome).resolve())
    arquivos.update(p.resolve() for p in (PROJETO/'docs/evidencias').glob('piloto_*_20261111_v1.txt')
                    if 'fechamento' not in p.name)
    manifesto={'criado_em_utc':datetime.now(timezone.utc).isoformat(),
        'destino':'GESTÃO DO PESQUISADOR; contém vínculo/estratos/classes. Não enviar este ZIP aos avaliadores.',
        'status':'piloto proposto, sem respostas; nenhuma acurácia, alvo ou treino definitivo',
        'preservacao_checkpoint_anterior':True,'preservacao_rasters_39_tamanho_mtime':True,
        'preservacao_fontes_hashes':True,'legado_hashes_preservados':True,
        'sem_operacao_docker_banco_deploy':True,
        'checkpoint_anterior_sha256':sha(checkpoint_anterior/'manifesto_checkpoint.json'),
        'ambiente':{n:importlib.metadata.version(n) for n in ('numpy','pandas','rasterio','geopandas','shapely','pyproj','Pillow')},
        'pacotes_cegos':recibos,'2024_reservado_nao_usado':True,
        'sha256':{p.relative_to(PROJETO).as_posix():sha(p) for p in sorted(arquivos)}}
    with pronto.open('x',encoding='utf-8') as f: json.dump(manifesto,f,ensure_ascii=False,indent=2)
    arquivos.add(pronto.resolve()); zip_saida.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(zip_saida,'x',ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(arquivos): z.write(p,p.relative_to(PROJETO).as_posix())
    with ZipFile(zip_saida) as z:
        if z.testzip() is not None: raise ValueError('CRC do checkpoint inválido.')
        for nome,h in manifesto['sha256'].items():
            if hashlib.sha256(z.read(nome)).hexdigest()!=h: raise ValueError('Hash do checkpoint inválido.')
    h=sha(zip_saida)
    with zip_saida.with_suffix('.sha256').open('x',encoding='utf-8') as f: f.write(f'{h}  {zip_saida.name}\n')
    print(json.dumps({'zip_gestao':str(zip_saida),'arquivos':len(arquivos),'bytes':zip_saida.stat().st_size,
                     'sha256':h,'crc_hashes_cegamento_preservacao_verificados':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('piloto','checkpoint-anterior','resultados','zip-saida'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); executar(a.piloto,a.checkpoint_anterior,a.resultados,a.zip_saida)
