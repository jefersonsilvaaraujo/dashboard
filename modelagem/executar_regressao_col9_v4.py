"""Ajustes no desenvolvimento e uma única avaliação selada; sem banco/dashboard."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid
import warnings
from zipfile import ZIP_DEFLATED

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.impute import SimpleImputer,MissingIndicator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge,ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
import skops.io as sio
from xgboost import XGBRegressor
from threadpoolctl import threadpool_limits

PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto,mascaras,folds_internos,gravar_json,ALGORITMOS,ORDEM_MODELOS

def metricas(y,p,target,limite_area=None):
    y=np.asarray(y,float);p=np.asarray(p,float)
    if y.shape!=p.shape or not np.isfinite(y).all() or not np.isfinite(p).all():raise ValueError('Predição/resposta não finita ou dimensões distintas.')
    e=p-y;sst=float(np.sum((y-y.mean())**2)) if len(y) else 0.
    r={'n':len(y),'MAE':float(np.mean(abs(e))) if len(y) else None,'RMSE':float(np.sqrt(np.mean(e*e))) if len(y) else None,
       'vies':float(np.mean(e)) if len(y) else None,'R2':float(1-np.sum(e*e)/sst) if sst>0 else None,
       'pred_min':float(p.min()) if len(y) else None,'pred_max':float(p.max()) if len(y) else None,
       'n_pred_negativas':int((p<0).sum()),'n_pred_acima_limite':int((p>100).sum()) if target=='R_pct' else
            (int((p>np.asarray(limite_area)).sum()) if limite_area is not None else None)}
    return r

def construir_pipeline(alg,params,seed):
    pre=FeatureUnion([
        ('valores',SimpleImputer(strategy='median',keep_empty_features=False)),
        ('ausencia',MissingIndicator(features='all'))])
    if alg=='ridge':est=Ridge(**params,solver='lsqr',tol=1e-6)
    elif alg=='elastic_net':est=ElasticNet(**params,max_iter=20000,tol=1e-3,selection='cyclic',random_state=seed)
    elif alg=='random_forest':est=RandomForestRegressor(**params,random_state=seed,n_jobs=1)
    elif alg=='xgboost':est=XGBRegressor(**params,objective='reg:squarederror',tree_method='hist',random_state=seed,n_jobs=1,verbosity=0)
    else:raise ValueError('Algoritmo não congelado.')
    etapas=[('pre',pre)]
    if alg in ['ridge','elastic_net']:etapas.append(('escala',StandardScaler()))
    return Pipeline(etapas+[('modelo',est)])

def ajustar(alg,params,transform,x,y,seed):
    v=np.asarray(y,float)
    if transform=='log1p':
        if (v<0).any():raise ValueError('log1p não autorizado para resposta negativa.')
        v=np.log1p(v)
    centro=float(v.mean());escala=float(v.std(ddof=0))
    if escala==0:escala=1.
    pipe=construir_pipeline(alg,params,seed)
    with threadpool_limits(limits=1),warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always');pipe.fit(x,(v-centro)/escala)
    converg=[str(a.message) for a in w if issubclass(a.category,ConvergenceWarning)]
    if converg:raise RuntimeError('Não convergiu no limite congelado:'+converg[0])
    avisos=[{'tipo':a.category.__name__,'mensagem':str(a.message)} for a in w]
    return pipe,{'centro':centro,'escala':escala,'transformacao':transform,'avisos':avisos}

def prever(pipe,meta,x):
    with threadpool_limits(limits=1):
        p=np.asarray(pipe.predict(x),float)*meta['escala']+meta['centro']
    if meta['transformacao']=='log1p':
        with np.errstate(over='raise',invalid='raise'):p=np.expm1(p)
    if not np.isfinite(p).all():raise ValueError('Predição não finita: interromper, não truncar.')
    return p

def salvar_modelo(pipe,meta,pasta,alg):
    pasta.mkdir(parents=True,exist_ok=False)
    if alg=='xgboost':
        sio.dump(pipe[:-1],pasta/'preprocessamento.skops',compression=ZIP_DEFLATED)
        pipe[-1].save_model(pasta/'modelo_xgboost.json')
        arquivos=['preprocessamento.skops','modelo_xgboost.json']
    else:
        sio.dump(pipe,pasta/'pipeline.skops',compression=ZIP_DEFLATED);arquivos=['pipeline.skops']
    desconhecidos={n:sio.get_untrusted_types(file=pasta/n) for n in arquivos if n.endswith('.skops')}
    gravar_json({**meta,'algoritmo':alg,'arquivos_sha256':{n:sha(pasta/n) for n in arquivos},
        'tipos_requerem_revisao_skops':desconhecidos,
        'persistencia':'Sem pickle/joblib. skops para sklearn; JSONnativoXGBoost. Não carregar tipos desconhecidos automaticamente.'},pasta/'modelo.json')

def ler_modelo(pasta):
    m=json.loads((pasta/'modelo.json').read_text(encoding='utf-8'))
    for n,h in m['arquivos_sha256'].items():
        if sha(pasta/n)!=h:raise ValueError('Modelo diverge do hash.')
    if m['algoritmo'] in ['media_historica','mediana_historica','persistencia']:return None,m
    for n,tipos in m['tipos_requerem_revisao_skops'].items():
        if set(tipos)-{'numpy.dtype','sklearn.tree._tree.Tree'}:raise ValueError('Modelo requer revisão explícita dos tipos:'+str(tipos))
    if m['algoritmo']=='xgboost':
        pre=sio.load(pasta/'preprocessamento.skops',trusted=['numpy.dtype','sklearn.tree._tree.Tree'])
        est=XGBRegressor();est.load_model(pasta/'modelo_xgboost.json')
        return Pipeline(list(pre.steps)+[('modelo',est)]),m
    return sio.load(pasta/'pipeline.skops',trusted=['numpy.dtype','sklearn.tree._tree.Tree']),m

@lru_cache(maxsize=2)
def carregar_dev(raizstr):
    raiz=Path(raizstr);p=carregar_manifesto(raiz)
    # Nenhum caminho teste é lido aqui.
    x=pd.read_parquet(raiz/'dados/X_desenvolvimento.parquet')
    y=pd.read_parquet(raiz/'dados/y_desenvolvimento.parquet')
    d=x.merge(y[['row_id','R_pct','C_ha']],on='row_id',how='left',validate='one_to_one')
    return p,d

def congelar_historicos(avaliacao,completa,ano_corte,colunas):
    out=avaliacao.copy()
    ref=completa.loc[completa.ano_t.eq(ano_corte),['CD_MUN']+colunas].set_index('CD_MUN')
    if ref.index.duplicated().any():raise ValueError('Histórico congelado ambíguo.')
    for c in colunas:out[c]=out.CD_MUN.map(ref[c])
    return out

def baseline_prever(meta,x,target):
    if meta['algoritmo']=='media_historica':return np.full(len(x),meta['media'])
    if meta['algoritmo']=='mediana_historica':return np.full(len(x),meta['mediana'])
    col='mb_taxa_passada_pct' if target=='R_pct' else 'mb_conv_passada_ha'
    return x[col].fillna(meta['mediana']).to_numpy(float)

def info_spec(coorte,contexto,target,bloco,alg,pasta,meta):
    return {'coorte':coorte,'contexto':contexto,'target':target,'bloco':bloco,'algoritmo':alg,
        'modelo_dir':str(pasta.relative_to(PROJETO)).replace('\\','/'),'meta':meta}

def desenvolver_grupo(tarefa):
    raizstr,coorte,contexto,target,bloco=tarefa;raiz=Path(raizstr);p,d=carregar_dev(raizstr)
    grupo=raiz/'desenvolvimento'/coorte/contexto/target/bloco
    pronto=grupo/'concluido.json'
    if pronto.exists():
        ck=json.loads(pronto.read_text(encoding='utf-8'))
        for n,h in ck['artefatos'].items():
            if sha(grupo/n)!=h:raise ValueError('Checkpoint de desenvolvimento alterado.')
        return {'grupo':str(grupo.relative_to(raiz)),'retomado':True}
    tentativa=grupo/'tentativas'/uuid.uuid4().hex[:10];tentativa.mkdir(parents=True)
    uf=None if contexto=='temporal' else contexto;minimo=p['coortes'][coorte]['ano_t_min']
    cols=p['blocos'][bloco];xx=d[cols].astype(float)
    tr,va=mascaras(d,uf,minimo=minimo)
    if not tr.any() or not va.any():raise ValueError('Partição vazia.')
    y=d[target].to_numpy(float);yy=y[tr]
    ids=d.loc[tr,'row_id'].to_numpy()
    if uf and d.loc[tr|va,'SIGLA_UF'].eq(uf).any():raise ValueError('UFretida no desenvolvimento.')
    cortes=np.quantile(yy,[.25,.5,.75]).tolist()
    base={'coorte':coorte,'contexto':contexto,'target':target,'bloco':bloco,'features':cols,
        'n_treino_inicial':int(tr.sum()),'n_validacao':int(va.sum()),'UF_excluida':uf,
        'cortes_magnitude_treino':cortes,'row_ids_treino_sha256':hashlib.sha256(ids.tobytes()).hexdigest()}
    cvlinhas=[];preds=[];especs=[];validacoes=[]
    if bloco=='T0':
        refit=d.ano_t.between(minimo,2017)&d.ano_t.ne(2014)
        if uf:refit &= d.SIGLA_UF.ne(uf)
        med=float(np.median(y[refit]));media=float(np.mean(y[refit]))
        for alg in ['media_historica','mediana_historica','persistencia']:
            ini={**base,'bloco':'BASE','algoritmo':alg,'media':float(yy.mean()),'mediana':float(np.median(yy))}
            pv=baseline_prever(ini,d.loc[va],target)
            v={**{k:ini[k] for k in ['coorte','contexto','target','bloco','algoritmo']},'regime':'movel',**metricas(y[va],pv,target,d.loc[va,'mb_vn_t_ha'])}
            validacoes.append(v)
            tab=d.loc[va,['row_id','CD_MUN','SIGLA_UF','ano_t']].copy();tab['observado']=y[va];tab['previsto']=pv
            for k in ['coorte','contexto','target','bloco','algoritmo']:tab[k]=ini[k]
            tab['regime']='movel';preds.append(tab)
            for j,(fim,a,b) in enumerate(folds_internos(coorte)):
                ti,vi=mascaras(d,uf,fim,a,b,minimo)
                bm={**ini,'media':float(y[ti].mean()),'mediana':float(np.median(y[ti]))}
                vv=baseline_prever(bm,d.loc[vi],target)
                cvlinhas.append({**{k:ini[k] for k in ['coorte','contexto','target','bloco','algoritmo']},'config':-1,'fold':j,
                    'transformacao':'identidade','parametros':'{}','valida':True,**metricas(y[vi],vv,target)})
            dest=tentativa/alg/'final';dest.mkdir(parents=True)
            final={**ini,'media':media,'mediana':med,'n_treino_final':int(refit.sum()),
                   'treino_final_ate':2017,'refit_exclui2014':True,'arquivos_sha256':{},'tipos_requerem_revisao_skops':{}}
            gravar_json(final,dest/'modelo.json');especs.append(info_spec(coorte,contexto,target,'BASE',alg,dest,final))
            if coorte=='principal' and alg=='persistencia':
                hist=p['grupos']['historico_estoques']+p['grupos']['historico_conversoes']
                vf=congelar_historicos(d.loc[va],d,2014,hist)
                pp=baseline_prever(ini,vf,target)
                validacoes.append({**{k:ini[k] for k in ['coorte','contexto','target','bloco','algoritmo']},'regime':'congelado',**metricas(y[va],pp,target)})
    for alg in ALGORITMOS:
        melhor=None;melhor_chave=None
        modos=p['transformacoes_y'][target];numero=0
        for modo in modos:
            for params in p['grade'][alg]:
                erros=[];quad=[];valid=True
                for j,(fim,a,b) in enumerate(folds_internos(coorte)):
                    ti,vi=mascaras(d,uf,fim,a,b,minimo)
                    try:
                        pi,mi=ajustar(alg,params,modo,xx.loc[ti],y[ti],p['semente'])
                        yp=prever(pi,mi,xx.loc[vi])
                        met=metricas(y[vi],yp,target);erros.extend(abs(yp-y[vi]));quad.extend((yp-y[vi])**2)
                        cvlinhas.append({**{k:base[k] for k in ['coorte','contexto','target','bloco']},'algoritmo':alg,
                            'config':numero,'fold':j,'transformacao':modo,'parametros':json.dumps(params,sort_keys=True),'valida':True,**met})
                    except (ValueError,RuntimeError,FloatingPointError) as exc:
                        valid=False
                        cvlinhas.append({**{k:base[k] for k in ['coorte','contexto','target','bloco']},'algoritmo':alg,'config':numero,
                            'fold':j,'transformacao':modo,'parametros':json.dumps(params,sort_keys=True),'valida':False,'erro':str(exc)})
                        break
                if valid:
                    chave=(float(np.mean(erros)),float(np.sqrt(np.mean(quad))),numero)
                    if melhor_chave is None or chave<melhor_chave:melhor_chave=chave;melhor=(params,modo,numero)
                numero+=1
        if melhor is None:raise RuntimeError('Nenhuma configuração válida para'+alg)
        params,modo,num=melhor
        pi,mi=ajustar(alg,params,modo,xx.loc[tr],y[tr],p['semente'])
        vp=prever(pi,mi,xx.loc[va])
        meta={**base,**mi,'algoritmo':alg,'parametros':params,'config':num,'MAE_CV':melhor_chave[0],'RMSE_CV':melhor_chave[1],
            'n_colunas_entrada':len(cols),'colunas_totalmente_ausentes_treino':[c for c in cols if xx.loc[tr,c].isna().all()]}
        validacoes.append({**{k:meta[k] for k in ['coorte','contexto','target','bloco','algoritmo']},'regime':'movel',
            'config':num,'transformacao':modo,'parametros':json.dumps(params,sort_keys=True),**metricas(y[va],vp,target,d.loc[va,'mb_vn_t_ha'])})
        tab=d.loc[va,['row_id','CD_MUN','SIGLA_UF','ano_t']].copy();tab['observado']=y[va];tab['previsto']=vp
        for k in ['coorte','contexto','target','bloco','algoritmo']:tab[k]=meta[k]
        tab['regime']='movel';preds.append(tab)
        if contexto=='temporal':
            salvar_modelo(pi,meta,tentativa/alg/'inicial',alg)
        if coorte=='principal' and bloco=='T3':
            hist=p['grupos']['historico_estoques']+p['grupos']['historico_conversoes']
            vf=congelar_historicos(d.loc[va],d,2014,hist)
            pp=prever(pi,mi,vf[cols].astype(float))
            validacoes.append({**{k:meta[k] for k in ['coorte','contexto','target','bloco','algoritmo']},'regime':'congelado',**metricas(y[va],pp,target)})
        refit=d.ano_t.between(minimo,2017)&d.ano_t.ne(2014)
        if uf:refit &= d.SIGLA_UF.ne(uf)
        pf,mf=ajustar(alg,params,modo,xx.loc[refit],y[refit],p['semente'])
        final={**meta,**mf,'n_treino_final':int(refit.sum()),'treino_final_ate':2017,'refit_exclui2014':True}
        dest=tentativa/alg/'final';salvar_modelo(pf,final,dest,alg)
        # Round-trip usa apenas validação, nunca o teste.
        resto,mr=ler_modelo(dest)
        np.testing.assert_allclose(prever(pf,mf,xx.loc[va].head(5)),prever(resto,mr,xx.loc[va].head(5)),rtol=1e-6,atol=1e-6)
        especs.append(info_spec(coorte,contexto,target,bloco,alg,dest,final))
    pd.DataFrame(cvlinhas).to_parquet(tentativa/'CV.parquet',index=False)
    pd.DataFrame(validacoes).to_parquet(tentativa/'validacao_metricas.parquet',index=False)
    pd.concat(preds,ignore_index=True).to_parquet(tentativa/'validacao_predicoes.parquet',index=False)
    gravar_json(especs,tentativa/'especificacoes_modelos.json')
    ck={'tentativa':str(tentativa.relative_to(grupo)),'protocolo_sha256':sha(raiz/'PROTOCOLO_CONGELADO.json'),
        'artefatos':{str(f.relative_to(grupo)):sha(f) for f in tentativa.rglob('*') if f.is_file()}}
    gravar_json(ck,pronto)
    return {'grupo':str(grupo.relative_to(raiz)),'retomado':False,'modelos_finais':len(especs)}

def grupo_pronto(grupo):
    ck=json.loads((grupo/'concluido.json').read_text(encoding='utf-8'));p=grupo/ck['tentativa']
    for n,h in ck['artefatos'].items():
        if sha(grupo/n)!=h:raise ValueError('Checkpoint de desenvolvimento não íntegro.')
    return p

def desenvolver(raiz):
    p=carregar_manifesto(raiz);concluido=raiz/'DESENVOLVIMENTO_CONCLUIDO.json'
    if concluido.exists():raise FileExistsError('Desenvolvimento fechado: reutilizar artefatos, não ajustar novamente.')
    tarefas=[(str(raiz.resolve()),c,ctx,t,b) for t in ['R_pct','C_ha'] for c,co in p['coortes'].items()
        for ctx in p['contextos'] for b in co['blocos']]
    inicio=time.monotonic()
    with ProcessPoolExecutor(max_workers=p['workers_contextos']) as pool:
        fs={pool.submit(desenvolver_grupo,t):t for t in tarefas}
        for j,f in enumerate(as_completed(fs),1):
            retorno=f.result();print(f'Desenvolvimento {j}/{len(tarefas)} {json.dumps(retorno,ensure_ascii=False)}',flush=True)
    specs=[];valid=[];cv=[]
    for co,meta in p['coortes'].items():
        for ctx in p['contextos']:
            for target in ['R_pct','C_ha']:
                for b in meta['blocos']:
                    pasta=grupo_pronto(raiz/'desenvolvimento'/co/ctx/target/b)
                    specs+=json.loads((pasta/'especificacoes_modelos.json').read_text(encoding='utf-8'))
                    valid.append(pd.read_parquet(pasta/'validacao_metricas.parquet'));cv.append(pd.read_parquet(pasta/'CV.parquet'))
    vd=pd.concat(valid,ignore_index=True);vdc=pd.concat(cv,ignore_index=True)
    vd.to_parquet(raiz/'METRICAS_VALIDACAO_CONGELADAS.parquet',index=False)
    vdc.to_parquet(raiz/'AJUSTES_CV_DESENVOLVIMENTO.parquet',index=False)
    gravar_json(specs,raiz/'MODELOS_PARA_TESTE.json')
    vencedores=[]
    vd['ordem_algoritmo']=vd.algoritmo.map({n:i for i,n in enumerate(ORDEM_MODELOS)})
    vd['ordem_bloco']=vd.bloco.map({'BASE':0,'T0':1,'T1':2,'T2':3,'T3':4,'T4':5})
    for (co,ctx,target),v in vd.loc[vd.regime.eq('movel')].groupby(['coorte','contexto','target']):
        for categoria,conjunto in [('incluindo_baselines',v),('supervisionado',v.loc[v.algoritmo.isin(ALGORITMOS)])]:
            w=conjunto.sort_values(['MAE','RMSE','ordem_algoritmo','ordem_bloco']).iloc[0]
            vencedores.append({'coorte':co,'contexto':ctx,'target':target,'categoria':categoria,
                'bloco':w.bloco,'algoritmo':w.algoritmo,'MAE_validacao':float(w.MAE),'RMSE_validacao':float(w.RMSE)})
    gravar_json(vencedores,raiz/'VENCEDORES_PELA_VALIDACAO.json')
    registro={'protocolo_sha256':sha(raiz/'PROTOCOLO_CONGELADO.json'),'grupos':len(tarefas),'modelos_finais':len(specs),
        'tempo_segundos':time.monotonic()-inicio,'escolhas_definidas_antes_teste':True,
        'artefatos_sha256':{n:sha(raiz/n) for n in ['METRICAS_VALIDACAO_CONGELADAS.parquet','AJUSTES_CV_DESENVOLVIMENTO.parquet','MODELOS_PARA_TESTE.json','VENCEDORES_PELA_VALIDACAO.json']}}
    gravar_json(registro,concluido)
    print(json.dumps(registro,ensure_ascii=False,indent=2),flush=True)

def avaliar_teste_uma_vez(raiz):
    p=carregar_manifesto(raiz)
    if (raiz/'TESTE_INICIADO.json').exists():raise FileExistsError('Teste já iniciado: nenhuma nova passagem é autorizada por este comando.')
    dev=json.loads((raiz/'DESENVOLVIMENTO_CONCLUIDO.json').read_text(encoding='utf-8'))
    for n,h in dev['artefatos_sha256'].items():
        if sha(raiz/n)!=h:raise ValueError('Escolhas do desenvolvimento foram modificadas.')
    for n,h in p['dados_estagiados_sha256'].items():
        if sha(raiz/'dados'/n)!=h:raise ValueError('Dados selados alterados.')
    # Predições de todos os protocolos são fixadas ANTES de abrir respostas.
    gravar_json({'inicio_UTC':datetime.now(timezone.utc).isoformat(),'protocolo_sha256':sha(raiz/'PROTOCOLO_CONGELADO.json'),
        'vencedores_sha256':sha(raiz/'VENCEDORES_PELA_VALIDACAO.json'),'nova_passagem_proibida':True},raiz/'TESTE_INICIADO.json')
    specs=json.loads((raiz/'MODELOS_PARA_TESTE.json').read_text(encoding='utf-8'))
    xt=pd.read_parquet(raiz/'dados/X_teste_selado.parquet')
    xd=pd.read_parquet(raiz/'dados/X_desenvolvimento.parquet')
    pasta=raiz/'teste';pasta.mkdir();todos=[]
    hist=p['grupos']['historico_estoques']+p['grupos']['historico_conversoes']
    for j,s in enumerate(specs,1):
        ctx=s['contexto'];a=xt.loc[xt.SIGLA_UF.eq(ctx)] if ctx!='temporal' else xt
        if not a.ano_t.between(2019,2022).all():raise ValueError('Período de teste indevido.')
        modelo,meta=ler_modelo(PROJETO/s['modelo_dir'])
        regimes=['movel']
        if s['coorte']=='principal' and (s['bloco']=='T3' or s['algoritmo']=='persistencia'):regimes+=['congelado']
        for regime in regimes:
            z=congelar_historicos(a,xd,2018,hist) if regime=='congelado' else a
            if modelo is None:yp=baseline_prever(meta,z,s['target'])
            else:yp=prever(modelo,meta,z[meta['features']].astype(float))
            if not np.isfinite(yp).all():raise ValueError('Interromper antes de ler yteste.')
            out=a[['row_id','CD_MUN','NM_MUN','SIGLA_UF','ano_t','mb_vn_t_ha']].copy();out['previsto']=yp
            for k in ['coorte','contexto','target','bloco','algoritmo']:out[k]=s[k]
            out['regime']=regime;todos.append(out)
        if j%30==0:print(f'Teste: predições congeladas semY {j}/{len(specs)}',flush=True)
    pred=pd.concat(todos,ignore_index=True)
    pred.to_parquet(pasta/'PREDICOES_ANTES_ABRIR_Y.parquet',index=False)
    gravar_json({'abertura_UTC':datetime.now(timezone.utc).isoformat(),'predicoes_sha256':sha(pasta/'PREDICOES_ANTES_ABRIR_Y.parquet'),
                 'uma_passagem':True},raiz/'ABERTURA_UNICA_Y_TESTE.json')
    yy=pd.read_parquet(raiz/'dados/y_teste_selado.parquet')
    long=yy.melt(id_vars=['row_id'],value_vars=['R_pct','C_ha'],var_name='target',value_name='observado')
    out=pred.merge(long,on=['row_id','target'],how='left',validate='many_to_one')
    if out.observado.isna().any():raise ValueError('Chaves de resposta não isoladas corretamente.')
    out['erro']=out.previsto-out.observado;out['erro_absoluto']=abs(out.erro)
    out.to_parquet(pasta/'RESULTADOS_IMUTAVEIS_TESTE.parquet',index=False)
    ch=['coorte','contexto','target','bloco','algoritmo','regime']
    metric=[]
    for key,g in out.groupby(ch):
        metric.append({**dict(zip(ch,key)),**metricas(g.observado,g.previsto,key[2],g.mb_vn_t_ha)})
    pd.DataFrame(metric).to_parquet(pasta/'METRICAS_TESTE_FINAL.parquet',index=False)
    # Resumos são calculados das mesmas predições, não novas execuções de modelos.
    for nome,extra in [('ESTADO',['SIGLA_UF']),('ANO',['ano_t'])]:
        linhas=[]
        for key,g in out.groupby(ch+extra):
            linhas.append({**dict(zip(ch+extra,key)),**metricas(g.observado,g.previsto,key[2],g.mb_vn_t_ha)})
        pd.DataFrame(linhas).to_parquet(pasta/f'METRICAS_TESTE_POR_{nome}.parquet',index=False)
    bins={}
    for s in specs:
        k='|'.join([s['coorte'],s['contexto'],s['target']]);bins[k]=s['meta']['cortes_magnitude_treino']
    faixas=[]
    for key,g in out.groupby(ch):
        k='|'.join(key[:3]);cortes=bins[k]
        faixa=np.searchsorted(cortes,g.observado.to_numpy(),side='right')+1
        for f in range(1,5):
            a=g.loc[faixa==f]
            if len(a):faixas.append({**dict(zip(ch,key)),'faixa_treino_quartil':f,**metricas(a.observado,a.previsto,key[2],a.mb_vn_t_ha)})
    pd.DataFrame(faixas).to_parquet(pasta/'METRICAS_POR_MAGNITUDE.parquet',index=False)
    gravar_json({'fim_UTC':datetime.now(timezone.utc).isoformat(),'avaliacoes_finais':1,'sem_novo_ajuste':True,
        'modelos_arquivos':len(specs),'linhas_predicoes':len(out),'novas_escolhas_permitidas':False,
        'artefatos_sha256':{f.name:sha(f) for f in pasta.iterdir() if f.is_file()}},raiz/'TESTE_CONCLUIDO.json')
    print('Teste final único concluído. Nenhuma escolha alterada apósYteste.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--fase',choices=['desenvolvimento','teste'],required=True);a=p.parse_args()
    if a.fase=='desenvolvimento':desenvolver(a.checkpoint)
    else:avaliar_teste_uma_vez(a.checkpoint)

