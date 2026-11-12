"""Contratos científicos: referências incompletas, grades e inferência não presumida."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip('geopandas')
rasterio=pytest.importorskip('rasterio')
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from processamento.avaliar_pontos_oficiais_col9 import (
    codificar,grupos,evento,persistencia,resumo_binario,ler_celulas)
from processamento.auditoria_complementar_oficial_col9 import intervalo_prodes,confronto_prodes
from processamento.diagnosticos_pontos_oficiais_col9 import coincidencias_janela


def test_referencia_coarse_ua_sem_inventar_terminal():
    a=codificar(pd.Series(['LAVOURA TEMPORÁRIA','LAVOURA PERENE','VEGETAÇÃO URBANA',
                          'OUTRA FORMAÇÃO NÃO FLORESTAL',None,'FORMAÇ��O FLORESTAL']))
    assert a.tolist()==[19,36,-1,13,-1,-1]
    assert grupos(a,True).tolist()==[2,2,-1,-1,-1,-1]


def test_evento_aprovado_e_sensibilidade():
    a=np.array([3,29,32,3,27,0,15]);b=np.array([15,15,15,25,15,15,3])
    valid,event=evento(a,b)
    assert event.tolist()==[True,False,False,False,False,False,False]
    assert valid.tolist()==[True,True,True,True,False,False,True]
    _,sens=evento(a,b,extras_o=[29,32],extras_d=[25])
    assert sens.tolist()==[True,True,True,True,False,False,False]


def test_nao_observado_nao_e_nao_evento():
    valid,event=evento(np.array([3,3]),np.array([-1,27]),True)
    assert not valid.any() and not event.any()


def test_matriz_detecta_comissao_e_omissao():
    r=resumo_binario([1,0,1,0],[1,1,0,0])
    assert [r[k] for k in ['TP','FP','FN','TN']]==[1,1,1,1]
    assert r['precisao_descritiva']==r['sensibilidade_descritiva']==.5
    rw=resumo_binario([1,0,1,0],[1,1,0,0],[1,2,3,4])
    assert rw['precisao_descritiva']==pytest.approx(1/3)
    assert rw['sensibilidade_descritiva']==.25


def test_denominador_zero_nao_vira_zero_acuracia():
    r=resumo_binario([0,0],[0,0])
    assert r['precisao_descritiva'] is None and r['sensibilidade_descritiva'] is None
    with pytest.raises(ValueError):resumo_binario([1],[1],[0])


def test_futuro_censurado_e_reversoes():
    a=np.full((3,39),15,dtype=np.int16)
    a[0,:3]=[3,15,3]
    a[1,:3]=[3,15,27]
    a[2,-2:]=[3,15]
    comum,c,p,rev,rc=persistencia(a)
    assert c[0,0] and p[0,0]==0 and rev[0,0]==rc[0,0]==1
    assert c[1,0] and p[1,0]==-1
    assert c[2,-1] and p[2,-1]==rev[2,-1]==rc[2,-1]==-1
    with pytest.raises(ValueError):persistencia(np.ones((1,40)))


def test_leitura_categorica_sem_deslocamento_e_limites():
    a=np.arange(25,dtype=np.uint8).reshape(5,5)
    with MemoryFile() as mem:
        with mem.open(driver='GTiff',height=5,width=5,count=1,dtype='uint8',
                      crs='EPSG:4326',transform=from_origin(0,5,1,1),nodata=0) as s:
            s.write(a,1)
            v,ok=ler_celulas(s,[2,0,99],[2,0,99])
    assert v[0].tolist()==[6,7,8,11,12,13,16,17,18]
    assert v[1,4]==0 and not ok[1,4]
    assert not ok[2].any()


def test_todos_pontos_fora_grade_nao_quebra():
    with MemoryFile() as mem:
        with mem.open(driver='GTiff',height=2,width=2,count=1,dtype='uint8',
                      crs='EPSG:4326',transform=from_origin(0,2,1,1)) as s:
            v,ok=ler_celulas(s,[99],[99])
    assert not ok.any() and not v.any()


def test_prodes_intervalos_nao_equivalem_ano_exato():
    assert intervalo_prodes('2 d2002','CERRADO')==(2001,2002)
    assert intervalo_prodes('10 d2010','CERRADO')==(2009,2010)
    assert intervalo_prodes('10 d2010','AMAZÔNIA')==(2010,2010)
    assert intervalo_prodes('0 d2000','CERRADO')==(None,2000)
    assert intervalo_prodes('100 Vegetação Nativa','CERRADO') is None
    with pytest.raises(ValueError):intervalo_prodes('24 d2024','CERRADO')


def test_ausencia_prodes_nao_vira_erro_col9():
    assert confronto_prodes('100 Vegetação Nativa',2023,'CERRADO').startswith('inconclusivo')
    assert confronto_prodes('22 d2022',2022,'AMAZÔNIA').startswith('coincidencia')
    assert confronto_prodes('22 d2022',2023,'AMAZÔNIA').startswith('proximidade')
    assert confronto_prodes('10 d2010',2022,'AMAZÔNIA').startswith('cronologia_distinta_inconclusiva')


def test_janela_temporal_exige_referencia_observada():
    ok,sim=coincidencias_janela([[1,1,0]],[[0,1,0]],1)
    assert ok.tolist()==[[True,False,False]]
    assert sim.tolist()==[[True,True,True]]
    # Referência positiva vizinha não torna observada uma janela com ausências.
    assert not ok[0,-1]


def test_calibracao_espectral_nao_ignora_offset2022():
    pytest.importorskip('PIL')
    from processamento.auditoria_espectral_col9 import calibrar,deduplicar_tarefas
    a=np.array([2000])
    r,c=calibrar(a,{'raster:bands':[{'scale':.0001,'offset':-.1}]},False)
    assert r[0]==pytest.approx(.1)
    r,c=calibrar(np.array([10000]),{},True)
    assert r[0]==pytest.approx(.075)
    with pytest.raises(ValueError):calibrar(a,{},False)
    t=({'id':'p'},{'ano':2001},{'id':'cena'},Path('catalogo.json'))
    u,rep=deduplicar_tarefas([t,t])
    assert len(u)==len(rep)==1
    outro=(t[0],t[1],{'id':'outra_cena'},t[3])
    with pytest.raises(ValueError):deduplicar_tarefas([t,outro])


def test_hipoteses_radiometricas_nao_confundem_invalidade_com_zero():
    from processamento.sensibilidade_radiometrica_col9 import calcular_ndvi
    red=np.array([[400]],dtype=np.uint16);nir=np.array([[3000]],dtype=np.uint16)
    w=np.array([[900.]])
    val,frac=calcular_ndvi(red,nir,w,.0001,0)
    assert val==pytest.approx(2600/3400) and frac==1
    val,frac=calcular_ndvi(red,nir,w,.0001,-.1)
    assert val is None and frac==0


def test_checkpoint_oficial_se_disponivel():
    p=Path('validacao_cientifica_col9/oficial_col9_20261112_v1/avaliacao')
    if not (p/'resumo_execucao.json').exists():pytest.skip('Execução integral ainda não disponível.')
    r=json.loads((p/'resumo_execucao.json').read_text(encoding='utf-8'))
    assert r['pontos_recorte']==8586 and r['municipios_com_pontos']==253
    assert r['treinamento_recorte']==1305 and r['n_ref2023_recorte']==1
    assert r['anos_csv']==list(range(1985,2024))
    assert r['sem_Y_homologado'] and r['sem_treinamento']
    z=pd.read_csv(p/'comparacoes_ponto_par.csv',sep=';',encoding='utf-8-sig')
    assert len(z)==8586*38*2
    assert not z.duplicated(['TARGETID','ano_origem','versao_referencia']).any()
    assert z.ano_destino.max()==2023 and z.ano_origem.max()==2022
    assert z.loc[~z.comparavel,'evidencia'].eq('inconclusivo').all()
    assert not z.loc[(z.ano_destino==2023)&(z.versao_referencia=='vetor_auxiliar'),'comparavel'].any()
    assert (z.loc[(z.ano_destino==2023)&(z.versao_referencia=='csv_principal'),'comparavel'].sum()<=1)
    c=pd.read_csv(p/'concordancia_global.csv',sep=';',encoding='utf-8-sig')
    primary=z.loc[z.comparavel & z.versao_referencia.eq('csv_principal') & z.AMOSTRA_AM.eq(0)]
    expected=resumo_binario(primary.evento_referencia,primary.evento_mapa)
    row=c.loc[c.versao_referencia.eq('csv_principal')&c.coorte.eq('sem_marcacao_treino')].iloc[0]
    for k in ['TP','FP','FN','TN']:assert row[k]==expected[k]
    assert not any('IC95' in col for col in c.columns)


def test_auditorias_finais_nao_confundem_cobertura_com_validacao():
    p=Path('validacao_cientifica_col9/oficial_col9_20261112_v1')
    if not (p/'cenarios_evidencias/manifesto_cenarios_evidencias.json').exists():pytest.skip('Auditoria ainda não disponível.')
    a=pd.read_csv(p/'cenarios_evidencias/cenarios_cobertura_referencias_87210.csv',sep=';',encoding='utf-8-sig')
    assert len(a)==9690*9 and a.CD_MUN.nunique()==255
    assert not a.duplicated(['CD_MUN','ano_origem','cenario','Q_min_pct']).any()
    assert a.ano_destino.max()==2023
    last=a.query('ano_destino==2023')
    assert last.n_comparaveis.sum()==9 and not last.n_eventos_ref.any()
    assert 'Y' not in a.columns and 'Y_homologado' not in a.columns
    r=pd.read_csv(p/'radiometria/NDVI_duas_hipoteses.csv',sep=';',encoding='utf-8-sig')
    assert len(r)==84 and r.conflito_metadados.sum()==38
    assert r.loc[r.conflito_metadados,'evidencia'].eq('inconclusiva_calibracao_conflitante').all()
    assert r.ano.max()==2023


def test_mascara_tripla_buriticupu_preserva_magnitude_consolidada():
    raiz=Path('resultados_transicoes_col9/integral_255_1985_2023_20261111')
    if not (raiz/'concluido.json').exists():pytest.skip('Acervo externo de matrizes indisponível.')
    p=raiz/'municipios/2102325';ck=json.loads((p/'concluido.json').read_text(encoding='utf-8'))
    q=pd.read_csv(raiz/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    from processamento.avaliar_pontos_oficiais_col9 import VN,UA
    with np.load(p/ck['npz'],allow_pickle=False) as z:
        cl=z['classes'];a=z['tripla_area_ha']
        vn=np.flatnonzero(np.isin(cl,VN));ua=np.flatnonzero(np.isin(cl,UA))
        conv=a[:,vn,:][:,:,ua].sum(axis=(1,2))
        den=a[:,vn,:].sum(axis=(1,2))
    r=q.query('CD_MUN==2102325 and ano_origem in [2001,2002]').sort_values('ano_origem')
    np.testing.assert_allclose(conv,r.area_convertida_ha,rtol=1e-10,atol=1e-6)
    np.testing.assert_allclose(den,r.vn_inicial_elegivel_ha,rtol=1e-10,atol=1e-6)
