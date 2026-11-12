"""Relaciona cenários candidatos à cobertura das referências; não homologa Y."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import conferir_acervo,csv_novo,CENARIOS,QUALIDADES,sha
from processamento.avaliar_pontos_oficiais_col9 import grupos


def executar(avaliacao,matrizes,saida):
    if saida.exists():raise FileExistsError('Preservar resultados anteriores.')
    saida.mkdir(parents=True)
    q=conferir_acervo(matrizes)
    l=pd.read_csv(avaliacao/'comparacoes_ponto_par.csv',sep=';',encoding='utf-8-sig')
    z=l.loc[l.versao_referencia.eq('csv_principal') & l.AMOSTRA_AM.eq(0)].copy()
    z['referencia_VN_inicial_comparavel']=z.comparavel&(grupos(z.ref_t,True)==1)
    z['conv_ref_comparavel']=z.comparavel & z.evento_referencia
    z['conv_mapa_comparavel']=z.comparavel & z.evento_mapa
    cov=z.groupby(['CD_MUN','ano_origem']).agg(n_pontos_sem_treino=('TARGETID','size'),
        n_comparaveis=('comparavel','sum'),n_ref_VN_inicial=('referencia_VN_inicial_comparavel','sum'),
        n_eventos_ref=('conv_ref_comparavel','sum'),n_eventos_mapa_com_ref=('conv_mapa_comparavel','sum')).reset_index()
    r=q[['CD_MUN','NM_MUN','SIGLA_UF','ano_origem','ano_destino','area_convertida_ha',
         'vn_inicial_elegivel_ha','taxa_conversao_pct','elegibilidade_vn_pct']].merge(
            cov,on=['CD_MUN','ano_origem'],how='left',validate='one_to_one')
    campos=['n_pontos_sem_treino','n_comparaveis','n_ref_VN_inicial','n_eventos_ref','n_eventos_mapa_com_ref']
    r[campos]=r[campos].fillna(0).astype(int)
    todos=[];resumos={k:[] for k in ['global','ano','estado','municipio']}
    for c,(tau,amin) in CENARIOS.items():
        for qmin in QUALIDADES:
            a=r.copy();aval=a.elegibilidade_vn_pct.ge(qmin)&a.vn_inicial_elegivel_ha.gt(0)
            candidato=aval&a.taxa_conversao_pct.ge(tau)&a.area_convertida_ha.ge(amin)
            a['cenario']=c;a['tau_pct']=tau;a['A_min_ha']=amin;a['Q_min_pct']=qmin
            a['status_cenario']=np.where(~aval,'excluido_qualidade',np.where(candidato,'candidato_nao_homologado','abaixo_criterios'))
            a['candidato_sem_referencia_par']=candidato&a.n_comparaveis.eq(0)
            a['candidato_sem_ponto_ref_VN_inicial']=candidato&a.n_ref_VN_inicial.eq(0)
            a['candidato_com_evento_ref_na_amostra']=candidato&a.n_eventos_ref.gt(0)
            a['nota']='Cobertura na amostra não confirma/refuta evento municipal; sem acurácia representativa.'
            todos.append(a)
            for nome,g in [('global',[]),('ano',['ano_destino']),('estado',['SIGLA_UF']),('municipio',['CD_MUN','NM_MUN','SIGLA_UF'])]:
                b=a.assign(candidato=candidato,avaliavel=aval).groupby(['cenario','Q_min_pct']+g,dropna=False).agg(
                    n_pares=('CD_MUN','size'),n_avaliaveis=('avaliavel','sum'),n_candidatos=('candidato','sum'),
                    n_candidatos_sem_ref_par=('candidato_sem_referencia_par','sum'),
                    n_candidatos_sem_ponto_ref_VN=('candidato_sem_ponto_ref_VN_inicial','sum'),
                    n_candidatos_com_evento_ref_na_amostra=('candidato_com_evento_ref_na_amostra','sum')).reset_index()
                resumos[nome].append(b)
    csv_novo(pd.concat(todos,ignore_index=True),saida/'cenarios_cobertura_referencias_87210.csv')
    for nome,val in resumos.items():csv_novo(pd.concat(val,ignore_index=True),saida/f'cobertura_cenarios_{nome}.csv')
    (saida/'manifesto_cenarios_evidencias.json').write_text(json.dumps({'matrizes_sha256':sha(matrizes/'concluido.json'),
        'sem_Y_homologado':True,'criterio':'C>=A_min E R>=tau; Q verifica elegibilidade VN, não acurácia temática.',
        'arquivos':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},ensure_ascii=False,indent=2),encoding='utf-8')
    print(pd.concat(resumos['global']).to_string(index=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--avaliacao',type=Path,required=True)
    p.add_argument('--matrizes',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();executar(a.avaliacao,a.matrizes,a.saida)
