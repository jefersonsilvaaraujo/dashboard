"""Subamostra piloto cega, preservando os 120 estratos e a amostra já sorteada."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha,csv_novo

SEMENTE='DefesaMestrado-piloto-20261111-v1'
COLUNAS_CEGAS=['caso','longitude','latitude','ano_t','ano_t1','situacao_referencia']
RESPOSTAS=['avaliador','inicio_utc','fim_utc','minutos_ativos','estado_t','estado_t1',
    'classe_ou_descricao_t','classe_ou_descricao_t1','confianca_t','confianca_t1',
    'fracao_mista_t_pct','fracao_mista_t1_pct','georregistro_adequado',
    'cena_ids_t','cena_ids_t1','evidencias_t','evidencias_t1','limite_temporal_inferior',
    'limite_temporal_superior','conversao_interpretada','confianca_conversao',
    'situacao','motivo_inconclusivo','justificativa','solicita_complemento','observacoes']


def ordem(chave,identificador):
    return hashlib.sha256(f'{SEMENTE}|{chave}|{identificador}'.encode()).hexdigest()


def selecionar(pontos):
    d=pontos[pontos.desenho.eq('probabilistica')].copy()
    if len(d)!=3744 or d.id.duplicated().any() or d.estrato_psu.nunique()!=120:
        raise ValueError('Amostra original não corresponde ao checkpoint aprovado provisoriamente.')
    ranks=[]
    for estrato,g in d.groupby('estrato_psu',sort=True):
        g=g.copy(); g['chave_sorteio']=g.id.map(lambda x:ordem(estrato,x))
        g=g.sort_values(['chave_sorteio','id']).reset_index(drop=True)
        g['ordem_ampliacao_no_estrato']=np.arange(1,len(g)+1)
        g['N_pontos_amostra_pai_no_estrato']=len(g)
        g['pi_subamostra_condicional']=1/len(g)
        ranks.append(g)
    ranking=pd.concat(ranks,ignore_index=True)
    piloto=ranking[ranking.ordem_ampliacao_no_estrato.eq(1)].copy()
    piloto['chave_alias']=piloto.id.map(lambda x:ordem('alias',x))
    piloto=piloto.sort_values('chave_alias').reset_index(drop=True)
    piloto['caso']=[f'P{i:03d}' for i in range(1,len(piloto)+1)]
    return piloto.drop(columns='chave_alias'),ranking


def ficha_cega(piloto,avaliador):
    d=piloto[['caso','longitude','latitude','ano_origem','ano_destino']].rename(
        columns={'ano_origem':'ano_t','ano_destino':'ano_t1'}).copy()
    d['situacao_referencia']='aguarda_catalogacao'
    for c in RESPOSTAS: d[c]=''
    d['avaliador']=avaliador; d['situacao']='nao_iniciado'
    d['ordem_apresentacao']=d.caso.map(lambda x:ordem('ordem_'+avaliador,x))
    d=d.sort_values('ordem_apresentacao').drop(columns='ordem_apresentacao')
    return d.reset_index(drop=True)


def executar(amostra,saida):
    if saida.exists(): raise FileExistsError('Piloto anterior preservado; escolher outro checkpoint.')
    ck=json.loads((amostra/'concluido_amostragem.json').read_text(encoding='utf-8'))
    for nome,h in ck['arquivos_sha256'].items():
        if sha(amostra/nome)!=h: raise ValueError('Amostra original alterada: '+nome)
    p=pd.read_csv(amostra/'pontos_com_contexto_mapeado.csv',sep=';',encoding='utf-8-sig')
    piloto,ranking=selecionar(p)
    saida.mkdir(parents=True); tecnico=saida/'gestao_restrita'; tecnico.mkdir()
    csv_novo(piloto,tecnico/'vinculo_piloto_amostra_original.csv')
    csv_novo(ranking,tecnico/'ordem_ampliacao_predefinida.csv')
    for avaliador in ('A','B'):
        pasta=saida/('avaliador_'+avaliador); pasta.mkdir()
        csv_novo(ficha_cega(piloto,avaliador),pasta/'ficha_independente.csv')
    protocolo={'semente':SEMENTE,'n_pontos':len(piloto),'n_estratos':piloto.estrato_psu.nunique(),
        'desenho':'SRS de um ponto dentro de cada estrato da amostra-pai já realizada; ordenação por hash com semente fixa.',
        'probabilidade_condicional':'1/M_h, sobre a amostra-pai realizada; pesos originais preservados separadamente.',
        'inferencia':'Nenhuma estimativa representativa ou variância será calculada a partir do piloto isolado; não promover produto de probabilidades condicionais a peso final sem derivar desenho multifásico.',
        'ampliacao':'Próxima posição predefinida em todos os estratos de uma rodada; jamais substitui caso indisponível.',
        'exclusao_2024':True,'sem_rotulos_homologados':True,'sem_treinamento':True,
        'amostra_pai_sha256':sha(amostra/'concluido_amostragem.json'),'codigo_sha256':sha(Path(__file__)),
        'composicao_tecnica':{'subestratos_pixels':piloto.estrato_pixel.value_counts().to_dict(),
            'periodos':piloto.estrato_psu.str.split('|').str[1].value_counts().to_dict(),
            'UF':piloto.estrato_psu.str.split('|').str[0].value_counts().to_dict()}}
    with (tecnico/'protocolo_selecao.json').open('x',encoding='utf-8') as f:
        json.dump(protocolo,f,ensure_ascii=False,indent=2)
    print(json.dumps(protocolo,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--amostra',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.amostra,a.saida)
