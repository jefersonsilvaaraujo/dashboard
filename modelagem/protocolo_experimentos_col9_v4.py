"""Auditoria e congelamento ANTES de qualquer ajuste; entradas aprovadas imutáveis."""
import argparse
from datetime import datetime,timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import numpy as np
import pandas as pd

PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha
from modelagem.preparar_regressao_continua_col9 import validar_X,CHAVES

PREPARACAO=PROJETO/'validacao_cientifica_col9/preparacao_regressao_20261112_v2'
SEMENTE=20261112
GRADE={
 'ridge':[{'alpha':a} for a in [.1,10.,1000.]],
 'elastic_net':[{'alpha':a,'l1_ratio':r} for a in [.001,.05] for r in [.25,.75]],
 'random_forest':[
   {'n_estimators':100,'max_depth':6,'min_samples_leaf':15,'max_features':1.},
   {'n_estimators':100,'max_depth':10,'min_samples_leaf':10,'max_features':.7}],
 'xgboost':[
   {'n_estimators':160,'max_depth':2,'learning_rate':.05,'min_child_weight':10,'reg_lambda':5.,'subsample':.9,'colsample_bytree':.9},
   {'n_estimators':200,'max_depth':4,'learning_rate':.05,'min_child_weight':20,'reg_lambda':10.,'subsample':.9,'colsample_bytree':.9}]}
ALGORITMOS=list(GRADE)
ORDEM_MODELOS=['media_historica','mediana_historica','persistencia']+ALGORITMOS

def gravar_json(d,p):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False)

def carregar_manifesto(raiz):
    d=json.loads((raiz/'PROTOCOLO_CONGELADO.json').read_text(encoding='utf-8'))
    recibo=json.loads((raiz/'RECIBO_CONGELAMENTO.json').read_text(encoding='utf-8'))
    if sha(raiz/'PROTOCOLO_CONGELADO.json')!=recibo['sha256_protocolo']:raise ValueError('Protocolo alterado.')
    for n,h in d['codigo_modelagem_sha256'].items():
        if sha(PROJETO/n)!=h:raise ValueError('Código de ajuste/teste diverge do congelamento.')
    return d

def blocos(catalogo):
    b0=[m['variavel'] for m in catalogo if m['bloco']=='territorio']
    histconv=[m['variavel'] for m in catalogo if m['fonte_id']=='transicoes_col9_encerradas' or
        m['variavel']=='lacuna_conversao_passada' or m['variavel'].startswith('lacuna_janela_conversao_')]
    histstock=[m['variavel'] for m in catalogo if
        'variacao_liquida' in m['variavel'] or 'tendencia_' in m['variavel'] or
        m['variavel'].startswith('mb_vn_pct_media_') or m['variavel'].startswith('lacuna_janela_estoque_')]
    atual=[m['variavel'] for m in catalogo if m['variavel'] not in set(b0+histconv+histstock)]
    retorno={'T0':b0,'T1':b0+atual,'T2':b0+atual+histstock,'T3':b0+atual+histstock+histconv}
    retorno['T4']=retorno['T3']+['focos_log1p_registros_ano','focos_meses_com_registro']
    return retorno,{'territorio':b0,'composicao_qualidade_t':atual,'historico_estoques':histstock,'historico_conversoes':histconv}

def folds_internos(coorte):
    return [(2001,2003,2005),(2005,2007,2009),(2009,2011,2013)] if coorte=='principal' else [(2005,2007,2009),(2009,2011,2013)]

def mascaras(d,uf=None,fim_treino=2013,inicio_val=2015,fim_val=2017,minimo=1985):
    apto=d.ano_t.ge(minimo)
    if uf:apto &= d.SIGLA_UF.ne(uf)
    tr=apto & d.ano_t.le(fim_treino);va=apto & d.ano_t.between(inicio_val,fim_val)
    if set(d.loc[tr,'row_id'])&set(d.loc[va,'row_id']):raise ValueError('Partições sobrepostas.')
    if va.any() and tr.any() and d.loc[va,'ano_t'].min()<=d.loc[tr,'ano_t'].max()+1:raise ValueError('Embargo ausente.')
    return tr.to_numpy(),va.to_numpy()

def congelar(raiz,docs):
    if raiz.exists() or docs.exists():raise FileExistsError('Usar novas pastas para outro protocolo.')
    p=PREPARACAO/'matriz'
    x=pd.read_parquet(p/'MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet')
    y=pd.read_parquet(p/'RESPOSTAS_CONTINUAS_COL9.parquet')
    i=pd.read_parquet(p/'INDICE_CANONICO_9690_COL9.parquet')
    q=pd.read_parquet(p/'QUALIDADE_ELEGIBILIDADE_COL9.parquet')
    cat=json.loads((PREPARACAO/'metadados/catalogo_atributos.json').read_text(encoding='utf-8'))
    validar_X(x,cat)
    canon=json.loads((PROJETO/'referencias/territorio_col9_hashes.json').read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    if len(x)!=9690 or len(y)!=9690 or len(q)!=9690 or set(x.CD_MUN)!=set(canon) or x.duplicated(CHAVES).any():
        raise ValueError('Interromper: chaves/universo incoerentes.')
    for f in [x,y,q]:
        pd.testing.assert_frame_equal(f[CHAVES].reset_index(drop=True),i[CHAVES].reset_index(drop=True))
    if not x.groupby('CD_MUN').ano_t.apply(lambda s:s.tolist()==list(range(1985,2023))).all():raise ValueError('Intervalos incoerentes.')
    np.testing.assert_allclose(y.R_pct,100*y.C_ha/y.D_ha,rtol=1e-12,atol=1e-10)
    if not y.D_ha.gt(0).all() or not y.R_pct.between(0,100).all():raise ValueError('Resposta inválida.')
    orig=pd.read_csv(PROJETO/'resultados_transicoes_col9/integral_255_1985_2023_20261111/metricas_municipio_ano.csv',dtype={'CD_MUN':str})
    erros_leitor={}
    for novo,velho in [('C_ha','area_convertida_ha'),('D_ha','vn_inicial_elegivel_ha'),('R_pct','taxa_conversao_pct')]:
        erros_leitor[novo]=float(np.max(abs(y[novo].to_numpy()-orig[velho].to_numpy())))
        # Leitores CSV pandas2.3/3.1 diferem em poucosULP. Nada é corrigido:
        # preservar os floats do Parquet aprovado; tolerância absoluta1e-8ha/%.
        np.testing.assert_allclose(y[novo],orig[velho],rtol=0,atol=1e-8)
    disp=pd.read_parquet(PREPARACAO/'metadados/DISPONIBILIDADE_ATRIBUTOS_COL9.parquet')
    if not disp.ano_max_informacao_fenomeno.le(disp.ano_t).all():raise ValueError('Interromper: fenômeno futuro direto.')
    preparado=json.loads((PREPARACAO/'manifesto_final_preparacao.json').read_text(encoding='utf-8'))
    for n,h in preparado['sha256'].items():
        if sha(PROJETO/n)!=h:raise ValueError('Preparação/checkpoint alterado:'+n)
    m=json.loads((PROJETO/'referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    for r in m['rasters'].values():
        st=(Path(m['base_dados'])/r['arquivo']).stat()
        if (st.st_size,st.st_mtime_ns)!=(r['bytes'],r['mtime_ns']):raise ValueError('Raster alterado.')
    # Janela de referência é validada sem presumir completude física de detecção.
    f=pd.read_parquet(PREPARACAO/'complementares/FOCOS_ANUAIS_CANDIDATOS_SEPARADOS.parquet')
    f=f.loc[f.ano_t.between(2003,2022)].copy()
    audf=pd.read_csv(PREPARACAO/'complementares/AUDITORIA_FOCOS_POR_ARQUIVO.csv',sep=';')
    for c in ['n_data_coordenada_id_invalida_ou_outro_ano','n_duplicatas_exatas','n_ids_conflitantes','n_ambiguos_limite_linhas']:
        if audf[c].sum():raise ValueError('T4 bloqueado: auditoria de focos inconsistente.')
    if len(f)!=5100 or f.CD_MUN.nunique()!=255 or not f.fonte_anual_local_presente.all():raise ValueError('Cobertura T4 incompatível.')
    f['focos_log1p_registros_ano']=np.log1p(f.focos_registrados_ano)
    f=f.rename(columns={'meses_com_registro':'focos_meses_com_registro'})
    colf=['focos_log1p_registros_ano','focos_meses_com_registro']
    z=i[CHAVES+['NM_MUN','SIGLA_UF']].merge(x,on=CHAVES,validate='one_to_one').merge(f[CHAVES+colf],on=CHAVES,how='left',validate='one_to_one')
    z['row_id']=np.arange(len(z),dtype=np.int64)
    eleg=y.D_ha.gt(0)&q.Q_pct.ge(99.5)
    if not eleg.all():raise ValueError('Coorte mudou; requer novo protocolo antes de treinar.')
    yy=y[CHAVES+['R_pct','C_ha']].copy();yy['row_id']=z.row_id
    b,grupos=blocos(cat)
    if set(b['T3'])!=set(x)-set(CHAVES) or len(set(b['T3']))!=53:raise ValueError('Blocos não particionam53 atributos.')
    raiz.mkdir(parents=True);docs.mkdir(parents=True);(raiz/'dados').mkdir();(raiz/'auditoria').mkdir()
    for papel,sel in [('desenvolvimento',z.ano_t.le(2018)),('teste_selado',z.ano_t.between(2019,2022))]:
        z.loc[sel].to_parquet(raiz/'dados'/f'X_{papel}.parquet',index=False)
        seley=sel&yy.ano_t.ne(2014)&yy.ano_t.ne(2018)
        yy.loc[seley].to_parquet(raiz/'dados'/f'y_{papel}.parquet',index=False)
    z[CHAVES+['row_id','NM_MUN','SIGLA_UF']].to_parquet(raiz/'dados/indice_completo.parquet',index=False)
    aus=pd.DataFrame({'variavel':list(x.drop(columns=CHAVES)),'ausentes':[int(x[c].isna().sum()) for c in x if c not in CHAVES]})
    aus.to_csv(raiz/'auditoria/cobertura_atributos.csv',sep=';',index=False)
    diario_anterior=PROJETO/'docs/DECISOES_DEFESA_MESTRADO.md'
    diario=(
        '# Adendo ao diário de decisões científicas —12/11/2026\n\n'
        'O pesquisador informou concordância do orientador e autorizou explicitamente implementação, treinamento e avaliação neste encaminhamento.\n'
        'R=100C/D é o desfecho principal; C emha é complementar em experimento próprio; A/B/C permanecem exploratórios sem homologação de limiar.\n'
        'Predição retrospectiva de origem móvel, horizonte t+1,255 municípios IBGE2025, exclusivamente Col9/1985–2023.2024 reservado.\n'
        'Mantidas as limitações temáticas, referência2023 insuficiente e risco algorítmico retrospectivo. Nenhuma precisão pontual corrige hectares.\n'
        'Não alterar dados/rasters/matrizes/banco/dashboard/DOCX. Diário anterior preservado, SHA256:'+sha(diario_anterior)+'.\n'
        'Este adendo versionado atualiza o registro sem substituir os diários/checkpoints anteriores.\n')
    (docs/'DIARIO_DECISOES_CIENTIFICAS_COL9.md').write_text(diario,encoding='utf-8')
    auditoria={'status':'APTO_PARA_EXPERIMENTO_RETROSPECTIVO_COM_RISCOS_DECLARADOS','chaves':9690,'municipios':255,'atributos_candidatos':53,
        'duplicatas':0,'desfechos_proibidos_em_X':0,'fenomeno_direto_posterior_a_t':0,
        'dependencia_produtor':'Não eliminada por teste de colunas/janelas.50 atributos Col9 sujeitos a informação retrospectiva futura potencial.',
        'T4':{'status':'admitido_somente_como_proxy_de_registros_na_coorte2003','linhas':5100,'NA_anuais':int(f.focos_log1p_registros_ano.isna().sum()),
              'calendario':'UTC conforme fonte; não garante completude instrumental nem ausência de fogo; sem zero imputado'},
        'preservacao_preparacao_arquivos':len(preparado['sha256']),'rasters39_tamanho_mtime_conferem':True,
        'matriz_preparacao_sha256':sha(p/'MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet'),'reconstrucao_R_confere':True,
        'diferenca_max_leitores_CSV':erros_leitor,'tolerancia_conferencia_CSV_absoluta':1e-8,
        'nota_numerica':'Diferenças de representação de poucosULP entre leitores CSV. Valores Parquet preservados sem correção; não é incoerência temática/de chave.'}
    gravar_json(auditoria,raiz/'auditoria/auditoria_pre_treino.json')
    fontes=[p/'MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet',p/'RESPOSTAS_CONTINUAS_COL9.parquet',p/'QUALIDADE_ELEGIBILIDADE_COL9.parquet',
        p/'PARTICOES_TEMPORAIS_COL9.parquet',p/'PARTICOES_LOSO_COL9.parquet',p/'FOLDS_INTERNOS_AVANCO_COL9.parquet',
        PREPARACAO/'complementares/FOCOS_ANUAIS_CANDIDATOS_SEPARADOS.parquet',PREPARACAO/'manifesto_final_preparacao.json']
    protocolo={'id':'regressao_col9_20261112_v4','congelado_UTC':datetime.now(timezone.utc).isoformat(),
        'autorizacao':'Encaminhamento explícito do pesquisador após concordância informada do orientador; execução autorizada nesta conversa.',
        'respostas':{'R_pct':'100C/D, principal, percentual mapeado','C_ha':'área convertida mapeada, experimento próprio, nuncaR×D_realizado'},
        'AB_C':'exploratórios, sem definição/homologação de limiares','periodo_principal':[1985,2023],'2024_utilizado':False,
        'elegibilidade':'D>0,Rfinita[0,100],Q>=99.5; mantém9690. Q só filtra/diagnostica, não é preditor.',
        'blocos':b,'grupos':grupos,'coortes':{'principal':{'ano_t_min':1985,'blocos':['T0','T1','T2','T3']},
            'focos2003':{'ano_t_min':2003,'blocos':['T0','T1','T2','T3','T4']}},
        'contextos':['temporal','MA','MT','PA','RO','TO'],
        'particoes':{'treino':[1985,2013],'embargo':[2014,2018],'validacao':[2015,2017],'teste':[2019,2022],
                     'internos_principal':folds_internos('principal'),'internos_focos2003':folds_internos('focos2003')},
        'regime_principal':'origem_movel: fenômenos até t; lags anteriores dentro do bloco de teste são covariáveis, nunca amostras adicionais para ajuste.',
        'sensibilidade_congelada':'T3 principal, mesmos modelos/hiperparâmetros escolhidos em origem móvel, sem retreino; somente históricos T2/T3 congelados no ano de embargo anterior à avaliação (2014 para validação,2018 para teste). Composição emt permanece atual.',
        'focos':'Dois atributos de registros/meses, não área queimada. Apenas coorte2003; NA preservado e imputação do treino.',
        'ausencias':'SimpleImputer mediana somente treino; coluna totalmente vazia removida da parte de valores; MissingIndicator para todas. Sem interpretar imputação como ausência do fenômeno.',
        'preprocessamento':'FeatureUnion(imputação,indicadores); StandardScaler apenasRidge/ElasticNet; nenhuma seleção supervisionada de colunas.',
        'normalizacao_y':'Média/DP exclusivamente treino de cada ajuste, em identidade oulog1p; inversão antes das métricas; sem correção por precisão cartográfica/smearing.',
        'transformacoes_y':{'R_pct':['identidade'],'C_ha':['identidade','log1p']},
        'baselines':{'media_historica':'média global do treino/contexto','mediana_historica':'mediana global do treino/contexto',
                     'persistencia':'última conversão encerrada emt do arquivoX; fallback mediana do treino se ausente; contextoLOSO não ajusta com UFretida'},
        'grade':GRADE,'ordem_modelos_desempate':ORDEM_MODELOS,
        'criterio_tuning':'MAE original agregado dos folds internos até2013; desempateRMSE,ordem fixa de configuração.',
        'falhas_configuracao':'Não convergência ou previsão não finita invalida configuração somente no desenvolvimento; se nenhuma configuração válida, interromper. Sem ajuste silencioso de limites/iterações após teste.',
        'criterio_melhor_modelo':'menorMAE na validação2015–2017 entre modelosT0–T3 da coorteprincipal; reportar melhor supervisionado e melhor incluindo baselines. Nunca selecionar pelo teste.',
        'refit_final':'Mesma configuração, apenas desenvolvimento até2017 excluindo2014; UFretida excluída emtodos os ajustes.',
        'metricas':['MAE','RMSE','vies=pred-obs','R2_sem_force_finite','fora_limites_fisicos'],
        'restricoes_predicao':'Sem clipping. Extrapolações finitas são reportadas; não finitas interrompem antes deabrirYteste.',
        'faixas_magnitude':'Pontos de corte quartis da resposta no treino inicial de cada contexto/coorte; congelados antesdo teste.',
        'importancias':'Somente vencedores supervisionados principaisR/C na validação,5 permutações de trajetórias municipais dentrodaUF; nãocausal,DPnãoéIC.',
        'teste_uma_passagem':'Selar arquivos; desenvolvimento não lêX/yteste. Gerar todas as predições finais semYteste; marcador exclusivo antesdeabertura finalY. Repetição da avaliação é recusada.',
        'persistencia_segura_tipos_revisados':['numpy.dtype','sklearn.tree._tree.Tree'],'revisao_tecnica':'v1 preservada; apenas compatibilidade de leitura skops. Nenhum ajuste cientifico executado sobv1.','teste_ja_explorado_cientificamente':True,'alegacao_operacional_historica':False,'semente':SEMENTE,'workers_contextos':2,'threads_por_ajuste':1,
        'versoes':{'python':platform.python_version(),**{n:importlib.metadata.version(n) for n in ['numpy','pandas','pyarrow','scikit-learn','xgboost','scipy','matplotlib','skops','geopandas']}},
        'fontes_sha256':{str(f.relative_to(PROJETO)).replace('\\','/'):sha(f) for f in fontes},
        'dados_estagiados_sha256':{p.name:sha(p) for p in (raiz/'dados').glob('*.parquet')},
        'codigo_modelagem_sha256':{f'modelagem/{n}.py':sha(PROJETO/'modelagem'/f'{n}.py') for n in ['protocolo_experimentos_col9_v4','executar_regressao_col9_v4']}}
    gravar_json(protocolo,raiz/'PROTOCOLO_CONGELADO.json')
    gravar_json({'sha256_protocolo':sha(raiz/'PROTOCOLO_CONGELADO.json'),'antes_de_qualquer_ajuste':True,'auditoria_sha256':sha(raiz/'auditoria/auditoria_pre_treino.json')},raiz/'RECIBO_CONGELAMENTO.json')
    texto='# Protocolo experimental congelado —Coleção9\n\nCongelado antes de qualquer ajuste. O JSON é a especificação executável integral, comhashes de código, fontes, partições e ambiente.\n\n'
    texto+='R principal; C complementar independente. Origem móvel; dados retrospectivos não demonstram disponibilidade histórica. Teste2019–2022 será aberto umaúnica vez, sem seleção porseus resultados.2024 não utilizado.\n\n'
    texto+='T0–T3 na coorte1985; T0–T4 na coorte2003, comparações diretas apenas dentrodamessmacoorte. Focos são registros observados, comNA, não hectares ou ausência comprovada de fogo.\n\n'
    texto+='TuningMAE por avanço interno; vencedor porMAE da validação2015–2017; refit até2017 exclui2014. LOSO excluiUFretida dotreinamento, tuning, transformação e calibração. Mediana do treino é imputação computacional, nãoprova de ausência.\n\n'
    texto+='As predições nãoserão truncadas. Importância será avaliada nopedíodo devalidação. Históricos congelados são sensibilidade predefinida sem retuning. Limitações temáticas e algorítmicas permanecem.\n\n'
    texto+='## Configuração integral\n\n'+chr(96)*3+'json\n'+json.dumps(protocolo,ensure_ascii=False,indent=2)+'\n'+chr(96)*3+'\n'
    (docs/'PROTOCOLO_EXPERIMENTAL_CONGELADO_COL9.md').write_text(texto,encoding='utf-8')
    (docs/'RELATORIO_AUDITORIA_PRE_TREINO_COL9.md').write_text('# Auditoria pré-treino\n\n'+json.dumps(auditoria,ensure_ascii=False,indent=2)+'\n\nNão há vazamento direto identificado nas janelas/colunas. Isso não prova independência temporal do produto: filtros retrospectivos podem carregar informação posterior. Fontes, banco, dashboard eDOCX não foram alterados.\n',encoding='utf-8')
    print(json.dumps({'status':'CONGELADO_ANTES_DE_AJUSTES','protocolo_sha256':sha(raiz/'PROTOCOLO_CONGELADO.json'),'tamanhos_blocos':{n:len(v) for n,v in b.items()},'auditoria':auditoria},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--saida',type=Path,required=True);p.add_argument('--docs',type=Path,required=True)
    a=p.parse_args();congelar(a.saida,a.docs)

