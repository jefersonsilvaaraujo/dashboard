"""Fecha pacote independente de preparação; somente leitura de fontes anteriores."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile,ZIP_DEFLATED

PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha


def ler_log(p):
    b=p.read_bytes();return b.decode('utf-16') if b.startswith((b'\xff\xfe',b'\xfe\xff')) else b.decode('utf-8-sig')


def executar(raiz,docs,pacote):
    mf=raiz/'manifesto_final_preparacao.json'
    if mf.exists() or pacote.exists():raise FileExistsError('Preservar pacote/checkpoint já fechado.')
    auditoria=json.loads((raiz/'auditoria_v3/auditoria.json').read_text(encoding='utf-8'))
    if auditoria['divergencias_checkpoints'] or auditoria['informacao_direta_posterior_a_t_em_X']:
        raise ValueError('Auditoria não aprovada.')
    for nome,a in auditoria['checkpoints_anteriores'].items():
        f=PROJETO/nome
        if sha(f)!=a['sha256']:raise ValueError('Manifesto anterior alterado.')
        d=json.loads(f.read_text(encoding='utf-8'))
        for n,h in d['sha256'].items():
            if sha(PROJETO/n)!=h:raise ValueError('Checkpoint anterior alterado.')
    for nome,h in auditoria['legado'].items():
        if sha(PROJETO/nome)!=h:raise ValueError('Legado alterado.')
    for nome in ['contrato_preparacao.json','diagnosticos/manifesto_diagnostico.json',
                 'complementares/manifesto_blocos_integridade_v2.json']:
        mm=json.loads((raiz/nome).read_text(encoding='utf-8'));p=raiz/Path(nome).parent
        for n,h in mm['artefatos_sha256'].items():
            if sha(p/n)!=h:raise ValueError(f'Artefato candidato modificado:{n}')
    for d in docs.glob('*.md'):
        t=d.read_text(encoding='utf-8')
        if t.count(chr(96)*3)%2:raise ValueError('Bloco Markdown não fechado.')
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',t):
            if not link.startswith(('http:','https:')) and not (docs/link).exists():raise ValueError('Link local ausente.')
    reg=PROJETO/'docs/evidencias/preparacao_regressao_regressao_principal_20261112.txt'
    geo=PROJETO/'docs/evidencias/preparacao_regressao_regressao_geo_20261112.txt'
    if '70 passed, 6 skipped' not in ler_log(reg) or '55 passed' not in ler_log(geo):raise ValueError('Testes finais não confirmados.')
    pastas={'matriz','metadados','diagnosticos','complementares','auditoria_v3','fontes'}
    arquivos={p.resolve() for p in raiz.rglob('*') if p.is_file() and
              (p.relative_to(raiz).parts[0] in pastas or p.name=='contrato_preparacao.json')}
    scripts=['preparar_regressao_continua_col9','diagnosticar_resposta_continua_col9',
        'blocos_complementares_regressao_col9','auditar_preparacao_regressao_col9',
        'relatorios_preparacao_regressao_col9','fechar_preparacao_regressao_col9']
    arquivos.update((PROJETO/'modelagem'/f'{n}.py').resolve() for n in scripts)
    arquivos.update(p.resolve() for p in docs.glob('*.md'))
    arquivos.add((PROJETO/'testes/test_preparacao_regressao_continua_col9_geo.py').resolve())
    for n in ['processamento/cenarios_validacao_col9.py','processamento/relatorios_oficiais_col9.py',
              'modelagem/contrato_matriz_col9.py','referencias/manifesto_rasters_transicoes_col9.json',
              'referencias/territorio_col9_hashes.json','referencias/legenda_col9.csv','referencias/metodologia_col9.json']:
        arquivos.add((PROJETO/n).resolve())
    arquivos.update(p.resolve() for p in (PROJETO/'docs/evidencias').glob('preparacao_regressao_*_20261112.txt') if 'fechamento' not in p.name)
    for p in arquivos:
        if not p.is_relative_to(PROJETO) or p.name=='.env':raise ValueError('Arquivo fora do escopo.')
        if p.suffix=='.py':compile(p.read_text(encoding='utf-8'),str(p),'exec')
    manifesto={'criado_UTC':datetime.now(timezone.utc).isoformat(),'tipo':'Preparação científica, sem aprendizado supervisionado',
        'status':'R principal é proposta para orientador; C secundário candidato; objetivos não homologados',
        'treinamento_otimizacao_desempenho_teste':False,'2024_utilizado':False,'dados_originais_modificados':False,
        'dimensoes':{'municipios':255,'intervalos':38,'linhas_X':9690,'atributos':53,'linhas2023_sem_resposta':255},
        'testes':{'principal_passaram':70,'geo_passaram':55,'novos':20,'total_distintos':125,
            'modulos_geo_ignorados_somente_no_ambiente_principal':6},
        'preservacao':auditoria,'ambiente':{p:importlib.metadata.version(p) for p in ['numpy','pandas','pyarrow','geopandas','shapely','pyproj']},
        'dependencia_adicionada':'pyarrow26.0.1 em pastaTEMP isolada; sem alterar ambientes existentes',
        'codigo_original_complementar_preservado':'metadados/codigo_executado_blocos_v1.py; correção atual afeta somente emissão de hash',
        'tentativas_nao_ativas_preservadas':['preparacao_regressao_20261112_v1','auditoria','auditoria_v2'],
        'nao_duplicados':['rasters completos','NPZs/fontes anteriores','banco','GeoPackage','biomas','ZIPs de focos','pacotes de dependências'],
        'sha256':{p.relative_to(PROJETO).as_posix():sha(p) for p in sorted(arquivos)}}
    with mf.open('x',encoding='utf-8') as f:json.dump(manifesto,f,ensure_ascii=False,indent=2)
    arquivos.add(mf.resolve());pacote.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(pacote,'x',ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(arquivos):z.write(p,p.relative_to(PROJETO).as_posix())
    with ZipFile(pacote) as z:
        if z.testzip() is not None:raise ValueError('CRC inválido.')
        for n,h in manifesto['sha256'].items():
            if hashlib.sha256(z.read(n)).hexdigest()!=h:raise ValueError('Hash interno inválido.')
    r={'pacote':str(pacote),'sha256':sha(pacote),'bytes':pacote.stat().st_size,'arquivos':len(arquivos),
       'manifesto_sha256':sha(mf),'CRC_e_hashes_internos_conferidos':True,'sem_treinamento':True,'sem_homologacao':True}
    with (raiz/'recibo_final_preparacao.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
    print(json.dumps(r,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--docs',type=Path,required=True);p.add_argument('--pacote',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint,a.docs,a.pacote)
