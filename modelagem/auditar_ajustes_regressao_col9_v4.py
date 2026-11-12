"""Conferência independente dos ajustes finais antes de abrir o teste reservado."""
import argparse,json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto,gravar_json
from modelagem.executar_regressao_col9_v4 import carregar_dev,ler_modelo
from processamento.cenarios_validacao_col9 import sha

def executar(raiz):
    p=carregar_manifesto(raiz)
    if (raiz/'TESTE_INICIADO.json').exists():raise ValueError('Auditoria precisa anteceder teste.')
    saida=raiz/'auditoria_ajustes'
    if saida.exists():raise FileExistsError('Auditoria anterior preservada.')
    saida.mkdir()
    _,d=carregar_dev(str(raiz.resolve()))
    specs=json.loads((raiz/'MODELOS_PARA_TESTE.json').read_text(encoding='utf-8'))
    registros=[]
    for s in specs:
        meta=s['meta'];uf=None if s['contexto']=='temporal' else s['contexto']
        mini=p['coortes'][s['coorte']]['ano_t_min']
        sel=d.ano_t.between(mini,2017)&d.ano_t.ne(2014)
        if uf:sel &= d.SIGLA_UF.ne(uf)
        if uf and d.loc[sel,'SIGLA_UF'].eq(uf).any():raise ValueError('UFretida indevidamente incluída.')
        y=d.loc[sel,s['target']].to_numpy(float)
        if not np.isfinite(y).all() or len(y)!=meta['n_treino_final']:raise ValueError('Partição de refit não confere.')
        pipe,mm=ler_modelo(PROJETO/s['modelo_dir'])
        if pipe is None:
            np.testing.assert_allclose([meta['media'],meta['mediana']],[y.mean(),np.median(y)],rtol=1e-12,atol=1e-10)
            entrada_efetiva=['mb_taxa_passada_pct' if s['target']=='R_pct' else 'mb_conv_passada_ha'] if s['algoritmo']=='persistencia' else []
            err=0.
        else:
            if meta['features']!=p['blocos'][s['bloco']]:raise ValueError('Lista de atributos modificada.')
            yt=np.log1p(y) if meta['transformacao']=='log1p' else y
            escala=float(yt.std(ddof=0)) or 1.
            np.testing.assert_allclose([meta['centro'],meta['escala']],[yt.mean(),escala],rtol=1e-12,atol=1e-10)
            x=d.loc[sel,meta['features']].astype(float)
            esperado=x.median().to_numpy()
            estimado=pipe.named_steps['pre'].transformer_list[0][1].statistics_
            np.testing.assert_allclose(estimado,esperado,rtol=1e-12,atol=1e-8,equal_nan=True)
            err=float(np.nanmax(abs(estimado-esperado)))
            entrada_efetiva=meta['features']
        registros.append({'coorte':s['coorte'],'contexto':s['contexto'],'target':s['target'],'bloco':s['bloco'],
            'algoritmo':s['algoritmo'],'n_ajuste_final':len(y),'ano_min':int(d.loc[sel,'ano_t'].min()),'ano_max':2017,
            'UF_retida_excluida':True,'normalizacao_y_confere':True,'imputacao_treino_confere':True,
            'max_diferenca_mediana_imputacao':err,'atributos_efetivos':json.dumps(entrada_efetiva)})
    pd.DataFrame(registros).to_parquet(saida/'VERIFICACAO_MODELOS_FINAIS.parquet',index=False)
    cv=pd.read_parquet(raiz/'AJUSTES_CV_DESENVOLVIMENTO.parquet')
    resumo={'modelos_verificados':len(registros),'normalizacao_y_e_imputacao_conferem':True,
        'UFs_retidas_excluidas_em_todos_ajustes':True,'teste_ainda_fechado':True,
        'linhas_avaliacao_CV':len(cv),'falhas_configuracao_registradas':int((~cv.valida).sum()),
        'sem_reajuste':True,'codigo_sha256':sha(Path(__file__)),
        'artefatos_sha256':{f.name:sha(f) for f in saida.iterdir() if f.is_file()}}
    gravar_json(resumo,saida/'AUDITORIA_AJUSTES_APROVADA.json')
    print(json.dumps(resumo,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint)

