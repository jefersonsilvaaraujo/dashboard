# Validação temporal
Nenhum resultado 2019–2022 foi usado para tuning ou seleção. O marcador de
abertura única foi criado depois de todas as predições finais serem salvas
sem Y. A apresentação reagrupa essas mesmas predições; não executa novos modelos.

Taxa: vencedor T3/xgboost.
| ano_t | n | MAE | RMSE | vies | R2 | n_pred_negativas | n_pred_acima_limite |
|---|---|---|---|---|---|---|---|
| 2019 | 255 | 0.6882 | 0.9852 | -0.0188 | 0.6925 | 0 | 0 |
| 2020 | 255 | 0.6394 | 0.9602 | -0.0182 | 0.6956 | 0 | 0 |
| 2021 | 255 | 3.5519 | 7.4633 | -3.4002 | 0.0059 | 0 | 0 |
| 2022 | 255 | 4.2735 | 8.7610 | -3.9941 | 0.0830 | 0 | 0 |

Área: vencedor T3/random_forest.
| ano_t | n | MAE | RMSE | vies | R2 | n_pred_negativas | n_pred_acima_limite |
|---|---|---|---|---|---|---|---|
| 2019 | 255 | 509.4876 | 890.6665 | -106.5695 | 0.8965 | 0 | 0 |
| 2020 | 255 | 578.6661 | 1278.7345 | -28.7770 | 0.7790 | 0 | 0 |
| 2021 | 255 | 1877.3682 | 3984.4602 | -1773.3715 | 0.3221 | 0 | 0 |
| 2022 | 255 | 2146.8340 | 3641.7593 | -1877.9162 | 0.5848 | 0 | 0 |

Os erros não devem ser atribuídos apenas à mudança temporal: o modelo final
foi reajustado com desenvolvimento até 2017, enquanto a validação usa ajuste
inicial até 2013. Extremos e anos finais já haviam sido explorados cientificamente:
o teste não é completamente cego à formulação. Referência 2023 insuficiente
limita a interpretação ambiental do último intervalo 2022→2023.

Figuras observado×previsto, resíduos, série anual e calibração estão em apresentacao/figuras.
Faixas de calibração foram definidas pelas predições da validação antes do teste.
Faixas de magnitude dos erros usam quartis da resposta do treino inicial;
não se recalcularam cortes com o teste. R² indefinido em grupos sem variância
permanece ausente; MAPE não foi métrica principal.

Treino inicial t=1985–2013, embargo 2014, validação 2015–2017; refit final até 2017 excluindo 2014, embargo 2018 e teste 2019–2022. Coorte de focos: treino a partir de 2003, com mesmos anos de validação/teste e folds internos adaptados. Tuning por MAE na escala original nos folds internos; escolhas de algoritmo/bloco pela validação, jamais pelo teste. A origem móvel admite históricos observados até t, inclusive de intervalos anteriores do bloco reservado, sem usar esses rótulos para reajuste. 50 atributos derivados da Coleção 9 têm risco retrospectivo do produtor, não eliminado pelos testes de colunas. R/C são conversão mapeada, não verdade ambiental corrigida. Nenhum dado 2024, PRODES, área queimada ou socioeconomia entrou nos modelos.
