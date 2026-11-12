# Resultados dos baselines
Média/mediana históricas são globais do treino de cada contexto, não municipais;
LOSO as calcula apenas nos estados não retidos. Persistência usa a última
conversão encerrada até t; eventual falta recebe a mediana do treino, sem
ser interpretada como ausência de conversão. As baselines não utilizam D futuro.

| coorte | target | algoritmo | regime | n | MAE_validacao | MAE | RMSE | vies | R2 |
|---|---|---|---|---|---|---|---|---|---|
| focos2003 | C_ha | media_historica | movel | 1020 | 2140.8087 | 2594.1117 | 4364.4212 | -495.6910 | -0.0131 |
| focos2003 | C_ha | mediana_historica | movel | 1020 | 1574.2659 | 2456.3115 | 4735.2788 | -1902.7354 | -0.1925 |
| focos2003 | C_ha | persistencia | movel | 1020 | 565.0882 | 1232.9309 | 2721.1648 | -597.6619 | 0.6062 |
| focos2003 | R_pct | media_historica | movel | 1020 | 1.3861 | 3.1078 | 6.6646 | -1.7798 | -0.0768 |
| focos2003 | R_pct | mediana_historica | movel | 1020 | 1.2574 | 3.1429 | 6.8146 | -2.2783 | -0.1258 |
| focos2003 | R_pct | persistencia | movel | 1020 | 0.6547 | 1.9895 | 4.7879 | -1.2470 | 0.4442 |
| principal | C_ha | media_historica | movel | 1020 | 2837.8448 | 3062.7841 | 4380.1962 | 619.3993 | -0.0204 |
| principal | C_ha | mediana_historica | movel | 1020 | 1632.3915 | 2421.2788 | 4617.0549 | -1585.7911 | -0.1337 |
| principal | C_ha | persistencia | congelado | 1020 | 833.4723 | 1613.3693 | 3200.8598 | -1157.0472 | 0.4551 |
| principal | C_ha | persistencia | movel | 1020 | 565.0882 | 1232.9309 | 2721.1648 | -597.6619 | 0.6062 |
| principal | R_pct | media_historica | movel | 1020 | 1.6086 | 3.1484 | 6.5520 | -1.2963 | -0.0407 |
| principal | R_pct | mediana_historica | movel | 1020 | 1.2686 | 3.1258 | 6.7746 | -2.1555 | -0.1126 |
| principal | R_pct | persistencia | congelado | 1020 | 0.9132 | 2.8101 | 6.3963 | -2.1531 | 0.0082 |
| principal | R_pct | persistencia | movel | 1020 | 0.6547 | 1.9895 | 4.7879 | -1.2470 | 0.4442 |

As três alternativas foram congeladas antes do teste. A melhor alternativa
incluindo baselines, segundo validação, foi R: BASE/persistencia
e C: T3/random_forest. O teste não redefiniu essa escolha.
Treino inicial t=1985–2013, embargo 2014, validação 2015–2017; refit final até 2017 excluindo 2014, embargo 2018 e teste 2019–2022. Coorte de focos: treino a partir de 2003, com mesmos anos de validação/teste e folds internos adaptados. Tuning por MAE na escala original nos folds internos; escolhas de algoritmo/bloco pela validação, jamais pelo teste. A origem móvel admite históricos observados até t, inclusive de intervalos anteriores do bloco reservado, sem usar esses rótulos para reajuste. 50 atributos derivados da Coleção 9 têm risco retrospectivo do produtor, não eliminado pelos testes de colunas. R/C são conversão mapeada, não verdade ambiental corrigida. Nenhum dado 2024, PRODES, área queimada ou socioeconomia entrou nos modelos.
