# Modelo de referência: risco de desmatamento no ano seguinte

Gerado por `modelagem/modelo_base.py` a partir de `historico/painel_municipio_ano.csv`.

- **Alvo:** taxa de desmatamento PRODES no ano seguinte (% da vegetação nativa no início daquele ano).
- **Divisão temporal, sem embaralhar anos:** configuração escolhida treinando com 2013–2017 e validando em 2018–2019; depois, treino com 2013–2019 (1820 linhas) e avaliação única no teste 2020–2024 (1300 linhas).
- **Modelo:** gradient boosting de histogramas (scikit-learn), 41 variáveis (áreas como fração da área do município), alvo em log(1 + taxa).
- **Regras de referência:** persistência (o ano seguinte repete o atual) e média dos últimos 3 anos.

## Escolha da configuração (validação 2018–2019)

| modelo | erro_medio_absoluto_pp | correlacao_ranking_spearman | acerto_top_20pct |
|---|---|---|---|
| moderado | 0.631 | 0.630 | 0.490 |
| moderado + desvio da persistência | 0.638 | 0.598 | 0.481 |
| regularizado | 0.603 | 0.670 | 0.529 |
| regularizado + desvio da persistência | 0.602 | 0.645 | 0.519 |

Escolhida pela maior correlação de ranking: **regularizado**.

## Desempenho no teste

| modelo | erro_medio_absoluto_pp | correlacao_ranking_spearman | acerto_top_20pct |
|---|---|---|---|
| Persistência (repete o ano atual) | 0.688 | 0.711 | 0.581 |
| Média dos últimos 3 anos | 0.683 | 0.734 | 0.577 |
| Gradient boosting (regularizado) | 0.675 | 0.721 | 0.515 |

- `erro_medio_absoluto_pp`: erro médio absoluto, em pontos percentuais de taxa (menor é melhor).
- `correlacao_ranking_spearman`: concordância entre a ordem prevista e a real dos municípios (maior é melhor).
- `acerto_top_20pct`: entre os 20% de municípios com maior risco previsto em cada ano, fração que estava de fato entre os 20% com maior taxa real.

## Variáveis mais importantes

Queda na correlação de ranking (teste) quando a variável é embaralhada; média de 10 repetições.

| variavel | importancia | desvio |
|---|---|---|
| pd_desmatamento_ha_lag1 | 0.144 | 0.011 |
| pd_taxa_desmatamento | 0.089 | 0.009 |
| pd_desmatamento_ha_mm3 | 0.067 | 0.008 |
| pd_desmatamento_ha_lag2 | 0.022 | 0.002 |
| latitude | 0.009 | 0.002 |
| fq_densidade_focos | 0.008 | 0.001 |
| pd_desmatamento_acumulado_ha | 0.006 | 0.003 |
| pct_amazonia | 0.004 | 0.001 |
| pd_residuo_ha | 0.003 | 0.003 |
| longitude | 0.003 | 0.001 |
| pct_cerrado | 0.002 | 0.000 |
| fq_focos_lag2 | 0.001 | 0.000 |
| fq_focos_ano_civil | 0.001 | 0.000 |
| fq_focos_mm3 | 0.001 | 0.000 |
| fq_dias_sem_chuva_medio | 0.000 | 0.000 |

## Risco previsto para 2026

Modelo treinado com todos os anos com alvo e aplicado ao último ano do painel. Arquivo completo:
`risco_previsto_2026.csv`. Os 15 municípios de maior risco:

| posicao | nm_mun | sigla_uf | bioma_predominante | taxa_prevista_pct |
|---|---|---|---|---|
| 1 | Bernardo do Mearim | MA | Cerrado | 3.607 |
| 2 | Marajá do Sena | MA | Cerrado | 3.222 |
| 3 | Joselândia | MA | Cerrado | 3.070 |
| 4 | Lagoa Grande do Maranhão | MA | Cerrado | 2.813 |
| 5 | Pedreiras | MA | Cerrado | 2.789 |
| 6 | Santo Antônio dos Lopes | MA | Cerrado | 2.756 |
| 7 | Pirapemas | MA | Cerrado | 2.644 |
| 8 | Matões do Norte | MA | Cerrado | 2.557 |
| 9 | Peritoró | MA | Cerrado | 2.460 |
| 10 | Alto Alegre do Maranhão | MA | Cerrado | 2.445 |
| 11 | Lima Campos | MA | Cerrado | 2.439 |
| 12 | Buriti do Tocantins | TO | Amazônia | 2.413 |
| 13 | Aguiarnópolis | TO | Cerrado | 2.355 |
| 14 | Coroatá | MA | Cerrado | 2.343 |
| 15 | São Luís Gonzaga do Maranhão | MA | Cerrado | 2.251 |

## Leitura dos resultados

O modelo supera as regras simples em: erro médio. Não supera a melhor regra simples em: ranking, acerto nos 20% de maior risco. As variáveis de histórico de desmatamento respondem por 91% da importância total: o desmatamento futuro de um município é previsto sobretudo pelo seu próprio passado recente. Para ir além da persistência, a modelagem da dissertação precisa de fatores externos ao histórico (acesso por estradas, distância à borda do desmatamento, situação fundiária/CAR, embargos, preços de commodities, anomalias climáticas).

## Limitações

- Modelo de referência, com uma busca pequena de configurações; serve de linha de base para os modelos da dissertação.
- A taxa é relativa à vegetação nativa restante: municípios com pouca vegetação remanescente tendem a taxas altas mesmo com pouca área desmatada. Para priorização territorial, considere também a área prevista em hectares.
- Atributos de focos (FRP, risco de fogo, dias sem chuva) faltam em parte dos anos; o modelo trata ausências nativamente.
- As variáveis de vizinhança usam o mesmo ano das demais (não antecipam o alvo, que é do ano seguinte).
