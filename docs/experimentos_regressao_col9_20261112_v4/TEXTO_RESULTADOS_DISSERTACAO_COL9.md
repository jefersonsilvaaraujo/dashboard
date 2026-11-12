# Texto proposto para resultados e discussão da dissertação
O protocolo foi auditado e congelado antes do ajuste, utilizando 9.690
observações município–ano de 255 municípios e a Coleção 9 em 1985–2023.
Compararam-se regressões Ridge/Elastic Net, Random Forest e XGBoost,
além de média, mediana e persistência. O ajuste de hiperparâmetros ocorreu
por avanço temporal no desenvolvimento, e a seleção final pela validação
de 2015–2017. A avaliação reservada abrangeut 2019–2022; 2024 não foi utilizado.

Para a taxa percentual R, o melhor modelo supervisionado segundo validação
foixgboost comT3, MAE de validação
0,660 pontos percentuais. No teste, obteve
MAE 2,288 p.p., RMSE 5,795 p.p., viés
-1,858 p.p. e R²0,186. A persistência apresentou
MAE 1,989 p.p. no mesmo suporte. Essa comparação não foi
utilizada para trocar o modelo escolhido na validação.

A validação espacial reteve integralmente cada estado do desenvolvimento
do seu fold. As predições dos modelos por UF escolhidos na validação externa
à UF tiveramMAE micro 2,211 p.p. para R e
1.282,871 ha para C. As médias macro entreUFs foram
1,978 p.p. e 1.544,396 ha, respectivamente.
Essas agregações têm pesos distintos, e RO possui apenas cinco municípios.

No experimento independente de área, o vencedor supervisionado por validação
foirandom_forest comT3. No teste, MAE
1.278,089 ha, RMSE 2.809,216 ha, viés
-946,659 ha e R²0,580; persistência:
MAE 1.232,931 ha. As previsões de C não foram derivadas de R usando
D futuro. A interpretação absoluta difere da pressão relativaR e foi mantida
separada na análise, com retorno à escala original após transformações.

As ablaçõesT0–T3 compartilharam coorte e partições. A análise de focos foi
separada, comparandoT0–T4 na coorte 2003–2022, mantendoNA quando inexistiam
registros e sem tratar focos como área queimada. A sensibilidade com históricos
congelados reutilizou modelos/hiperparâmetros, alterando apenas entradas históricas,
sem retuning. Essas comparações não demonstram causalidade ou ausência de
dependência temporal nos produtos derivados daColeção 9.

Os resultados expressam desempenho de regressão contra conversão mapeada.
Não corrigem erro cartográfico nem validam conversão ambiental real. A baixa
coincidência descritiva das transições anuais com referências, a lacuna de 2023,
a filtragem retrospectiva e a exploração científica anterior dos anos finais
limitam afirmações confirmatórias. O teste foi separado do ajuste e aberto
uma única vez para avaliação final, mas não era completamente cego à formulação
do estudo. Previsões fora dos limites físicos foram explicitamente reportadas,
sem truncamento silencioso. Importância preditiva não foi interpretada causalmente.


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
