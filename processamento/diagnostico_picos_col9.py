"""Decompõe picos por UF/código e por município prioritário, sem atribuição causal."""
import argparse
from pathlib import Path
import sys
import json

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import VN,UA,csv_novo,sha


def executar(resultados,limiares,amostra,saida):
    if saida.exists(): raise FileExistsError('Diagnóstico anterior preservado.')
    q=pd.read_csv(resultados/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    uf=q[['CD_MUN','SIGLA_UF']].drop_duplicates().set_index('CD_MUN').SIGLA_UF
    linhas=[]
    with np.load(resultados/'matrizes_completas_255.npz',allow_pickle=False) as z:
        classes=z['classes']; anos=z['anos']; a=z['area_ha']; cds=z['CD_MUN']
        n=np.isin(classes,VN); u=np.isin(classes,UA)
        for estado in sorted(uf.unique()):
            idx=[i for i,c in enumerate(cds) if uf.loc[c]==estado]
            regional=a[idx].sum(axis=0)
            for j,t in enumerate(anos[:-1]):
                for x,y in zip(*np.nonzero(regional[j])):
                    if not n[x] or not u[y]: continue
                    linhas.append({'SIGLA_UF':estado,'ano_origem':int(t),'ano_destino':int(t+1),
                        'classe_origem':int(classes[x]),'classe_destino':int(classes[y]),'area_ha':regional[j,x,y]})
    saida.mkdir(parents=True)
    f=pd.DataFrame(linhas); csv_novo(f,saida/'conversao_por_uf_ano_classe.csv')
    totais=f.groupby(['ano_origem','ano_destino','classe_origem','classe_destino'],as_index=False).area_ha.sum()
    totais['participacao_conversao_anual_pct']=100*totais.area_ha/totais.groupby('ano_origem').area_ha.transform('sum')
    csv_novo(totais,saida/'conversao_por_ano_classe.csv')
    fluxo=pd.read_csv(limiares/'fluxos_prioritarios.csv',sep=';')
    cadastro=q[['CD_MUN','NM_MUN','SIGLA_UF']].drop_duplicates()
    prioridades=[]
    for (cd,t),g in fluxo[fluxo.conversao_principal].groupby(['CD_MUN','ano_origem']):
        maior=g.sort_values('area_ha',ascending=False).iloc[0]
        r=q[q.CD_MUN.eq(cd)&q.ano_origem.eq(t)].iloc[0].to_dict()
        r.update({'origem_dominante':int(maior.classe_origem),'destino_dominante':int(maior.classe_destino),
            'area_fluxo_dominante_ha':maior.area_ha,'participacao_fluxo_dominante_pct':100*maior.area_ha/r['area_convertida_ha']})
        prioridades.append(r)
    csv_novo(pd.DataFrame(prioridades),saida/'serie_prioritarios_38_pares.csv')
    p=pd.read_csv(amostra/'pontos_com_contexto_mapeado.csv',sep=';')
    p=p[p.estrato_pixel.eq('VN_UA')]
    persist=p.groupby(['desenho','ano_origem','ano_destino'],as_index=False).agg(
        n_pontos=('id','size'),n_contexto_t2=('destino_persiste_em_t_mais2','count'),
        n_mesma_classe_em_t2=('destino_persiste_em_t_mais2','sum'))
    csv_novo(persist,saida/'persistencia_amostral_diagnostica.csv')
    (saida/'manifesto.json').write_text(json.dumps({'codigo_sha256':sha(Path(__file__)),
        'sem_referencia_independente':'Decomposição do próprio mapa, não validação temática ou causalidade.',
        'sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},indent=2),encoding='utf-8')
    print(totais[totais.ano_destino.isin([2021,2022,2023])].sort_values(['ano_destino','area_ha'],ascending=[True,False]).groupby('ano_destino').head(5).to_string(index=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('resultados','limiares','amostra','saida'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); executar(a.resultados,a.limiares,a.amostra,a.saida)
