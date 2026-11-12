# Validação espacial: todos os cinco estados
Cada UF fica integralmente fora de ajuste, tuning, seleção, normalização,
imputação e calibração do seu experimento. O modelo/bloco porUF foi escolhido
na validação dos demais estados e só então aplicado à UF em 2019–2022.

| target | UF_retida | municipios | bloco | algoritmo | MAE_validacao | n | MAE | RMSE | vies | R2 |
|---|---|---|---|---|---|---|---|---|---|---|
| R_pct | MA | 95 | T3 | elastic_net | 0.6019 | 380 | 2.6366 | 6.0198 | -1.5848 | 0.3623 |
| R_pct | MT | 68 | T3 | random_forest | 0.7384 | 272 | 1.6389 | 5.5230 | -1.2338 | 0.1984 |
| R_pct | PA | 15 | T3 | xgboost | 0.6284 | 60 | 2.2642 | 3.2936 | -1.7499 | 0.0307 |
| R_pct | RO | 5 | T3 | xgboost | 0.6649 | 20 | 1.0913 | 2.0121 | -1.0199 | 0.4000 |
| R_pct | TO | 72 | T3 | xgboost | 0.6310 | 288 | 2.2566 | 5.1623 | -1.8322 | 0.0630 |
| C_ha | MA | 95 | T3 | xgboost | 660.6446 | 380 | 990.5662 | 2360.8308 | -707.6156 | 0.5719 |
| C_ha | MT | 68 | T3 | random_forest | 363.1824 | 272 | 1831.9047 | 3756.1811 | -1126.1408 | 0.4943 |
| C_ha | PA | 15 | T3 | random_forest | 524.4870 | 60 | 2534.8953 | 4837.0597 | -2383.9765 | 0.5541 |
| C_ha | RO | 5 | T3 | xgboost | 537.5898 | 20 | 1489.8044 | 2050.7493 | -1189.6852 | 0.5932 |
| C_ha | TO | 72 | T3 | xgboost | 604.4816 | 288 | 874.8097 | 1610.4348 | -675.3446 | 0.4924 |

| target | UF_retida | municipios | n | observado_min | observado_mediana | observado_max |
|---|---|---|---|---|---|---|
| R_pct | MA | 95 | 380 | 0.0535 | 3.4119 | 52.0325 |
| R_pct | MT | 68 | 272 | 0.1242 | 1.2203 | 52.9902 |
| R_pct | PA | 15 | 60 | 0.6423 | 4.0117 | 16.7103 |
| R_pct | RO | 5 | 20 | 0.4713 | 1.9499 | 11.2955 |
| R_pct | TO | 72 | 288 | 0.3686 | 3.0629 | 38.6754 |
| C_ha | MA | 95 | 380 | 6.6966 | 1180.3759 | 33943.0529 |
| C_ha | MT | 68 | 272 | 20.1892 | 3022.7639 | 36697.7641 |
| C_ha | PA | 15 | 60 | 106.5183 | 2253.2103 | 32913.0554 |
| C_ha | RO | 5 | 20 | 759.4390 | 4358.4397 | 12205.2079 |
| C_ha | TO | 72 | 288 | 72.2328 | 1441.1640 | 13823.7688 |

MAE macro entre os cinco estados: R=1,978 p.p.;
C=1.544,396 ha. O resumo também fornece métricas micro das
predições LOSO reunidas, com cada município presente apenas em sua UF retida.
Macro e micro têm pesos diferentes; RO possui apenas 5 municípios/20 respostas.
Não se escolheu o melhor estado para apresentação nem se estimaram IC iid.

A transferência admite covariáveis locais conhecidas até t, inclusive histórico
mapeado no regime móvel; não simula uma região sem qualquer histórico.
Correlação entre municípios próximos/fronteiras permanece; nenhum buffer ou
grafo antigo 268 foi criado ou herdado. MapasLOSO combinam modelos possivelmente
distintos porUF, identificados na tabela, e não um único modelo nacional.
Cobertura dos preditores, contagens de ajuste e verificação das medianas estão
na auditoria de ajustes; as 52 ausências anuais de focos foram mantidas comoNA
na coorte restrita, antes da imputação computacional de cada treino.
