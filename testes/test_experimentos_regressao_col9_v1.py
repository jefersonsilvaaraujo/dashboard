"""Testes de desenho, isolamento e serialização; sintéticos após congelamento."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
pytestmark=pytest.mark.skip(reason='Revisao tecnica v1 aposentada antes de ajuste cientifico; suite ativa v2.')
pytest.importorskip('sklearn');pytest.importorskip('xgboost');pytest.importorskip('skops')
from modelagem.protocolo_experimentos_col9_v1 import carregar_manifesto,mascaras,folds_internos,blocos
from modelagem.executar_regressao_col9_v1 import metricas,congelar_historicos,ajustar,prever,salvar_modelo,ler_modelo,avaliar_teste_uma_vez
RAIZ=Path('experimentos_regressao_col9/execucao_20261112_v1')

def test_registro_antecede_ajustes():
    p=carregar_manifesto(RAIZ)
    assert json.loads((RAIZ/'RECIBO_CONGELAMENTO.json').read_text(encoding='utf-8'))['antes_de_qualquer_ajuste']
    assert p['2024_utilizado'] is False and p['teste_ja_explorado_cientificamente']
    assert len(p['blocos']['T0'])==3 and len(p['blocos']['T3'])==53 and len(p['blocos']['T4'])==55

def test_coortes_e_embargo_loso():
    d=pd.DataFrame([{'row_id':j*39+a-1985,'CD_MUN':str(j),'SIGLA_UF':uf,'ano_t':a} for j,uf in enumerate(['MA','MT','PA','RO','TO']) for a in range(1985,2024)])
    for co in ['principal','focos2003']:
        for uf in ['MA','MT','PA','RO','TO']:
            for fim,a,b in folds_internos(co):
                tr,va=mascaras(d,uf,fim,a,b,1985 if co=='principal' else 2003)
                assert not d.loc[tr|va,'SIGLA_UF'].eq(uf).any()
                assert d.loc[tr,'ano_t'].max()+2==d.loc[va,'ano_t'].min()
                assert not d.loc[tr|va,'ano_t'].ge(2019).any()

def test_estagiamento_isola_respostas_teste():
    x=pd.read_parquet(RAIZ/'dados/X_desenvolvimento.parquet')
    y=pd.read_parquet(RAIZ/'dados/y_desenvolvimento.parquet')
    xt=pd.read_parquet(RAIZ/'dados/X_teste_selado.parquet')
    assert not {'R_pct','C_ha','D_ha','Q_pct'}&set(x)
    assert x.ano_t.max()==2018 and y.ano_t.max()==2017 and not y.ano_t.isin([2014,2018]).any()
    assert xt.ano_t.between(2019,2022).all()
    assert not set(x.row_id)&set(xt.row_id)

def test_congelamento_nao_atualiza_historico_nem_composicao():
    d=pd.DataFrame({'CD_MUN':['1','1','1'],'ano_t':[2018,2019,2020],'historico':[1.,2.,3.],'composicao':[10.,20.,30.]})
    r=congelar_historicos(d[d.ano_t.ge(2019)],d,2018,['historico'])
    assert r.historico.tolist()==[1.,1.] and r.composicao.tolist()==[20.,30.]

def test_metricas_escala_sinal_e_limites():
    r=metricas([1.,3.],[-1.,5.],'R_pct')
    assert r['MAE']==r['RMSE']==2 and r['vies']==0 and r['n_pred_negativas']==1 and r['R2']==-3
    assert metricas([1.,1.],[1.,1.],'R_pct')['R2'] is None
    with pytest.raises(ValueError):metricas([1],[np.inf],'R_pct')

@pytest.mark.parametrize('alg,params',[
    ('ridge',{'alpha':1.}),
    ('elastic_net',{'alpha':.05,'l1_ratio':.5}),
    ('random_forest',{'n_estimators':5,'max_depth':3,'min_samples_leaf':2,'max_features':1.}),
    ('xgboost',{'n_estimators':5,'max_depth':2,'learning_rate':.1})])
@pytest.mark.parametrize('modo',['identidade','log1p'])
def test_pipeline_roundtrip_seguro_e_imputacao_treino(tmp_path,alg,params,modo):
    carregar_manifesto(RAIZ) # nenhum ajuste sintético sem registro congelado
    x=pd.DataFrame({'a':np.arange(30,dtype=float),'b':[np.nan]*30,'c':[1.,np.nan,3.]*10})
    y=2+np.arange(30)/3
    m,t=ajustar(alg,params,modo,x,y,20261112)
    out=prever(m,t,x.head(3))
    t.update(features=list(x),target='C_ha')
    p=tmp_path/'modelo';salvar_modelo(m,t,p,alg);m2,t2=ler_modelo(p)
    np.testing.assert_allclose(out,prever(m2,t2,x.head(3)),rtol=1e-6,atol=1e-6)
    assert not list(p.glob('*.pkl')) and not list(p.glob('*.joblib'))
    assert t2['centro']==pytest.approx((np.log1p(y) if modo=='log1p' else y).mean())

def test_teste_segunda_passagem_recusada(tmp_path):
    # A verificação de marcador só ocorre após autenticar o protocolo; usar o real
    if (RAIZ/'TESTE_INICIADO.json').exists():
        with pytest.raises(FileExistsError):avaliar_teste_uma_vez(RAIZ)
    else:
        assert not (RAIZ/'ABERTURA_UNICA_Y_TESTE.json').exists()

def test_congelamento_fonte_e_desenho_nao_modificado():
    p=carregar_manifesto(RAIZ)
    assert p['regime_principal'].startswith('origem_movel')
    assert p['particoes']['teste']==[2019,2022]
    assert p['metricas'][0]=='MAE'
    assert 'D_ha' not in p['blocos']['T4']

