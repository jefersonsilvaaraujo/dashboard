# Entrega dos experimentos de regressão —Coleção 9

1. [Protocolo congelado](PROTOCOLO_EXPERIMENTAL_CONGELADO_COL9.md)
2. [Auditoria pré-treino](RELATORIO_AUDITORIA_PRE_TREINO_COL9.md)
3. [Decisões aprovadas](DIARIO_DECISOES_CIENTIFICAS_COL9.md)
4. [Baselines](RESULTADOS_BASELINES_COL9.md)
5. [Regressão da taxa](RESULTADOS_REGRESSAO_CONTINUA_COL9.md)
6. [Validação temporal](RESULTADOS_VALIDACAO_TEMPORAL_COL9.md)
7. [Validação espacial](RESULTADOS_VALIDACAO_ESPACIAL_COL9.md)
8. [Ablações e históricos congelados](RESULTADOS_ABLACAO_COL9.md)
9. [Área em hectares](RESULTADOS_REGRESSAO_AREA_HA_COL9.md)
10. [Interpretação e extremos](RELATORIO_INTERPRETACAO_MODELOS_COL9.md)
11. [Texto para dissertação](TEXTO_RESULTADOS_DISSERTACAO_COL9.md)
12. [Resumo executivo](RESUMO_EXECUTIVO_MODELOS_COL9.md)

O diretório ativo éexperimentos_regressao_col 9/execucao_20261112_v4.
Dados/previsões/erros estão em Parquet/CSV; gráficos em PNG/SVG e modelos
em skops/JSON nativo, sem pickle/joblib. O checkpoint inclui protocolo,
fontes, versões, grades, resultados, configurações e hashes. Reutilizar as
predições imutáveis para apresentação; a passagem do teste não será repetida.
Os 39 rasters e acervos anteriores são referenciados sem duplicação.

T4 usa apenas a coorte 2003–2022 com comparações pareadasT0–T4. A sensibilidade
congelada fixa os históricos, não a composição contemporânea de cobertura.
Resultados são magnitudes mapeadas, não probabilidades binárias ou áreas reais
corrigidas. 2024 permanece reservado e oDOCX não foi atualizado.

O arquivoMANIFESTO_FINAL_MODELOS_COL9.json e o recibo do pacote registram a
integridade e as verificações de preservação. Um carregamento seguro requer
as versões fixadas e os dois tipos estruturais explicitamente revisados:
numpy.dtype e sklearn.tree._tree.Tree. Não autorizar tipos arbitrários.

13. [Reprodução, testes e pendências](REPRODUCAO_TESTES_PENDENCIAS_COL9.md)

14. [Guia de figuras, tabelas e auditorias](GUIA_FIGURAS_E_ARQUIVOS_COL9.md)
