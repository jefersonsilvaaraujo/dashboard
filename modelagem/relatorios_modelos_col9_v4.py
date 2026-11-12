"""Relatórios científicos a partir de escolhas e predições já congeladas."""
import argparse,json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.relatorios_oficiais_col9 import tabela
from modelagem.executar_regressao_col9_v4 import metricas
from modelagem.interpretar_regressao_col9_v4 import escolher_tabela
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto
from modelagem.relatorios_preparacao_regressao_col9 import revisar_prosa

def numero(v,n=3):
    if v is None or pd.isna(v):return 'não definido'
    return f'{float(v):,.{n}f}'.replace(',','§').replace('.',',').replace('§','.')

def executar(raiz,docs):
    p=carregar_manifesto(raiz)
    if not (raiz/'TESTE_CONCLUIDO.json').exists():raise ValueError('Teste não concluído.')
    def escrever(nome,t):
        with (docs/nome).open('x',encoding='utf-8') as f:f.write(revisar_prosa(t))
    m=pd.read_parquet(raiz/'teste/METRICAS_TESTE_FINAL.parquet')
    va=pd.read_parquet(raiz/'METRICAS_VALIDACAO_CONGELADAS.parquet')
    y=pd.read_parquet(raiz/'teste/RESULTADOS_IMUTAVEIS_TESTE.parquet')
    anos=pd.read_parquet(raiz/'teste/METRICAS_TESTE_POR_ANO.parquet')
    states=pd.read_csv(raiz/'apresentacao/VALIDACAO_ESPACIAL_TODOS_ESTADOS.csv',sep=';')
    winners=json.loads((raiz/'VENCEDORES_PELA_VALIDACAO.json').read_text(encoding='utf-8'))
    resumo=json.loads((raiz/'apresentacao/RESUMO_VENCEDORES_E_TESTE.json').read_text(encoding='utf-8'))
    cv=pd.read_parquet(raiz/'AJUSTES_CV_DESENVOLVIMENTO.parquet')
    audit=json.loads((raiz/'auditoria_ajustes/AUDITORIA_AJUSTES_APROVADA.json').read_text(encoding='utf-8'))
    principais=m.loc[m.coorte.eq('principal')&m.contexto.eq('temporal')&m.regime.eq('movel')]
    vr=next(w for w in winners if w['coorte']=='principal' and w['contexto']=='temporal' and w['target']=='R_pct' and w['categoria']=='supervisionado')
    vc=next(w for w in winners if w['coorte']=='principal' and w['contexto']=='temporal' and w['target']=='C_ha' and w['categoria']=='supervisionado')
    rr=escolher_tabela(m,vr).iloc[0];rc=escolher_tabela(m,vc).iloc[0]
    br=principais.loc[principais.target.eq('R_pct')&principais.algoritmo.eq('persistencia')].iloc[0]
    bc=principais.loc[principais.target.eq('C_ha')&principais.algoritmo.eq('persistencia')].iloc[0]
    geralr=next(w for w in winners if w['coorte']=='principal' and w['contexto']=='temporal' and w['target']=='R_pct' and w['categoria']=='incluindo_baselines')
    geralc=next(w for w in winners if w['coorte']=='principal' and w['contexto']=='temporal' and w['target']=='C_ha' and w['categoria']=='incluindo_baselines')
    col=['target','bloco','algoritmo','n','MAE','RMSE','vies','R2','n_pred_negativas','n_pred_acima_limite']
    baseline=m.loc[m.contexto.eq('temporal')&m.bloco.eq('BASE')]
    bval=va[['coorte','contexto','target','bloco','algoritmo','regime','MAE']].rename(columns={'MAE':'MAE_validacao'})
    baseline=baseline.merge(bval,on=['coorte','contexto','target','bloco','algoritmo','regime'],validate='one_to_one')
    texto_metodo=(
        'Treino inicial t=1985–2013, embargo2014, validação2015–2017; refit final até2017 excluindo2014, embargo2018 e teste2019–2022. '
        'Coorte de focos: treino a partir de2003, com mesmos anos de validação/teste e folds internos adaptados. '
        'Tuning porMAE na escala original nos folds internos; escolhas de algoritmo/bloco pela validação, jamais pelo teste. '
        'A origem móvel admite históricos observados até t, inclusive de intervalos anteriores do bloco reservado, sem usar esses rótulos para reajuste. '
        '50 atributos derivados daCol9 têm risco retrospectivo do produtor, não eliminado pelos testes de colunas. '
        'R/C são conversão mapeada, não verdade ambiental corrigida. Nenhum dado2024, PRODES, área queimada ou socioeconomia entrou nos modelos.')
    escrever('RESULTADOS_BASELINES_COL9.md',f'''
# Resultados dos baselines
Média/mediana históricas são globais do treino de cada contexto, não municipais;
LOSO as calcula apenas nos estados não retidos. Persistência usa a última
conversão encerrada até t; eventual falta recebe a mediana do treino, sem
ser interpretada como ausência de conversão. As baselines não utilizam D futuro.

{tabela(baseline[['coorte','target','algoritmo','regime','n','MAE_validacao','MAE','RMSE','vies','R2']])}

As três alternativas foram congeladas antes do teste. A melhor alternativa
incluindo baselines, segundo validação, foi R:{geralr['bloco']}/{geralr['algoritmo']}
e C:{geralc['bloco']}/{geralc['algoritmo']}. O teste não redefiniu essa escolha.
{texto_metodo}
''')
    escrever('RESULTADOS_REGRESSAO_CONTINUA_COL9.md',f'''
# Regressão da taxa percentual anual mapeada
O vencedor supervisionado da validação foi **{vr['bloco']}/{vr['algoritmo']}**,
MAE de validação{numero(vr['MAE_validacao'])} pontos percentuais.
No teste reservado:MAE{numero(rr.MAE)}p.p.; RMSE{numero(rr.RMSE)}p.p.;
viés{numero(rr.vies)}p.p.; R²{numero(rr.R2)}. O viés tem sinal previsto−observado.

{tabela(principais.loc[principais.target.eq('R_pct'),col])}

São1020 observações dos255 municípios emt2019–2022, com respostas2020–2023.
A tabela mostra todos os modelos e baselines, não um vencedor escolhido pelo
teste. Predições negativas/acima de100 foram mantidas e contadas, sem clipping.
As diferenças finitas não foram corrigidas pelos26,81% de precisão temática
descritiva. O desempenho mede concordância preditiva com a conversão mapeada.

As escolhas e métricas de validação estão emMETRICAS_VALIDACAO_CONGELADAS.parquet;
configurações/folds emAJUSTES_CV_DESENVOLVIMENTO.parquet. As grades têm3Ridge,
4ElasticNet,2Forest e2XGBoost por transformação. R usa identidade; C compara
identidade/log1p no desenvolvimento. Normalização de y usa média/DP do treino
e é invertida antes das métricas. Colunas ausentes usam medianas do treino e
indicadores; coluna totalmente ausente é removida da parte de valores, sem
inventar zero físico. A auditoria conferiu os parâmetros de{audit['modelos_verificados']} modelos finais.

{texto_metodo}
''')
    aval_r=escolher_tabela(anos,vr);aval_c=escolher_tabela(anos,vc)
    escrever('RESULTADOS_VALIDACAO_TEMPORAL_COL9.md',f'''
# Validação temporal
Nenhum resultado2019–2022 foi usado para tuning ou seleção. O marcador de
abertura única foi criado depois de todas as predições finais serem salvas
sem Y. A apresentação reagrupa essas mesmas predições; não executa novos modelos.

Taxa: vencedor{vr['bloco']}/{vr['algoritmo']}.
{tabela(aval_r,['ano_t','n','MAE','RMSE','vies','R2','n_pred_negativas','n_pred_acima_limite'])}

Área: vencedor{vc['bloco']}/{vc['algoritmo']}.
{tabela(aval_c,['ano_t','n','MAE','RMSE','vies','R2','n_pred_negativas','n_pred_acima_limite'])}

Os erros não devem ser atribuídos apenas à mudança temporal: o modelo final
foi reajustado com desenvolvimento até2017, enquanto a validação usa ajuste
inicial até2013. Extremos e anos finais já haviam sido explorados cientificamente:
o teste não é completamente cego à formulação. Referência2023 insuficiente
limita a interpretação ambiental do último intervalo2022→2023.

Figuras observado×previsto, resíduos, série anual e calibração estão emapresentacao/figuras.
Faixas de calibração foram definidas pelas predições da validação antes do teste.
Faixas de magnitude dos erros usam quartis da resposta do treino inicial;
não se recalcularam cortes com o teste. R² indefinido em grupos sem variância
permanece ausente; MAPE não foi métrica principal.

{texto_metodo}
''')
    macro=states.groupby('target').MAE.mean().to_dict()
    ds=[]
    for target in ['R_pct','C_ha']:
        for uf in ['MA','MT','PA','RO','TO']:
            a=y.loc[y.coorte.eq('principal')&y.contexto.eq(uf)&y.target.eq(target)&y.regime.eq('movel')].drop_duplicates('row_id')
            ds.append({'target':target,'UF_retida':uf,'municipios':a.CD_MUN.nunique(),'n':len(a),'observado_min':a.observado.min(),
                       'observado_mediana':a.observado.median(),'observado_max':a.observado.max()})
    pd.DataFrame(ds).to_csv(raiz/'apresentacao/DISTRIBUICOES_DESFECHOS_POR_FOLD.csv',sep=';',index=False)
    escrever('RESULTADOS_VALIDACAO_ESPACIAL_COL9.md',f'''
# Validação espacial: todos os cinco estados
Cada UF fica integralmente fora de ajuste, tuning, seleção, normalização,
imputação e calibração do seu experimento. O modelo/bloco porUF foi escolhido
na validação dos demais estados e só então aplicado à UF em2019–2022.

{tabela(states,['target','UF_retida','municipios','bloco','algoritmo','MAE_validacao','n','MAE','RMSE','vies','R2'])}

{tabela(pd.DataFrame(ds))}

MAE macro entre os cinco estados:R={numero(macro['R_pct'])}p.p.;
C={numero(macro['C_ha'])}ha. O resumo também fornece métricas micro das
predições LOSO reunidas, com cada município presente apenas em sua UF retida.
Macro e micro têm pesos diferentes; RO possui apenas5 municípios/20 respostas.
Não se escolheu o melhor estado para apresentação nem se estimaram IC iid.

A transferência admite covariáveis locais conhecidas até t, inclusive histórico
mapeado no regime móvel; não simula uma região sem qualquer histórico.
Correlação entre municípios próximos/fronteiras permanece; nenhum buffer ou
grafo antigo268 foi criado ou herdado. MapasLOSO combinam modelos possivelmente
distintos porUF, identificados na tabela, e não um único modelo nacional.
Cobertura dos preditores, contagens de ajuste e verificação das medianas estão
na auditoria de ajustes; as52 ausências anuais de focos foram mantidas comoNA
na coorte restrita, antes da imputação computacional de cada treino.
''')
    partes=[]
    for co in ['principal','focos2003']:
        for target in ['R_pct','C_ha']:
            t=m.loc[m.coorte.eq(co)&m.contexto.eq('temporal')&m.target.eq(target)&m.regime.eq('movel')&m.algoritmo.isin(['ridge','elastic_net','random_forest','xgboost'])]
            pivot=t.pivot(index='algoritmo',columns='bloco',values='MAE').reset_index()
            partes.append(f'## {co} — {target}\n\n'+tabela(pivot))
    f=m.loc[m.coorte.eq('principal')&m.contexto.eq('temporal')&((m.bloco.eq('T3'))|m.algoritmo.eq('persistencia'))]
    f=f.pivot(index=['target','bloco','algoritmo'],columns='regime',values='MAE').reset_index()
    f['delta_congelado_menos_movel']=f.congelado-f.movel
    escrever('RESULTADOS_ABLACAO_COL9.md','''
# Ablações e sensibilidade de históricos
T0:território; T1:+composição/qualidade somente t; T2:+variações/tendências;
T3:+conversões encerradas até t; T4:+registros de focos.
As comparações diretas abaixo mantêm algoritmo e coorte. A coorte principal
começa em1985; T0–T4 de focos usam2003–2022. Seus períodos de treino diferem,
portanto mudanças entre coortes não são isoladamente efeito dos focos.

'''+ '\n\n'.join(partes)+f'''

## Históricos congelados: sensibilidade sem novo ajuste
{tabela(f)}

Usam-se os mesmos modelos/hiperparâmetros do regime móvel. Só os históricos
deT2/T3 foram fixados no ano de embargo anterior à avaliação:2014 na
validação,2018 no teste. Composição do mapa de t continua atual. Isso é uma
sensibilidade de entrada, não um segundo modelo retreinado nem uma simulação
operacional histórica completa. Nenhuma escolha foi refeita pelos resultados.

Retirar Col9 ou seus históricos não prova ausência de vazamento do produtor.
Os mapas históricos podem carregar filtros de anos posteriores, mesmo emT1/T2.
As ablações descrevem associação incremental com a resposta mapeada, não
causalidade. Resultados de todos os algoritmos/estados estão nas tabelas completas;
não se selecionou a ablação de menor erro no teste para substituir o protocolo.
''')
    modos=pd.DataFrame([{'coorte':a['coorte'],'contexto':a['contexto'],'bloco':a['bloco'],'algoritmo':a['algoritmo'],
                         'transformacao_escolhida_no_CV':a['meta'].get('transformacao','original_baseline')} for a in json.loads((raiz/'MODELOS_PARA_TESTE.json').read_text(encoding='utf-8'))
                         if a['target']=='C_ha' and a['contexto']=='temporal'])
    escrever('RESULTADOS_REGRESSAO_AREA_HA_COL9.md',f'''
# Experimento complementar de área convertida
C foi ajustada diretamente como resposta própria, nunca R prevista×D realizado.
O vencedor supervisionado por validação foi{vc['bloco']}/{vc['algoritmo']},
MAE de validação{numero(vc['MAE_validacao'])}ha; no teste:
MAE{numero(rc.MAE)}ha, RMSE{numero(rc.RMSE)}ha, viés{numero(rc.vies)}ha,
R²{numero(rc.R2)}. Persistência teve MAE{numero(bc.MAE)}ha no mesmo teste.

{tabela(principais.loc[principais.target.eq('C_ha'),col])}

{tabela(modos)}

Identidade/log1p foram comparadas somente no CV do desenvolvimento. Toda
predição retornou à escala original antes das métricas, sem smearing ajustado
com teste ou correção por precisão cartográfica. Inversão da média log não
equivale automaticamente à média original; a seleção foi pela perdaMAE emha.

Negativas são reportadas sem clipping. O limite superior diagnóstico é a VN
observada somente em t, não D da máscara futura. Isso não é uma restrição
aplicada ao modelo nem uso de D como preditor. Extremos, distribuição porUF,
período e estoque devem ser considerados antes de extrapolar a interpretação.

R mede pressão relativa sobre estoque elegível; C mede escala absoluta municipal.
Não se comparaMAE emha com pontos percentuais para declarar uma resposta superior.
A soma das áreas anuais não significa área única desmatada. Este é desempenho
contra conversão mapeada, distinto de acurácia temática e conversão ambiental real.
''')
    im=pd.read_csv(raiz/'interpretacao_pre_teste/IMPORTANCIAS_VALIDACAO.csv',sep=';')
    partes=[]
    for target in ['R_pct','C_ha']:
        a=im[im.target.eq(target)&~im.variavel_ou_grupo.str.startswith('GRUPO_')].sort_values('mean',ascending=False).head(15)
        partes.append('## '+target+'\n\n'+tabela(a,['variavel_ou_grupo','mean','std']))
    extr=raiz/'apresentacao'
    er=pd.read_csv(extr/'EXTREMOS_ERRO_R_pct.csv',sep=';')
    ec=pd.read_csv(extr/'EXTREMOS_ERRO_C_ha.csv',sep=';')
    escrever('RELATORIO_INTERPRETACAO_MODELOS_COL9.md','''
# Interpretação e diagnósticos
Importâncias foram calculadas somente na validação2015–2017, antes de abrir
Yteste, para os vencedores supervisionados principais. Em cinco repetições,
trajetórias municipais foram permutadas dentrodaUF. O incrementoMAE médio
mede dependência preditiva nesse suporte; DPdas cinco permutações não éIC.
Colinearidade pode dividir/ocultar importância; permutação pode produzir
combinações pouco usuais. A validação também selecionou o modelo, portanto
não é estimativa externa independente de importância. Nenhum atributo foi
retirado por essa inspeção e nenhuma importância foi interpretada como causa.

'''+ '\n\n'.join(partes)+f'''

## Maiores erros no teste —R
{tabela(er.head(10),['NM_MUN','SIGLA_UF','ano_t','observado','previsto','erro'])}

## Maiores erros no teste —C
{tabela(ec.head(10),['NM_MUN','SIGLA_UF','ano_t','observado','previsto','erro'])}

As figuras incluem observado×previsto, resíduos, distribuição de erros, médias
por ano, erros porUF, calibração e mapas. A análise usa as mesmas predições
imutáveis; nenhum modelo foi reexecutado para melhorar sua apresentação.
Os mapas são médias municipais2019–2022 nos255 polígonos canônicos, em
pontos percentuais ouha; não probabilidades binárias nem áreas reais corrigidas.
Escalas visuais abrangem os valores previstos/observados sem ocultar extrapolações.

Limitações centrais: referência2023 insuficiente, baixa coincidência temática
no ano exato, possível filtragem retrospectiva do produtor, autocorrelação,
desigualdade entre estados, assimetria e extremos. Melhor desempenho de um
bloco não valida sua independência temporal. Intervalos preditivos formais
não foram calculados nem confundidos com incerteza cartográfica. Novos links,
perdas ou buffers exigiriam outro protocolo e decisão antes de novo teste,
não ajustes ao protocolo encerrado para melhorar os números apresentados.
''')
    losor=next(x['LOSO_micro'] for x in resumo if x['target']=='R_pct')
    losoc=next(x['LOSO_micro'] for x in resumo if x['target']=='C_ha')
    escrever('TEXTO_RESULTADOS_DISSERTACAO_COL9.md',f'''
# Texto proposto para resultados e discussão da dissertação
O protocolo foi auditado e congelado antes do ajuste, utilizando9.690
observações município–ano de255 municípios e a Coleção9 em1985–2023.
Compararam-se regressões Ridge/Elastic Net, Random Forest e XGBoost,
além de média, mediana e persistência. O ajuste de hiperparâmetros ocorreu
por avanço temporal no desenvolvimento, e a seleção final pela validação
de2015–2017. A avaliação reservada abrangeut2019–2022;2024 não foi utilizado.

Para a taxa percentual R, o melhor modelo supervisionado segundo validação
foi{vr['algoritmo']} com{vr['bloco']}, MAE de validação
{numero(vr['MAE_validacao'])}pontos percentuais. No teste, obteve
MAE{numero(rr.MAE)}p.p., RMSE{numero(rr.RMSE)}p.p., viés
{numero(rr.vies)}p.p. eR²{numero(rr.R2)}. A persistência apresentou
MAE{numero(br.MAE)}p.p. no mesmo suporte. Essa comparação não foi
utilizada para trocar o modelo escolhido na validação.

A validação espacial reteve integralmente cada estado do desenvolvimento
do seu fold. As predições dos modelos porUF escolhidos na validação externa
à UF tiveramMAE micro{numero(losor['MAE'])}p.p. paraR e
{numero(losoc['MAE'])}ha paraC. As médias macro entreUFs foram
{numero(macro['R_pct'])}p.p. e{numero(macro['C_ha'])}ha, respectivamente.
Essas agregações têm pesos distintos, e RO possui apenas cinco municípios.

No experimento independente de área, o vencedor supervisionado por validação
foi{vc['algoritmo']} com{vc['bloco']}. No teste, MAE
{numero(rc.MAE)}ha, RMSE{numero(rc.RMSE)}ha, viés
{numero(rc.vies)}ha eR²{numero(rc.R2)}; persistência:
MAE{numero(bc.MAE)}ha. As previsões deC não foram derivadas deR usando
D futuro. A interpretação absoluta difere da pressão relativaR e foi mantida
separada na análise, com retorno à escala original após transformações.

As ablaçõesT0–T3 compartilharam coorte e partições. A análise de focos foi
separada, comparandoT0–T4 na coorte2003–2022, mantendoNA quando inexistiam
registros e sem tratar focos como área queimada. A sensibilidade com históricos
congelados reutilizou modelos/hiperparâmetros, alterando apenas entradas históricas,
sem retuning. Essas comparações não demonstram causalidade ou ausência de
dependência temporal nos produtos derivados daColeção9.

Os resultados expressam desempenho de regressão contra conversão mapeada.
Não corrigem erro cartográfico nem validam conversão ambiental real. A baixa
coincidência descritiva das transições anuais com referências, a lacuna de2023,
a filtragem retrospectiva e a exploração científica anterior dos anos finais
limitam afirmações confirmatórias. O teste foi separado do ajuste e aberto
uma única vez para avaliação final, mas não era completamente cego à formulação
do estudo. Previsões fora dos limites físicos foram explicitamente reportadas,
sem truncamento silencioso. Importância preditiva não foi interpretada causalmente.
''')
    escrever('RESUMO_EXECUTIVO_MODELOS_COL9.md',f'''
# Resumo executivo dos experimentos autorizados
Melhor supervisionado pela validação:R={vr['bloco']}/{vr['algoritmo']};
C={vc['bloco']}/{vc['algoritmo']}. Melhor incluindo baselines:
R={geralr['bloco']}/{geralr['algoritmo']}; C={geralc['bloco']}/{geralc['algoritmo']}.
Nenhuma escolha foi refeita pelo teste.

| Resposta | MAE validação do supervisionado | MAE teste | RMSE teste | Viés teste | R² teste | MAE persistência teste |
|---|---:|---:|---:|---:|---:|---:|
| R, p.p. |{numero(vr['MAE_validacao'])}|{numero(rr.MAE)}|{numero(rr.RMSE)}|{numero(rr.vies)}|{numero(rr.R2)}|{numero(br.MAE)}|
| C, ha |{numero(vc['MAE_validacao'])}|{numero(rc.MAE)}|{numero(rc.RMSE)}|{numero(rc.vies)}|{numero(rc.R2)}|{numero(bc.MAE)}|

LOSO micro:R MAE{numero(losor['MAE'])}p.p.; C MAE{numero(losoc['MAE'])}ha.
Todos os cinco estados são apresentados, com seus números de municípios.
Os108 grupos de desenvolvimento produziram504 modelos finais, incluindo
baselines. A auditoria independente conferiu alvo/normalização/imputação
dos{audit['modelos_verificados']} modelos e exclusão das UFs retidas.

Ablacões, focos em coorte separada e históricos congelados estão documentados
sem escolha pós-teste. Os maiores erros, extrapolações e diferenças regionais
devem orientar a discussão; não foram eliminados para melhorar métricas.

Recomendação científica:discutir os resultados contra a persistência e os
blocos territoriais, explicitando a resposta mapeada, instabilidade temática,
dependência retrospectiva e desigualdade entre estados. Não reivindicar
conversão real corrigida, causalidade, disponibilidade operacional histórica
ou validação representativa própria da cartografia.

Banco, dashboard, rasters, matrizes, fontes eDOCX não foram alterados.
A aprovação foi registrada por adendo versionado ao diário. Os testes anteriores
e os15 novos da revisão ativa passaram. Versões técnicas preliminares foram
preservadas antes do ajuste científico; revisaram apenas compatibilidade de
persistência segura, sem mudar grades, dados, partições ou critérios.
O protocolo e o marcador de abertura única permanecem verificáveis.
''')
    escrever('ENTREGA_MODELOS_COL9.md','''
# Entrega dos experimentos de regressão —Coleção9

1. [Protocolo congelado](PROTOCOLO_EXPERIMENTAL_CONGELADO_COL9.md)
2. [Auditoria pré-treino](RELATORIO_AUDITORIA_PRE_TREINO_COL9.md)
3. [Decisões aprovadas](DIARIO_DECISOES_CIENTIFICAS_COL9.md)
4. [Baselines](RESULTADOS_BASELINES_COL9.md)
5. [Regressão da taxa](RESULTADOS_REGRESSAO_CONTINUA_COL9.md)
6. [Validação temporal](RESULTADOS_VALIDACAO_TEMPORAL_COL9.md)
7. [Validação espacial](RESULTADOS_VALIDACAO_ESPACIAL_COL9.md)
8. [Ablações e históricos congelados](RESULTADOS_ABLACAO_COL9.md)
9. [Área em hectares](RESULTADOS_REGRESSAO_AREA_HA_COL9.md)
10. [Interpretação e extremos](RELATORIO_INTERPRETACAO_MODELOS_COL9.md)
11. [Texto para dissertação](TEXTO_RESULTADOS_DISSERTACAO_COL9.md)
12. [Resumo executivo](RESUMO_EXECUTIVO_MODELOS_COL9.md)

O diretório ativo éexperimentos_regressao_col9/execucao_20261112_v4.
Dados/previsões/erros estão emParquet/CSV; gráficos emPNG/SVG e modelos
emskops/JSON nativo, sem pickle/joblib. O checkpoint inclui protocolo,
fontes, versões, grades, resultados, configurações e hashes. Reutilizar as
predições imutáveis para apresentação; a passagem do teste não será repetida.
Os39 rasters e acervos anteriores são referenciados sem duplicação.

T4 usa apenas a coorte2003–2022 com comparações pareadasT0–T4. A sensibilidade
congelada fixa os históricos, não a composição contemporânea de cobertura.
Resultados são magnitudes mapeadas, não probabilidades binárias ou áreas reais
corrigidas.2024 permanece reservado e oDOCX não foi atualizado.

O arquivoMANIFESTO_FINAL_MODELOS_COL9.json e o recibo do pacote registram a
integridade e as verificações de preservação. Um carregamento seguro requer
as versões fixadas e os dois tipos estruturais explicitamente revisados:
numpy.dtype e sklearn.tree._tree.Tree. Não autorizar tipos arbitrários.
''')
    print('Relatórios científicos e resumo executivo concluídos, sem novas escolhas ou ajustes.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--docs',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint,a.docs)

