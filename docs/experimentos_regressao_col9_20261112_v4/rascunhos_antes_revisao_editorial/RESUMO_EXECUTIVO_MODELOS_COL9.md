# Resumo executivo dos experimentos autorizados
Melhor supervisionado pela validação: R=T 3/xgboost;
C=T3/random_forest. Melhor incluindo baselines:
R=BASE/persistencia; C=T3/random_forest.
Nenhuma escolha foi refeita pelo teste.

| Resposta | MAE validação do supervisionado | MAE teste | RMSE teste | Viés teste | R² teste | MAE persistência teste |
|---|---: |---: |---: |---: |---: |---: |
| R, p.p. |0,660|2,288|5,795|-1,858|0,186|1,989|
| C, ha |538,793|1.278,089|2.809,216|-946,659|0,580|1.232,931|

LOSO micro: R MAE 2,211 p.p.; C MAE 1.282,871 ha.
Todos os cinco estados são apresentados, com seus números de municípios.
Os 108 grupos de desenvolvimento produziram 504 modelos finais, incluindo
baselines. A auditoria independente conferiu alvo/normalização/imputação
dos 504 modelos e exclusão das UFs retidas.

Ablacões, focos em coorte separada e históricos congelados estão documentados
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
