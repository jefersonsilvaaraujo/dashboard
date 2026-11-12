"""Especificação executável de chaves/disponibilidade/divisões. Não monta X nem Y, não treina."""
import argparse
import json
from pathlib import Path
import sys

import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import csv_novo,sha

PROIBIDOS={'C_ha','D_ha','R_pct','Q_pct','area_convertida_ha','taxa_conversao_pct',
            'elegibilidade_vn_pct','pixels_comuns','candidato','classe_t1','alvo_prodes','Y'}


def verificar_disponibilidade(nome,corte,referencia_fim,publicado_em,dependencia_fim):
    motivos=[]
    if nome in PROIBIDOS or nome.startswith('alvo_'): motivos.append('variavel_do_desfecho_ou_qualidade_futura')
    def instante(v):
        t=pd.Timestamp(v)
        return (t.tz_localize('America/Sao_Paulo') if t.tzinfo is None else t).tz_convert('UTC')
    limite=instante(corte)
    for campo,valor in [('referencia_fim',referencia_fim),('publicado_em',publicado_em),('dependencia_fim',dependencia_fim)]:
        if valor is None or pd.isna(valor): motivos.append(campo+'_desconhecido')
        elif instante(valor)>limite: motivos.append(campo+'_posterior_ao_corte')
    return motivos


def indice(municipios):
    codigos=sorted(set(int(c) for c in municipios))
    if len(codigos)!=255: raise ValueError('O contrato exige exatamente os 255 municípios aprovados.')
    d=pd.MultiIndex.from_product([codigos,range(1985,2024)],names=['CD_MUN','ano_t']).to_frame(index=False)
    d['ano_desfecho']=pd.array(d.ano_t+1,dtype='Int64')
    d.loc[d.ano_t.eq(2023),'ano_desfecho']=pd.NA
    d['situacao_desfecho']=d.ano_t.map(lambda t:'nao_observado_col9' if t==2023 else 'transicao_mapeada_aguarda_validacao')
    d['corte_previsao']=d.ano_t.astype(str)+'-12-31T23:59:59-03:00'
    return d


def divisao_temporal(anos):
    a=pd.Series(anos)
    r=pd.Series('embargo',index=a.index)
    r.loc[a.le(2013)]='treino'
    r.loc[a.between(2015,2017)]='validacao'
    r.loc[a.between(2019,2022)]='teste_reservado'
    r.loc[a.ge(2023)]='sem_desfecho_observado'
    return r


def divisao_loso(d,uf):
    r=divisao_temporal(d.ano_t)
    teste=d.SIGLA_UF.eq(uf)&d.ano_t.between(2019,2022)
    r.loc[d.SIGLA_UF.eq(uf)]='estado_retido_fora_desenvolvimento'
    r.loc[~d.SIGLA_UF.eq(uf)&d.ano_t.ge(2019)]='fora_teste_deste_fold'
    r.loc[teste]='teste_estado_retido'
    r.loc[d.ano_t.ge(2023)]='sem_desfecho_observado'
    return r


def executar(resultados,saida):
    if saida.exists(): raise FileExistsError('Especificação anterior preservada.')
    q=pd.read_csv(resultados/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    cadastro=q[['CD_MUN','NM_MUN','SIGLA_UF']].drop_duplicates()
    if cadastro.CD_MUN.duplicated().any(): raise ValueError('Cadastro divergente.')
    d=indice(cadastro.CD_MUN).merge(cadastro,on='CD_MUN',validate='many_to_one')
    saida.mkdir(parents=True)
    csv_novo(d,saida/'indice_255_1985_2023_sem_rotulos.csv')
    d['divisao']=divisao_temporal(d.ano_t)
    csv_novo(d,saida/'divisao_temporal_proposta.csv')
    folds=[]
    for uf in sorted(d.SIGLA_UF.unique()):
        f=d.copy(); f['UF_retida']=uf; f['divisao']=divisao_loso(f,uf); folds.append(f)
    csv_novo(pd.concat(folds,ignore_index=True),saida/'divisoes_loso_propostas.csv')
    fontes=[]
    for nome,arquivo,colano in [('focos','historico/focos_municipio_mensal.csv','ano'),
                               ('prodes','historico/prodes_area_classe_municipio.csv','ano'),
                               ('painel_legado','historico/painel_municipio_ano.csv','ano')]:
        p=PROJETO/arquivo; a=pd.read_csv(p,sep=';',encoding='utf-8-sig')
        codigo='CD_MUN' if 'CD_MUN' in a else 'cd_mun'
        origem=set(a[codigo].dropna().astype(int)); aprovados=set(cadastro.CD_MUN.astype(int))
        fontes.append({'fonte':nome,'arquivo':arquivo,'sha256':sha(p),'linhas':len(a),
            'municipios_total':len(origem),'intersecao_255':len(origem&aprovados),
            'ausentes_255':sorted(aprovados-origem),'ano_min':int(a[colano].min()),'ano_max':int(a[colano].max()),
            'colunas':list(a.columns),'status':'somente inventário; geometria/data/vintage não habilitados como X'})
    (saida/'inventario_fontes_locais.json').write_text(json.dumps(fontes,ensure_ascii=False,indent=2),encoding='utf-8')
    resumo={'linhas_indice':len(d),'pares_com_transicao_mapeada':int(d.ano_t.le(2022).sum()),
        'linhas_2023_sem_desfecho':int(d.ano_t.eq(2023).sum()),'sem_coluna_Y':True,'sem_treinamento':True,
        'proposta_folds_internos':[{'treino_ate':2001,'validacao':[2003,2005]},
                                 {'treino_ate':2005,'validacao':[2007,2009]},
                                 {'treino_ate':2009,'validacao':[2011,2013]}],
        'codigo_sha256':sha(Path(__file__)),
        'arquivos_sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}}
    (saida/'manifesto.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in resumo.items() if k!='arquivos_sha256'},indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--resultados',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.resultados,a.saida)
