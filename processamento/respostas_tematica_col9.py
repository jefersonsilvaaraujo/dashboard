"""Audita fichas cegas. Respostas pendentes/inconclusivas nunca viram acertos ou negativos."""
import argparse
import json
from pathlib import Path

import pandas as pd


def auditar(pontos,fichas):
    if pontos.id.duplicated().any() or fichas.id.duplicated().any(): raise ValueError('IDs duplicados.')
    if set(pontos.id)!=set(fichas.id): raise ValueError('Fichas não correspondem à amostra sorteada.')
    a=pontos.merge(fichas,on='id',suffixes=('','_ficha'),validate='one_to_one')
    a=a[a.desenho.eq('probabilistica')]
    classes={'VN','UA','OUTROS'}
    validos=a.referencia_t.isin(classes)&a.referencia_t1.isin(classes)&a.situacao.eq('concluido')
    campos=['fonte','interprete','evidencia_arquivo','data_imagem_t','data_imagem_t1','justificativa']
    for c in campos: validos &= a[c].notna()&a[c].astype(str).str.strip().ne('')
    return {'n_probabilisticos':len(a),'n_com_resposta_documentada':int(validos.sum()),
        'n_pendentes_ou_inconclusivos':int((~validos).sum()),
        'acuracia_estimada':None,
        'situacao':'respostas_completas_requerem_estimador_do_desenho_e_adjudicacao' if validos.all() else 'referencia_insuficiente_nao_estimar_acuracia',
        'dirigidos_excluidos_da_inferencia':True,
        'regra':'Não estimar acurácia por casos completos quando houver não resposta; não resposta pode ser informativa.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--amostra',type=Path,required=True)
    p.add_argument('--fichas',type=Path,required=True); p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args(); r=auditar(pd.read_csv(a.amostra,sep=';'),pd.read_csv(a.fichas,sep=';'))
    with a.saida.open('x',encoding='utf-8') as f: json.dump(r,f,ensure_ascii=False,indent=2)
    print(json.dumps(r,ensure_ascii=False,indent=2))
