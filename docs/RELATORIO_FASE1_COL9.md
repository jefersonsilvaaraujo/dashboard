# Relatório da Fase 1 Coleção 9

Data: 11 de novembro de 2026. **Fase 1 concluída para o contrato de dados e os
indicadores descritivos aprovados D1–D4.** Transições e variável-alvo de modelagem
não estão homologadas e não fazem parte deste aceite descritivo.

## Implementação e arquivos

| Arquivo | Alteração |
|---|---|
| referencias/metodologia_col9.json | Aprovação do pesquisador, versão defesa_col9_d1d4_v1, conjuntos D1/D3, denominadores, agregação e limitações |
| analise_col9.py | Categorias operacionais, áreas/percentuais, sensibilidades 29+32 e 25, médias anuais por década e variação líquida de estoques |
| dados_col9.py | Metadados aprovados; leitura da geometria original, áreas geodésicas independentes, GeoJSON simplificado só para desenho; validação de hashes territoriais |
| referencias/legenda_col9.json | Esclarece a independência entre fonte oficial e taxonomia operacional; CSV da legenda não foi alterado |
| referencias/territorio_col9_hashes.json | Contrato de 255 hashes SHA-256 das geometrias originais, conferidos com o GeoPackage |
| processamento/auditar_col9.py | Relatórios novos por município–ano e indicadores regionais, sem execução do ETL legado |
| processamento/verificar_territorio_col9.py | Verifica igualdade exata das geometrias banco/GeoPackage e preserva contratos já existentes |
| testes/test_analise_col9.py | Razão entre somas, denominador, sensibilidade, dados ausentes, décadas, comparação e proveniência |
| testes/test_fase2_integracao.py | Auditoria real dos 9.945 pares e consistência dos indicadores agregados |
| docs/PROPOSTA_METODOLOGICA_FASE1_COL9.md | Registra aprovação D1–D4 sem confundir o histórico da proposta com seu aceite |

A classificação oficial permanece no CSV de legenda. A categoria operacional
e a versão da metodologia são campos novos nos dados derivados. Nenhuma tabela
ou coluna do banco foi criada, substituída, atualizada ou excluída.

## Regras executadas

VN principal: 3,4,5,6,49,11,12,50. O cenário ampliado acrescenta 29/32 ao numerador.
Usos antrópicos: 9,15,20,21,24,30,31,35,39,40,41,46,47,48,62. O cenário alternativo
acrescenta 25. Área classificada inclui 25/33 e exclui não observado. As razões
regionais são calculadas pelas somas das áreas, não por médias de percentuais.
O filtro de classes não recalcula o denominador nem muda esses conjuntos.

Não se preenchem municípios/anos ausentes com zero. Ausência de uma classe só
vira zero em grupo observado e validado. Área classificada zero produz percentual
NA. A comparação de estoques é chamada variação líquida de área e não gera alvo.

## Auditoria independente

[CSV completo com 9.945 pares](evidencias/auditoria_col9_d1d4_20261111/auditoria_municipio_ano.csv)
e [resumo](evidencias/auditoria_col9_d1d4_20261111/resumo.json).
Áreas territoriais são calculadas sobre os polígonos originais:

- Cadastro: `area_geom_km2 * 100`.
- WGS84: `ST_Area(ST_Transform(geom,4326)::geography,true) / 10000`.
- GRS80/SIRGAS: `ST_Area(geom::geography,true) / 10000`, SRID 4674.

O método esferoidal segue a [documentação ST_Area do PostGIS](https://postgis.net/docs/ST_Area.html).
O GeoJSON simplificado não entra nesses cálculos. As 255 geometrias foram
conferidas por SHA-256 de WKB NDR com o GeoPackage de hash previamente conhecido:
**255/255 idênticas**. Essa verificação garante a mesma delimitação nos dados,
mapas municipais e pré-visualizações raster.

| Razão ou diferença | Mínimo | Mediana | Máximo |
|---|---:|---:|---:|
| Classificada / cadastrada (%) | 98,122960 | 99,475716 | 99,997807 |
| Classificada / geodésica WGS84 (%) | 99,576201 | 99,999859 | 100,040687 |
| Desvio cadastro frente à geodésica (%) | 0,002069 | 0,520606 | 1,881265 |

O resíduo frente à área cadastrada não pode ser rotulado automaticamente como
NoData. A referência de área explica uma diferença numérica importante, mas a
origem do cálculo de AREA_GEOM_KM2 continua a investigar. Pequenos resíduos
raster/polígono também não são classificados causalmente só por essa razão.
O percentual de origem foi preservado, e não substituído por outro silenciosamente.

Resultados descritivos regionais reproduzidos em
[indicadores anuais](evidencias/auditoria_col9_d1d4_20261111/indicadores_anuais_255.csv):

| Ano | VN principal (%) | VN com 29/32 (%) | Usos antrópicos (%) | Usos com 25 (%) |
|---|---:|---:|---:|---:|
| 1985 | 85,394299 | 85,726757 | 12,803237 | 13,120618 |
| 2023 | 55,434798 | 55,765319 | 42,807753 | 43,230608 |

Denominador: área classificada dos 255. Estes são estoques/composição mapeada,
sem interpretação automática de conversão bruta, desmatamento ou legalidade.

## Testes e aceite

Os 36 testes anteriores foram preservados e passaram. A suíte principal, com
novos testes de análise e integração, passou com 49 testes e um módulo geoespacial
dispensado no ambiente leve. O teste adicional de integridade dos mapas passou
separadamente. Dois testes geoespaciais passaram no ambiente apropriado.
Total deste checkpoint F1/F2: **52 testes distintos aprovados**. Há ainda smoke
test em Python 3.12 documentado no relatório da Fase 2.

Evidências: [suíte](evidencias/fases1_2_testes_20261111.txt),
[teste adicional](evidencias/fase2_testes_proveniencia_mapas_20261111.txt),
[execução da auditoria](evidencias/fase1_auditoria_d1d4_execucao_20261111.txt).

## Pendências e preservação

O cálculo histórico de AREA_GEOM_KM2 permanece uma investigação de proveniência;
isso não redefine o denominador principal aprovado. A máscara de Buriticupu 2002
continua exigindo auditoria espacial antes de modelagem.

A [proposta de variável-alvo](PROPOSTA_VARIAVEL_ALVO_CONVERSAO_COL9.md) separa
conversão pixel a pixel de variação líquida, define uma taxa candidata e explicita
o processo de validação do limiar. Nenhum limiar foi escolhido ou alvo gerado.

Banco, fontes, dashboard legado e contêiner app em execução preservados.
Não houve migração, carga, refresh de materializada ou implantação.
