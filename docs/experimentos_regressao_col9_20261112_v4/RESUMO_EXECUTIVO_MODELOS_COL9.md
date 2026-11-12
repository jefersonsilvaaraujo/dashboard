# Resumo executivo dos experimentos autorizados
Melhor supervisionado pela validação: R=T3/xgboost;
C=T3/random_forest. Melhor incluindo baselines:
R=BASE/persistencia; C=T3/random_forest.
Nenhuma escolha foi refeita pelo teste.

| Resposta | MAE validação do supervisionado | MAE teste | RMSE teste | Viés teste | R² teste | MAE persistência teste |
|---|---:|---:|---:|---:|---:|---:|
| R, p.p. |0,660|2,288|5,795|-1,858|0,186|1,989|
| C, ha |538,793|1.278,089|2.809,216|-946,659|0,580|1.232,931|

LOSO micro: R MAE 2,211 p.p.; C MAE 1.282,871 ha.
Todos os cinco estados são apresentados, com seus números de municípios.
Os 108 grupos de desenvolvimento produziram 504 modelos finais, incluindo
baselines. A auditoria independente conferiu alvo/normalização/imputação
dos 504 modelos e exclusão das UFs retidas.

Ablações, focos em coorte separada e históricos congelados estão documentados
sem escolha pós-teste. Os maiores erros, extrapolações e diferenças regionais
devem orientar a discussão; não foram eliminados para melhorar métricas.

Recomendação científica: discutir os resultados contra a persistência e os
blocos territoriais, explicitando a resposta mapeada, instabilidade temática,
dependência retrospectiva e desigualdade entre estados. Não reivindicar
conversão real corrigida, causalidade, disponibilidade operacional histórica
ou validação representativa própria da cartografia.

Banco, dashboard, rasters, matrizes, fontes e DOCX não foram alterados.
A aprovação foi registrada por adendo versionado ao diário. Os testes anteriores
e os 15 novos da revisão ativa passaram. Versões técnicas preliminares foram
preservadas antes do ajuste científico; revisaram apenas compatibilidade de
persistência segura, sem mudar grades, dados, partições ou critérios.
O protocolo e o marcador de abertura única permanecem verificáveis.


## Leitura substantiva dos resultados

A persistência é a referência central: já foi a melhor opção geral para R na
validação (MAE 0,6547 p.p., contra 0,6602 do XGBoost/T3). No teste, o MAE
do XGBoost foi aproximadamente 15,0% maior que o da persistência (2,2883
contra 1,9895 p.p.). Para C, a Random Forest/T3 venceu na validação, mas seu
MAE de teste foi aproximadamente 3,7% maior que o da persistência (1.278,09
contra 1.232,93 ha). Esses resultados não autorizam afirmar superioridade dos
modelos supervisionados sobre a continuidade recente da conversão mapeada.
As escolhas anteriores ao teste permanecem registradas, sem troca de vencedor.

Os erros cresceram nos intervalos com resposta em 2022 e 2023. Para R, o
XGBoost/T3 teve MAE de 0,6882 e 0,6394 p.p. em t=2019 e 2020; em t=2021
e 2022, 3,5519 e 4,2735 p.p. A subestimação é forte: viés global de
−1,8578 p.p. e de −3,9941 p.p. em t=2022. Isso descreve dificuldade diante
dos picos cartográficos; não demonstra aumento ambiental real na mesma medida,
nem permite separar mudança do processo ambiental de instabilidade de classificação.

As ablações mostram ganhos dos históricos em relação a T0 dentro da mesma
coorte, mas ganhos incrementais de T3 sobre T2 não são uniformes. Na coorte
2003, acrescentar focos em T4 não trouxe redução consistente de MAE entre os
quatro algoritmos. O resultado não justifica interpretar ausência de efeito
ambiental dos incêndios: os atributos representam registros observados de focos,
com limitações instrumentais e de cobertura, não área queimada harmonizada.

Na sensibilidade do vencedor principal para R, congelar os históricos em 2018
aumentou o MAE de 2,2883 para 2,7086 p.p.; para C, de 1.278,09 para
1.548,35 ha. Os modelos são os mesmos. A comparação evidencia dependência das
entradas recentes nesse experimento, sem provar ausência de informação futura
no processamento retrospectivo do produtor. Ela não representa uma simulação
operacional histórica completa.

No LOSO de R, o MAE variou de 1,0913 p.p. (RO, 20 observações) a 2,6366
p.p. (MA, 380). O composto micro foi 2,2110 p.p.; os modelos por estado
foram escolhidos sem a UF retida. Comparar diretamente esse valor com o teste
temporal não isola efeito espacial, porque modelos e conjuntos de ajuste diferem.
Houve três previsões negativas no fold MA de Elastic Net, preservadas e reportadas.

A conclusão sustentada é que há associação preditiva com a série mapeada,
sobretudo com sua continuidade recente, mas a generalização aos picos finais é
limitada. A contribuição científica deve incluir esse limite, a ausência de
estimativa representativa própria da acurácia de transições e a lacuna de
referência em 2023. Uma nova transformação ou protocolo motivado por estes
resultados exigiria nova decisão e avaliação independente; o teste encerrado
não poderá fundamentar uma nova alegação confirmatória sobre o mesmo suporte.
