# Recomendação sobre o desfecho e cenários A/B/C — Col 9

Data: 12/11/2026. **Nenhum cenário homologado; nenhum modelo treinado.**
A evidência atual recomenda conservar C e R como medidas de conversão **mapeada**,
mantendo candidatos A/B/C apenas como hipóteses. Sua denominação não deve sugerir
conversão verdadeira confirmada, relevância ambiental demonstrada ou significância estatística.

## Critérios e cobertura da evidência

C é a área VN(t)→UA(t+1) na máscara válida comum; D é a VN inicial nessa mesma
máscara; R=100 C/D; Q=100 D/VN inicial observada. O evento candidato exige
simultaneamente R≥tau eC≥A_min, entre pares com D>0 eQ≥Q_min.
Q mede elegibilidade do suporte, não acurácia temática nem cobertura de validação.

A:tau 0,25% e 25 ha; B: 0,50% e 100 ha; C: 1,00% e 250 ha.
As contagens anteriores foram conferidas, sem alterar matrizes:

| cenario | Q_min_pct | n_pares | n_avaliaveis | n_candidatos | n_candidatos_sem_ref_par | n_candidatos_sem_ponto_ref_VN | n_candidatos_com_evento_ref_na_amostra | prevalencia_mapeada_pct |
|---|---|---|---|---|---|---|---|---|
| A | 99.5000 | 9690 | 9690 | 9315 | 363 | 1124 | 1619 | 96.1300 |
| B | 99.5000 | 9690 | 9690 | 8757 | 357 | 1072 | 1536 | 90.3715 |
| C | 99.5000 | 9690 | 9690 | 7285 | 329 | 944 | 1302 | 75.1806 |

EmQ 99,9% e 99,95%, cada cenário perde apenas Buriticupu 2002→2003 por elegibilidade,
ficando 9.314/8.756/7.284 candidatos em 9.689 avaliáveis. Essa alteração não resolve
discordância temática de outros municípios ou falta de referência 2023.
As prevalências altas não são motivo para elevar limiares visando balanceamento:
podem refletir pressão difundida, denominadores remanescentes, definição operacional
e erros/datação do produto em combinação. Não foi escolhida uma explicação única.

| cenario | Q_min_pct | ano_destino | n_pares | n_avaliaveis | n_candidatos | n_candidatos_sem_ref_par | n_candidatos_sem_ponto_ref_VN | n_candidatos_com_evento_ref_na_amostra |
|---|---|---|---|---|---|---|---|---|
| A | 99.5000 | 2022 | 255 | 255 | 252 | 3 | 26 | 17 |
| A | 99.5000 | 2023 | 255 | 255 | 250 | 249 | 249 | 0 |
| B | 99.5000 | 2022 | 255 | 255 | 245 | 3 | 25 | 17 |
| B | 99.5000 | 2023 | 255 | 255 | 245 | 244 | 244 | 0 |
| C | 99.5000 | 2022 | 255 | 255 | 220 | 3 | 22 | 14 |
| C | 99.5000 | 2023 | 255 | 255 | 222 | 221 | 221 | 0 |

Dos 250 candidatos A de 2023,249 não têm referência de par no município; para B são
244 de 245 e para C 221 de 222. Ter um ponto comparável também não valida o agregado.
Para A/B/C,1.124/1.072/944 candidatos no conjunto não têm sequer ponto de referência
VN inicial comparável. As tabelas por município, UF e ano preservam os zeros e
explicitam essa cobertura, sem transformá-la em probabilidade de verdade do evento.

## Consequências das auditorias

No ano exato, a precisão descritiva entre pontos sem marcação de treino é 26,81%
e a sensibilidade 35,12%; em 2022 a primeira cai a 8,75%, com apenas 21 eventos de
referência. Isso é evidência contrária à adoção imediata de uma etiqueta anual
de ocorrência verdadeira. Não é estimativa válida de erro da área municipal,
nem permite multiplicar C por 26,81% para “corrigir” hectares.

Referências em anos próximos melhoram a coincidência, mas não confirmam horizonte
anual. A persistência do raster é alta e depende dos seus filtros. PRODES tem
escopo/calendário próprios; os proxies espectrais dirigidos são limitados por
calibração, sazonalidade e QA. Nenhuma dessas fontes autoriza homologar o cenário
C por ser mais restritivo, nem supor que A/B estejam ambientalmente errados.

As sensibilidades 25/29/32 nas matrizes permanecem nos relatórios anteriores;
as novas comparações pontuais não mudam com 29/32 e melhoram apenas marginalmente
com 25. A ausência de efeito na amostra não comprova ausência territorial.
Comparação global original das variantes emQ 99,5%:

| cenario | variante | n_eventos_candidatos | n_discordantes_principal |
|---|---|---|---|
| A | mais25 | 9331 | 16 |
| A | mais29 | 9315 | 0 |
| A | mais29_32 | 9314 | 1 |
| A | mais29_32_25 | 9329 | 16 |
| A | mais32 | 9314 | 1 |
| A | principal | 9315 | 0 |
| B | mais25 | 8784 | 27 |
| B | mais29 | 8757 | 2 |
| B | mais29_32 | 8757 | 2 |
| B | mais29_32_25 | 8783 | 28 |
| B | mais32 | 8757 | 0 |
| B | principal | 8757 | 0 |
| C | mais25 | 7353 | 68 |
| C | mais29 | 7280 | 5 |
| C | mais29_32 | 7278 | 7 |
| C | mais29_32_25 | 7345 | 66 |
| C | mais32 | 7283 | 2 |
| C | principal | 7285 | 0 |

## Significado ambiental a decidir

O componente relativo representa a pressão sobre o estoque elegível remanescente;
o absoluto representa hectares municipais somados, que podem estar dispersos.
Nenhum dos dois mede sozinho integridade de habitat, conectividade, tipo de
formação, condição primária/secundária, permanência de uso ou consequências locais.
A_min não é área mínima de uma mancha e não deve ser equiparado à unidade mínima
de outro sistema. Tau não deve receber interpretação normativa/biológica sem hipótese.

A definição defensável precisa declarar a consequência de interesse: perda de uma
fração substantiva do remanescente, escala absoluta de transformação ou alteração
persistente de uso. O pesquisador poderá escolher uma definição substantiva mesmo
com prevalência elevada; a escolha deverá apoiar-se no processo ambiental e na
qualidade do desfecho, sem otimização por balanceamento ou resultados de modelos.

## Magnitude contínua como análise complementar

É viável especificar futuramente C(t,t+1) em hectares e R(t,t+1) em% como respostas contínuas
de **conversão mapeada**, retendo D,Q e o motivo de ausência. Isso preserva magnitude
e evita uma dicotomia ainda não fundamentada. Não elimina erros de classificação,
denominadores pequenos, assimetria, dependência espacial/temporal ou revisão retrospectiva.
Sugere-se avaliar C e R separadamente e conjuntamente com o suporte; log1p(C) pode
ser transformação pré-especificada, sem alterar as áreas originais ou substituir
o estimando sem discussão. Um valor ausente por suporte não vira zero.

Em eventual experimento autorizado, relatar erros nas unidades originais (MAE em hectares,
erro percentual/pontos percentuais de R), calibração e comportamento por estoque,
UF e período. Toda transformação/normalização será ajustada apenas no treino.
Não há treinamento nem seleção de melhor resposta nesta entrega.

## Horizonte e protocolo retrospectivo preservados

Mantêm-se 255 municípios,38 transições, previsores até o final de t e desfecho
entre t e t+1; 2023 não recebe rótulo observado de t+1 e 2024 permanece reservado.
Confirmar uma conversão em t+2 pode ser adjudicação posterior do evento t→t+1,
mas acrescenta um ano de disponibilidade da referência; redefinir o evento como
persistente em t+2 altera o desfecho. No segundo caso, somente t≤2021 é observável
dentro de 1985–2023. A transição 2022→2023 fica censurada, sem consultar 2024.
Nenhum índice de t+2 será previsor de t. Não se selecionou critério de persistência.

O experimento segue retrospectivo, sem reivindicar disponibilidade operacional
histórica de todas as fontes. Mantêm-se validação temporal e leave-one-state-out;
os últimos anos e extremos já foram explorados e os testes não são completamente
cegos à formulação do desfecho. O protocolo anterior permanece preservado.

## Decisões que dependem de validação científica

1. Se o objetivo será ocorrência verdadeira relevante ou magnitude mapeada com
   incerteza explícita; uma eventual mudança de estimando exige aprovação.
2. Qual justificativa ambiental sustentaria tau/A_min, sem usar desempenho preditivo.
3. Como tratar o ano final sem referência e a discordância de datação, sem corrigir
   automaticamente a matriz nem deslocar anos para aumentar concordância.
4. Se persistência será apenas auditoria ou parte da definição, com censura/horizonte explícitos.
5. Como resolver proveniência/inclusão dos pontos e calibração dos auxiliares antes
   de qualquer afirmação representativa.

Recomendação atual: manter A/B/C em aberto; conservar as medidas contínuas para
auditoria e preparar apenas uma proposta complementar de regressão retrospectiva.
Não homologar Y nem iniciar treinamento definitivo com as evidências atuais.
