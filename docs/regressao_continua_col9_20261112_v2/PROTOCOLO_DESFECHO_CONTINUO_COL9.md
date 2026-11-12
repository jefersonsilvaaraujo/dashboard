# Protocolo do desfecho contínuo candidato — Coleção 9
12/11/2026. Proposta para apreciação do orientador, sem homologação de objetivos ou treinamento.

## Estimando
R(m,t)=100 ×C(m,t)/D(m,t), taxa percentual anual de conversão mapeada na ZCS
Cerrado–Amazônia. C é a área geodésica em hectares dos pixels VN(t)→UA(t+1)
na máscara válida comum. D é a vegetação nativa inicial nessa mesma máscara,
diferente da VN observada somente em t. São 255 municípios IBGE 2025 fixos,
39 mapas Col 9 e 38 transições: t=1985–2022,9.690 pares. As 255 linhas de 2023
ficam separadas sem resposta. 2024 permanece reservado e não foi utilizado.

VN=[3,4,5,6,49,11,12,50]; UA=[9,15,20,21,24,30,31,35,39,40,41,46,47,48,62].
A legenda oficial não muda; 25 é separada e 29/32 permanecem naturais específicas.
As sensibilidades e cenários A/B/C anteriores são preservados como exploratórios.

Fisicamente 0≤C≤D e 0≤R≤100. D=0 ou suporte insuficiente implicaria resposta
não avaliável, nunca zero imputado. Atualmente todos os 9.690 pares têm C>0 e D>0;
isso não permite presumir ausência de zeros em observações futuras.

Recomenda-se C em hectares como resposta secundária de experimento independente
complementar, caso aprovado. Não é estatisticamente equivalente aR. Converter
R prevista em C usando D realizado utilizaria suporte futuro indisponível emt.
Uma aproximação pela VN observada emt teria outro estimando e não seria C exato.

## Distribuição e heterogeneidade
| medida | mínimo | p05 | p25 | mediana | p75 | p95 | p99 | máximo | média | DP | assimetria |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R_pct | 0.0008 | 0.3241 | 1.1117 | 2.3067 | 4.0467 | 9.2927 | 16.6663 | 52.9902 | 3.2364 | 3.5901 | 4.2559 |
| C_ha | 0.8037 | 182.1778 | 654.9623 | 1627.7880 | 4127.5277 | 14654.4981 | 27297.6177 | 118394.6586 | 3700.4253 | 5742.0447 | 4.2297 |
| D_ha | 2080.1283 | 9709.1453 | 29951.6053 | 71835.0198 | 205176.7280 | 994238.2331 | 1841628.2356 | 2602022.5663 | 209420.3982 | 352652.9121 | 3.1413 |

O maior R é 52,9902% em Figueirópolis D'Oeste no par 2022→2023. O maior C é
118.394,66 ha em Vila Bela da Santíssima Trindade em 1985→1986. Não houve exclusão
de extremos, truncamento ou winsorização. Assimetria, IQR, MAD, quantis e dispersão
por município/UF/ano estão nas tabelas de diagnóstico, sem testes iid de significância.

| SIGLA_UF | n | R_pct_mediana | C_ha_mediana | taxa_razao_somas_pct |
|---|---|---|---|---|
| MA | 3610 | 2.5787 | 956.6853 | 2.4226 |
| MT | 2584 | 1.3987 | 3868.1864 | 1.4102 |
| PA | 570 | 4.2669 | 4435.7674 | 4.2628 |
| RO | 190 | 1.5004 | 4403.0256 | 1.4198 |
| TO | 2736 | 2.5496 | 1342.9945 | 1.8708 |

A taxa por razão das somas é 100ΣC/ΣD; globalmente 1,7670%, diferente da média
não ponderada 3,2364%. Agregar pela razão das somas não equivale à média das taxas.
Somar C ao longo do tempo não identifica área única sem reconversões/repetições.

| quintil_D_descritivo | n | D_ha_min | D_ha_max | R_pct_mediana | C_ha_mediana |
|---|---|---|---|---|---|
| Q1_menor_D | 1938 | 2080.1283 | 23760.1228 | 3.8323 | 503.8410 |
| Q2 | 1938 | 23782.5161 | 52551.5335 | 2.9642 | 1096.1694 |
| Q3 | 1938 | 52560.0562 | 107127.3228 | 2.1834 | 1654.2467 |
| Q4 | 1938 | 107190.8716 | 268131.3235 | 1.6918 | 2638.6736 |
| Q5_maior_D | 1938 | 268251.6725 | 2602022.5663 | 1.1331 | 7616.8947 |

No quintil de menor D, a mediana de R é 3,8323% e de C 503,84 ha; no maior,
R 1,1331% e C 7.616,89 ha. Isso demonstra sensibilidade ao denominador e não
equivalência das respostas, sem inferir causalidade. Os quintis globais são apenas
descritivos; não são limiares de elegibilidade ou parâmetros de aprendizado.

| periodo | n | R_pct_mediana | C_ha_mediana | taxa_razao_somas_pct |
|---|---|---|---|---|
| 1985–1989_5anos | 1275 | 1.7814 | 1967.5367 | 1.6680 |
| 1990–1999_10anos | 2550 | 2.5636 | 2035.0059 | 2.0777 |
| 2000–2009_10anos | 2550 | 2.4827 | 1575.8093 | 1.8990 |
| 2010–2019_10anos | 2550 | 2.0312 | 1205.7794 | 1.2345 |
| 2020–2022_3anos | 765 | 2.8937 | 1904.0144 | 2.0015 |

Os períodos referem-se ao ano t; os extremos têm 5 e 3 anos. Mudanças abruptas
entre taxas/áreas de intervalos consecutivos são tabeladas separadamente; não
são novas transições nem variação líquida de estoque.

## Máscara e transformações candidatas
Q=100 D/VN inicial observada mede elegibilidade, não acurácia temática. Todos
os pares foram mantidos com flags separados Q≥99,5/99,9/99,95%; os dois últimos
retirariam apenas Buriticupu 2002→2003 (Q≈99,7016%). Nenhum corte foi selecionado.
A auditoria anterior com máscara tripla 2001–2003 permanece preservada; suporte
coincidente não valida o tema e diferenças não são automaticamente NoData.

log1p(C/1 ha) tem assimetria−0,3876 no diagnóstico. Melhor aparência estatística
não justifica sua adoção. C/R originais foram preservados. Uma futura inversão
expm 1 precederá métricas em hectares; inverter a média log não recupera automaticamente
a média original. R direta é primeira candidata; logit(R/100) exige interior(0,1)
e decisão para eventuais 0/100, sem epsilon arbitrário. Links/perdas limitados
devem ser pré-especificados no desenvolvimento. Nada foi aplicado definitivamente.

## Limitações ambientais
R/C são conversão mapeada, não área real corrigida, relevância ecológica
demonstrada, variação líquida ou desmatamento PRODES. A comparação oficial
anterior apresentou precisão descritiva 26,81% e sensibilidade 35,12% no ano exato,
sem inferência representativa própria. Em 2023 há somente um ponto local com
referência; datação, filtros temporais e qualidade das referências permanecem
limitações. Não corrigir hectares multiplicando pela precisão pontual.
A resposta contínua evita dicotomização ainda não fundamentada, mas não remove
erro de medição. Persistência em t+2 não integra a resposta nem utiliza 2024.
