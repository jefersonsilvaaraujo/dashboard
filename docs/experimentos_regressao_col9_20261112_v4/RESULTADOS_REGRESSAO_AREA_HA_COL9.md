# Experimento complementar de área convertida
C foi ajustada diretamente como resposta própria, nunca R prevista×D realizado.
O vencedor supervisionado por validação foiT3/random_forest,
MAE de validação 538,793 ha; no teste:
MAE 1.278,089 ha, RMSE 2.809,216 ha, viés-946,659 ha,
R²0,580. Persistência teve MAE 1.232,931 ha no mesmo teste.

| target | bloco | algoritmo | n | MAE | RMSE | vies | R2 | n_pred_negativas | n_pred_acima_limite |
|---|---|---|---|---|---|---|---|---|---|
| C_ha | BASE | media_historica | 1020 | 3062.7841 | 4380.1962 | 619.3993 | -0.0204 | 0 | 12 |
| C_ha | BASE | mediana_historica | 1020 | 2421.2788 | 4617.0549 | -1585.7911 | -0.1337 | 0 | 0 |
| C_ha | BASE | persistencia | 1020 | 1232.9309 | 2721.1648 | -597.6619 | 0.6062 | 0 | 0 |
| C_ha | T0 | elastic_net | 1020 | 2123.8975 | 3632.0650 | 619.3993 | 0.2984 | 0 | 0 |
| C_ha | T0 | random_forest | 1020 | 1671.7772 | 2993.3448 | -209.8152 | 0.5235 | 0 | 0 |
| C_ha | T0 | ridge | 1020 | 2368.1573 | 5349.2580 | -460.6205 | -0.5219 | 0 | 0 |
| C_ha | T0 | xgboost | 1020 | 1698.5427 | 3162.0484 | -398.6611 | 0.4682 | 0 | 0 |
| C_ha | T1 | elastic_net | 1020 | 1898.1002 | 3146.5328 | 332.3996 | 0.4734 | 58 | 0 |
| C_ha | T1 | random_forest | 1020 | 1468.7379 | 3118.0371 | -965.2825 | 0.4829 | 0 | 0 |
| C_ha | T1 | ridge | 1020 | 1942.2784 | 3194.1234 | 232.1416 | 0.4574 | 59 | 0 |
| C_ha | T1 | xgboost | 1020 | 1509.0271 | 3199.5311 | -959.2954 | 0.4556 | 0 | 0 |
| C_ha | T2 | elastic_net | 1020 | 1316.7167 | 2596.6028 | -497.5444 | 0.6414 | 18 | 0 |
| C_ha | T2 | random_forest | 1020 | 1291.6317 | 2787.3232 | -824.3531 | 0.5868 | 0 | 0 |
| C_ha | T2 | ridge | 1020 | 1326.5709 | 2574.1455 | -497.0716 | 0.6476 | 36 | 0 |
| C_ha | T2 | xgboost | 1020 | 1258.4423 | 2698.0176 | -826.4896 | 0.6129 | 0 | 0 |
| C_ha | T3 | elastic_net | 1020 | 1325.0958 | 2727.2674 | -834.2190 | 0.6044 | 30 | 0 |
| C_ha | T3 | random_forest | 1020 | 1278.0890 | 2809.2162 | -946.6586 | 0.5803 | 0 | 0 |
| C_ha | T3 | ridge | 1020 | 1365.0643 | 2750.4356 | -875.2758 | 0.5977 | 53 | 0 |
| C_ha | T3 | xgboost | 1020 | 1279.7092 | 2850.5630 | -979.3806 | 0.5678 | 0 | 0 |

| coorte | contexto | bloco | algoritmo | transformacao_escolhida_no_CV |
|---|---|---|---|---|
| principal | temporal | BASE | media_historica | original_baseline |
| principal | temporal | BASE | mediana_historica | original_baseline |
| principal | temporal | BASE | persistencia | original_baseline |
| principal | temporal | T0 | ridge | log1p |
| principal | temporal | T0 | elastic_net | identidade |
| principal | temporal | T0 | random_forest | log1p |
| principal | temporal | T0 | xgboost | log1p |
| principal | temporal | T1 | ridge | identidade |
| principal | temporal | T1 | elastic_net | identidade |
| principal | temporal | T1 | random_forest | log1p |
| principal | temporal | T1 | xgboost | log1p |
| principal | temporal | T2 | ridge | identidade |
| principal | temporal | T2 | elastic_net | identidade |
| principal | temporal | T2 | random_forest | log1p |
| principal | temporal | T2 | xgboost | log1p |
| principal | temporal | T3 | ridge | identidade |
| principal | temporal | T3 | elastic_net | identidade |
| principal | temporal | T3 | random_forest | log1p |
| principal | temporal | T3 | xgboost | log1p |
| focos2003 | temporal | BASE | media_historica | original_baseline |
| focos2003 | temporal | BASE | mediana_historica | original_baseline |
| focos2003 | temporal | BASE | persistencia | original_baseline |
| focos2003 | temporal | T0 | ridge | log1p |
| focos2003 | temporal | T0 | elastic_net | identidade |
| focos2003 | temporal | T0 | random_forest | log1p |
| focos2003 | temporal | T0 | xgboost | log1p |
| focos2003 | temporal | T1 | ridge | log1p |
| focos2003 | temporal | T1 | elastic_net | identidade |
| focos2003 | temporal | T1 | random_forest | log1p |
| focos2003 | temporal | T1 | xgboost | log1p |
| focos2003 | temporal | T2 | ridge | identidade |
| focos2003 | temporal | T2 | elastic_net | identidade |
| focos2003 | temporal | T2 | random_forest | log1p |
| focos2003 | temporal | T2 | xgboost | log1p |
| focos2003 | temporal | T3 | ridge | identidade |
| focos2003 | temporal | T3 | elastic_net | identidade |
| focos2003 | temporal | T3 | random_forest | log1p |
| focos2003 | temporal | T3 | xgboost | log1p |
| focos2003 | temporal | T4 | ridge | identidade |
| focos2003 | temporal | T4 | elastic_net | identidade |
| focos2003 | temporal | T4 | random_forest | log1p |
| focos2003 | temporal | T4 | xgboost | log1p |

Identidade/log1p foram comparadas somente no CV do desenvolvimento. Toda
predição retornou à escala original antes das métricas, sem smearing ajustado
com teste ou correção por precisão cartográfica. Inversão da média log não
equivale automaticamente à média original; a seleção foi pela perdaMAE em hectares.

Negativas são reportadas sem clipping. O limite superior diagnóstico é a VN
observada somente em t, não D da máscara futura. Isso não é uma restrição
aplicada ao modelo nem uso de D como preditor. Extremos, distribuição por UF,
período e estoque devem ser considerados antes de extrapolar a interpretação.

R mede pressão relativa sobre estoque elegível; C mede escala absoluta municipal.
Não se comparaMAE em hectares com pontos percentuais para declarar uma resposta superior.
A soma das áreas anuais não significa área única desmatada. Este é desempenho
contra conversão mapeada, distinto de acurácia temática e conversão ambiental real.
