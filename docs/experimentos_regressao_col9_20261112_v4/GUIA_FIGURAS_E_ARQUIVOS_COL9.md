# Figuras, tabelas e auditorias

As figuras finais abaixo foram geradas das predições imutáveis. A revisão visual
melhorou legendas e disposição dos painéis; as primeiras figuras foram preservadas.
As oito figuras finais têm versões PNG e SVG no mesmo diretório. As demais figuras
de resíduos, erros por estado, médias anuais e calibração estão no diretório
`apresentacao/figuras`. Todas integram o manifesto final.

- [Taxa: observado e previsto](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/observado_previsto_R_pct.png)
- [Taxa: mapas municipais](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/mapas_municipais_R_pct.png)
- [Taxa: mapas LOSO](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/mapas_LOSO_R_pct.png)
- [Taxa: importância na validação](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/importancias_validacao_R_pct.png)
- [Hectares: observado e previsto](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/observado_previsto_C_ha.png)
- [Hectares: mapas municipais](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/mapas_municipais_C_ha.png)
- [Hectares: mapas LOSO](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/mapas_LOSO_C_ha.png)
- [Hectares: importância na validação](../../experimentos_regressao_col9/execucao_20261112_v4/apresentacao/figuras_publicacao/importancias_validacao_C_ha.png)

Os mapas mostram médias aritméticas municipais dos quatro intervalos de teste;
não são taxas agregadas pela razão de somas de áreas. São resumos do desempenho
municipal do regressor. Azul no mapa de erro indica subestimação. As escalas de
observado e previsto são iguais dentro de cada prancha municipal. No LOSO, os
modelos por UF podem ser distintos e foram escolhidos na validação externa à UF.

O eixo de tempo é o ano t; o desfecho ocorre entre t e t+1. A cor do diagrama de
dispersão identifica t. Os atributos de importância têm seus nomes técnicos
preservados para permitir cruzamento com o dicionário da preparação. As barras
mostram o desvio padrão de cinco permutações de trajetórias dentro da UF, sem
representar intervalo de confiança ou efeito causal.

## Tabelas e registros

- `METRICAS_VALIDACAO_CONGELADAS.parquet`: comparação anterior ao teste.
- `AJUSTES_CV_DESENVOLVIMENTO.parquet`: todas as configurações e folds internos.
- `VENCEDORES_PELA_VALIDACAO.json`: escolhas congeladas de algoritmo/bloco.
- `teste/RESULTADOS_IMUTAVEIS_TESTE.parquet`: previsões, respostas, resíduos e chaves.
- `teste/METRICAS_TESTE_FINAL.parquet`: todos os modelos, coortes e regimes.
- `teste/METRICAS_TESTE_POR_ANO.parquet` e `POR_ESTADO`: grupos temporais e regionais.
- `teste/METRICAS_POR_MAGNITUDE.parquet`: faixas definidas pelos quartis do treino.
- `apresentacao/TODOS_RESULTADOS_TESTE.csv`: versão tabular de consulta.
- `apresentacao/VALIDACAO_ESPACIAL_TODOS_ESTADOS.csv`: todos os folds LOSO.
- `apresentacao/EXTREMOS_ERRO_*.csv`: trinta maiores erros de cada resposta.
- `auditoria_ajustes/VERIFICACAO_MODELOS_FINAIS.parquet`: verificação dos 504 modelos.
- `auditoria_final/COBERTURA_ATRIBUTOS_POR_AJUSTE_FINAL.parquet`: ausências e UFs de treino.
- `auditoria_final/AUDITORIA_FINAL_APROVADA.json`: integridade e preservação.
- `MANIFESTO_FINAL_MODELOS_COL9.json`: hashes dos arquivos entregues.
- `RECIBO_ENTREGA_MODELOS_COL9.json`: hash externo do ZIP e do manifesto.

Todos esses caminhos são relativos a `experimentos_regressao_col9/execucao_20261112_v4`.
As 191.760 linhas de predições repetem o suporte entre experimentos: não são
191.760 unidades independentes. Cada experimento temporal principal avalia
1.020 município–anos. As 255 linhas de t=2023 permanecem sem desfecho no
checkpoint de preparação e não foram utilizadas para obter respostas de 2024.
