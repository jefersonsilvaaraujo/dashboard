"""Proteções científicas dos cenários, inferência e relógio de previsão."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import avaliar,agregar
from processamento.respostas_tematica_col9 import auditar
from modelagem.contrato_matriz_col9 import indice,divisao_temporal,divisao_loso,verificar_disponibilidade


def base():
    return pd.DataFrame({'CD_MUN':[1,2,3,4,5], 'C_ha':[100,99,120,120,120],
        'D_ha':[20000,19800,30000,24000,0], 'VN_inicial_ha':[20000,19800,30000,24100,120],
        'R_pct':[.5,.5,.4,.5,np.nan], 'Q_pct':[100,100,100,99.6,0]})


def test_criterios_sao_simultaneos_e_limites_inclusivos():
    r=avaliar(base(),.5,100,99.5)
    assert r.candidato.tolist()==[True,False,False,True,False]
    assert not r.avaliavel.iloc[-1]


def test_qualidade_nao_e_evento_negativo():
    r=avaliar(base(),.5,100,99.9)
    assert r.exclusao_qualidade.tolist()==[False,False,False,True,True]
    r['cenario']='B'; r['discordante_principal']=False
    a=agregar(r,['cenario']).iloc[0]
    assert (a.n_avaliaveis,a.n_eventos_candidatos,a.n_excluidos_qualidade)==(3,1,2)
    assert a.proporcao_eventos_avaliaveis_pct==pytest.approx(100/3)


def test_proximidade_apenas_fronteira_conjunta():
    r=avaliar(base(),.5,100,99.5)
    assert r.proximo.tolist()==[True,True,False,True,False]


def test_cenarios_aninhados_quando_mesma_classificacao_qualidade():
    a=avaliar(base(),.25,25,99.5).candidato
    b=avaliar(base(),.5,100,99.5).candidato
    c=avaliar(base(),1,250,99.5).candidato
    assert not (b&~a).any() and not (c&~b).any()


def test_2023_nao_possui_ano_de_desfecho():
    d=indice(range(255))
    assert len(d)==9945 and d.ano_desfecho.notna().sum()==9690
    assert d[d.ano_t.eq(2023)].ano_desfecho.isna().all()
    assert not {'Y','candidato','alvo_prodes'}&set(d.columns)
    with pytest.raises(ValueError): indice(range(268))


def test_disponibilidade_vintage_futuro_bloqueada():
    assert verificar_disponibilidade('mb_vn_ha','2022-12-31','2022-12-31','2024-08-31','2023-12-31')==[
        'publicado_em_posterior_ao_corte','dependencia_fim_posterior_ao_corte']
    assert not verificar_disponibilidade('frp','2022-12-31','2022-12-01','2022-12-02','2022-12-01')
    assert 'publicado_em_desconhecido' in verificar_disponibilidade('frp','2022-12-31','2022-12-01',None,'2022-12-01')


def test_medidas_futuras_nao_entram_em_X():
    for nome in ['C_ha','D_ha','Q_pct','alvo_taxa','classe_t1']:
        assert 'variavel_do_desfecho_ou_qualidade_futura' in verificar_disponibilidade(nome,'2022-12-31','2020-01-01','2020-01-01','2020-01-01')


def test_disponibilidade_respeita_fusos_e_instante_do_corte():
    assert not verificar_disponibilidade('frp','2022-12-31T23:59:59-03:00',
        '2022-12-31','2023-01-01T02:59:58Z','2022-12-31')
    assert 'publicado_em_posterior_ao_corte' in verificar_disponibilidade('frp','2022-12-31T23:59:59-03:00',
        '2022-12-31','2023-01-01T03:00:00Z','2022-12-31')


def test_cortes_temporais_e_estados_sem_intersecao():
    d=pd.DataFrame([(uf,t) for uf in ['MA','MT','PA','RO','TO'] for t in range(1985,2024)],columns=['SIGLA_UF','ano_t'])
    r=divisao_temporal(d.ano_t)
    assert d.loc[r.eq('treino'),'ano_t'].max()+1<d.loc[r.eq('validacao'),'ano_t'].min()
    assert d.loc[r.eq('validacao'),'ano_t'].max()+1<d.loc[r.eq('teste_reservado'),'ano_t'].min()
    for uf in d.SIGLA_UF.unique():
        f=divisao_loso(d,uf)
        assert not d.loc[f.isin(['treino','validacao']),'SIGLA_UF'].eq(uf).any()
        assert d.loc[f.eq('teste_estado_retido'),'SIGLA_UF'].eq(uf).all()
        assert d.loc[f.eq('teste_estado_retido'),'ano_t'].between(2019,2022).all()


def test_nao_resposta_e_dirigidos_nao_geram_acuracia():
    pontos=pd.DataFrame({'id':['p1','p2','d1'],'desenho':['probabilistica','probabilistica','dirigida']})
    fichas=pd.DataFrame({'id':['p1','p2','d1'],'referencia_t':['VN',None,'VN'],'referencia_t1':['UA',None,'UA'],
        'situacao':['concluido','inconclusivo','concluido'],
        **{k:['documentado']*3 for k in ['fonte','interprete','evidencia_arquivo','data_imagem_t','data_imagem_t1','justificativa']}})
    a=auditar(pontos,fichas)
    assert a['n_probabilisticos']==2 and a['n_com_resposta_documentada']==1
    assert a['acuracia_estimada'] is None
    with pytest.raises(ValueError): auditar(pontos,fichas.iloc[:2])
