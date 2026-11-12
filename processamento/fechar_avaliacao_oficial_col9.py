"""Fecha checkpoint aditivo, verifica fontes e pacote, sem banco/Docker/alvo."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
from zipfile import ZipFile,ZIP_DEFLATED

import pandas as pd
import rasterio

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha,conferir_acervo

SCRIPTS=[
    'fontes_oficiais_col9','avaliar_pontos_oficiais_col9','diagnosticos_pontos_oficiais_col9',
    'auditoria_complementar_oficial_col9','auditoria_espectral_col9','sensibilidade_radiometrica_col9',
    'cenarios_evidencias_oficiais_col9','relatorios_oficiais_col9','fechar_avaliacao_oficial_col9']
DOCS=['RELATORIO_PONTOS_OFICIAIS_COL9','RELATORIO_CONSISTENCIA_REFERENCIAS_COL9',
      'AVALIACAO_INFERENCIA_PONTOS_COL9','RECOMENDACAO_DESFECHO_CENARIOS_COL9',
      'TEXTO_METODOLOGIA_LIMITACOES_COL9','CHECKPOINT_AVALIACAO_OFICIAL_COL9']


def ler_log(path):
    b=path.read_bytes()
    return b.decode('utf-16') if b.startswith((b'\xff\xfe',b'\xfe\xff')) else b.decode('utf-8-sig')


def executar(raiz,pacote):
    if (raiz/'manifesto_final.json').exists() or pacote.exists():
        raise FileExistsError('Checkpoint/pacote existente preservado.')
    antigos={};caminhos=set()
    for nome in ['validacao_cientifica_col9/checkpoint_20261111/manifesto_checkpoint.json',
                 'validacao_cientifica_col9/piloto_interpretacao_20261111_v1/manifesto_gestao.json']:
        f=PROJETO/nome;d=json.loads(f.read_text(encoding='utf-8'))
        for a,h in d['sha256'].items():
            if sha(PROJETO/a)!=h:raise ValueError(f'Checkpoint anterior alterado: {a}')
            caminhos.add(a)
        antigos[nome]={'sha256':sha(f),'arquivos_verificados':len(d['sha256'])}
    base_m=PROJETO/'resultados_transicoes_col9/integral_255_1985_2023_20261111'
    q=conferir_acervo(base_m)
    if len(q)!=9690:raise ValueError('Contrato de matrizes violado.')
    mpath=PROJETO/'referencias/manifesto_rasters_transicoes_col9.json'
    m=json.loads(mpath.read_text(encoding='utf-8'));base=Path(m['base_dados'])
    raster_stats={}
    for ano,r in m['rasters'].items():
        st=(base/r['arquivo']).stat()
        if st.st_size!=r['bytes'] or st.st_mtime_ns!=r['mtime_ns']:raise ValueError('Raster alterado.')
        raster_stats[ano]={'tamanho_mtime_conferem':True,'sha256_preexistente':r['sha256']}
    fontes={}
    for k in ['territorio','consolidado','complemento']:
        r=m[k];f=base/r['arquivo']
        if sha(f)!=r['sha256']:raise ValueError(f'Fonte aprovada alterada: {k}')
        fontes[k]={'arquivo':str(f),'sha256':r['sha256']}
    legado={}
    for n,h in {'app.py':'a71cf9d8ccf45aa52c08cc734093208952b736d49fdbea9842d0d3cdfc1fbc87',
                'dados.py':'e7fe3009b1a4b5978499bfe891272c3455e11b0e215f91070f2a9a06d9ba8fba'}.items():
        if sha(PROJETO/n)!=h:raise ValueError('Legado alterado.')
        legado[n]=h
    a=raiz/'avaliacao';r=json.loads((a/'resumo_execucao.json').read_text(encoding='utf-8'))
    if r['pontos_recorte']!=8586 or r['n_ref2023_recorte']!=1 or r['treinamento_recorte']!=1305:
        raise ValueError('Resultados oficiais inesperados.')
    for pasta,arquivo,chave in [
        ('complementar','manifesto_auditoria.json','arquivos'),
        ('diagnosticos','manifesto_diagnosticos.json','arquivos'),
        ('espectral_v2','manifesto_espectral.json','arquivos'),
        ('radiometria','manifesto_radiometria.json','arquivos'),
        ('cenarios_evidencias','manifesto_cenarios_evidencias.json','arquivos')]:
        mm=json.loads((raiz/pasta/arquivo).read_text(encoding='utf-8'))
        for n,h in mm[chave].items():
            if sha(raiz/pasta/n)!=h:raise ValueError('Auditoria derivada divergiu do manifesto.')
    download=json.loads((raiz/'fontes/manifesto_download.json').read_text(encoding='utf-8'))
    for f in download['fontes']:
        if sha(raiz/'fontes'/f['arquivo'])!=f['sha256']:raise ValueError('Download oficial alterado.')
        if 'csv_extraido' in f and sha(raiz/'fontes'/f['csv_extraido'])!=f['csv_sha256']:
            raise ValueError('CSV oficial extraído alterado.')
    reg=PROJETO/'docs/evidencias/oficial_col9_regressao_20261112.txt'
    geo=PROJETO/'docs/evidencias/oficial_col9_testes_geo_finais_20261112.txt'
    if '70 passed, 5 skipped' not in ler_log(reg):
        raise ValueError('Regressão não confirmada.')
    if '35 passed' not in ler_log(geo):
        raise ValueError('Testes geo não confirmados.')
    arquivos={p.resolve() for p in raiz.rglob('*') if p.is_file() and 'espectral' not in p.relative_to(raiz).parts[:1]}
    arquivos.update((PROJETO/'processamento'/f'{n}.py').resolve() for n in SCRIPTS)
    arquivos.update((PROJETO/'docs'/f'{n}.md').resolve() for n in DOCS)
    arquivos.add((PROJETO/'testes/test_pontos_oficiais_col9_geo.py').resolve())
    arquivos.update(p.resolve() for p in (PROJETO/'docs/evidencias').glob('oficial_col9_*_20261112.txt') if 'fechamento' not in p.name)
    for nome in ['processamento/cenarios_validacao_col9.py','processamento/manifesto_transicoes_col9.py',
                 'processamento/referencias_tematica_col9.py','referencias/manifesto_rasters_transicoes_col9.json',
                 'referencias/legenda_col9.csv','referencias/metodologia_col9.json','referencias/territorio_col9_hashes.json',
                 'referencias/encaminhamento_avaliacao_oficial_col9_v1.json']:
        arquivos.add((PROJETO/nome).resolve())
    for f in arquivos:
        if f.suffix=='.py':compile(f.read_text(encoding='utf-8'),str(f),'exec')
        if f.name=='.env':raise ValueError('Arquivo de credenciais proibido no pacote.')
    manifesto={'criado_UTC':datetime.now(timezone.utc).isoformat(),
        'status':'Comparação e auditoria concluídas; validação representativa e desfecho não homologados.',
        'periodo':[1985,2023],'2024_nao_utilizado':True,'sem_treinamento_modelos':True,
        'sem_nova_interpretacao_humana':True,'sem_Docker_banco_deploy':True,
        'checkpoints_anteriores':antigos,'n_caminhos_anteriores_distintos_verificados':len(caminhos),
        'fontes_aprovadas_preservadas':fontes,'rasters_39':raster_stats,'legado':legado,
        'concluido_matrizes_sha256':sha(base_m/'concluido.json'),
        'teste_principal':{'passaram':70,'modulos_geo_ignorados_neste_ambiente':5,'log_sha256':sha(reg)},
        'teste_geoespacial':{'passaram':35,'log_sha256':sha(geo)},'total_testes_distintos':105,
        'ambiente':{'python':platform.python_version(),'GDAL':rasterio.__gdal_version__,
            **{n:importlib.metadata.version(n) for n in ['numpy','pandas','rasterio','geopandas','shapely','pyproj']}},
        'nao_duplicados_no_pacote':['rasters completos','GeoPackage canônico','matrizes anteriores','banco PostgreSQL','checkpoint anterior completo'],
        'tentativa_nao_ativa_preservada':{'caminho':str(raiz/'espectral'),
            'motivo':'Primeira tentativa encontrou cenas duplicadas em catálogos. Não é fonte de resultados finais; logs preservados.'},
        'sha256':{str(f.relative_to(PROJETO)).replace('\\','/'):sha(f) for f in sorted(arquivos)}}
    mf=raiz/'manifesto_final.json'
    with mf.open('x',encoding='utf-8') as f:json.dump(manifesto,f,ensure_ascii=False,indent=2)
    arquivos.add(mf.resolve());pacote.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(pacote,'x',ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(arquivos):z.write(f,str(f.relative_to(PROJETO)).replace('\\','/'))
    with ZipFile(pacote) as z:
        if z.testzip() is not None:raise ValueError('CRC inválido.')
        for nome,h in manifesto['sha256'].items():
            if hashlib.sha256(z.read(nome)).hexdigest()!=h:raise ValueError('Hash interno inválido.')
    recibo={'pacote':str(pacote),'bytes':pacote.stat().st_size,'sha256':sha(pacote),
        'manifesto_final_sha256':sha(mf),'n_arquivos_zip':len(arquivos),'CRC_e_hashes_internos_verificados':True,
        'n_checkpoints_anteriores':len(antigos),'n_arquivos_anteriores_distintos':len(caminhos),'divergencias':0,
        'sem_Y_homologado':True,'sem_treinamento':True}
    with (raiz/'recibo_pacote.json').open('x',encoding='utf-8') as f:json.dump(recibo,f,indent=2,ensure_ascii=False)
    print(json.dumps(recibo,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--pacote',type=Path,required=True);a=p.parse_args();executar(a.checkpoint,a.pacote)
