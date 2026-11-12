"""Sensibilidades espacial/temporal e avaliação explícita do suporte inferencial."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.avaliar_pontos_oficiais_col9 import evento,grupos,resumo_binario,codificar
from processamento.cenarios_validacao_col9 import csv_novo,sha


def coincidencias_janela(ref_valid,ref_event,janela):
    """Disponibilidade explícita: nenhuma referência na janela NÃO equivale a negativo."""
    v=np.asarray(ref_valid,bool);e=np.asarray(ref_event,bool)
    ok=np.zeros_like(v);sim=np.zeros_like(e)
    for j in range(v.shape[1]):
        a,b=max(0,j-janela),min(v.shape[1],j+janela+1)
        # Exigir observação de TODA a janela (inclusive se não houve mudança).
        ok[:,j]=v[:,a:b].all(axis=1)
        sim[:,j]=(e[:,a:b]&v[:,a:b]).any(axis=1)
    return ok,sim


def executar(avaliacao,fontes,saida):
    if saida.exists():raise FileExistsError('Preservar saída anterior.')
    saida.mkdir(parents=True)
    pts=pd.read_csv(avaliacao/'pontos_selecionados.csv',sep=';',encoding='utf-8-sig',low_memory=False)
    l=pd.read_csv(avaliacao/'comparacoes_ponto_par.csv',sep=';',encoding='utf-8-sig')
    with np.load(avaliacao/'extracao_rasters.npz',allow_pickle=False) as z:
        np.testing.assert_array_equal(z['TARGETID'],pts.TARGETID)
        v=z['classes_vizinhanca'];mapa=v[:,:,4]
    with np.load(avaliacao/'referencias_harmonizadas.npz',allow_pickle=False) as z:
        np.testing.assert_array_equal(z['TARGETID'],pts.TARGETID)
        ref=z['csv_principal']
    counts=pts[[f'COUNT_{a}' for a in range(1985,2024)]].to_numpy(int)
    nont=pts.AMOSTRA_AM.eq(0).to_numpy()
    rv,re=evento(ref[:,:-1],ref[:,1:],True);rv &= (counts[:,:-1]>0)&(counts[:,1:]>0)
    mv,me=evento(mapa[:,:-1],mapa[:,1:])
    # Sensibilidades de classes recomputadas em ambas as referências, nunca nas matrizes.
    sens=[]
    for nome,o,d in [('principal',[],[]),('mais25',[],[25]),('mais29',[29],[]),
                     ('mais32',[32],[]),('mais29_32',[29,32],[]),('mais29_32_25',[29,32],[25])]:
        vr,er=evento(ref[:,:-1],ref[:,1:],True,o,d)
        vm,em=evento(mapa[:,:-1],mapa[:,1:],False,o,d)
        ok=vr&vm&(counts[:,:-1]>0)&(counts[:,1:]>0)&nont[:,None]
        sens.append({'variante':nome,'n_pares':int(ok.sum()),'n_pontos':int(ok.any(axis=1).sum()),
                     **resumo_binario(er[ok],em[ok]),'escopo':'descritivo_sem_IC'})
    csv_novo(pd.DataFrame(sens),saida/'sensibilidade_classes_25_29_32.csv')
    timing=[];detalhes=[]
    for janela in [0,1,2]:
        ok,sim=coincidencias_janela(rv,re,janela)
        for j,ano in enumerate(range(1986,2024)):
            sel=nont&me[:,j]&mv[:,j]&ok[:,j]
            timing.append({'janela_mais_menos_anos':janela,'ano_destino':ano,
                'n_conversoes_mapa_com_janela_ref_observada':int(sel.sum()),
                'n_com_evento_ref_na_janela':int(sim[sel,j].sum()),
                'nota':'Diagnóstico de datação. Janela truncada nos limites1985/2023; não é validação do ano nem seleção de melhor alinhamento.'})
    csv_novo(pd.DataFrame(timing),saida/'sensibilidade_datacao.csv')
    # Comparação entre mesma célula e vizinhança: oportunismo de múltiplas células
    # explicitamente impede usar esse resultado como acurácia melhorada.
    vv,ee=evento(v[:,:-1,:],v[:,1:,:]);anyevent=(vv&ee).any(axis=2)
    sel=nont[:,None]&rv&mv
    espac=[]
    for nome,em in [('celula_na_coordenada',me),('alguma_das_9_celulas',anyevent)]:
        espac.append({'suporte':nome,'n_pares':int(sel.sum()),**resumo_binario(re[sel],em[sel]),
            'nota':'3x3 mistura suportes e aumenta chances de coincidir; não corrige registro nem valida área.'})
    csv_novo(pd.DataFrame(espac),saida/'sensibilidade_registro_3x3.csv')
    z=l.loc[l.versao_referencia.eq('csv_principal') & l.AMOSTRA_AM.eq(0) & l.comparavel].copy()
    z['grupo_ref_t']=grupos(z.ref_t,True);z['grupo_ref_t1']=grupos(z.ref_t1,True)
    z['resultado']=np.where(z.evento_mapa,np.where(z.evento_referencia,'TP','FP'),
                              np.where(z.evento_referencia,'FN','TN'))
    csv_novo(z.groupby(['resultado','ref_t','ref_t1','mapa_t','mapa_t1']).size().rename('n').reset_index(),
             saida/'discordancias_por_classes.csv')
    csv_novo(z.groupby(['resultado','grupo_ref_t','grupo_ref_t1']).size().rename('n').reset_index(),
             saida/'discordancias_por_grupos.csv')
    # Pontos repetidos: soma dos pares nunca é tamanho de amostra independente.
    porp=z.groupby('TARGETID').agg(n_pares=('ano_origem','size'),
        n_eventos_mapa=('evento_mapa','sum'),n_eventos_ref=('evento_referencia','sum')).reset_index()
    csv_novo(porp,saida/'dependencia_temporal_por_ponto.csv')
    csv_novo(pts.loc[pts.municipio_diverge_vetor,['TARGETID','LON','LAT','CD_MUN','NM_MUN','SIGLA_UF',
        'CD_MUN_vetor_publicado']],saida/'municipios_vetor_divergentes.csv')
    # Concordância ANUAL de grupos, separada da concordância de mudança.
    annual=[]
    for j,ano in enumerate(range(1985,2024)):
        gr,gm=grupos(ref[:,j],True),grupos(mapa[:,j])
        ok=nont&(gr>0)&(gm>0)&(counts[:,j]>0)
        annual.append({'ano':ano,'n_pontos_comparaveis':int(ok.sum()),
            'n_concordam_grupo':int((gr[ok]==gm[ok]).sum()),
            'concordancia_grupos_descritiva':float((gr[ok]==gm[ok]).mean()) if ok.any() else None})
    csv_novo(pd.DataFrame(annual),saida/'concordancia_anual_grupos_sem_treino.csv')
    pp=pts[['TARGETID','CD_MUN','NM_MUN','SIGLA_UF']].copy()
    pp['n_anos_alternancia_classe']=np.sum((mapa[:,1:]!=mapa[:,:-1])&mv,axis=1)
    pp['n_eventos_mapeados']=me.sum(axis=1)
    pp['AMOSTRA_AM']=pts.AMOSTRA_AM
    csv_novo(pp,saida/'alternancias_por_ponto.csv')
    estratos=pd.read_csv(avaliacao/'estratos_originais_nacionais_recorte.csv',sep=';',encoding='utf-8-sig')
    motivos=[
        'Remoção de9999 pontos de treinamento não acompanha probabilidades condicionais publicadas verificadas; apêndice cita10000.',
        'Não resposta anual/temática e seleção de subconjunto2023 sem mecanismo de inclusão documentado.',
        'Referência de classes gerais, não amostra dimensionada para conversão rara por município; dois municípios sem pontos.',
        'Pesos constantes e inversos das probabilidades são necessários, mas não bastam para garantir validade após exclusões.',
        'COUNT é resumo de concordância, não votos individuais nem certeza calibrada; filtros COUNT/BORDA alteram domínio.',
        'Repetição dos mesmos IDs ao longo do tempo; pares não são observações independentes.',
        'Revisões do conjunto oficial e imagens comuns ao mapeamento: independência temática absoluta não comprovada.']
    infer={'inferir_populacao_255':False,'IC_representativos_calculados':False,
        'matrizes_ponderadas':'Somas de pesos fornecidos e razões apenas descritivas de sensibilidade. Não estimativas homologadas de área/acurácia.',
        'estratos_nacionais_observados':len(estratos),'estratos_com_recorte':int(estratos.n_recorte.gt(0).sum()),
        'estratos_nacional_n_menor2':int(estratos.n_nacional.lt(2).sum()),
        'n_pares_csv_sem_treino':len(z),'n_pontos_csv_sem_treino':int(z.TARGETID.nunique()),
        'motivos':motivos,
        'condicoes_para_inferencia_futura':[
            'Esclarecer versão da referência e ID de treino ausente, mecanismo de retirada/atualização e cobertura2023.',
            'Obter população/área dos estratos e probabilidades válidas para o conjunto independente realmente utilizado.',
            'Estimação de domínio sobre desenho nacional completo: indicadoresI_D, sem renormalização arbitrária por município.',
            'TotaisHT por células; razões para precisão/sensibilidade com variância linearizada ou replicação estratificada documentada.',
            'A unidade é o ponto espacial para todos os anos: agregar contribuição temporal dentro do ID antes de estimar variância.',
            'Diagnosticar eventos raros, graus de liberdade e estratos isolados; não prometer IC municipais onde suporte é insuficiente.'],
        'sem_rejeitar_desenho_original':'O desenho nacional é probabilístico. A limitação é a reconstrução das inclusões/referências válidas para este domínio e desfecho.'}
    (saida/'avaliacao_suporte_inferencial.json').write_text(json.dumps(infer,ensure_ascii=False,indent=2),encoding='utf-8')
    (saida/'manifesto_diagnosticos.json').write_text(json.dumps({'avaliacao_sha256':sha(avaliacao/'resumo_execucao.json'),
        'arquivos':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Diagnósticos de sensibilidade concluídos sem inferência populacional.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--avaliacao',type=Path,required=True)
    p.add_argument('--fontes',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();executar(a.avaliacao,a.fontes,a.saida)
