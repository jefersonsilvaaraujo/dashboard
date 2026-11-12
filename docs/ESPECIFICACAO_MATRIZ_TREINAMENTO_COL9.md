# Especificação da matriz município–ano Coleção 9

11/11/2026. Etapa C: especificação e índices sem rótulos executados; X, Y e
treinamento definitivo não produzidos. Depende da validação temática e da
aprovação científica de tau, A_min, elegibilidade e tratamento de ambiguidade.

## Unidade, chave e relógios

Chave primária `(CD_MUN, ano_t)`, com os 255 códigos e os limites IBGE 2025
verificados por WKB/SHA256. `CD_MUN` é identificador, não previsor contínuo.
UF serve para agrupamento/avaliação, com hipótese explícita se entrar em X.
O universo de desenvolvimento tem 9.690 chaves: t=1985…2022, desfecho entre
os mapas t e t+1, finalizando em 2023. O índice adicional possui 255 linhas
t=2023 **sem desfecho observado**, nunca preenchidas com zero. Total do índice:
9.945 linhas; `ano_desfecho` é ausente em 2023 e nenhuma coluna Y é criada.

O corte idealizado é 31/dez/t às 23:59:59 em America/Sao_Paulo. Os registros
em UTC devem ser convertidos antes de comparar com o corte. Quatro relógios
devem ser armazenados: período de referência do fenômeno, data da observação,
data efetiva de publicação da versão e data máxima de qualquer informação
utilizada no processamento. Data de download/mtime não prova disponibilidade
histórica. Meses/anos sem dia conhecido devem ter intervalo de disponibilidade;
usar o limite superior conservador ou bloquear, sem inventar uma data precisa.

Estruturas futuras separadas:

| Estrutura | Campos essenciais | Uso |
|---|---|---|
| cadastro_territorial | código, UF, geometria/hash, área, versão | contrato fixo dos 255 |
| observacoes_previsores | código, variável, referência início/fim, valor/unidade, observado_em, publicado_em, dependência máxima, versão/hash, qualidade | linhagem longa, nenhuma função de t+1 |
| X_asof | chave, corte, atributos aprovados, flags de lacuna e linhagem | somente observável até corte |
| desfechos_continuos | chave, t+1, C, D, R, suporte e qualidade | área de resposta; nunca anexar automaticamente a X |
| referencias_tematicas | unidade sorteada, respostas/evidências/adjudicação | incerteza e validação |
| Y_versionado_futuro | chave, Y/NA, regra aprovada, motivo de NA, versão, quando disponível | ainda não autorizado/homologado |
| particoes | chave, papel, fold, estado retido, hash e data de congelamento | isolamento de treino/validação/teste |

Todos os joins devem ser `one_to_one` ou `many_to_one` declarados, mantendo
todas as chaves canônicas e relatórios de anti-join. Não usar inner join que
reduza silenciosamente para 251 ou 268 municípios. Não criar tabelas no banco
como parte desta entrega; esses são nomes lógicos propostos.

## Disponibilidade: limitação científica central

A Coleção 9 cobre 1985–2023, mas foi publicada em **agosto/2024**, conforme
[histórico oficial MapBiomas](https://old-brasil.mapbiomas.org/produtos/).
Logo, nenhuma variável extraída diretamente desse produto estava disponível
como Coleção 9 no final dos anos t de 1985–2023. Há também risco de dependência
futura de revisão/processamento temporal; o nome `classification_t` não garante
que seu cálculo utilizou somente informações até t.

São necessários dois experimentos distintos, que não devem ser confundidos:

- **Retrospectivo:** X reconstruído de produtos revisados, com corte nominal
  dos anos dos atributos. Pode estudar associação/predição retrospectiva, mas
  não demonstra desempenho operacional histórico. A dependência temporal dos
  algoritmos deve ser auditada; mesmo t−1 pode conter informação futura se o
  produto foi filtrado/revisado posteriormente.
- **Operacional as-of:** somente versões e dependências disponíveis no corte.
  Requer arquivos históricos de publicação, observações primárias processadas
  causalmente ou uma fonte alternativa validada. O acervo atual não comprova
  esse requisito para todos os 38 pares. Não basta aplicar `shift(1)` a um
  produto revisado de 2024/2025.

A resposta pode ser apurada e validada depois do evento; isso é normal em
supervisão retrospectiva. Sua publicação tardia, porém, impede alegar que o
treinamento/reajuste histórico já dispunha daqueles rótulos. Cada experimento
deve declarar se usa separação nominal de anos ou simulação operacional real.
Nenhum treino será iniciado ocultando essa limitação.

## Inventário dos previsores candidatos

O inventário computado em
`validacao_cientifica_col9/checkpoint_20261111/matriz_especificacao_v2/inventario_fontes_locais.json`
registra hashes, colunas, anos e municípios dos CSVs existentes. Eles foram
somente lidos. Presença no legado não significa compatibilidade territorial.

| Família e candidatos | Referência e acervo real | Disponibilidade efetiva e regra | Lacunas/decisões antes de X |
|---|---|---|---|
| MapBiomas Col9: áreas/proporções das classes, VN principal, UA, 25/29/32/33, composição e fragmentação | 255×39; rasters/estoques aprovados, 1985–2023 | Produto agosto/2024; dia exato não fixado aqui; usar intervalo do mês. Em modo operacional, bloquear para todos os t históricos; dependências do classificador a auditar | mesma geometria/área classificada; regra de fragmentação e resolução precisam protocolo próprio. Não substituir por Col10.1 |
| Col9: variação líquida t−1→t, tendências móveis 3/5 anos, conversão histórica até t | calculáveis dos estoques/matrizes, sem usar t→t+1 | mesma limitação da publicação/revisões; janelas somente para trás; transições encerradas até t | primeiros anos sem histórico são NA, não zero; variação líquida não é desmatamento nem resposta |
| PRODES: incremento anual, estoque acumulado, resíduos separados, lags | CSV 9.583 linhas/268; interseção 251/255; classes com anos 2000–2025. Raster local versão 2025 v20261020 | Ano PRODES agosto–julho, não ano civil. Na Amazônia, estimativa até dezembro e consolidado no semestre seguinte segundo [INPE](https://www.obt.inpe.br/OBT/noticias-obt-inpe/inpe-esclarece-sobre-sistemas-de-monitoramento). É preciso data real de **cada** versão municipal; taxa estimada divulgada não prova disponibilidade do mapa consolidado | 2101772,2108504,2112274,5101837 ausentes; reinterseção dos rasters nos limites fixos ainda necessária. Não transformar ausência em zero ou reutilizar alvo PRODES. O raster 2025 é retrospectivo para anos anteriores |
| Focos: contagem civil/mensal/sazonal, densidade, FRP, dias sem chuva, risco e precipitação nos focos | CSV 41.367 linhas/268; interseção 251/255; 2003–2025. ZIPs do satélite de referência 2003–2025 presentes | [FAQ INPE](https://data.inpe.br/queimadas/faq/) informa atualização frequente após QA, mas não comprova a latência histórica de cada foco/atributo arquivado. Exigir timestamp de publicação/arquivo as-of; 31/dez completo pode não estar disponível no próprio corte | mesmos quatro ausentes; meses sem linha não são automaticamente zero; FRP/meteo não existem em todas as épocas. Atributos condicionados a haver foco não são clima médio municipal. Cobertura espacial/satélite e revisões devem ser auditadas |
| Área queimada: ha/% anual, recorrência e lags | não há série integrada para os 255 nem rasters de área queimada identificados entre as entradas usadas pelo código atual | candidato: versão específica MapBiomas Fogo, sem equivalência com coleção de cobertura. Exemplo oficial [Coleção 4](https://old-brasil.mapbiomas.org/en/lancamentos/): 1985–2024, lançamento 24/06/2025. Bloquear operacional histórico sem vintage anterior causal | ainda adquirir/fixar versão, manifestar grades, calcular suporte nos mesmos 255; foco não equivale a hectare queimado; não substituir fogo em VN por conversão |
| IBGE PAM/PPM: área plantada/colhida, produção, efetivo bovino, densidades e lags | não integrados para os 255 neste checkout | calendário e revisão específicos por publicação. Exemplo: [PAM 2023](https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/41296-pam-2023-safra-bate-recorde-mas-valor-da-producao-cai.html), divulgada 12/09/2024; não disponível em dez/2023. Para cada ano e variável, data documental é obrigatória | divisões/criações municipais e limites estatísticos históricos não equivalem ao limite 2025; exigir correspondência ou declarar incompatibilidade; não ratear automaticamente |
| IBGE PIB/população/censos | não integrados como candidatos Col9 | [PIB municipal 2022–2023](https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088-produtointerno-bruto-dos-municipios.html) é publicação de 2025, não informação disponível em 2023. Censo/estimativas têm calendários próprios. Datas exatas por versão ainda pendentes | não interpolar usando censos futuros, nem retropreencher PIB divulgado depois do corte; censos ausentes não são população zero |
| Território: área geodésica, latitude, relevo, bioma, distâncias a estradas/áreas protegidas, fronteira e vizinhança | GeoPackage 255 disponível; biomas IBGE 2019 locais. Relevo/estradas/áreas protegidas históricas ainda não integrados | recorte IBGE 2025 é convenção retrospectiva da unidade. Publicação de cada camada histórica precisa auditoria. Relevo estático não autoriza usar estrada criada em t+1 ou proteção decretada depois | gerar a partir da geometria canônica; variável estática explicitamente separada de variável dinâmica; grafo antigo dos 268 e normalização com teste não podem ser reutilizados |

Na série de focos o INPE documenta mudança de satélite de referência em 2002,
NOAA-12→AQUA, e revisões da base; a série local começa em 2003. Não extrapolar
esses dados para 1985–2002 com zeros. Atualização de um serviço a cada dez
minutos não é prova de publicação imediata de cada produto anual consolidado.
As datas desconhecidas permanecem **desconhecidas/bloqueadas**, não estimadas
por conveniência. Aquisição e harmonização das famílias pendentes são trabalho
futuro separado; este inventário não libera o uso científico de 251 geometrias antigas.

## Ausência, transformação e barreiras contra vazamento

- Distinguir `nao_observado`, `nao_disponivel_no_corte`, `fora_escopo`,
  `ausencia_de_evento_com_cobertura_confirmada` e `falha_de_processamento`.
  Zero só no quarto caso, com evidência de cobertura válida completa.
- Não preencher os quatro municípios ausentes com zero. Para município recém
  criado sem série harmonizada, manter lacuna e a decisão explícita da pesquisa.
- Tabelas de qualidade do desfecho — máscara comum t/t+1, D elegível, C, R,
  Q, referência/adjudicação, exclusões e estado candidato — ficam fora de X.
  A VN **observada em t** pode ser atributo; D sobre máscara t/t+1 não pode.
- Agregações móveis devem ser retrospectivas e por município; não usar janela
  central, interpolação com futuro, estatística dos anos completos, total de
  eventos futuros, taxa futura de vizinhos ou codificação por alvo calculada no teste.
- Imputação, seleção, escalas, pesos, reamostragem e ajuste de probabilidade
  são aprendidos só no treino de cada fold. Guardar indicadores de ausência;
  não imputar resposta. Categorias novas em estado retido precisam regra prévia.
- Aplicar uma barreira de disponibilidade por atributo e linha: referência,
  publicação da versão e dependência máxima ≤ corte. Data desconhecida bloqueia.
  `verificar_disponibilidade()` implementa esse contrato, inclusive fusos.
  Seu teste sintético não certifica a linhagem dos dados reais.

## Avaliação futura temporal e leave-one-state-out

Proposta congelável **antes de treinar**; não é uma seleção automática de períodos:

| Papel temporal | Anos t | Desfechos | Observação |
|---|---|---|---|
| Desenvolvimento/treino inicial | 1985–2013 | 1986–2014 | filtrado por disponibilidade e qualidade aprovadas |
| Embargo | 2014 | 2015 | separar pares adjacentes |
| Validação | 2015–2017 | 2016–2018 | escolhas empíricas permitidas somente no desenvolvimento |
| Embargo | 2018 | 2019 | não ajustar pelo teste |
| Teste temporal reservado | 2019–2022 | 2020–2023 | avaliação final única após congelamento científico/modelo |
| Previsão sem resposta Col9 | 2023 | não observado | nunca rótulo negativo |

Dentro do desenvolvimento inicial, avanço temporal proposto:
treino até 2001/validação 2003–2005; até 2005/2007–2009; até 2009/2011–2013.
Somente arquivos causais/as-of podem sustentar alegação operacional nesses cortes.
O embargo de um ano é proteção mínima contra compartilhamento de mapas dos
pares adjacentes; não elimina autocorrelação. Ampliar por critério ambiental
pré-especificado, nunca pelo melhor resultado no teste.

LOSO: cinco folds, retendo uma UF inteira (MA, MT, PA, RO, TO). Todos os anos
do estado retido ficam fora de treino, seleção e calibração; testar esse estado
apenas em t=2019–2022. Nas quatro UFs restantes, usar os mesmos cortes de treino
e validação. Estados/municípios vizinhos podem ser dependentes; um experimento
com buffer na fronteira deve ter distância e perda de amostra registradas antes
do ajuste. Não selecionar o melhor estado ou descartar o pior fold. Reportar
desempenho por UF e macroagregado, além de volume e qualidade do suporte.

Modelos/configurações, imputação e calibração do teste de uma UF não podem ter
visto respostas daquele estado em qualquer ano. Cada fold é uma avaliação
separada: não juntar previsões de folds para escolher hiperparâmetros. Após a
escolha no desenvolvimento, permitir reajuste nas outras UFs até t=2017,
preservando o embargo de 2018 e o teste retido. Não acessar respostas futuras
de vizinhos nem reusar a vizinhança materializada do legado de 268 municípios.

**Independência e exposição já ocorrida:** os relatórios científicos solicitados
incluem todos os anos/UFs e inspeções de extremos, inclusive 2022/2023. Portanto
o teste proposto é separado do ajuste, mas **não é um teste científico totalmente
cego à exploração/definição do evento**. Não é possível apagar essa exposição.
Registrar o acesso, congelar agora hipóteses/regras e evitar ajuste de tau por
frequências/resultados do teste. Uma confirmação inteiramente nova exigiria
coorte externa ou anos posteriores com produto e comparabilidade aprovados;
não substituir automaticamente 2024 por dados Col10.1.

Métricas futuras: average precision/curva precisão–revocação, precisão, recall,
F1, matriz de confusão, AUROC complementar, Brier/calibração e incerteza por
conglomerados/blocos temporais. Definir população, prevalência e política de NA;
comparar referências simples. Limiar ecológico tau não é limiar de probabilidade
do classificador. Nenhuma dessas métricas foi calculada nesta entrega.

## Artefatos, testes e decisões pendentes

`modelagem/contrato_matriz_col9.py` gera o índice e as propostas de partições,
sem X/Y. Saída ativa: `validacao_cientifica_col9/checkpoint_20261111/matriz_especificacao_v2/`.
A primeira especificação foi preservada; v2 acrescenta tratamento explícito de
fuso na barreira de disponibilidade. Os índices não foram usados para treino.

Testes: chaves 255×39, 38 transições observáveis, 2023 sem desfecho, rejeição
de 268, datas futuras/desconhecidas e fusos, bloqueio de atributos da resposta,
separação temporal e exclusão integral da UF retida. Suíte completa: 61 testes
principais e 16 geoespaciais aprovados, 77 distintos; três módulos são ignorados
no ambiente principal e executados no geoespacial. Logs em `docs/evidencias/validacao_*`.

Antes de montar X/Y: aprovar resultado temático e critérios de relevância;
decidir retrospectivo versus operacional; recuperar/harmonizar variáveis dos
255 municípios; fixar versões/datas efetivas; validar ausência e dependências;
congelar partições e protocolos. Nenhum treino definitivo ou homologação de
variável-alvo foi iniciado. Banco PostgreSQL, fontes, dashboard e checkpoints
anteriores permanecem preservados.
