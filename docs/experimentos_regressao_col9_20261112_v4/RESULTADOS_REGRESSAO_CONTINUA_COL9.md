# Regressão da taxa percentual anual mapeada
O vencedor supervisionado da validação foi **T3/xgboost**,
MAE de validação 0,660 pontos percentuais.
No teste reservado: MAE 2,288 p.p.; RMSE 5,795 p.p.;
viés-1,858 p.p.; R²0,186. O viés tem sinal previsto−observado.

| target | bloco | algoritmo | n | MAE | RMSE | vies | R2 | n_pred_negativas | n_pred_acima_limite |
|---|---|---|---|---|---|---|---|---|---|
| R_pct | BASE | media_historica | 1020 | 3.1484 | 6.5520 | -1.2963 | -0.0407 | 0 | 0 |
| R_pct | BASE | mediana_historica | 1020 | 3.1258 | 6.7746 | -2.1555 | -0.1126 | 0 | 0 |
| R_pct | BASE | persistencia | 1020 | 1.9895 | 4.7879 | -1.2470 | 0.4442 | 0 | 0 |
| R_pct | T0 | elastic_net | 1020 | 2.9677 | 6.4271 | -1.2963 | -0.0014 | 4 | 0 |
| R_pct | T0 | random_forest | 1020 | 2.6081 | 5.7421 | -1.2944 | 0.2007 | 0 | 0 |
| R_pct | T0 | ridge | 1020 | 2.9841 | 6.4081 | -1.2963 | 0.0045 | 8 | 0 |
| R_pct | T0 | xgboost | 1020 | 2.6161 | 5.7299 | -1.2969 | 0.2041 | 0 | 0 |
| R_pct | T1 | elastic_net | 1020 | 2.6897 | 5.8528 | -0.6321 | 0.1695 | 0 | 0 |
| R_pct | T1 | random_forest | 1020 | 2.5702 | 6.1688 | -1.7735 | 0.0775 | 0 | 0 |
| R_pct | T1 | ridge | 1020 | 2.6620 | 5.8348 | -0.6530 | 0.1746 | 0 | 0 |
| R_pct | T1 | xgboost | 1020 | 2.5758 | 6.1698 | -1.7462 | 0.0772 | 0 | 0 |
| R_pct | T2 | elastic_net | 1020 | 2.3140 | 5.5899 | -1.1708 | 0.2425 | 17 | 0 |
| R_pct | T2 | random_forest | 1020 | 2.2507 | 5.6785 | -1.5889 | 0.2183 | 0 | 0 |
| R_pct | T2 | ridge | 1020 | 2.3156 | 5.5905 | -1.1724 | 0.2423 | 19 | 0 |
| R_pct | T2 | xgboost | 1020 | 2.2518 | 5.6630 | -1.6387 | 0.2225 | 0 | 0 |
| R_pct | T3 | elastic_net | 1020 | 2.2324 | 5.3996 | -1.7287 | 0.2932 | 24 | 0 |
| R_pct | T3 | random_forest | 1020 | 2.2123 | 5.6456 | -1.7104 | 0.2273 | 0 | 0 |
| R_pct | T3 | ridge | 1020 | 2.2437 | 5.4090 | -1.7370 | 0.2907 | 30 | 0 |
| R_pct | T3 | xgboost | 1020 | 2.2883 | 5.7954 | -1.8578 | 0.1857 | 0 | 0 |

São 1020 observações dos 255 municípios emt 2019–2022, com respostas 2020–2023.
A tabela mostra todos os modelos e baselines, não um vencedor escolhido pelo
teste. Predições negativas/acima de 100 foram mantidas e contadas, sem clipping.
As diferenças finitas não foram corrigidas pelos 26,81% de precisão temática
descritiva. O desempenho mede concordância preditiva com a conversão mapeada.

As escolhas e métricas de validação estão em METRICAS_VALIDACAO_CONGELADAS.parquet;
configurações/folds em AJUSTES_CV_DESENVOLVIMENTO.parquet. As grades têm 3 Ridge,
4 ElasticNet,2 Forest e 2 XGBoost por transformação. R usa identidade; C compara
identidade/log1p no desenvolvimento. Normalização de y usa média/DP do treino
e é invertida antes das métricas. Colunas ausentes usam medianas do treino e
indicadores; coluna totalmente ausente é removida da parte de valores, sem
inventar zero físico. A auditoria conferiu os parâmetros de 504 modelos finais.

Treino inicial t=1985–2013, embargo 2014, validação 2015–2017; refit final até 2017 excluindo 2014, embargo 2018 e teste 2019–2022. Coorte de focos: treino a partir de 2003, com mesmos anos de validação/teste e folds internos adaptados. Tuning por MAE na escala original nos folds internos; escolhas de algoritmo/bloco pela validação, jamais pelo teste. A origem móvel admite históricos observados até t, inclusive de intervalos anteriores do bloco reservado, sem usar esses rótulos para reajuste. 50 atributos derivados da Coleção 9 têm risco retrospectivo do produtor, não eliminado pelos testes de colunas. R/C são conversão mapeada, não verdade ambiental corrigida. Nenhum dado 2024, PRODES, área queimada ou socioeconomia entrou nos modelos.
