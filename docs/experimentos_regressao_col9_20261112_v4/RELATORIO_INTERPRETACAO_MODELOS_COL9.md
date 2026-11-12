# Interpretação e diagnósticos
Importâncias foram calculadas somente na validação 2015–2017, antes de abrir
Yteste, para os vencedores supervisionados principais. Em cinco repetições,
trajetórias municipais foram permutadas dentro da UF. O incrementoMAE médio
mede dependência preditiva nesse suporte; DP das cinco permutações não é IC.
Colinearidade pode dividir/ocultar importância; permutação pode produzir
combinações pouco usuais. A validação também selecionou o modelo, portanto
não é estimativa externa independente de importância. Nenhum atributo foi
retirado por essa inspeção e nenhuma importância foi interpretada como causa.

## R_pct

| variavel_ou_grupo | mean | std |
|---|---|---|
| mb_taxa_passada_pct | 0.4162 | 0.0257 |
| mb_taxa_passada_pct_media_5anos | 0.0267 | 0.0040 |
| mb_taxa_passada_pct_media_3anos | 0.0247 | 0.0029 |
| mb_vn_t_ha | 0.0189 | 0.0025 |
| mb_pastagem_t_pct | 0.0123 | 0.0024 |
| territorio_lon_referencia | 0.0110 | 0.0028 |
| mb_vn_t_pct_tendencia_5anos | 0.0086 | 0.0021 |
| territorio_lat_referencia | 0.0076 | 0.0026 |
| mb_formacoes_florestais_t_pct | 0.0076 | 0.0015 |
| mb_savanica_t_ha | 0.0062 | 0.0026 |
| mb_formacoes_florestais_t_ha | 0.0062 | 0.0015 |
| mb_conv_passada_ha | 0.0058 | 0.0012 |
| mb_conv_passada_ha_media_3anos | 0.0047 | 0.0021 |
| mb_agricultura_t_pct | 0.0043 | 0.0022 |
| territorio_area_geodesica_ha | 0.0043 | 0.0005 |

## C_ha

| variavel_ou_grupo | mean | std |
|---|---|---|
| mb_conv_passada_ha | 831.5624 | 20.4573 |
| mb_conv_passada_ha_media_3anos | 135.6078 | 24.3184 |
| mb_vn_variacao_liquida_1ano_ha | 11.5231 | 2.2788 |
| mb_conv_passada_ha_media_5anos | 7.1600 | 1.4492 |
| mb_vn_t_ha | 6.1906 | 6.4807 |
| mb_ua_t_ha | 5.1532 | 3.4527 |
| mb_vn_t_ha_tendencia_3anos | 2.5586 | 0.3839 |
| mb_vn_variacao_liquida_1ano_pct | 2.4648 | 0.7012 |
| mb_taxa_passada_pct | 1.9496 | 1.9105 |
| mb_campestre_t_ha | 1.8182 | 0.7423 |
| mb_mosaico_t_ha | 1.6768 | 0.2354 |
| mb_vn_t_pct_tendencia_3anos | 1.5797 | 0.7663 |
| mb_agricultura_t_ha | 1.5461 | 0.6555 |
| mb_pastagem_t_ha | 0.6902 | 3.0234 |
| mb_classe25_t_pct | 0.6622 | 1.5283 |

## Maiores erros no teste —R
| NM_MUN | SIGLA_UF | ano_t | observado | previsto | erro |
|---|---|---|---|---|---|
| Figueirópolis D'Oeste | MT | 2022 | 52.9902 | 4.6995 | -48.2906 |
| São José dos Quatro Marcos | MT | 2022 | 49.2066 | 6.3192 | -42.8875 |
| Santa Inês | MA | 2022 | 52.0325 | 10.5127 | -41.5198 |
| Indiavaí | MT | 2022 | 44.8716 | 5.7316 | -39.1400 |
| Bom Lugar | MA | 2022 | 46.9802 | 8.7832 | -38.1971 |
| Vitorino Freire | MA | 2022 | 47.6794 | 9.5921 | -38.0872 |
| Sampaio | TO | 2021 | 38.6754 | 2.0829 | -36.5925 |
| Colinas do Tocantins | TO | 2022 | 37.4663 | 2.4421 | -35.0242 |
| Vitorino Freire | MA | 2021 | 39.9863 | 6.0763 | -33.9100 |
| Altamira do Maranhão | MA | 2021 | 40.0007 | 6.1646 | -33.8361 |

## Maiores erros no teste —C
| NM_MUN | SIGLA_UF | ano_t | observado | previsto | erro |
|---|---|---|---|---|---|
| Vila Bela da Santíssima Trindade | MT | 2021 | 36697.7641 | 3939.7575 | -32758.0065 |
| Santa Luzia | MA | 2021 | 33943.0529 | 5487.9504 | -28455.1025 |
| Santa Maria das Barreiras | PA | 2022 | 32913.0554 | 13564.8098 | -19348.2456 |
| Comodoro | MT | 2021 | 24880.3890 | 7094.1182 | -17786.2708 |
| Pontes e Lacerda | MT | 2022 | 29870.9417 | 12965.6324 | -16905.3093 |
| Pontes e Lacerda | MT | 2021 | 19345.5627 | 3216.2627 | -16129.3000 |
| Santana do Araguaia | PA | 2022 | 28797.3486 | 14084.1780 | -14713.1706 |
| Conceição do Araguaia | PA | 2022 | 25462.0747 | 11050.5288 | -14411.5459 |
| Nova Olímpia | MT | 2021 | 15031.5286 | 1103.2715 | -13928.2571 |
| Juara | MT | 2022 | 25723.8806 | 13155.5380 | -12568.3426 |

As figuras incluem observado×previsto, resíduos, distribuição de erros, médias
por ano, erros por UF, calibração e mapas. A análise usa as mesmas predições
imutáveis; nenhum modelo foi reexecutado para melhorar sua apresentação.
Os mapas são médias municipais 2019–2022 nos 255 polígonos canônicos, em
pontos percentuais ouha; não probabilidades binárias nem áreas reais corrigidas.
Escalas visuais abrangem os valores previstos/observados sem ocultar extrapolações.

Limitações centrais: referência 2023 insuficiente, baixa coincidência temática
no ano exato, possível filtragem retrospectiva do produtor, autocorrelação,
desigualdade entre estados, assimetria e extremos. Melhor desempenho de um
bloco não valida sua independência temporal. Intervalos preditivos formais
não foram calculados nem confundidos com incerteza cartográfica. Novos links,
perdas ou buffers exigiriam outro protocolo e decisão antes de novo teste,
não ajustes ao protocolo encerrado para melhorar os números apresentados.
