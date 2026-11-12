# Proposta de adequação metodológica da variável-alvo: da conversão significativa binária à magnitude contínua da conversão mapeada da vegetação nativa

**Nota para discussão com o orientador —12/11/2026. Proposta, não alteração homologada.**

O objetivo original previa ocorrência de conversão significativa de vegetação
nativa no ano seguinte, em escala município–ano. A estrutura já construída
compreende 39 mapas da Coleção 9,38 matrizes de transição e 9.690 observações
nos 255 municípios IBGE 2025. Ela permite medir C em hectares de VN(t)→UA(t+1)
e R=100 C/D sobre a vegetação inicial elegível. São medidas mapeadas, diferentes
de conversão ambiental real corrigida, variação líquida e desmatamento PRODES.

A comparação com referências oficiais mostrou precisão descritiva 26,81% e
sensibilidade 35,12% no ano exato; ampliar janelas aumenta coincidência sem
confirmar a data anual. Não há estimativa representativa própria da acurácia
das transições no recorte. 2023 tem apenas um ponto local com referência.
Persistem incertezas de suporte, interpretação, datação e dependência dos produtos.
Mudar para resposta contínua não elimina esses problemas.

A/B/C combinam percentuais e áreas mínimas, mas nenhum limiar foi homologado.
Prevalências 96,13%,90,37% e 75,18% não justificam ajustar limiares para balancear
classes. Relevância ambiental exige definição substantiva de pressão, estoque,
escala e consequências, não conveniência de classificação ou desempenho futuro.

Propõe-se priorizar R como candidata principal por preservar a magnitude
observada e comparação relativa, evitando dicotomização sem fundamento suficiente.
Sua mediana é 2,3067%, máximo 52,9902%; C tem mediana 1.627,79 ha e máximo 118.394,66 ha.
As posições dos municípios diferem entre as respostas. Recomenda-se C como
resposta secundária com experimento de regressão independente, se aprovado,
sem convertê-la usando D futuro realizado.

Redação proposta de objetivo geral: **avaliar a capacidade de modelos de regressão,
em validação temporal e espacial, de predizer a magnitude anual da conversão
mapeada de vegetação nativa no horizonte t+1 na ZCS Cerrado–Amazônia**.
Objetivos específicos: comparar baselines/modelos, contribuição de blocos,
heterogeneidade/erros/calibração e análise complementar em hectares, mantendo A/B/C
exploratórios. A hipótese passa a tratar de associação/informação preditiva
além de referências históricas, sem presumir causalidade ou conversão real validada.
Essas mudanças ainda exigem concordância do orientador.

A preparação entrega 53 atributos candidatos, respostas/qualidade separadas,
histórico até t,2023 sem resposta e partições propostas. Modelos: Ridge/Elastic Net,
Random Forest Regressor e XGBoost Regressor. Métricas: MAE/RMSE/viés em pontos
percentuais e R² complementar; para C, unidades em hectares. Nenhum treinamento,
otimização ou seleção de transformação foi executado.

Mantêm-se treino 1985–2013, embargo 2014, validação 2015–2017, embargo 2018 e
teste 2019–2022, com avanço interno; LOSO retém integralmente cada estado do
desenvolvimento e o avalia no período reservado. Extremos/anos finais já foram
explorados: o teste não é completamente cego à formulação. 2024 fica reservado.

Riscos restantes: erro/datação da resposta, filtragem retrospectiva, dependência
espacial/temporal, denominadores, coortes complementares e incompatibilidades
territoriais. Atributos construídos até t podem carregar informação posterior
no produto do classificador. Propõem-se ablações e decisão sobre origem móvel
versus históricos congelados no teste, sem resolver isso por publicação tardia.
Importância de variáveis será associação preditiva.

Solicita-se apreciação sobre objetivos/hipótese;R principal e papel de C;
A/B/C exploratórios; admissibilidade/ablações dos blocos; históricos, qualidade
e métricas; plano congelado de avaliação. Até concordância e posterior autorização
do pesquisador, não há objetivos alterados, desfecho definitivo ou treinamento homologados.
