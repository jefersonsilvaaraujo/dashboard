"""Interpretação na validação e apresentação das predições imutáveis de teste."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import geopandas as gpd

PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto,gravar_json,mascaras
from modelagem.executar_regressao_col9_v4 import carregar_dev,ler_modelo,prever,grupo_pronto,metricas

plt.rcParams.update({'font.size':10,'figure.dpi':120,'savefig.dpi':180,'axes.spines.top':False,'axes.spines.right':False})
KEY=['coorte','contexto','target','bloco','algoritmo','regime']

def escolher_tabela(d,w,regime='movel'):
    sel=d.coorte.eq(w['coorte'])&d.contexto.eq(w['contexto'])&d.target.eq(w['target'])&d.bloco.eq(w['bloco'])&d.algoritmo.eq(w['algoritmo'])
    if 'regime' in d:sel &= d.regime.eq(regime)
    return d.loc[sel].copy()

def interpretar_validacao(raiz):
    protocolo=carregar_manifesto(raiz)
    if (raiz/'TESTE_INICIADO.json').exists():raise ValueError('Importância/limites visuais devem ser preparados antes do teste.')
    saida=raiz/'interpretacao_pre_teste'
    if saida.exists():raise FileExistsError('Interpretação anterior preservada.')
    saida.mkdir()
    winners=json.loads((raiz/'VENCEDORES_PELA_VALIDACAO.json').read_text(encoding='utf-8'))
    p,d=carregar_dev(str(raiz.resolve()));_,va=mascaras(d)
    v=d.loc[va].copy()
    rng=np.random.default_rng(p['semente'])
    linhas=[];bins={}
    for target in ['R_pct','C_ha']:
        w=next(a for a in winners if a['coorte']=='principal' and a['contexto']=='temporal' and a['target']==target and a['categoria']=='supervisionado')
        pasta=grupo_pronto(raiz/'desenvolvimento/principal/temporal'/target/w['bloco'])
        modelo,meta=ler_modelo(pasta/w['algoritmo']/'inicial')
        cols=meta['features'];x=v[cols].astype(float);y=v[target].to_numpy()
        original=prever(modelo,meta,x);base=metricas(y,original,target)['MAE']
        bins[target]={'limites_quartis_predicao_validacao':np.unique(np.quantile(original,[.25,.5,.75])).tolist(),'modelo':w}
        conjuntos={n:[n] for n in cols}
        conjuntos.update({'GRUPO_'+n:[c for c in cc if c in cols] for n,cc in p['grupos'].items()})
        for nome,cc in conjuntos.items():
            if not cc:continue
            for rep in range(5):
                perm=x.copy()
                for uf,gr in v.groupby('SIGLA_UF'):
                    cds=sorted(gr.CD_MUN.unique());doador=dict(zip(cds,rng.permutation(cds)))
                    lookup=v.loc[gr.index].set_index(['CD_MUN','ano_t'])
                    keys=pd.MultiIndex.from_arrays([gr.CD_MUN.map(doador),gr.ano_t])
                    perm.loc[gr.index,cc]=lookup.reindex(keys)[cc].to_numpy(float)
                perda=metricas(y,prever(modelo,meta,perm),target)['MAE']
                linhas.append({'target':target,'bloco':w['bloco'],'algoritmo':w['algoritmo'],'variavel_ou_grupo':nome,
                    'repeticao':rep,'MAE_original_validacao':base,'incremento_MAE':perda-base})
        print('Importância calculada apenas na validação:',target,w['bloco'],w['algoritmo'],flush=True)
    pd.DataFrame(linhas).to_parquet(saida/'IMPORTANCIAS_REPETICOES_VALIDACAO.parquet',index=False)
    ag=pd.DataFrame(linhas).groupby(['target','bloco','algoritmo','variavel_ou_grupo']).incremento_MAE.agg(['mean','std','min','max']).reset_index()
    ag.to_csv(saida/'IMPORTANCIAS_VALIDACAO.csv',sep=';',index=False)
    gravar_json({'criado_UTC':datetime.now(timezone.utc).isoformat(),'antes_teste':True,'bins_calibracao':bins,
        'permutacao':'Cinco repetições; trajetórias municipais de2015–2017 permutadas dentrodaUF. Sem reajustar modelo ou selecionar atributos; média/DPnãoéIC.',
        'politica_figuras':'Mostrar todas as predições finitas semclipping; faixas visuais abrangem observados/previstos; mapas de média2019–2022 em unidadesoriginais.',
        'sem_uso_yteste':True,'arquivos_sha256':{f.name:sha(f) for f in saida.iterdir() if f.is_file()}},
        saida/'PLANO_INTERPRETACAO_PRE_TESTE.json')

def salvar_figura(fig,p):
    fig.savefig(p,bbox_inches='tight');fig.savefig(p.with_suffix('.svg'),bbox_inches='tight');plt.close(fig)

def apresentar(raiz):
    carregar_manifesto(raiz)
    registro=json.loads((raiz/'TESTE_CONCLUIDO.json').read_text(encoding='utf-8'))
    for n,h in registro['artefatos_sha256'].items():
        if sha(raiz/'teste'/n)!=h:raise ValueError('Resultados de teste alterados.')
    saida=raiz/'apresentacao'
    if saida.exists():raise FileExistsError('Apresentação existente preservada.')
    saida.mkdir();figs=saida/'figuras';figs.mkdir()
    d=pd.read_parquet(raiz/'teste/RESULTADOS_IMUTAVEIS_TESTE.parquet')
    m=pd.read_parquet(raiz/'teste/METRICAS_TESTE_FINAL.parquet')
    va=pd.read_parquet(raiz/'METRICAS_VALIDACAO_CONGELADAS.parquet')
    winners=json.loads((raiz/'VENCEDORES_PELA_VALIDACAO.json').read_text(encoding='utf-8'))
    plano=json.loads((raiz/'interpretacao_pre_teste/PLANO_INTERPRETACAO_PRE_TESTE.json').read_text(encoding='utf-8'))
    manifesto_geo=json.loads((PROJETO/'referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    gpkg=Path(manifesto_geo['base_dados'])/manifesto_geo['territorio']['arquivo']
    if sha(gpkg)!=manifesto_geo['territorio']['sha256']:raise ValueError('Mapa fora da geometria canônica.')
    g=gpd.read_file(gpkg).to_crs(5880);g.CD_MUN=g.CD_MUN.astype(str)
    resumo=[];espaciais=[];cal=[]
    for target in ['R_pct','C_ha']:
        unid='pontos percentuais' if target=='R_pct' else 'hectares'
        imp=pd.read_csv(raiz/'interpretacao_pre_teste/IMPORTANCIAS_VALIDACAO.csv',sep=';')
        imp=imp.loc[imp.target.eq(target)&~imp.variavel_ou_grupo.str.startswith('GRUPO_')].sort_values('mean').tail(15)
        fig,ax=plt.subplots(figsize=(9,max(3,.32*len(imp))))
        ax.barh(imp.variavel_ou_grupo,imp['mean'],xerr=imp['std'],color='#4c78a8')
        ax.axvline(0,color='black',lw=.8)
        ax.set(xlabel='Incremento MAE na validação: '+unid,title='Permutação por trajetórias/UF; barras=DP de5 permutações, nãoIC')
        salvar_figura(fig,figs/f'importancias_validacao_{target}.png')
        sup=next(w for w in winners if w['coorte']=='principal' and w['contexto']=='temporal' and w['target']==target and w['categoria']=='supervisionado')
        melhor=next(w for w in winners if w['coorte']=='principal' and w['contexto']=='temporal' and w['target']==target and w['categoria']=='incluindo_baselines')
        a=escolher_tabela(d,sup)
        r=escolher_tabela(m,sup).iloc[0].to_dict()
        resumo.append({**sup,'categoria_resumo':'melhor_supervisionado_pela_validacao','metricas_teste':r,'melhor_geral_validacao':melhor})
        bas=m.loc[m.coorte.eq('principal')&m.contexto.eq('temporal')&m.target.eq(target)&m.bloco.eq('BASE')&m.regime.eq('movel')]
        pd.concat([escolher_tabela(m,sup),bas]).to_csv(saida/f'VENCEDOR_E_BASELINES_{target}.csv',sep=';',index=False)
        fig,ax=plt.subplots(figsize=(7,6))
        ax.scatter(a.observado,a.previsto,s=15,alpha=.45,c=a.ano_t,cmap='viridis')
        lo=min(a.observado.min(),a.previsto.min());hi=max(a.observado.max(),a.previsto.max())
        ax.plot([lo,hi],[lo,hi],color='black',ls='--',lw=1)
        ax.set(xlabel='Observado: '+unid,ylabel='Previsto: '+unid,title=f'{target} | vencedor por validação: {sup["bloco"]}/{sup["algoritmo"]}')
        salvar_figura(fig,figs/f'observado_previsto_{target}.png')
        fig,axs=plt.subplots(1,2,figsize=(12,4))
        axs[0].scatter(a.previsto,a.erro,s=13,alpha=.4);axs[0].axhline(0,color='black',ls='--')
        axs[0].set(xlabel='Previsto: '+unid,ylabel='Previsto − observado',title='Resíduos na escala original')
        axs[1].hist(a.erro,bins=35,color='#4c78a8');axs[1].set(xlabel='Erro: '+unid,ylabel='Observações',title='Distribuição de erros')
        salvar_figura(fig,figs/f'residuos_{target}.png')
        byano=a.groupby('ano_t')[['observado','previsto']].mean()
        fig,ax=plt.subplots(figsize=(8,4));byano.plot(ax=ax,marker='o')
        ax.set(xlabel='Ano t (desfecho t→t+1)',ylabel=unid,title='Médias anuais das mesmas predições finais');ax.set_xticks(byano.index)
        salvar_figura(fig,figs/f'serie_erros_{target}.png')
        ufs=sorted(a.SIGLA_UF.unique())
        fig,ax=plt.subplots(figsize=(8,4));ax.boxplot([a.loc[a.SIGLA_UF.eq(uf),'erro'] for uf in ufs],tick_labels=ufs)
        ax.axhline(0,color='black',ls='--');ax.set(ylabel='Erro: '+unid,title='Distribuição dos erros porUF')
        salvar_figura(fig,figs/f'erros_estados_{target}.png')
        # Faixas determinadas na validação, sem adaptação ao teste.
        limites=plano['bins_calibracao'][target]['limites_quartis_predicao_validacao']
        a['grupo_calibracao']=np.searchsorted(limites,a.previsto,side='right')+1
        cc=a.groupby('grupo_calibracao').agg(n=('row_id','size'),previsto_medio=('previsto','mean'),observado_medio=('observado','mean')).reset_index()
        cc['target']=target;cal.append(cc)
        fig,ax=plt.subplots(figsize=(6,5));ax.plot(cc.previsto_medio,cc.observado_medio,'o-')
        lo=min(cc.previsto_medio.min(),cc.observado_medio.min());hi=max(cc.previsto_medio.max(),cc.observado_medio.max())
        ax.plot([lo,hi],[lo,hi],'--',color='black');ax.set(xlabel='Previsto médio',ylabel='Observado médio',title='Calibração descritiva: faixas da validação')
        salvar_figura(fig,figs/f'calibracao_{target}.png')
        cols=['CD_MUN','NM_MUN','SIGLA_UF','ano_t','observado','previsto','erro','erro_absoluto','mb_vn_t_ha']
        a.sort_values('erro_absoluto',ascending=False).head(30)[cols].to_csv(saida/f'EXTREMOS_ERRO_{target}.csv',sep=';',index=False)
        mun=a.groupby('CD_MUN')[['observado','previsto','erro']].mean().reset_index()
        mapa=g.merge(mun,on='CD_MUN',how='left',validate='one_to_one')
        vmin=float(min(mun.observado.min(),mun.previsto.min()));vmax=float(max(mun.observado.max(),mun.previsto.max()))
        fig,axs=plt.subplots(1,3,figsize=(15,7))
        for col,ax,tit in zip(['observado','previsto'],axs[:2],['Conversão mapeada observada','Magnitude prevista']):
            mapa.plot(column=col,ax=ax,cmap='YlGnBu',legend=True,vmin=vmin,vmax=vmax,linewidth=.1,edgecolor='#555555')
            ax.set_title(tit);ax.axis('off')
        lim=float(abs(mun.erro).max());mapa.plot(column='erro',ax=axs[2],cmap='RdBu_r',vmin=-lim,vmax=lim,legend=True,linewidth=.1,edgecolor='#555555')
        axs[2].set_title('Erro previsto−observado');axs[2].axis('off')
        fig.suptitle(f'{target}: média municipal2019–2022 | {unid} | mesmos255 polígonos')
        salvar_figura(fig,figs/f'mapas_municipais_{target}.png')
        mun.to_csv(saida/f'MAPAS_DADOS_{target}.csv',sep=';',index=False)
        # Todos os estados; modelo/bloco porUF escolhido sem sua participação.
        junt=[]
        for uf in ['MA','MT','PA','RO','TO']:
            w=next(x for x in winners if x['coorte']=='principal' and x['contexto']==uf and x['target']==target and x['categoria']=='supervisionado')
            r=escolher_tabela(m,w).iloc[0].to_dict()
            nmun=int(d.loc[d.contexto.eq(uf)&d.target.eq(target),'CD_MUN'].nunique())
            espaciais.append({**w,**r,'UF_retida':uf,'municipios':nmun})
            junt.append(escolher_tabela(d,w))
        conjunto=pd.concat(junt,ignore_index=True)
        espacial=conjunto.groupby('CD_MUN')[['observado','previsto','erro']].mean().reset_index()
        gm=g.merge(espacial,on='CD_MUN',validate='one_to_one')
        fig,axs=plt.subplots(1,2,figsize=(11,7))
        gm.plot(column='previsto',ax=axs[0],legend=True,cmap='YlGnBu',linewidth=.1,edgecolor='#555')
        le=float(abs(gm.erro).max());gm.plot(column='erro',ax=axs[1],legend=True,cmap='RdBu_r',vmin=-le,vmax=le,linewidth=.1,edgecolor='#555')
        for ax in axs:ax.axis('off')
        axs[0].set_title('LOSO: magnitude prevista');axs[1].set_title('LOSO: erro')
        fig.suptitle(f'{target} | modelos porUF selecionados na validação externa à UF')
        salvar_figura(fig,figs/f'mapas_LOSO_{target}.png')
        conjunto.to_parquet(saida/f'PREDICOES_LOSO_VENCEDORES_{target}.parquet',index=False)
        resumo[-1]['LOSO_micro']=metricas(conjunto.observado,conjunto.previsto,target,conjunto.mb_vn_t_ha)
    pd.DataFrame(espaciais).to_csv(saida/'VALIDACAO_ESPACIAL_TODOS_ESTADOS.csv',sep=';',index=False)
    pd.concat(cal,ignore_index=True).to_csv(saida/'CALIBRACAO_GRUPOS.csv',sep=';',index=False)
    # Ablações: todos os algoritmos, mesma coorte/contexto e previsões já fixadas.
    m.to_csv(saida/'TODOS_RESULTADOS_TESTE.csv',sep=';',index=False)
    va.to_csv(saida/'TODOS_RESULTADOS_VALIDACAO.csv',sep=';',index=False)
    gravar_json(resumo,saida/'RESUMO_VENCEDORES_E_TESTE.json')
    gravar_json({'resultado_teste_sha256':sha(raiz/'teste/RESULTADOS_IMUTAVEIS_TESTE.parquet'),'sem_novo_ajuste_ou_nova_predicao':True,
        'arquivos_sha256':{str(f.relative_to(saida)):sha(f) for f in saida.rglob('*') if f.is_file()}},saida/'manifesto_apresentacao.json')
    print('Apresentação gerada a partir de predições imutáveis, sem reabrir escolha.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--fase',choices=['validacao','apresentacao'],required=True);a=p.parse_args()
    if a.fase=='validacao':interpretar_validacao(a.checkpoint)
    else:apresentar(a.checkpoint)

