"""Proteções de desenho, cegamento, ano reservado e contrato retrospectivo."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.piloto_interpretacao_col9 import selecionar,ficha_cega
from processamento.pacote_avaliadores_col9 import verificar_ficha_cega,verificar_metadados
from modelagem.protocolo_retrospectivo_col9 import validar_previsor,BLOCOS


@pytest.fixture
def amostra():
    linhas=[]
    for h in range(120):
        for i in range(32 if h<114 else 16):
            linhas.append({'id':f'p_{h}_{i}','desenho':'probabilistica','estrato_psu':f'h{h:03d}',
                'ano_origem':2000,'ano_destino':2001,'longitude':-50.,'latitude':-10.,
                'classe_t':3,'classe_t1':15,'pi_inclusao':.001,'peso_expansao_ha':80.})
    return pd.DataFrame(linhas)


def test_piloto_e_subconjunto_dos_120_estratos_sem_reordenacao_dependente(amostra):
    p,r=selecionar(amostra); p2,r2=selecionar(amostra.sample(frac=1,random_state=15))
    pd.testing.assert_frame_equal(p,p2); pd.testing.assert_frame_equal(r,r2)
    assert len(p)==120 and p.estrato_psu.nunique()==120 and set(p.id)<=set(amostra.id)
    assert not p.id.duplicated().any()


def test_nao_muda_probabilidades_pai_e_ampliacao_nao_substitui(amostra):
    p,r=selecionar(amostra)
    assert p.pi_inclusao.eq(.001).all() and p.peso_expansao_ha.eq(80.).all()
    assert set(p.pi_subamostra_condicional)=={1/16,1/32}
    rodada2=r[r.ordem_ampliacao_no_estrato.eq(2)]
    assert len(rodada2)==120 and not set(rodada2.id)&set(p.id)
    assert set(rodada2.id)|set(p.id)<=set(amostra.id)


def test_dirigidos_nao_entram_no_piloto_e_amostra_errada_e_rejeitada(amostra):
    dirigido=amostra.iloc[:10].copy(); dirigido.desenho='dirigida'; dirigido.id='d_'+dirigido.id
    assert selecionar(pd.concat([amostra,dirigido]))[0].id.str.startswith('p_').all()
    with pytest.raises(ValueError): selecionar(amostra.iloc[:-1])
    ruim=amostra.copy(); ruim.loc[1,'id']=ruim.loc[0,'id']
    with pytest.raises(ValueError): selecionar(ruim)


def test_fichas_cegas_mesmos_casos_ordens_diferentes_sem_respostas(amostra):
    p,_=selecionar(amostra); a=ficha_cega(p,'A'); b=ficha_cega(p,'B')
    verificar_ficha_cega(a); verificar_ficha_cega(b)
    assert set(a.caso)==set(b.caso) and a.caso.tolist()!=b.caso.tolist()
    assert a.estado_t.eq('').all() and b.estado_t1.eq('').all()
    assert not {'id','classe_t','classe_t1','estrato_psu','pi_inclusao'}&set(a.columns)


def test_cegamento_e_ano_reservado_sao_barrados(amostra):
    p,_=selecionar(amostra); f=ficha_cega(p,'A'); f['classe_t']=3
    with pytest.raises(ValueError): verificar_ficha_cega(f)
    with pytest.raises(ValueError): verificar_metadados({'evidencias':[{'ano':2024}]})
    with pytest.raises(ValueError): verificar_metadados({'evidencias':[{'ano':2023,'situacao':'disponivel_para_interpretacao','data_imagem':'2024-01-01'}]})


def test_publicacao_tardia_nao_e_vazamento_automatico_no_modo_retrospectivo():
    r=validar_previsor('mb_composicao_t',2020,2020,'2024-08-01',2020)
    assert not r['erros'] and not r['apto_operacional_historico']
    assert any('publicacao_posterior' in x for x in r['riscos'])


def test_fenomeno_futuro_e_desfecho_corrente_continuam_proibidos():
    assert 'fenomeno_posterior_a_t' in validar_previsor('focos',2020,2021)['erros']
    for nome in ['C_ha','D_ha','R_pct','Q_pct','area_convertida_ha','taxa_conversao_pct','classe_t1','alvo_prodes']:
        assert validar_previsor(nome,2020,2020)['erros']
    assert validar_previsor('hist_conv_ha_ate_t',2020,2020)['erros']==[]


def test_dependencia_algoritmica_futura_e_risco_explicito():
    r=validar_previsor('mb_composicao_t',2020,2020,'2024-08-01',2023)
    assert any('informacao_futura' in x for x in r['riscos'])
    assert any('nao_auditada' in x for x in validar_previsor('x',2020,2020)['riscos'])
    assert validar_previsor('x',2023,2023)['erros'] and validar_previsor('x',2024,2024)['erros']


def test_blocos_classificam_acervo_sem_promover_legado():
    status={x[3] for x in BLOCOS}
    assert status=={'derivavel_acervo_harmonizado','acervo_presente_nao_harmonizado','fonte_adicional'}
    assert all('268' not in x[4] for x in BLOCOS)
