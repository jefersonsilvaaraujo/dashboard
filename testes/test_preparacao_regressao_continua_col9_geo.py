"""Contratos científicos da matriz candidata; nenhum estimador ou treinamento."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
pytest.importorskip('geopandas');pytest.importorskip('pyarrow')
from modelagem.preparar_regressao_continua_col9 import construir_cobertura,validar_X,exigir_autorizacao_treinamento,CHAVES,PROIBIDOS,GRUPOS
from processamento.cenarios_validacao_col9 import VN,UA,sha
RAIZ=Path('validacao_cientifica_col9/preparacao_regressao_20261112_v2')

def sinteticos():
    cl=[3,4,5,6,49,11,12,50,9,15,20,21,24,30,31,35,39,40,41,46,47,48,62,25,29,32,33,23,27]
    e=[];p=[]
    for cd in ['1100064','2102325']:
        for ano in range(1985,2024):
            r={'CD_MUN':cd,'ano_t':ano,'pixels_validos_t':1000}
            r.update({f'area_classe_{c}':0. if c==27 else 10. for c in cl})
            r['area_classe_3']=100.+2*(ano-1985);e.append(r)
            if ano>=1986:p.append({'CD_MUN':cd,'ano_t':ano,'C_passada_ha':float(ano-1985),'R_passada_pct':float(ano-1985)/10})
    geo=pd.DataFrame({'CD_MUN':['1100064','2102325'],'pixels_grade_municipio':[1001,1001],'territorio_area_geodesica_ha':[1000.,1000.]})
    return pd.DataFrame(e),pd.DataFrame(p),geo

def test_classes_aprovadas():
    assert GRUPOS['vn']==VN and GRUPOS['ua']==UA
    assert not set([25,29,32])&set(VN+UA)

def test_ausencia_historica_e_janelas_completas():
    e,p,g=sinteticos();x,cat=construir_cobertura(e,p,g);a=x[x.CD_MUN.eq('1100064')].set_index('ano_t')
    assert pd.isna(a.loc[1985,'mb_conv_passada_ha']) and a.loc[1985,'lacuna_conversao_passada']
    assert pd.isna(a.loc[1986,'mb_vn_t_ha_tendencia_3anos'])
    assert a.loc[1987,'mb_vn_t_ha_tendencia_3anos']==pytest.approx(2)
    assert pd.isna(a.loc[1989,'mb_conv_passada_ha_media_5anos'])
    assert a.loc[1990,'mb_conv_passada_ha_media_5anos']==pytest.approx(3)

def test_mutacao_futura_nao_altera_atributos_em_t():
    e,p,g=sinteticos();x,c=construir_cobertura(e,p,g);e2=e.copy();p2=p.copy()
    e2.loc[e2.ano_t.gt(2000),[a for a in e2 if a.startswith('area_classe_')]]=1e9
    p2.loc[p2.ano_t.gt(2000),['C_passada_ha','R_passada_pct']]=987654.
    y,_=construir_cobertura(e2,p2,g)
    pd.testing.assert_frame_equal(x.loc[x.ano_t.le(2000)],y.loc[y.ano_t.le(2000)])
    assert all(m['fim_fenomeno_offset']<=0 for m in c)

def test_denominador_de_composicao_inclui25_e33():
    e,p,g=sinteticos();x,c=construir_cobertura(e,p,g)
    den=e.loc[0,[n for n in e if n.startswith('area_classe_') and n!='area_classe_27']].sum()
    assert x.loc[0,'mb_area_classificada_t_ha']==den
    assert x.loc[0,'mb_classe25_t_pct']==pytest.approx(1000/den)

@pytest.mark.parametrize('coluna',['C_ha','D_ha','R_pct','Q_pct','pixels_comuns','classe_t1','SIGLA_UF','alvo_prodes'])
def test_injecao_desfecho_rejeitada(coluna):
    e,p,g=sinteticos();x,c=construir_cobertura(e,p,g);x[coluna]=0
    with pytest.raises(ValueError):validar_X(x,c)

def test_fim_fenomeno_futuro_e_mascara_futura_rejeitados():
    e,p,g=sinteticos();x,c=construir_cobertura(e,p,g);c[0]['fim_fenomeno_offset']=1
    with pytest.raises(ValueError):validar_X(x,c)
    c[0]['fim_fenomeno_offset']=0;c[0]['usa_mascara_desfecho_atual']=True
    with pytest.raises(ValueError):validar_X(x,c)

def test_treinamento_e_otimizacao_bloqueados():
    for operacao in ['treinar','otimizar','avaliar_teste']:
        with pytest.raises(PermissionError):exigir_autorizacao_treinamento(operacao)

@pytest.fixture
def real():
    if not (RAIZ/'contrato_preparacao.json').exists():pytest.skip('Acervo científico não preparado.')
    return RAIZ

def test_chaves_e_2023_sem_resposta(real):
    p=real/'matriz';i=pd.read_parquet(p/'INDICE_CANONICO_9690_COL9.parquet');s=pd.read_parquet(p/'INDICE_2023_SEM_RESPOSTA_COL9.parquet');r=pd.read_parquet(p/'RESPOSTAS_NAO_OBSERVADAS_2023_COL9.parquet')
    canon=json.loads(Path('referencias/territorio_col9_hashes.json').read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    assert len(i)==9690 and i.CD_MUN.nunique()==255 and set(i.CD_MUN)==set(canon)
    assert not i.duplicated(CHAVES).any() and set(i.ano_t)==set(range(1985,2023))
    assert i.groupby('CD_MUN').size().eq(38).all()
    assert len(s)==len(r)==255 and s.ano_t.eq(2023).all() and s.ano_t1.isna().all()
    assert r[['C_ha','D_ha','R_pct']].isna().all().all()

def test_resposta_exata_e_denominadores_distintos(real):
    p=real/'matriz';x=pd.read_parquet(p/'MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet');r=pd.read_parquet(p/'RESPOSTAS_CONTINUAS_COL9.parquet')
    o=pd.read_csv('resultados_transicoes_col9/integral_255_1985_2023_20261111/metricas_municipio_ano.csv',dtype={'CD_MUN':str})
    z=r.merge(o,left_on=CHAVES,right_on=['CD_MUN','ano_origem'],validate='one_to_one')
    for a,b in [('C_ha','area_convertida_ha'),('D_ha','vn_inicial_elegivel_ha'),('R_pct','taxa_conversao_pct')]:
        np.testing.assert_allclose(z[a],z[b],rtol=0,atol=1e-10)
    np.testing.assert_allclose(r.R_pct,100*r.C_ha/r.D_ha,rtol=1e-12,atol=1e-10)
    assert r.R_pct.between(0,100).all() and r.C_ha.le(r.D_ha+1e-6).all() and not set(x)&PROIBIDOS
    a=x.query("CD_MUN=='2102325' and ano_t==2002").iloc[0];b=r.query("CD_MUN=='2102325' and ano_t==2002").iloc[0]
    assert a.mb_vn_t_ha>b.D_ha

def test_metadados_e_dependencia_algoritmica_explicita(real):
    x=pd.read_parquet(real/'matriz/MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet')
    c=json.loads((real/'metadados/catalogo_atributos.json').read_text(encoding='utf-8'));validar_X(x,c)
    assert len(c)==53 and 'CD_MUN' not in {v['variavel'] for v in c}
    m=pd.read_parquet(real/'metadados/DISPONIBILIDADE_ATRIBUTOS_COL9.parquet')
    assert len(m)==9945*53 and m.ano_max_informacao_fenomeno.le(m.ano_t).all()
    assert not m.duplicated(CHAVES+['variavel']).any()
    mb=[v for v in c if v['colecao']=='9']
    assert all(v['status_temporal']=='sujeito_a_analise' for v in mb)
    assert all(v['dependencia_algoritmica_max_ano_conservadora']==2023 for v in mb)
    assert not any('fracao_' in n for n in x)

def test_particoes_e_estados_inteiramente_retidos(real):
    p=real/'matriz';t=pd.read_parquet(p/'PARTICOES_TEMPORAIS_COL9.parquet')
    assert t.papel.value_counts().to_dict()=={'treino':7395,'teste_reservado':1020,'validacao':765,'embargo':510}
    l=pd.read_parquet(p/'PARTICOES_LOSO_COL9.parquet');assert len(l)==9690*5
    for uf,a in l.groupby('UF_retida'):
        assert not a.loc[a.SIGLA_UF.eq(uf),'papel'].isin(['treino','validacao']).any()
        test=a[a.papel.eq('teste_estado_retido')]
        assert test.SIGLA_UF.eq(uf).all() and test.ano_t.between(2019,2022).all()
    f=pd.read_parquet(p/'FOLDS_INTERNOS_AVANCO_COL9.parquet')
    for _,a in f.groupby('fold'):
        fim=a.loc[a.papel.eq('treino'),'ano_t'].max();ini=a.loc[a.papel.eq('validacao_interna'),'ano_t'].min()
        assert ini==fim+2 and a.loc[a.papel.eq('validacao_interna'),'ano_t'].max()<=2013

def test_focos_separados_e_sem_zeros_imputados(real):
    p=real/'complementares';d=pd.read_parquet(p/'FOCOS_MENSAIS_CANDIDATOS_SEPARADOS.parquet')
    assert len(d)==255*39*12 and d.CD_MUN.nunique()==255 and d.ano_t.max()==2023
    assert d.loc[d.ano_t.lt(2003),'focos_registrados_mes'].isna().all()
    assert d.loc[~d.tem_registro_no_mes,'focos_registrados_mes'].isna().all()
    a=pd.read_csv(p/'AUDITORIA_FOCOS_POR_ARQUIVO.csv',sep=';')
    assert a.ano.max()==2023 and len(a)==21 and a.n_data_coordenada_id_invalida_ou_outro_ano.sum()==0

def test_hashes_e_contrato_sem_aprendizagem(real):
    d=json.loads((real/'contrato_preparacao.json').read_text(encoding='utf-8'))
    assert not d['treinamento_autorizado'] and not d['otimizacao_autorizada']
    for n,h in d['artefatos_sha256'].items():assert sha(real/n)==h

