# Protocolo proposto de regressão retrospectiva
12/11/2026. Proposta ao orientador; nenhum treinamento, otimização ou homologação.

## Pergunta, modelos e baselines
Prever R(m,t), conversão mapeada t→t+1, com fenômenos observados até t,
nos 255 limites fixos. C em hectares terá experimento secundário próprio, se aprovado.
A análise é retrospectiva, sem reivindicar disponibilidade operacional histórica.
A lista 53 é candidata. CD_MUN/ano_t são chaves, UF agrupamento e Q não é atributo.

Comparar Ridge/Elastic Net regularizados, Random Forest Regressor e XGBoost
Regressor. LogisticRegression classificatória não é baseline contínua.
Versões/sementes serão fixadas na autorização futura, não por instalação de
estimadores agora. Nenhum modelo adicional foi incluído automaticamente.

Referências simples: média/mediana do treino do fold; histórico municipal
calculado apenas no treino, com fallback global do treino para município/UF
retidos. Grupos territoriais não podem usar estatísticas reservadas.
Última taxa encerrada antes do intervalo é candidata quando disponível,
condicionada à decisão origem móvel versus histórico congelado na auditoria.
Comparar no mesmo suporte; falta de histórico não vira zero.
Não foram calculadas previsões dessas baselines.

## Escalas, limites e perdas
R direta em pontos percentuais é a primeira candidata. Forest com médias de
folhas/pesos não negativos respeita o intervalo de treino; lineares/boosting
quadrático podem extrapolar[0,100]. Futuramente contar/reportar extrapolações;
não truncar silenciosamente. Restrição/link limitado precisa pré-especificação,
comparando métricas originais e procedimento declarado, nunca escolha pelo teste.

Logit de R/100 exige interior(0,1) e regra para eventuais endpoints, sem epsilon
arbitrário. Após inversão, o estimando não é automaticamente a média original.
Transformações monotônicas só serão escolhidas no desenvolvimento; métricas
principais sempre após inversão correta.

ParaC: direta não negativa, log1p(C/1 ha) e perdas robustas são alternativas.
Gamma exigiria C estritamente positivo; a série atual não garante zeros ausentes
no futuro. Tweedie seria opcional com justificativa. Hectares não são contagem
Poisson por definição. Nada foi escolhido pela assimetria ou desempenho.

Converter R prevista usando D realizado é informação futura, não previsão
genuína em hectares. O experimentoC precisa estimando/modelo próprio e mesmas partições.
Não comparar respostas por uma métrica que misture unidades.

## Métricas e calibração regressiva
Proposta principal: MAE de R em pontos percentuais. Complementares: RMSE na mesma
unidade; viés=média(previsto−observado), sinal explícito; R², podendo ser negativo
eNA quando variância da resposta é nula, sem substituir indefinições por sucesso.
ParaC, MAE/RMSE/viés em hectares e R² próprio. MAPE não é principal por valores próximos
de zero. Modelos transformados retornam à escala original antes das métricas.

Reportar micro município–ano e macro por município/UF/ano, tamanho das coortes,
erros por magnitude, estoque e qualidade. Limites de faixas aprendidas devem
ser estimados no treino e congelados; não importar quintis globais do diagnóstico.
Analisar heterocedasticidade/extremos e dependência do erro em relação ao estoque.
D pode aparecer na análise posterior do erro, nunca como atributo corrente.
Ponderação por área/estoque altera o estimando e deve ser complementar.

Calibração: comparar magnitudes previstas/observadas por faixas de previsão
congeladas no desenvolvimento, com tamanho de grupos; não ajustar calibração
nos rótulos do teste. Brier/AUROC não são métricas principais desta regressão.

## Validação temporal
| Papel | Anos t | Chaves |
|---|---|---: |
| Treino inicial |1985–2013|7395|
| Embargo |2014|255|
| Validação |2015–2017|765|
| Embargo |2018|255|
| Teste reservado |2019–2022|1020|

Avanço interno: até 2001/2003–2005; até 2005/2007–2009; até 2009/2011–2013,
com um ano de embargo. Escolhas ficam no desenvolvimento; eventual reajuste
final até 2017 depende de congelamento anterior ao teste. Nenhuma busca foi feita.

O embargo separa pares adjacentes que compartilham ano de mapa, mas não remove
autocorrelação ou filtros longos. Não escolher extensão pelo melhor teste.
Anos finais/extremos já foram explorados cientificamente: o teste não é
completamente cego à formulação, embora separado do ajuste futuro.
2024 não é teste externo e não será usado.

## Validação espacial
Cinco folds MA/MT/PA/RO/TO, retirando integralmente cada UF de ajuste,
imputação, seleção, escala, transformação, validação interna e calibração
em todos os anos. Avaliar a UF retida apenas emt 2019–2022; demais UFs mantêm
os cortes. Não combinar previsões LOSO para ajustar o mesmo modelo ou escolher
o melhor estado. Matrizes de partições materializam a regra.

Covariáveis conhecidas da UF retida emt são distintas de usá-la no ajuste;
o regime dos históricos deve ser pré-especificado. Considerar correlação
de fronteira e eventual buffer como proposta adicional, não criar
automaticamente grafo/buffer nem herdar 268. RO tem 5 municípios, limitando
interpretação de incerteza espacial. Não assumir amostras iid.

## Controle de aprendizado, interpretação e incerteza
Imputação, padronização, seleção, regularização, transformações aprendidas,
calibração e grupos dependem somente do treino do fold. Flags já criados
são determinísticos; imputação não ocorreu. Coluna inteiramente ausente no
treino exige regra do treino, sem aprender em validação/teste.
Disponibilidade nativa de um algoritmo não dispensa transparência de ausência/coorte.

Prever comparações com baselines, importâncias documentadas com cautela à
correlação, erros por grupos e mapas municipais de R prevista/resíduos, além
de C quando houver experimento independente. Importância é associação preditiva,
não causalidade. Não apresentar mapas binários de probabilidade como principal.

Incerteza preditiva exige método próprio respeitando dependência temporal/
espacial e pressupostos de intervalos, quantis ou conformal. Não prometer
cobertura automática. Ela não mede acurácia cartográfica nem corrige a resposta.

Fontes técnicas: [vazamento, scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html),
[métricas](https://scikit-learn.org/stable/modules/model_evaluation.html),
[objetivos XGBoost](https://xgboost.readthedocs.io/en/stable/parameter.html),
consultadas 12/11/2026 e arquivadas. O desenho é da pesquisa, não dessas páginas.

Aprovar antes de treinar: estimando/objetivos; papel de C; admissibilidade/ablações;
históricos no teste; coorte/qualidade; perdas/métricas e plano congelado.
A guarda da preparação sempre recusa treino/otimização.
