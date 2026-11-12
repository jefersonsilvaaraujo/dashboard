# Relatório exploratório de transições espaciais Coleção 9

Status: resultados contábeis auditados para validação científica; nenhum tau,
A_min ou elegibilidade mínima definitiva foi adotado. Nenhum alvo binário ou modelo
foi produzido. Unidade temporal: par t→t+1, identificado pelo ano de destino.

## Cobertura e integridade

Foram calculados 255 municípios × 38 pares = **9.690 comparações**, entre 1985→1986
e 2022→2023. Matrizes completas 29×29, de pixels e hectares, preservam as demais
classes para auditoria. Zero/27/NoData não participam; a linha/coluna 27 permanece
zerada na matriz densa. O suporte é a máscara válida comum de cada par, sem reamostragem.

Os 9.945 estoques município–ano foram comparados ao consolidado aprovado:
erro máximo **0 pixels** e
**0,00005067 ha** por classe, compatível com o
arredondamento a quatro casas do consolidado. Soma de células, marginais, partições
de máscara e subconjunto triplo foram verificados independentemente.

O manifesto está em `referencias/manifesto_rasters_transicoes_col9.json`, com os
39 hashes, nomes, grades, NoData, origem, complemento e evidência de 2002. O raster
2002 validado é byte a byte idêntico ao alias usado no consolidado. A aprovação do
acervo e a validação amostral não são prova temática de todos os pixels dos 39 anos.

## Definição das medidas

VN inicial: 3,4,5,6,49,11,12,50. Destinos antrópicos: 9,15,20,21,24,30,31,35,
39,40,41,46,47,48,62. Área convertida C é a soma geodésica de VN(t)→UA(t+1).
Denominador D é a VN em t com observação válida nos dois anos. Taxa = 100 C/D;
denominador zero é NA, nunca evento negativo. Elegibilidade = 100 D/VN observada
inicialmente. A área de pixel varia com a latitude e foi calculada em WGS84.

As distribuições abaixo dão o mesmo peso a cada município–par observado. Elas
não são uma taxa regional por média simples: a taxa regional anual é calculada
separadamente por 100 soma(C)/soma(D). Quantis usam interpolação linear.

## Distribuições globais

| metrica | n_observados | n_na | min | p25 | mediana | p75 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|---|---|
| taxa_conversao_pct | 9690 | 0 | 0,0008 | 1,1117 | 2,3067 | 4,0467 | 9,2927 | 16,6663 | 52,9902 |
| area_convertida_ha | 9690 | 0 | 0,8037 | 654,9623 | 1.627,7880 | 4.127,5277 | 14.654,4981 | 27.297,6177 | 118.394,6586 |
| vn_inicial_elegivel_ha | 9690 | 0 | 2.080,1283 | 29.951,6053 | 71.835,0198 | 205.176,7280 | 994.238,2331 | 1.841.628,2356 | 2.602.022,5663 |
| elegibilidade_vn_pct | 9690 | 0 | 99,7016 | 100,0000 | 100,0000 | 100,0000 | 100,0000 | 100,0000 | 100,0000 |
| cobertura_comum_area_grade_pct | 9690 | 0 | 99,5787 | 100,0000 | 100,0000 | 100,0000 | 100,0000 | 100,0000 | 100,0000 |

CSV completo: `resultados_transicoes_col9\integral_255_1985_2023_20261111\analise_exploratoria\distribuicoes_globais.csv`. Distribuições por ano e por
município são fornecidas em arquivos próprios, com medianas, percentis e extremos.
Áreas somadas em anos diferentes representam hectares-evento e podem conter
reconversões do mesmo local; não equivalem a área territorial única.

## Maiores taxas municipais

| NM_MUN | SIGLA_UF | ano_destino | taxa_conversao_pct | area_convertida_ha | vn_inicial_elegivel_ha | elegibilidade_vn_pct |
|---|---|---|---|---|---|---|
| Figueirópolis D'Oeste | MT | 2023 | 52,9902 | 3.595,2532 | 6.784,7563 | 100,0000 |
| Santa Inês | MA | 2023 | 52,0325 | 4.055,9762 | 7.795,0801 | 100,0000 |
| São José dos Quatro Marcos | MT | 2023 | 49,2066 | 5.348,8469 | 10.870,1748 | 100,0000 |
| Vitorino Freire | MA | 2023 | 47,6794 | 6.481,4571 | 13.593,8386 | 100,0000 |
| Bom Lugar | MA | 2023 | 46,9802 | 977,2486 | 2.080,1283 | 100,0000 |
| Indiavaí | MT | 2023 | 44,8716 | 2.921,8337 | 6.511,5367 | 100,0000 |
| Altamira do Maranhão | MA | 2023 | 42,3055 | 3.028,0999 | 7.157,6977 | 100,0000 |
| Santa Inês | MA | 2022 | 40,5903 | 5.335,6791 | 13.145,2142 | 100,0000 |
| Altamira do Maranhão | MA | 2022 | 40,0007 | 4.774,7996 | 11.936,7774 | 100,0000 |
| Vitorino Freire | MA | 2022 | 39,9863 | 9.131,2301 | 22.835,9000 | 100,0000 |
| Bom Lugar | MA | 2022 | 39,0100 | 1.359,6724 | 3.485,4451 | 100,0000 |
| Sampaio | TO | 2022 | 38,6754 | 4.421,2431 | 11.431,6623 | 100,0000 |

Taxas altas precisam ser lidas junto à VN elegível e à área absoluta: pequenos
denominadores podem gerar valores extremos sem grande conversão em hectares.

## Maiores áreas absolutas convertidas

| NM_MUN | SIGLA_UF | ano_destino | taxa_conversao_pct | area_convertida_ha | vn_inicial_elegivel_ha | elegibilidade_vn_pct |
|---|---|---|---|---|---|---|
| Vila Bela da Santíssima Trindade | MT | 1986 | 10,0423 | 118.394,6586 | 1.178.956,4995 | 99,9994 |
| Pontes e Lacerda | MT | 1986 | 10,0246 | 65.730,4288 | 655.689,3916 | 99,9998 |
| Santa Luzia | MA | 1998 | 24,8787 | 63.993,8479 | 257.223,1920 | 100,0000 |
| Querência | MT | 2003 | 4,4201 | 62.364,7870 | 1.410.940,8770 | 100,0000 |
| Santana do Araguaia | PA | 2003 | 8,5326 | 61.772,9706 | 723.964,9327 | 100,0000 |
| Paranatinga | MT | 2003 | 3,3856 | 58.874,3828 | 1.738.984,9792 | 100,0000 |
| Santa Luzia | MA | 1989 | 15,0289 | 55.237,8502 | 367.545,3843 | 100,0000 |
| Juara | MT | 2004 | 3,3233 | 54.878,2291 | 1.651.302,7178 | 100,0000 |
| Gaúcha do Norte | MT | 2003 | 3,7984 | 53.072,2668 | 1.397.220,3516 | 100,0000 |
| Santa Luzia | MA | 1992 | 15,8130 | 51.982,6380 | 328.734,5778 | 100,0000 |
| Brasnorte | MT | 2004 | 4,5699 | 51.639,3283 | 1.129.998,4714 | 100,0000 |
| Nova Ubiratã | MT | 2003 | 7,1086 | 51.584,2413 | 725.659,2374 | 100,0000 |

Os arquivos `maiores_taxas.csv` e `maiores_areas.csv` contêm as 30 maiores
comparações, com códigos IBGE e ambos os anos para rastreamento.

## Variação temporal

| ano_destino | area_convertida_ha | vn_elegivel_ha | taxa_regional_razao_somas_pct | taxa_mediana_municipal_pct | elegibilidade_min_pct |
|---|---|---|---|---|---|
| 1986 | 1.394.059,2742 | 67.243.151,4021 | 2,0732 | 2,2364 | 99,9980 |
| 1987 | 1.087.260,8450 | 66.162.746,1606 | 1,6433 | 1,7678 | 99,9981 |
| 1988 | 1.058.228,0438 | 65.419.081,1867 | 1,6176 | 1,7718 | 99,9992 |
| 1989 | 1.066.370,2802 | 64.575.817,5614 | 1,6513 | 1,7231 | 99,9978 |
| 1990 | 851.774,1713 | 63.802.765,4959 | 1,3350 | 1,4874 | 99,9954 |
| 1991 | 903.674,1527 | 63.257.519,6176 | 1,4286 | 1,9169 | 99,9979 |
| 1992 | 1.237.849,9415 | 62.691.157,8245 | 1,9745 | 2,4497 | 99,9992 |
| 1993 | 1.196.047,4672 | 61.705.363,2958 | 1,9383 | 2,3286 | 99,9945 |
| 1994 | 1.310.296,4687 | 60.773.120,1048 | 2,1560 | 2,4299 | 99,9985 |
| 1995 | 1.458.729,0496 | 59.806.970,4659 | 2,4391 | 2,7806 | 99,9991 |
| 1996 | 1.297.403,7573 | 58.671.412,3646 | 2,2113 | 2,5480 | 99,9949 |
| 1997 | 1.219.668,2593 | 57.682.573,7094 | 2,1144 | 2,5730 | 99,9972 |
| 1998 | 1.334.767,6608 | 56.809.854,0340 | 2,3495 | 2,9056 | 99,9991 |
| 1999 | 1.241.396,3254 | 55.764.942,0178 | 2,2261 | 2,8674 | 99,9974 |
| 2000 | 1.098.427,2811 | 54.760.997,6608 | 2,0059 | 2,8995 | 99,9973 |
| 2001 | 1.070.874,7906 | 54.112.034,0414 | 1,9790 | 2,7815 | 99,9982 |
| 2002 | 1.146.138,1184 | 53.352.847,8156 | 2,1482 | 2,7406 | 99,9975 |
| 2003 | 1.639.858,3358 | 52.525.617,7788 | 3,1220 | 3,1154 | 99,7016 |
| 2004 | 1.373.913,6832 | 51.216.384,5950 | 2,6826 | 3,1949 | 99,9959 |
| 2005 | 1.097.794,6066 | 50.131.045,4314 | 2,1898 | 2,7521 | 99,9989 |
| 2006 | 787.995,2855 | 49.460.112,4351 | 1,5932 | 2,3103 | 99,9990 |
| 2007 | 684.549,1242 | 49.015.254,5984 | 1,3966 | 2,3062 | 99,9975 |
| 2008 | 768.676,6781 | 48.712.818,8683 | 1,5780 | 2,4018 | 99,9975 |
| 2009 | 526.726,7738 | 48.275.860,1015 | 1,0911 | 1,9465 | 99,9988 |
| 2010 | 490.810,2798 | 48.053.669,9156 | 1,0214 | 1,6283 | 99,9975 |
| 2011 | 558.033,9011 | 47.913.133,8115 | 1,1647 | 1,7001 | 99,9995 |
| 2012 | 584.945,9914 | 47.699.670,1561 | 1,2263 | 2,0368 | 99,9975 |
| 2013 | 688.055,6781 | 47.525.211,3475 | 1,4478 | 2,4249 | 99,9990 |
| 2014 | 561.987,3611 | 47.258.594,9117 | 1,1892 | 1,9496 | 99,9981 |
| 2015 | 625.099,1017 | 47.034.953,5202 | 1,3290 | 2,2399 | 99,9988 |
| 2016 | 562.808,6976 | 46.788.026,4870 | 1,2029 | 2,2554 | 99,9990 |
| 2017 | 520.010,9231 | 46.608.448,6774 | 1,1157 | 1,9842 | 99,9964 |
| 2018 | 526.559,0168 | 46.431.417,1822 | 1,1341 | 1,9140 | 99,9975 |
| 2019 | 599.905,9540 | 46.238.210,3291 | 1,2974 | 2,0278 | 99,9988 |
| 2020 | 568.441,4247 | 46.008.255,2092 | 1,2355 | 1,9488 | 99,9988 |
| 2021 | 544.652,8085 | 45.755.482,2986 | 1,1904 | 2,0104 | 99,9993 |
| 2022 | 963.808,9575 | 45.428.191,5373 | 2,1216 | 3,1308 | 99,9992 |
| 2023 | 1.209.521,0670 | 44.610.944,9495 | 2,7113 | 4,5318 | 99,9994 |

Oscilações e anos extremos são achados para inspeção, não evidência causal de
desmatamento real nem autorização para remover observações. A máscara comum
controla ausência de observação, mas não elimina erro temático ou instabilidade
de classificação entre anos. Antes de modelar, examinar independentemente os
casos extremos e a coerência temporal dos mapas de origem/destino.

## Sensibilidade às classes 25, 29 e 32

| cenario | mediana | p95 | max | mediana_delta_taxa_pp | min_delta_taxa_pp | max_delta_taxa_pp |
|---|---|---|---|---|---|---|
| principal | 2,3067 | 9,2927 | 52,9902 | 0,0000 | 0,0000 | 0,0000 |
| mais25 | 2,3312 | 9,3135 | 52,9902 | 0,0017 | -0,0000 | 4,1151 |
| mais29 | 2,2747 | 9,1602 | 52,0325 | 0,0000 | -7,9515 | 0,0012 |
| mais32 | 2,3049 | 9,2927 | 52,9902 | 0,0000 | -0,2913 | 0,0258 |
| mais29_32 | 2,2734 | 9,1602 | 52,0325 | 0,0000 | -7,9515 | 0,0258 |
| mais29_32_25 | 2,3049 | 9,1652 | 52,6895 | 0,0005 | -7,9271 | 3,9952 |

Incluir 25 como destino potencial aumenta o numerador, com denominador constante;
não transforma a classe 25 em uso antrópico comprovado. Incluir 29/32 no conjunto
inicial altera numerador **e** denominador e pode aumentar ou diminuir a taxa.
As versões principal, +29, +32, +29/32 e combinadas são cenários, sem consolidação
de uma nova definição operacional ou intervalo de confiança.

## Máscaras e Buriticupu

Elegibilidade da VN: mediana 100,00000000%,
mínimo 99,70158117%. A cobertura comum refere-se
à área da grade municipal por centro de pixel, não à diferença entre a área
cadastrada e a geodésica. Exclusões foram contadas diretamente nos rasters.

| ano_origem | ano_destino | pixels_comuns_par | pixels_comuns_tripla | area_convertida_ha_par | area_convertida_ha_tripla | taxa_conversao_pct_par | taxa_conversao_pct_tripla | delta_taxa_conversao_pct |
|---|---|---|---|---|---|---|---|---|
| 2001 | 2002 | 2.852.945,0000 | 2.852.945,0000 | 5.843,6122 | 5.843,6122 | 3,0621 | 3,0621 | 0,0000 |
| 2002 | 2003 | 2.852.945,0000 | 2.852.945,0000 | 23.350,9457 | 23.350,9457 | 12,0839 | 12,0839 | 0,0000 |

`buriticupu_pares_vs_tripla.csv` inclui áreas e pixels excluídos, denominadores,
elegibilidade e diferenças entre os suportes. A máscara tripla usa apenas pixels
válidos em 2001, 2002 e 2003 para ambos os pares. Não se contabiliza 0→classe
como conversão. Se uma elevação persistir com a máscara tripla, ela não pode ser
atribuída automaticamente à diferença de suporte; requer inspeção temática.

Para toda a série foi calculado um cenário lógico: VN inicialmente observada que
fica fora da máscara comum pode ter convertido zero ou toda sua área. Sobre a
VN inicial completa, a amplitude desse cenário é 100 − elegibilidade, em pontos
percentuais. Isso não é intervalo de confiança e não inclui erro de classificação.
O arquivo `sensibilidade_mascara.csv` preserva os valores contínuos por comparação.

## Valores candidatos para discussão científica

Propõem-se **candidatos**, não parâmetros finais:

- tau: 0,10%, 0,25%, 0,50%, 1,00% e 2,00% da VN inicial elegível por ano.
- A_min: 5, 10, 25, 50 e 100 ha de conversão mapeada no município–par.
- Elegibilidade mínima: 95%, 99%, 99,5%, 99,9% e 99,95%; 95% é referência
  permissiva de sensibilidade, não recomendação automática para treino.

A grade cobre diferentes escalas relativas e absolutas para discutir relevância
ambiental e viabilidade de confirmação em referência independente. A_min reduz
a dependência de poucos pixels, mas não garante continuidade espacial nem elimina
erro temático. tau evita que apenas municípios grandes definam relevância; A_min
evita que uma área muito pequena produza evento por denominador diminuto.
Nenhum valor foi escolhido por prevalência, balanceamento ou desempenho de modelo.

Como critério adicional a discutir, limitar a amplitude do cenário de máscara a
no máximo tau/2 exigiria elegibilidade ≥ 100 − tau/2: 99,95% para tau=0,10%;
99,875% para 0,25%; 99,75% para 0,50%; 99,5% para 1%; e 99% para 2%.
É uma proposta de controle de incerteza por ausência de observação, não garantia
de estabilidade de rótulo ou de acurácia temática. Casos próximos ao limiar ainda
exigem revisão. O requisito precisa ser validado pelo pesquisador.

Para dimensionar a relevância, tau=0,50% corresponde a 5, 50 e 500 ha quando
D é 1.000, 10.000 e 100.000 ha, respectivamente. A_min=10 ha é um exemplo
para discussão, não uma escolha. A área é agregada no município: não exige
uma mancha contínua de 10 ha. A combinação simultânea de tau e A_min também
é uma hipótese a validar; grandes áreas absolutas com taxa pequena continuam
no relatório. Uma regra alternativa com critérios ligados por “ou” exigiria
decisão científica própria e nova análise.

`candidatos_limiares_contagens_agregadas.csv` contém somente frequências agregadas
dos cenários e quantos cenários de máscara atravessariam tau. Não contém Y nem
uma coluna binária por município–ano. Essas contagens dimensionam a revisão;
não são critério suficiente para escolher o evento científico.

As recomendações de [Olofsson et al. (2014)](https://doi.org/10.1016/j.rse.2014.02.015)
fundamentam a necessidade de referência independente, amostragem adequada e
avaliação de erro para áreas de mudança. Elas não fornecem tau/A_min para esta
dissertação. Estes resultados são áreas mapeadas, sem ajuste amostral de erro ou
intervalos de confiança. É necessário verificar os extremos, fronteiras de classe,
casos próximos aos candidatos e estratos município/ano antes de validar limiares.

## Preservação e próximos passos

Nenhum raster, tabela, view, CSV anterior ou resultado das Fases 1/2 foi substituído.
Os novos resultados estão em `resultados_transicoes_col9\integral_255_1985_2023_20261111`; as matrizes densas estão em NPZ,
com os eixos de municípios, anos e classes incluídos e carregamento sem pickle.
As verificações/checkpoints por município permitem retomar sem substituir saídas.

Faltam validação temática independente e decisão científica dos candidatos.
Não houve geração de variável-alvo binária, treinamento ou escolha definitiva de
tau/A_min/elegibilidade mínima. A implantação das Fases 1/2 foi realizada em
atividade separada, após confirmação expressa, preservando banco e volume;
ver `docs/RELATORIO_IMPLANTACAO_COL9_20261111.md` para evidências e limitações.

## Leitura crítica dos resultados e prioridades de validação

Revisão dos CSVs consolidados em 11/11/2026, após a auditoria automática:

- A maior taxa é Figueirópolis D'Oeste/MT, 2022→2023: 52,9902%,
  3.595,25 ha convertidos sobre 6.784,76 ha elegíveis. A maior área absoluta
  é Vila Bela da Santíssima Trindade/MT, 1985→1986: 118.394,66 ha,
  taxa de 10,0423%. São prioridades distintas de inspeção, não eventos
  automaticamente confirmados em referência independente.
- Das 30 maiores taxas, 13 têm destino em 2023 e 10 em 2022. O P95 municipal
  sobe para 22,4627% em 2022 e 24,9844% em 2023. Essa concentração nos últimos
  anos exige examinar estabilidade temática e temporal, junto com exemplos
  de controle dos mesmos municípios em anos anteriores. Não demonstra,
  isoladamente, aceleração real nem erro do produto e não autoriza exclusão.
- A taxa regional máxima ocorre em 2002→2003: 3,1220%, com 1.639.858,34 ha
  mapeados. A soma dos 38 pares é 35.857.121,54 hectares-evento, que pode
  contar o mesmo local em reconversões; não é área única desmatada.
- Todas as comparações têm VN elegível positiva. O mínimo é 2.080,13 ha e
  a mediana, 71.835,02 ha. A elegibilidade é pelo menos 99,70158117%;
  somente Buriticupu 2002→2003 fica abaixo de 99,9% e de 99,95%. Assim,
  os candidatos de qualidade abaixo desse patamar não devem ser defendidos
  por conveniência de conservar mais linhas: seu fundamento deve ser o
  controle da ausência de observação.
- Em Buriticupu, ambas as máscaras retêm 2.852.945 pixels e excluem 12.063
  da grade municipal. C, D e R são idênticos por par e no suporte triplo:
  5.843,61 ha / 190.839,86 ha = 3,06205% em 2001→2002 e
  23.350,95 ha / 193.239,99 ha = 12,08391% em 2002→2003.
  A elevação persiste no suporte comum aos três anos. A amplitude do cenário
  lógico de ausência de VN no segundo par é 0,298419 ponto percentual,
  sobre o estoque inicial completo, sem contemplar erro temático.
- Incluir o destino 25 leva a mediana de 2,3067% para 2,3312% e acrescenta
  622.699,96 hectares-evento à série. O maior aumento de taxa é em Tabocão/TO,
  1990→1991: de 3,7291% para 7,8442% (+4,1151 pontos percentuais).
  Isso dimensiona a sensibilidade local, sem legitimar 25 como uso antrópico.
- Incluir 29+32 na origem leva a mediana para 2,2734%. A maior redução é
  Rio Branco/MT, 2022→2023: de 26,8482% para 18,8968%
  (−7,9515 pontos percentuais). Há também aumentos, como Raposa/MA,
  2002→2003: +0,0258 ponto percentual. Diferenças da ordem de 10⁻¹⁴ ponto
  percentual nas tabelas decorrem de ponto flutuante, sem interpretação temática.

**Como discutir os candidatos:** a mediana não estabelece relevância científica.
Tau de 0,10–2,00% representa diferentes frações anuais do estoque; A_min de
5–100 ha serve inicialmente para discutir escala e verificabilidade espacial.
O P05 da área convertida é 182,18 ha: mesmo o maior A_min dessa grade fica abaixo
desse percentil. Logo, essa grade absoluta é principalmente um piso de área e
não demonstra que 100 ha seja um limiar substantivo adequado à dissertação.
Se a hipótese científica exigir conversão de maior magnitude na paisagem,
devem ser avaliados novos candidatos absolutos com justificativa ambiental,
antes de construir a variável-alvo. Nenhum candidato tem aqui status normativo.

A validação deve combinar amostragem probabilística para estimar erro e revisão
dirigida dos casos acima, das mudanças por classe, de polígonos de borda e dos
casos próximos aos candidatos. A revisão dirigida não substitui amostragem
representativa. Recomenda-se incluir também controles de baixa taxa e todos
os intervalos de Buriticupu aqui auditados, com referência independente e
protocolo de interpretação documentado. A regra de combinação de taxa e área,
a elegibilidade e o tratamento de casos incertos permanecem decisões do
pesquisador, anteriores ao ajuste e à avaliação dos modelos.

## Figuras exploratórias

![Coleção 9 · 255 municípios · 9.690 pares anuais — Distribuição empírica das taxas mapeadas](../resultados_transicoes_col9/integral_255_1985_2023_20261111/analise_exploratoria/figuras/01_distribuicao_taxas.png)

![Coleção 9 · distribuição das áreas convertidas — Somente observações positivas no eixo logarítmico](../resultados_transicoes_col9/integral_255_1985_2023_20261111/analise_exploratoria/figuras/02_distribuicao_areas.png)

![Coleção 9 · VN(t) → usos antrópicos(t+1) — Áreas mapeadas por ano · máscara válida comum](../resultados_transicoes_col9/integral_255_1985_2023_20261111/analise_exploratoria/figuras/03_conversao_anual.png)

![Coleção 9 · taxas regionais e distribuição municipal — Razão regional ≠ média simples de percentuais](../resultados_transicoes_col9/integral_255_1985_2023_20261111/analise_exploratoria/figuras/04_taxas_anuais.png)

![Coleção 9 · taxa relativa versus conversão absoluta — Revisar extremos junto ao denominador e à elegibilidade](../resultados_transicoes_col9/integral_255_1985_2023_20261111/analise_exploratoria/figuras/05_taxa_area.png)

![Buriticupu/MA (2102325) · auditoria 2001–2003 — Conversão VN→UA sob dois suportes espaciais](../resultados_transicoes_col9/integral_255_1985_2023_20261111/analise_exploratoria/figuras/06_buriticupu.png)

