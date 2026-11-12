# Ablações e sensibilidade de históricos
T0: território; T1: +composição/qualidade somente t; T2: +variações/tendências;
T3: +conversões encerradas até t; T4: +registros de focos.
As comparações diretas abaixo mantêm algoritmo e coorte. A coorte principal
começa em 1985; T0–T4 de focos usam 2003–2022. Seus períodos de treino diferem,
portanto mudanças entre coortes não são isoladamente efeito dos focos.

## principal — R_pct

| algoritmo | T0 | T1 | T2 | T3 |
|---|---|---|---|---|
| elastic_net | 2.9677 | 2.6897 | 2.3140 | 2.2324 |
| random_forest | 2.6081 | 2.5702 | 2.2507 | 2.2123 |
| ridge | 2.9841 | 2.6620 | 2.3156 | 2.2437 |
| xgboost | 2.6161 | 2.5758 | 2.2518 | 2.2883 |

## principal — C_ha

| algoritmo | T0 | T1 | T2 | T3 |
|---|---|---|---|---|
| elastic_net | 2123.8975 | 1898.1002 | 1316.7167 | 1325.0958 |
| random_forest | 1671.7772 | 1468.7379 | 1291.6317 | 1278.0890 |
| ridge | 2368.1573 | 1942.2784 | 1326.5709 | 1365.0643 |
| xgboost | 1698.5427 | 1509.0271 | 1258.4423 | 1279.7092 |

## focos 2003 — R_pct

| algoritmo | T0 | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| elastic_net | 2.9219 | 2.5560 | 2.3410 | 2.2049 | 2.2049 |
| random_forest | 2.5408 | 2.5065 | 2.2273 | 2.3000 | 2.3005 |
| ridge | 2.9216 | 2.5289 | 2.3301 | 2.2112 | 2.2200 |
| xgboost | 2.5407 | 2.5154 | 2.2388 | 2.2861 | 2.2948 |

## focos 2003 — C_ha

| algoritmo | T0 | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| elastic_net | 1791.9112 | 1556.8787 | 1293.0606 | 1258.0859 | 1294.4648 |
| random_forest | 1493.7284 | 1507.7251 | 1323.2294 | 1328.8896 | 1358.3481 |
| ridge | 2089.5837 | 2126.5585 | 1259.0915 | 1290.1753 | 1334.3478 |
| xgboost | 1681.9500 | 1516.4194 | 1286.6592 | 1345.9924 | 1382.6185 |

## Históricos congelados: sensibilidade sem novo ajuste
| target | bloco | algoritmo | congelado | movel | delta_congelado_menos_movel |
|---|---|---|---|---|---|
| C_ha | BASE | persistencia | 1613.3693 | 1232.9309 | 380.4384 |
| C_ha | T3 | elastic_net | 1531.3497 | 1325.0958 | 206.2539 |
| C_ha | T3 | random_forest | 1548.3489 | 1278.0890 | 270.2599 |
| C_ha | T3 | ridge | 1554.2666 | 1365.0643 | 189.2023 |
| C_ha | T3 | xgboost | 1559.7457 | 1279.7092 | 280.0365 |
| R_pct | BASE | persistencia | 2.8101 | 1.9895 | 0.8206 |
| R_pct | T3 | elastic_net | 2.5957 | 2.2324 | 0.3632 |
| R_pct | T3 | random_forest | 2.7111 | 2.2123 | 0.4988 |
| R_pct | T3 | ridge | 2.5990 | 2.2437 | 0.3553 |
| R_pct | T3 | xgboost | 2.7086 | 2.2883 | 0.4203 |

Usam-se os mesmos modelos/hiperparâmetros do regime móvel. Só os históricos
de T2/T3 foram fixados no ano de embargo anterior à avaliação: 2014 na
validação, 2018 no teste. Composição do mapa de t continua atual. Isso é uma
sensibilidade de entrada, não um segundo modelo retreinado nem uma simulação
operacional histórica completa. Nenhuma escolha foi refeita pelos resultados.

Retirar Coleção 9 ou seus históricos não prova ausência de vazamento do produtor.
Os mapas históricos podem carregar filtros de anos posteriores, mesmo em T1/T2.
As ablações descrevem associação incremental com a resposta mapeada, não
causalidade. Resultados de todos os algoritmos/estados estão nas tabelas completas;
não se selecionou a ablação de menor erro no teste para substituir o protocolo.
