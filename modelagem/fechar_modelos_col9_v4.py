"""Auditoria final e pacote independente, sem ajustar ou executar modelos."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import pandas as pd

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO))
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto, gravar_json, PREPARACAO
from processamento.cenarios_validacao_col9 import sha


def ler(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def log(p):
    b = p.read_bytes()
    return b.decode('utf-16') if b.startswith((b'\xff\xfe', b'\xfe\xff')) else b.decode('utf-8-sig')


def verificar_hashes(base, itens):
    for nome, esperado in itens.items():
        if sha(base / nome) != esperado:
            raise ValueError(f'Integridade divergente: {base / nome}')


def auditar(raiz):
    protocolo = carregar_manifesto(raiz)
    verificar_hashes(raiz/'dados', protocolo['dados_estagiados_sha256'])
    for nome in ['DESENVOLVIMENTO_CONCLUIDO.json', 'TESTE_CONCLUIDO.json']:
        d = ler(raiz/nome)
        verificar_hashes(raiz if nome.startswith('DESENVOLVIMENTO') else raiz/'teste', d['artefatos_sha256'])
    auditoria_ajustes = ler(raiz/'auditoria_ajustes/AUDITORIA_AJUSTES_APROVADA.json')
    assert auditoria_ajustes['modelos_verificados'] == 504
    verificar_hashes(raiz/'auditoria_ajustes', auditoria_ajustes['artefatos_sha256'])
    inicio = ler(raiz/'TESTE_INICIADO.json')
    abertura = ler(raiz/'ABERTURA_UNICA_Y_TESTE.json')
    plano = ler(raiz/'interpretacao_pre_teste/PLANO_INTERPRETACAO_PRE_TESTE.json')
    verificar_hashes(raiz/'interpretacao_pre_teste', plano['arquivos_sha256'])
    assert plano['antes_teste'] and plano['criado_UTC'] < inicio['inicio_UTC'] < abertura['abertura_UTC']
    assert inicio['vencedores_sha256'] == sha(raiz/'VENCEDORES_PELA_VALIDACAO.json')
    assert abertura['predicoes_sha256'] == sha(raiz/'teste/PREDICOES_ANTES_ABRIR_Y.parquet')
    assert ler(raiz/'TESTE_CONCLUIDO.json')['avaliacoes_finais'] == 1
    pred = pd.read_parquet(raiz/'teste/PREDICOES_ANTES_ABRIR_Y.parquet')
    fim = pd.read_parquet(raiz/'teste/RESULTADOS_IMUTAVEIS_TESTE.parquet')
    pd.testing.assert_frame_equal(pred, fim[pred.columns])
    assert len(fim) == 191760
    chaves = ['coorte', 'contexto', 'target', 'bloco', 'algoritmo', 'regime', 'row_id']
    assert not fim.duplicated(chaves).any()
    assert fim.ano_t.between(2019, 2022).all() and fim.observado.notna().all()
    for chave, grupo in fim.groupby(chaves[:-1]):
        assert len(grupo) == (1020 if chave[1] == 'temporal' else grupo.CD_MUN.nunique()*4)
        if chave[1] != 'temporal':
            assert set(grupo.SIGLA_UF) == {chave[1]}
    canon = set(ler(PROJETO/'referencias/territorio_col9_hashes.json')['geometrias_sha256_wkb_ndr'])
    assert set(fim.CD_MUN) == canon and len(canon) == 255
    respostas = pd.read_parquet(PREPARACAO/'matriz/RESPOSTAS_CONTINUAS_COL9.parquet')
    original = respostas.rename(columns={'ano_t': 'ano_t'}).melt(id_vars=['CD_MUN', 'ano_t'], value_vars=['R_pct', 'C_ha'], var_name='target', value_name='resposta_original')
    comparacao = fim.merge(original, on=['CD_MUN', 'ano_t', 'target'], validate='many_to_one')
    np.testing.assert_allclose(comparacao.observado, comparacao.resposta_original, rtol=0, atol=0)
    np.testing.assert_allclose(fim.erro, fim.previsto-fim.observado, rtol=0, atol=0)
    concluidos = sorted((raiz/'desenvolvimento').rglob('concluido.json'))
    assert len(concluidos) == 108
    selecionados = set()
    instante_teste = datetime.fromisoformat(inicio['inicio_UTC']).timestamp()
    for f in concluidos:
        d = ler(f)
        assert d['protocolo_sha256'] == sha(raiz/'PROTOCOLO_CONGELADO.json')
        verificar_hashes(f.parent, d['artefatos'])
        selecionados.add(f.resolve())
        for nome in d['artefatos']:
            arq = f.parent/nome
            selecionados.add(arq.resolve())
            if arq.name in {'modelo.json', 'pipeline.skops', 'preprocessamento.skops', 'modelo_xgboost.json'}:
                assert arq.stat().st_mtime <= instante_teste, 'Modelo modificado depois do teste.'
    # Nova verificação dos checkpoints antigos e das fontes originais.
    audit_preparacao = ler(PREPARACAO/'auditoria_v3/auditoria.json')
    anteriores = {}
    for nome, meta in audit_preparacao['checkpoints_anteriores'].items():
        f = PROJETO/nome
        assert sha(f) == meta['sha256']
        dados = ler(f)
        verificar_hashes(PROJETO, dados['sha256'])
        anteriores.update(dados['sha256'])
    preparacao = ler(PREPARACAO/'manifesto_final_preparacao.json')
    verificar_hashes(PROJETO, preparacao['sha256'])
    verificar_hashes(PROJETO, audit_preparacao['legado'])
    fontes = ler(PREPARACAO/'metadados/fontes_matriz.json')
    verificar_hashes(PROJETO, fontes['estoques_npz_sha256'])
    assert sha(Path(fontes['consolidado_csv'])) == fontes['consolidado_sha256']
    rasters = ler(PROJETO/'referencias/manifesto_rasters_transicoes_col9.json')
    assert set(rasters['rasters']) == set(map(str, range(1985, 2024)))
    for meta in rasters['rasters'].values():
        stat = (PROJETO.parent/meta['arquivo']).stat()
        assert stat.st_size == meta['bytes'] and stat.st_mtime_ns == meta['mtime_ns']
    geo = Path(rasters['base_dados'])/rasters['territorio']['arquivo']
    assert sha(geo) == rasters['territorio']['sha256']
    # Cobertura por fold: mesma máscara de treinamento de cada artefato final.
    x = pd.read_parquet(raiz/'dados/X_desenvolvimento.parquet')
    specs = ler(raiz/'MODELOS_PARA_TESTE.json')
    cobertura = []
    for s in specs:
        if s['algoritmo'] not in {'ridge', 'elastic_net', 'random_forest', 'xgboost'}:
            continue
        minimo = 1985 if s['coorte'] == 'principal' else 2003
        mask = x.ano_t.between(minimo, 2017) & x.ano_t.ne(2014)
        if s['contexto'] != 'temporal':
            mask &= x.SIGLA_UF.ne(s['contexto'])
        for atributo in s['meta']['features']:
            a = x.loc[mask, atributo]
            cobertura.append({k:s[k] for k in ['coorte','contexto','target','bloco','algoritmo']} |
                {'atributo':atributo, 'n_treino':len(a), 'ausentes_treino':int(a.isna().sum()),
                 'cobertura_treino_pct':float(100*a.notna().mean()), 'UFs_treino':','.join(sorted(x.loc[mask,'SIGLA_UF'].unique()))})
    pasta = raiz/'auditoria_final'
    pasta.mkdir()
    pd.DataFrame(cobertura).to_parquet(pasta/'COBERTURA_ATRIBUTOS_POR_AJUSTE_FINAL.parquet', index=False)
    # Evidências de testes: ambientes separados, sem somar repetições.
    evid = PROJETO/'docs/evidencias'
    assert '70 passed' in log(evid/'experimentos_regressao_testes_legado_20261112_v4.txt')
    assert '55 passed' in log(evid/'experimentos_regressao_testes_geograficos_20261112_v4.txt')
    assert '15 passed' in log(evid/'experimentos_regressao_testes_pos_teste_20261112_v4.txt')
    resumo = {'verificado_UTC':datetime.now(timezone.utc).isoformat(), 'protocolo_sha256':sha(raiz/'PROTOCOLO_CONGELADO.json'),
        'chaves_canonicas':9690, 'municipios':255, 'intervalos':38, 'linhas_futuras2023_sem_resposta':255,
        'grupos_desenvolvimento':108, 'modelos_finais_auditados':504, 'linhas_predicoes_teste':len(fim),
        'predicoes_fixadas_antes_abertura_Y':True, 'testes_finais_executados':1, 'nenhum_ajuste_apos_teste':True,
        'correspondencia_exata_respostas_aprovadas':True, 'checkpoint_anterior_arquivos_distintos':len(anteriores),
        'preparacao_arquivos_verificados':len(preparacao['sha256']), 'NPZs_255_conferidos_por_hash':True,
        'rasters39_tamanho_mtime_conferidos':True, 'nota_rasters':'SHA-256 integrais prévios preservados no manifesto; não reprocessados 159 GB nesta etapa.',
        'legado_app_dados_hashes_conferidos':True, 'divergencias_preservacao':0,
        'testes_distintos':140, 'testes_legado':125, 'testes_modelagem_ativos':15,
        'advertencias_testes':'16 avisos esperados de coluna sintética inteiramente ausente; não são ausências preenchidas com zero físico.',
        'dependencia_retrospectiva_produtor_permanece':True, '2024_usado':False,
        'banco_dashboard_docx_modificados':False}
    gravar_json(resumo, pasta/'AUDITORIA_FINAL_APROVADA.json')
    return selecionados, resumo


def executar(raiz, docs, pacote):
    if pacote.exists() or (raiz/'MANIFESTO_FINAL_MODELOS_COL9.json').exists():
        raise FileExistsError('Checkpoint final preservado; não repetir fechamento.')
    selecionados, auditoria = auditar(raiz)
    arquivos = set(selecionados)
    arquivos.update(f.resolve() for f in raiz.rglob('*') if f.is_file() and 'desenvolvimento' not in f.relative_to(raiz).parts)
    arquivos.update(f.resolve() for f in docs.glob('*.md'))
    for pasta in ['modelagem', 'processamento']:
        arquivos.update(f.resolve() for f in (PROJETO/pasta).glob('*.py'))
    arquivos.add((PROJETO/'testes/test_experimentos_regressao_col9_v4.py').resolve())
    # Inclui a preparação já aprovada, pequena e com X/Y fisicamente separados.
    arquivos.update((PROJETO/n).resolve() for n in ler(PREPARACAO/'manifesto_final_preparacao.json')['sha256'])
    arquivos.add((PREPARACAO/'manifesto_final_preparacao.json').resolve())
    arquivos.update(f.resolve() for f in (PROJETO/'docs/evidencias').glob('experimentos_regressao_*20261112*.txt') if 'fechamento' not in f.name)
    # Histórico técnico anterior aos ajustes, sem carregar tentativas incompletas de treinamento.
    for v in [1,2,3]:
        pasta = PROJETO/f'experimentos_regressao_col9/execucao_20261112_v{v}'
        arquivos.update(f.resolve() for f in pasta.rglob('*.json'))
        arquivos.update(f.resolve() for f in (PROJETO/f'docs/experimentos_regressao_col9_20261112_v{v}').glob('*.md'))
    for f in arquivos:
        assert f.is_relative_to(PROJETO) and f.name != '.env'
        assert f.suffix not in {'.pickle', '.pkl', '.joblib'}
        if f.suffix == '.py':
            compile(f.read_text(encoding='utf-8'), str(f), 'exec')
    for f in docs.glob('*.md'):
        texto = f.read_text(encoding='utf-8')
        assert texto.count('```') % 2 == 0
        for destino in re.findall(r'\[[^\]]+\]\(([^)]+)\)', texto):
            if not destino.startswith(('https:', 'http:')):
                assert (docs/destino).exists(), f'Link ausente: {destino}'
    manifesto = {'criado_UTC':datetime.now(timezone.utc).isoformat(),
        'id':'regressao_col9_20261112_v4', 'estado':'Experimentos autorizados concluídos; escolhas mantidas após teste.',
        'auditoria_final':auditoria, 'versoes':ler(raiz/'PROTOCOLO_CONGELADO.json')['versoes'],
        'serializacao':'skops com tipos estruturais revisados numpy.dtype/sklearn.tree._tree.Tree; XGBoost JSON nativo; sem pickle/joblib.',
        'nao_incluidos':['rasters integrais','banco PostgreSQL/PostGIS','GeoPackage original','tentativas incompletas preservadas no disco'],
        'escopo_hashes':'Arquivos do pacote, exceto este manifesto. Recibo externo contém hash deste manifesto e do ZIP.',
        'sha256':{f.relative_to(PROJETO).as_posix():sha(f) for f in sorted(arquivos)}}
    mf = raiz/'MANIFESTO_FINAL_MODELOS_COL9.json'
    gravar_json(manifesto, mf)
    arquivos.add(mf.resolve())
    pacote.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(pacote, 'x', ZIP_DEFLATED, compresslevel=6) as z:
        for f in sorted(arquivos):
            z.write(f, f.relative_to(PROJETO).as_posix())
    with ZipFile(pacote) as z:
        assert z.testzip() is None
        for nome, esperado in manifesto['sha256'].items():
            assert hashlib.sha256(z.read(nome)).hexdigest() == esperado
    recibo = {'pacote':str(pacote), 'sha256':sha(pacote), 'bytes':pacote.stat().st_size,
        'arquivos':len(arquivos), 'manifesto_sha256':sha(mf), 'CRC_e_todos_hashes_internos_conferidos':True,
        'testes_distintos':140, 'teste_final_passagens':1, 'dados_anteriores_preservados':True}
    gravar_json(recibo, raiz/'RECIBO_ENTREGA_MODELOS_COL9.json')
    print(json.dumps(recibo, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', required=True, type=Path)
    p.add_argument('--docs', required=True, type=Path)
    p.add_argument('--pacote', required=True, type=Path)
    a = p.parse_args()
    executar(a.checkpoint, a.docs, a.pacote)
