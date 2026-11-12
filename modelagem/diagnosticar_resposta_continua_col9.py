"""Descrição de C/D/R, sem ajuste preditivo, exclusão, truncamento ou seleção."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import csv_novo,sha


def resumir(d):
    r={'n':len(d)}
    for c in ['R_pct','C_ha','D_ha']:
        s=d[c];prefix=c+'_'
        r.update({prefix+'min':s.min(),prefix+'max':s.max(),prefix+'media':s.mean(),
                  prefix+'mediana':s.median(),prefix+'dp':s.std(ddof=1),prefix+'assimetria':s.skew(),
                  prefix+'IQR':s.quantile(.75)-s.quantile(.25),prefix+'MAD_mediana':(s-s.median()).abs().median()})
        r.update({prefix+f'p{int(q*100):02d}':s.quantile(q) for q in [.01,.05,.1,.25,.5,.75,.9,.95,.99]})
    r['taxa_razao_somas_pct']=100*d.C_ha.sum()/d.D_ha.sum() if d.D_ha.sum()>0 else np.nan
    return r


def agrupar(d,chaves):
    out=[]
    for key,a in d.groupby(chaves,observed=True,dropna=False):
        key=key if isinstance(key,tuple) else (key,)
        out.append({**dict(zip(chaves,key)),**resumir(a)})
    return pd.DataFrame(out)


def executar(checkpoint,saida):
    if saida.exists():raise FileExistsError('Preservar diagnósticos anteriores.')
    saida.mkdir(parents=True)
    pasta=checkpoint/'matriz'
    i=pd.read_parquet(pasta/'INDICE_CANONICO_9690_COL9.parquet');r=pd.read_parquet(pasta/'RESPOSTAS_CONTINUAS_COL9.parquet')
    q=pd.read_parquet(pasta/'QUALIDADE_ELEGIBILIDADE_COL9.parquet')
    d=i.merge(r,on=['CD_MUN','ano_t'],validate='one_to_one').merge(q,on=['CD_MUN','ano_t'],validate='one_to_one')
    if len(d)!=9690 or not d.D_ha.gt(0).all() or not d.R_pct.between(0,100).all():raise ValueError('Resposta viola domínio físico.')
    np.testing.assert_allclose(d.R_pct,100*d.C_ha/d.D_ha,rtol=1e-12,atol=1e-10)
    csv_novo(pd.DataFrame([resumir(d)]),saida/'DISTRIBUICAO_GLOBAL_C_D_R.csv')
    csv_novo(agrupar(d,['SIGLA_UF']),saida/'DISTRIBUICAO_POR_ESTADO.csv')
    csv_novo(agrupar(d,['CD_MUN','NM_MUN','SIGLA_UF']),saida/'DISTRIBUICAO_POR_MUNICIPIO.csv')
    csv_novo(agrupar(d,['ano_t','ano_t1']),saida/'DISTRIBUICAO_POR_ANO.csv')
    d['periodo']=pd.cut(d.ano_t,[1984,1989,1999,2009,2019,2022],labels=['1985–1989_5anos','1990–1999_10anos',
        '2000–2009_10anos','2010–2019_10anos','2020–2022_3anos'])
    csv_novo(agrupar(d,['periodo']),saida/'DISTRIBUICAO_PERIODOS.csv')
    d['quintil_D_descritivo']=pd.qcut(d.D_ha,5,labels=['Q1_menor_D','Q2','Q3','Q4','Q5_maior_D'])
    csv_novo(agrupar(d,['quintil_D_descritivo']),saida/'DISTRIBUICAO_ESTOQUE_ELEGIVEL.csv')
    csv_novo(agrupar(d,['SIGLA_UF','quintil_D_descritivo']),saida/'ESTOQUE_POR_ESTADO.csv')
    cols=['CD_MUN','NM_MUN','SIGLA_UF','ano_t','ano_t1','C_ha','D_ha','R_pct','Q_pct']
    for col,nome in [('R_pct','MAIORES_TAXAS'),('C_ha','MAIORES_AREAS'),('D_ha','MENORES_ESTOQUES')]:
        csv_novo(d.sort_values(col,ascending=col=='D_ha').head(30)[cols],saida/(nome+'.csv'))
    ab=d.sort_values(['CD_MUN','ano_t']).copy()
    ab['variacao_entre_taxas_pp']=ab.groupby('CD_MUN').R_pct.diff()
    ab['variacao_entre_areas_convertidas_ha']=ab.groupby('CD_MUN').C_ha.diff()
    ab['variacao_absoluta_taxa']=ab.variacao_entre_taxas_pp.abs()
    csv_novo(ab.sort_values('variacao_absoluta_taxa',ascending=False).head(40)[cols+[
        'variacao_entre_taxas_pp','variacao_entre_areas_convertidas_ha']],saida/'MUDANCAS_ABRUPTAS.csv')
    qualidade=[]
    for corte in [99.5,99.9,99.95]:
        for passa in [False,True]:
            s=d.loc[d.Q_pct.ge(corte).eq(passa)]
            qualidade.append({'Q_min_pct':corte,'passa':passa,**resumir(s)})
    csv_novo(pd.DataFrame(qualidade),saida/'SENSIBILIDADE_QUALIDADE_MASCARA.csv')
    csv_novo(d[['R_pct','C_ha','D_ha']].corr().rename_axis('variavel').reset_index(),saida/'CORRELACOES_PEARSON_DESCRITIVAS.csv')
    csv_novo(d[['R_pct','C_ha','D_ha']].rank().corr().rename_axis('variavel').reset_index(),saida/'CORRELACOES_SPEARMAN_DESCRITIVAS.csv')
    log=np.log1p(d.C_ha)
    csv_novo(pd.DataFrame([{'escala':'log1p(C/1ha), somente diagnóstico',
        'min':log.min(),'max':log.max(),'media':log.mean(),'mediana':log.median(),'dp':log.std(),'assimetria':log.skew(),
        'nenhuma_transformacao_consolidada':True}]),saida/'DIAGNOSTICO_TRANSFORMACAO_LOG1P_C.csv')
    hist=[]
    for var,bins in [('R_pct',[0,.25,.5,1,2,5,10,20,50,100]),('C_ha',[0,25,100,250,1000,5000,25000,125000])]:
        d['faixa_descritiva']=pd.cut(d[var],bins,include_lowest=True)
        for (uf,faixa),s in d.groupby(['SIGLA_UF','faixa_descritiva'],observed=False):
            hist.append({'variavel':var,'SIGLA_UF':uf,'faixa':str(faixa),'n':len(s)})
    csv_novo(pd.DataFrame(hist),saida/'HISTOGRAMAS_POR_ESTADO.csv')
    info={'n':len(d),'nao_ajustou_modelos':True,'nao_selecionou_transformacoes':True,
        'quintis_D':'Somente diagnóstico global; não são limiares de elegibilidade nem atributos aprendidos.',
        'periodos':'Anos t; períodos extremos incompletos identificados; nenhuma observação2024.',
        'exposicao_teste':'Diagnóstico descritivo autorizado de toda a série; não desempenho preditivo. Documentar exposição científica.',
        'codigo_sha256':sha(Path(__file__)),'artefatos_sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}}
    with (saida/'manifesto_diagnostico.json').open('x',encoding='utf-8') as f:json.dump(info,f,ensure_ascii=False,indent=2)
    print(pd.DataFrame([resumir(d)])[['n','R_pct_mediana','R_pct_max','R_pct_assimetria','C_ha_mediana','C_ha_max','C_ha_assimetria','D_ha_min']].to_string(index=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True);a=p.parse_args();executar(a.checkpoint,a.saida)
