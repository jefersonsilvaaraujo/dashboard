# Proposta de variável alvo de conversão significativa em t mais 1

Status: **proposta para validação antes da modelagem**. Não há limiar escolhido,
variável-alvo produzida ou modelo novo treinado. D1–D4 aprovadas regulam os
indicadores descritivos; não autorizam converter automaticamente seus estoques
líquidos em rótulos de conversão.

## Pergunta e unidade de previsão

Prever, no fim do ano civil t, se o município terá conversão espacial significativa
de vegetação nativa para usos antrópicos mapeados entre os mapas t e t+1.
A unidade é município–ano, sempre nos 255 limites fixos IBGE 2025.
São possíveis 38 pares anuais (1985→1986 até 2022→2023), não 39 alvos observados.
O ano 2023 não possui rótulo t+1 nesta coleção e não será preenchido com zero.

Uma variação líquida pode ocultar simultaneamente conversão e recuperação, ou
resultar de diferença de máscara. Por isso o alvo virá de coincidência espacial
de pixels, nunca de `A_VN(t+1) - A_VN(t)` nem dos alvos do painel legado.

## Pré-requisitos geoespaciais

1. Manifesto explícito de um raster anual aprovado por ano, com hash, grade, CRS,
   transform, tamanho, NoData e proveniência. Os vários candidatos de 2002 precisam
   de identificação explícita; não escolher arquivos por glob ou pelo tamanho.
2. Conferir coincidência exata das grades. Não empregar bilinear/cúbica em classes.
   Qualquer necessidade de harmonização de grade exige procedimento próprio e
   auditoria antes de calcular transições.
3. Reproduzir o complemento dos três municípios do MA apenas em zeros, preservando
   os rasters físicos. Guardar a origem e a quantidade de pixels complementados.
   As imagens reduzidas da Fase 2 não são entradas para essa análise.
4. Usar a geometria original verificada por hash. Recomenda-se manter a regra de
   centro do pixel do processamento atual, declarando a aproximação de borda;
   uma regra fracionária seria outro protocolo a validar separadamente.
5. Calcular pesos de área geodésica dos pixels conforme a latitude, compatíveis
   com a grade original e o método WGS84 dos CSVs. Não pressupor 0,09 ha por pixel.

## Máscara comum e matriz de transições

Para cada município m e par t,t+1, definir `M_comum` como os pixels dentro do limite
municipal que tenham observação válida nos dois mapas. Excluir 0, 27 e o NoData
de cada arquivo; código desconhecido interrompe a análise. Pixels ausentes em
apenas um dos anos não viram conversão nem permanência.

Produzir a matriz completa origem→destino por código Col9, com número de pixels
e soma das áreas geodésicas. Isso permite auditar mudanças entre classes nativas,
água, classe 25 e usos antrópicos sem interpretar todas como conversão de interesse.

Conjuntos principais já aprovados:

- `VN = {3,4,5,6,49,11,12,50}`.
- `UA = {9,15,20,21,24,30,31,35,39,40,41,46,47,48,62}`.

Numerador da conversão bruta mapeada:

`C(m,t) = soma da área dos pixels em M_comum com classe(t) em VN e classe(t+1) em UA`.

Denominador da taxa:

`D(m,t) = soma da área dos pixels em M_comum com classe(t) em VN`.

Taxa proposta: `R(m,t) = 100 * C(m,t) / D(m,t)`.

Essa taxa responde qual fração da vegetação nativa inicial elegível mudou para
uso antrópico no ano seguinte. Não usa a área total classificada como denominador:
é uma medida de transição, distinta dos indicadores descritivos D2.
Denominador zero ou observação inadequada resulta em rótulo não avaliável, não negativo.

Guardar também a fração da vegetação nativa de t que permaneceu elegível na máscara
comum. A conversão em uma amostra muito pequena não pode representar o município
inteiro silenciosamente. Um mínimo de elegibilidade deverá ser validado junto ao limiar.

## Limiar de significância e qualidade do rótulo

Proposta de forma do evento:

`Y(m,t) = 1 se R(m,t) >= tau e C(m,t) >= A_min; 0 se abaixo dos critérios e avaliável; NA se não avaliável`.

`tau` é um limiar percentual de relevância substantiva; `A_min` é uma salvaguarda
de área mínima para evitar que poucos pixels determinem eventos em denominadores
pequenos. Ainda é preciso decidir se os dois critérios serão exigidos e quais
valores se justificam. “Significativa” será uma definição operacional de relevância,
não uma declaração automática de significância estatística ou de impacto ambiental.

O procedimento recomendado é:

1. Separar antecipadamente uma amostra de referência para verificar transições,
   incluindo casos estáveis, fronteiras de classe, áreas pequenas e anos críticos.
   Usar interpretação temporal independente ou referência primária apropriada;
   acurácia global da coleção não certifica cada transição municipal anual.
2. Quantificar transições espúrias e persistência das mudanças; examinar matrizes
   e amostras espacialmente distribuídas. Uma exigência de persistência em t+2
   alteraria o alvo e o último ano utilizável, e precisa de aprovação separada.
3. Avaliar uma grade de candidatos a tau/A_min com justificativa científica e
   análise de estabilidade. Não escolher o limiar apenas por balancear classes
   ou maximizar o desempenho do modelo. Não fixar valores por conveniência.
4. Usar somente o período/conjunto de desenvolvimento para escolhas empíricas.
   Reservar anos e municípios/blocos geográficos independentes para verificar a
   qualidade do rótulo e a estabilidade, sem reajustar o limiar no teste final.
5. Registrar prevalência do evento, casos próximos ao limiar e sensibilidade de
   cada município a diferentes tau/A_min e critérios mínimos de elegibilidade.

A classe 25 continuará separada. Recomenda-se um cenário incluindo VN→25 como
conversão potencial. Se esse cenário mudar o rótulo em relação ao cenário principal,
propor uma marca de ambiguidade e avaliar sua exclusão do treinamento principal,
em vez de impor um rótulo negativo. Isso ainda depende de validação específica.
O cenário com 29/32 no conjunto inicial também será reportado separadamente.
Mudanças para a classe 33 não podem ser automaticamente atribuídas a reservatórios
antrópicos a partir desse código apenas.

## Auditoria obrigatória de Buriticupu em 2001–2003

Código IBGE 2102325. Avaliar separadamente 2001→2002 e 2002→2003, com:

- Pixels/áreas válidos em cada ano, interseção válida, perdas/ganhos de máscara
  e pixels complementados; reportar numerador e denominador elegíveis.
- Matriz completa de transições por par com máscara comum própria.
- Repetição sobre a interseção válida dos três anos, como teste de sensibilidade
  da diferença de suporte espacial entre os dois pares.
- Inspeção espacial de mudanças próximas às bordas e pixels excluídos, comparando
  com municípios de controle e os casos documentados de Urbano Santos/Santo Amaro.
- Verificação independente da origem do raster 2002 e das auditorias históricas,
  sem tratar a concordância amostral anterior como validação de todos os pixels.

A auditoria de estoques da Fase 1 encontrou, em Buriticupu:

| Ano | Área classificada (ha) | Área geodésica do limite (ha) | Diferença (ha) |
|---|---:|---:|---:|
| 2001 | 254.280,9387 | 255.363,1662 | −1.082,2275 |
| 2002 | 255.356,6783 | 255.363,1662 | −6,4879 |
| 2003 | 254.280,9389 | 255.363,1662 | −1.082,2273 |

Esses valores reforçam a necessidade da auditoria de máscara, mas não são
transições calculadas nem fornecem, sozinhos, um rótulo de conversão.

## Construção sem vazamento temporal

O rótulo usa t+1; os preditores devem estar disponíveis até o corte de previsão em t.
Não usar C(m,t), R(m,t), área observada em t+1, estatísticas futuras, medidas de
qualidade que só se tornam conhecidas em t+1 ou qualquer função do rótulo como atributos.
Guardar covariáveis e rótulos em estruturas separadas com tempos de referência.

As divisões devem respeitar simultaneamente tempo e dependência espacial. Propõe-se
validação por avanço temporal e um teste espacial separado por blocos/grupos de
municípios. Um corte só temporal não demonstra generalização para municípios novos;
um corte só espacial não protege contra informação futura. Ajustes de imputação,
seleção de atributos, escalas, pesos e hiperparâmetros ficam restritos ao treino.
Os rótulos de treino devem estar encerrados e disponíveis até o corte de cada rodada.

A documentação de [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
trata a ordem temporal, enquanto [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
separa grupos. Nenhum dos dois, isoladamente, implementa todo o protocolo espacial
e temporal aqui proposto; as divisões precisam ser verificadas explicitamente.

Se PRODES/queimadas forem utilizados depois da Fase 3, explicitar suas janelas e
datas de disponibilidade. Não reutilizar automaticamente o painel legado ou
variáveis reconstruídas a partir de estoques finais futuros.

Há ainda uma limitação de disponibilidade: a Col9 é um produto retrospectivo.
Usar seus mapas históricos para avaliar previsões caracteriza um experimento
retrospectivo; não prova que os mesmos atributos estavam disponíveis operacionalmente
naquelas datas. Essa distinção deve constar na dissertação.

Para classificadores, priorizar precisão–revocação/PR-AUC, recall, precisão, F1,
matriz de confusão e calibração, com AUROC complementar. Separar o limiar
ecológico tau do limiar de probabilidade usado para decidir a previsão do modelo.
Comparar com referências simples e não modificar o teste final para melhorar métricas.
As definições de métricas e sua implementação devem seguir a
[documentação de avaliação do scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html#precision-recall-f-measure-metrics),
registrando se foi usada average precision ou integração da curva precisão–revocação.

## Entregáveis exigidos antes de treinar

1. Manifesto de rasters e de correções, código versionado e testes de máscaras,
   grade, áreas, somas da matriz, eventos e casos NA.
2. Relatório completo de Buriticupu e análise de sensibilidade regional/municipal.
3. Definição aprovada de taxa, tau, A_min, elegibilidade, ambiguidade e persistência.
4. Tabela município–ano com C, D, R, flags de qualidade, versão do rótulo e Y.
5. Plano de divisões temporais/espaciais e disponibilidade dos preditores.

Nenhum desses resultados de transição ou modelagem foi declarado pronto neste
checkpoint. A proposta deve ser revisada antes de iniciar essa etapa.
