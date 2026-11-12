# Protocolo consolidado proposto de modelagem retrospectiva — Coleção 9

O pesquisador definiu **predição retrospectiva** como experimento principal,
com horizonte t+1 e avaliação temporal/espacial. Este documento consolida essa
decisão; a especificação anterior é preservada como histórico, inclusive sua
distinção entre retrospectivo e as-of. A simulação operacional histórica não
será a descrição do experimento principal. Não houve seleção definitiva de
atributos, montagem de X/Y, treinamento ou homologação de desfecho.

## Unidade, resposta e fronteira temporal

255 municípios nos limites fixos IBGE2025 verificados por hash. Chave `(CD_MUN,t)`;
t=1985…2022, 38 transições e **9.690 oportunidades** de resposta t→t+1.
As matrizes anuais completas continuam imutáveis. C/R são medidas mapeadas,
não diferenças líquidas de estoque nem rótulos tematicamente certificados.
Definição de relevância, elegibilidade e incerteza ainda depende de aprovação.

T=2023 não tem resposta t+1 observada na Col9: não receberá zero e está fora
do índice supervisionado principal. **2024 permanece reservado** para definição
metodológica separada; não é teste externo automático, dado para confirmar
persistência, previsor ou fonte para completar uma linha. Não se adota Col10.1.

O corte conceitual das variáveis é o final do ano t. O experimento usa produtos
retrospectivos cuja publicação/revisão pode ser posterior a t. Isso é permitido
como reconstrução retrospectiva, com versão/linhagem declaradas; não prova
que esses valores estavam disponíveis operacionalmente naquele ano.

Três restrições distintas devem ser mantidas:

1. **Fenômeno observado:** atributos devem se referir a informações até t,
   nunca ao intervalo de resposta t→t+1 ou a qualidade conhecida só depois.
2. **Publicação/revisão:** datas posteriores são metadados de retrospectividade,
   não uma barreira automática como no experimento operacional antigo.
3. **Dependência algorítmica:** uso de anos futuros no processamento de um mapa
   histórico pode criar informação antecipatória no conteúdo do atributo.
   Aceitar publicação tardia não resolve isso. Documentar o risco, auditar o
   método do produto e propor análise sem o bloco afetado/ablação antes de
   interpretar desempenho. Ausência de documentação não certifica ausência
   de vazamento; eventual inclusão desse bloco exige decisão explícita.

## Blocos de variáveis candidatas

Nenhuma linha abaixo está automaticamente selecionada. O catálogo executável
`catalogo_blocos_candidatos.csv` classifica cada grupo por estado do acervo:
`derivavel_acervo_harmonizado`, `acervo_presente_nao_harmonizado` ou `fonte_adicional`.

| Bloco | Proposta de explicativas até t | Estado real do acervo | Restrição/pendência |
|---|---|---|---|
| Histórico de cobertura | composição de classes, VN e UA, 25/29/32/33 separados, estoque de t, cobertura válida somente de t, variação líquida t−1→t, tendências móveis 3/5 anos, conversão passada encerrada até t | Col9 255×39, rasters e matrizes harmonizados; atributos deriváveis, X ainda não montado | manter taxonomia oficial/operacional separadas; auditar dependência temporal/revisões e avaliar ablação de atributos do mesmo produto que gera a resposta |
| Território básico | área geodésica, latitude/localização e relações de vizinhança | geometria canônica disponível; área/localização deriváveis; grafo ainda não calculado | não herdar cadastro/grafo de268; código do município não é variável numérica contínua |
| Território/ambiente | frações de biomas, relevo/solos, distâncias a estradas/áreas protegidas e conectividade | biomas IBGE2019 presentes mas não reintersectados; relevo/solos/camadas históricas exigem fontes adicionais | vigência de estradas/proteção ≤t; geometria2025 é convenção retrospectiva, não realidade administrativa disponível em1985 |
| Focos/queimadas | contagem civil, densidade, sazonalidade, lags, FRP e atributos no local dos focos | ZIPs INPE2003–2025 e CSV legado presentes; interseção251/255, ainda não harmonizados | mesmos limites255, calendário civil coerente; focos não são hectares queimados; FRP/meteorologia condicionados aos focos não são clima médio municipal |
| Área queimada | área/fração anual, recorrência, interação com VN e lags | fonte adicional a adquirir/fixar; nenhuma série255 pronta | versão própria de Fogo não equivale à coleção de cobertura; não extrair informação de t+1; registro de grade/máscaras |
| PRODES | incremento anual, resíduos separados e estoques/acumulados passados | raster local versão2025 e CSV legado presentes;251/255, ainda não harmonizados | reinterseção255, janelas agosto–julho e diferenças de bioma/época; sem reutilizar alvo PRODES ou supor equivalência com toda VN operacional |
| Socioeconomia | PAM/PPM, área agrícola/rebanhos, população, PIB e estrutura produtiva, contemporâneos ou lags com referência até t | fontes adicionais e correspondências territoriais a adquirir/construir | revisões/metadados declarados; limites históricos podem divergir de2025; não interpolar usando futuro para simular série observada |

As quatro entradas ausentes nas tabelas complementares legadas são
2101772, 2108504, 2112274 e 5101837. Presença de registros nos outros251 não
comprova harmonização espacial/temporal. O painel antigo de268 não é a matriz nova.

Publicações posteriores já documentadas (Col9 em2024, PRODES local2025, PAM/PIB
com atrasos) são mantidas na linhagem como versões retrospectivas. Isso não
transforma informações do fenômeno em t+1 em atributos permitidos para t.
Datas de referência, dependência máxima e versão permanecem campos obrigatórios.

## Montagem futura, sem atalhos de ausência

- Derivar atributos por município, em janelas somente para trás e com joins
  auditados. Conservar as 9.690 chaves no índice e registrar exclusões,
  disponibilidade e motivo de NA por bloco; não reduzir silenciosamente a251.
- Não preencher 1985–2002 sem focos com zero. Não tratar mês sem linha como
  ausência confirmada de fogo, nem município sem estatística como população zero.
- Para lags/janelas iniciais, conservar NA e indicador de falta de histórico;
  qualquer recorte de coorte deve ser declarado e comparado no mesmo suporte.
- C(m,t), R(m,t), D do suporte t/t+1, Q do desfecho, classe t+1, eventos
  candidatos, respostas temáticas/adjudicação e flags futuros ficam fora de X.
  Um atributo histórico de conversão deve terminar em t (origem no máximo t−1).
- Variação líquida passada é um atributo distinto de conversão espacial, sem
  ser chamada de desmatamento. 25 permanece separado; sensibilidades29/32
  não redefinem automaticamente o atributo principal ou a resposta.
- Imputação, escalas, seleção, regularização, pesos/reponderação,
  calibração e limiar de probabilidade são aprendidos somente no treino do
  respectivo fold. Não aprender transformações com teste ou toda a série.
- O limiar ambiental não será escolhido por frequência de positivos ou
  desempenho de ML. Uma variável de resposta ainda não homologada não será
  silenciosamente gerada a partir dos estados candidatos A/B/C.

## Validação temporal e espacial preservada

Mantém-se a proposta anterior para aprovação antes do treino:

| Papel | Anos t | Quantidade de chaves no índice completo |
|---|---|---:|
| Treino inicial | 1985–2013 | 7.395 |
| Embargo | 2014 | 255 |
| Validação | 2015–2017 | 765 |
| Embargo | 2018 | 255 |
| Teste temporal reservado para ajuste | 2019–2022 | 1.020 |

Validação interna por avanço temporal no desenvolvimento inicial:
treino até2001/validação2003–2005; até2005/2007–2009; até2009/2011–2013.
Embargo de um ano evita compartilhar o mesmo mapa dos pares imediatamente
adjacentes entre treino e validação/teste, mas não elimina autocorrelação ou
dependência do algoritmo de classificação. Alterações de embargo precisam
critério científico prévio; não serão escolhidas pelo melhor teste.

LOSO: cinco folds MA/MT/PA/RO/TO. A UF retida fica fora do ajuste, escolha
de atributos/hiperparâmetros e calibração em **todos** os anos. Nas demais UFs,
usar os mesmos cortes temporais. Testar a retida em t2019–2022. Eventual reajuste
final usa somente as outras UFs até2017, preservando embargo2018 e teste.
Não escolher o melhor estado, juntar previsões LOSO para ajustar o modelo ou
usar respostas futuras de vizinhos. Um grafo novo deve ter regra explícita
para estado não visto; buffers de fronteira são análise adicional a definir,
não eliminação automática de municípios difíceis.

Reportar resultados por UF/período, macroagregados, tamanho da coorte,
suporte e qualidade, sem esconder estados com desempenho ruim. Métricas
futuras dependerão do objetivo aprovado: para binário, precisão–revocação,
average precision, precisão/recall/F1, calibração/Brier e AUROC complementar;
para magnitude contínua, uma alternativa distinta requer protocolo e aprovação.
Incerteza deve respeitar dependência espacial/temporal; não bootstrap de linhas
independentes por conveniência. Nenhuma métrica de modelo foi calculada aqui.

## Exposição científica do teste

Os últimos anos, picos e municípios extremos **já foram explorados**, e o
piloto também inclui casos recentes. O teste é separado do ajuste futuro,
mas **não é completamente cego à formulação do desfecho**. Registrar essa
exposição e congelar hipóteses/regras antes de treinar; não alegar que a
pesquisa manteve os rótulos inteiramente desconhecidos. Aprovação científica
de tau não pode ser substituída por otimização nos anos/UFs de teste.

Uma confirmação totalmente nova exigiria decisão sobre dados externos/anos
adicionais. Este encaminhamento não decide o papel de2024 nem o transforma
em teste automaticamente. Não há autorização de treinamento definitivo.

## Artefatos e situação

`modelagem/protocolo_retrospectivo_col9.py` gera o catálogo de blocos,
índice principal sem rótulos e partições propostas em
`validacao_cientifica_col9/piloto_interpretacao_20261111_v1/modelagem_retrospectiva/`.
`validar_previsor()` separa erro de fenômeno futuro/desfecho corrente de
risco de publicação/revisão tardia. Ele não certifica a causalidade do produto
ou libera automaticamente blocos; a interpretação de dependências permanece
parte da decisão científica. A função antiga as-of foi preservada com seus
testes, mas não rege o experimento principal escolhido agora.

Próximas decisões: concluir piloto, validar protocolo de referência e
definição de relevância, resolver dependência temporal dos atributos, aprovar
blocos e harmonizações, congelar partições e só depois autorizar uma etapa
de montagem/avaliação de modelos. Nenhum X/Y definitivo ou modelo foi criado.
