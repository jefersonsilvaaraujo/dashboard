# Comparação científica dos limiares candidatos — Coleção 9

11/11/2026. Etapa B executada nos 9.690 pares, preservando o acervo anterior.
Nenhum cenário foi homologado como Y, selecionado por balanceamento ou usado para treinar.

## Regras e denominadores

A: R≥0,25% **e** C≥25 ha; B: R≥0,50% **e** C≥100 ha;
C: R≥1,00% **e** C≥250 ha. R=100 C/D; D é a VN inicial no suporte comum.
Igualdade satisfaz o critério. Comparadas Q≥99,5%, 99,9% e 99,95%.
Q é a fração da VN inicial observada que permanece no suporte comum.
Ausência, D=0 ou qualidade insuficiente são não avaliáveis, não negativos.

Proporção entre avaliáveis = candidatos/avaliáveis; proporção no universo =
candidatos/total. Ambos os denominadores estão nos CSVs. A segunda medida não
transforma exclusões em negativos. Contagens municipais têm 38 oportunidades;
por UF/ano usam a quantidade efetiva de pares. São frequências de eventos
municipais mapeados, não percentuais da área regional.

Casos próximos: `abs(min(R/tau,C/A_min)−1)≤0,10`, entre avaliáveis. É uma faixa
de auditoria de ±10% relativa à fronteira conjunta, não incerteza estatística
nem tolerância para modificar o evento. CSVs incluem margens em ha e pontos percentuais.

## Resultado principal

| cenario | Q_min_pct | n_avaliaveis | n_eventos_candidatos | proporcao_eventos_avaliaveis_pct | n_excluidos_qualidade | n_proximos_limite |
|---|---|---|---|---|---|---|
| A | 99,5000 | 9690 | 9315 | 96,1300 | 0 | 81 |
| A | 99,9000 | 9689 | 9314 | 96,1296 | 1 | 81 |
| A | 99,9500 | 9689 | 9314 | 96,1296 | 1 | 81 |
| B | 99,5000 | 9690 | 8757 | 90,3715 | 0 | 243 |
| B | 99,9000 | 9689 | 8756 | 90,3705 | 1 | 243 |
| B | 99,9500 | 9689 | 8756 | 90,3705 | 1 | 243 |
| C | 99,5000 | 9690 | 7285 | 75,1806 | 0 | 589 |
| C | 99,9000 | 9689 | 7284 | 75,1780 | 1 | 589 |
| C | 99,9500 | 9689 | 7284 | 75,1780 | 1 | 589 |

A exclusão principal em 99,9%/99,95% é Buriticupu 2002→2003,
Q=99,70158117%. A máscara tripla mantém os resultados anteriores; essa
exclusão por cenário não apaga a observação nem certifica sua incorreção temática.

## Quantidade por ano de destino — principal, Q≥99,5%

| ano_destino | A | B | C |
|---|---|---|---|
| 1986 | 240 | 227 | 191 |
| 1987 | 246 | 228 | 184 |
| 1988 | 240 | 223 | 171 |
| 1989 | 242 | 221 | 175 |
| 1990 | 236 | 213 | 165 |
| 1991 | 237 | 219 | 179 |
| 1992 | 236 | 225 | 197 |
| 1993 | 241 | 228 | 198 |
| 1994 | 243 | 231 | 194 |
| 1995 | 247 | 236 | 198 |
| 1996 | 245 | 231 | 204 |
| 1997 | 245 | 235 | 199 |
| 1998 | 244 | 236 | 211 |
| 1999 | 247 | 240 | 214 |
| 2000 | 246 | 240 | 213 |
| 2001 | 244 | 237 | 207 |
| 2002 | 245 | 237 | 210 |
| 2003 | 243 | 232 | 206 |
| 2004 | 245 | 238 | 216 |
| 2005 | 246 | 240 | 211 |
| 2006 | 243 | 224 | 192 |
| 2007 | 245 | 228 | 189 |
| 2008 | 249 | 232 | 200 |
| 2009 | 244 | 220 | 178 |
| 2010 | 243 | 218 | 160 |
| 2011 | 245 | 227 | 171 |
| 2012 | 246 | 229 | 185 |
| 2013 | 249 | 236 | 197 |
| 2014 | 245 | 230 | 172 |
| 2015 | 247 | 233 | 183 |
| 2016 | 247 | 226 | 172 |
| 2017 | 247 | 226 | 181 |
| 2018 | 250 | 224 | 175 |
| 2019 | 254 | 234 | 188 |
| 2020 | 250 | 233 | 183 |
| 2021 | 251 | 230 | 174 |
| 2022 | 252 | 245 | 220 |
| 2023 | 250 | 245 | 222 |

As demais qualidades, proporções, proximidades e exclusões estão em
`validacao_cientifica_col9\checkpoint_20261111\limiares\comparacao_por_ano.csv`; 2.052 combinações ano/cenário/qualidade/classificação.

## Estados — principal, Q≥99,5%

| SIGLA_UF | cenario | n_total | n_eventos_candidatos | proporcao_eventos_avaliaveis_pct | n_proximos_limite |
|---|---|---|---|---|---|
| MA | A | 3610 | 3340 | 92,5208 | 37 |
| MT | A | 2584 | 2493 | 96,4783 | 34 |
| PA | A | 570 | 570 | 100,0000 | 0 |
| RO | A | 190 | 190 | 100,0000 | 0 |
| TO | A | 2736 | 2722 | 99,4883 | 10 |
| MA | B | 3610 | 3140 | 86,9806 | 79 |
| MT | B | 2584 | 2244 | 86,8421 | 104 |
| PA | B | 570 | 567 | 99,4737 | 4 |
| RO | B | 190 | 170 | 89,4737 | 11 |
| TO | B | 2736 | 2636 | 96,3450 | 45 |
| MA | C | 3610 | 2698 | 74,7368 | 209 |
| MT | C | 2584 | 1646 | 63,6997 | 251 |
| PA | C | 570 | 558 | 97,8947 | 6 |
| RO | C | 190 | 122 | 64,2105 | 14 |
| TO | C | 2736 | 2261 | 82,6389 | 109 |

Tabela completa por estado: `validacao_cientifica_col9\checkpoint_20261111\limiares\comparacao_por_estado.csv`.
Tabela por cada um dos 255 municípios: `validacao_cientifica_col9\checkpoint_20261111\limiares\comparacao_por_municipio.csv`,
com 13.770 combinações e as mesmas contagens/proporções/flags agregadas.
Não são substituídas por rankings dos extremos. As somas por ano, estado e
município foram conferidas contra as 54 linhas globais para todas as contagens.

## Sensibilidade de classificação — Q≥99,5%

| cenario | variante | n_eventos_candidatos | n_discordantes_principal | n_proximos_limite |
|---|---|---|---|---|
| A | mais25 | 9331 | 16 | 73 |
| A | mais29 | 9315 | 0 | 81 |
| A | mais29_32 | 9314 | 1 | 79 |
| A | mais29_32_25 | 9329 | 16 | 71 |
| A | mais32 | 9314 | 1 | 79 |
| A | principal | 9315 | 0 | 81 |
| B | mais25 | 8784 | 27 | 248 |
| B | mais29 | 8757 | 2 | 244 |
| B | mais29_32 | 8757 | 2 | 244 |
| B | mais29_32_25 | 8783 | 28 | 249 |
| B | mais32 | 8757 | 0 | 243 |
| B | principal | 8757 | 0 | 243 |
| C | mais25 | 7353 | 68 | 602 |
| C | mais29 | 7280 | 5 | 592 |
| C | mais29_32 | 7278 | 7 | 590 |
| C | mais29_32_25 | 7345 | 66 | 608 |
| C | mais32 | 7283 | 2 | 587 |
| C | principal | 7285 | 0 | 589 |

29/32 ampliam a origem e alteram C, D e o estoque inicial usado em Q;
25 amplia somente o destino. A elegibilidade de cada variante foi recalculada
com os estoques por classe dos NPZs, sem reutilizar silenciosamente Q principal.
Há discordâncias mesmo quando o total líquido de candidatos permanece igual
(por exemplo B, +29): entradas e saídas podem se compensar. A taxonomia oficial
não foi alterada. Esses cenários não tornam 25 uso antrópico comprovado.

Arquivos detalhados: `casos_proximos.csv`, `exclusoes_qualidade.csv`,
`discordancias_classificacao.csv`, `medidas_sensibilidades_continuas.csv`.
Os estados exploratórios candidato/abaixo/não avaliável não são rótulos homologados
e devem ficar fora de qualquer X ou Y definitivo.

## Interpretação ambiental e recomendação

O limiar efetivo em hectares é `max(A_min,tau D/100)`. As áreas elegíveis em que
as duas condições se igualam são 10.000 ha (A), 20.000 ha (B) e 25.000 ha (C).
Na mediana de D=71.835,02 ha, os pisos efetivos são aproximadamente 179,59 ha,
359,18 ha e 718,35 ha. A descreve a perda de pelo menos 1/400 do estoque
e 25 ha; B, 1/200 e 100 ha; C, 1/100 e 250 ha por comparação anual.
Essas são interpretações operacionais, não padrões oficiais de relevância ecológica.

O piso é agregado no município: não garante uma mancha contínua, elimina erro
temático ou mede fragmentação, biodiversidade e conectividade. A mesma perda
relativa pode ter impactos diferentes entre formações florestais, savânicas,
campestres e alagáveis. A prioridade ambiental deve ser vinculada a uma hipótese
explícita sobre perda de estoque e escala espacial, apoiada por referência independente.

Recomenda-se **manter A/B/C em avaliação**, sem hierarquia de vencedor. A reduz
o piso substantivo; C exige maior perda relativa/absoluta; B ocupa escala
intermediária. Nenhum é recomendado porque gera mais ou menos positivos.
As proporções acima dimensionam os cenários e não justificam sua escolha.
Antes de homologar: concluir respostas temáticas, avaliar incerteza perto de
cada fronteira, justificar a escala ambiental e decidir o tratamento dos
casos ambíguos. A inspeção dirigida encontrou heterogeneidade e não autoriza
certificar nenhum dos três cenários para treinamento neste checkpoint.

## Reprodução, testes e arquivos

`processamento/cenarios_validacao_col9.py` calcula os 54 cenários; a assinatura
de `concluido.json` anterior e os hashes municipais são conferidos antes da leitura.
`processamento/relatorios_validacao_cientifica_col9.py` gera este relatório.
Saídas novas em `validacao_cientifica_col9\checkpoint_20261111`. Testes de AND, igualdade, qualidade, D=0,
denominadores, proximidade e aninhamento em `testes/test_validacao_cientifica_col9.py`.
77 testes distintos passaram na regressão completa (61 principais +16 geoespaciais).
Nenhum banco, raster, CSV anterior, checkpoint ou dashboard foi substituído.
