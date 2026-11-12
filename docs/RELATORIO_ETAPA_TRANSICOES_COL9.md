# Entrega — construção e auditoria das transições Coleção 9

11/11/2026. Etapa computacional concluída; resultados aguardam validação
científica. Esta entrega não conclui as demais integrações/modelagem das Fases 3–5.

## Implementação e arquivos

| Arquivo | Resultado |
|---|---|
| `processamento/manifesto_transicoes_col9.py` | Proveniência, hashes integrais, grades, 2002 e complemento |
| `referencias/manifesto_rasters_transicoes_col9.json` | Manifesto efetivo dos 39 anos e fontes territoriais |
| `processamento/transicoes_col9.py` | Matrizes completas, áreas geodésicas, suporte comum, métricas contínuas e checkpoints |
| `processamento/relatorio_transicoes_col9.py` | Auditoria independente e exploração sem alvo |
| `processamento/exportar_matriz_col9.py` | Matrizes densas CSV por município/par/suporte |
| `processamento/figuras_transicoes_col9.py` | Seis figuras científicas estáticas com hashes |
| `processamento/empacotar_transicoes_col9.py` | ZIP de entrega com manifesto e verificação de conteúdo |
| `testes/test_transicoes_col9_geo.py` | Dez testes dos cálculos geoespaciais |
| `testes/test_exportar_matriz_col9.py` | Teste da direção, eixos, zeros e exportação |
| `.gitignore`, `.dockerignore` | Resultados/checkpoints volumosos fora de Git/imagem |
| `README.md`, `docs/DECISOES_DEFESA_MESTRADO.md` | Estado atual e decisões registradas |

Documentação: [relatório científico](RELATORIO_EXPLORATORIO_TRANSICOES_COL9.md)
com distribuições, rankings, séries, sensibilidades, candidatos e interpretação;
[protocolo reprodutível](PROTOCOLO_TRANSICOES_COL9.md) com fontes, fórmulas,
ambiente, comandos, preservação, testes e limites.

## Resultados e verificação

- 255 municípios, 38 pares consecutivos, 9.690 matrizes 29×29 em pixels e hectares.
- 9.945 estoques município–ano comparados ao consolidado por classe:
  erro máximo zero pixels e 0,00005067 ha, dentro da tolerância documentada.
- Conservação das matrizes, marginais, partições de pixels, C/D/R, suporte
  triplo e hashes verificados no conjunto integral.
- Regra de complemento preservada; nenhuma divergência de pixels já
  classificados foi aceita. Todos os suportes têm denominador nativo positivo.
- Buriticupu: matrizes densas dos dois pares e dos dois suportes exportadas;
  máscara tripla não altera C/D/R dos pares. Elevação em 2002→2003 permanece
  achado para validação temática, sem atribuição automática a NoData.
- Regressão: 51 testes principais passaram; dois módulos foram ignorados
  nesse ambiente e executados no geoespacial, onde 12 testes passaram.
  Total de 63 testes distintos. Testes anteriores preservados.
- Seis PNGs científicos foram gerados em contêiner temporário sem rede/banco
  e inspecionados visualmente. O relatório distingue essa inspeção da
  conferência visual completa do dashboard, ainda pendente.

Saída integral:
`resultados_transicoes_col9/integral_255_1985_2023_20261111/`.
Inclui `matrizes_completas_255.npz`, métricas contínuas, estoques auditados,
checkpoints por município, `auditoria_buriticupu_csv/` e `analise_exploratoria/`.
Somente tentativas concluídas participam do consolidado e da entrega ZIP.
Logs de execução, retomada e testes estão em `docs/evidencias/transicoes_*`.

## Implantação separada e preservação

Após confirmação expressa, somente o app foi substituído pela candidata
previamente testada. Banco e volume conservaram suas identidades; nenhum ETL,
migração ou escrita no banco foi executado. A imagem anterior permanece
disponível para retorno. Procedimento em `deploy/implantacao_col9.ps1`;
testes funcionais em `testes/verificar_fase2_container.py`; detalhes e arquivos
da atividade no [relatório de implantação](RELATORIO_IMPLANTACAO_COL9_20261111.md).

Os hashes de `app.py` e `dados.py` continuam iguais aos do checkpoint inicial.
Fontes rasters, dados originais, views, tabelas e resultados anteriores foram
preservados. A nova rotina científica não acessa PostgreSQL.

## Pendências para validação

1. Validar tematicamente as transições, extremos, classes sensíveis e casos
   próximos aos candidatos com referência independente e amostragem apropriada.
2. Decidir tau, A_min, combinação dos critérios e elegibilidade mínima;
   as contagens exploratórias não escolhem esses parâmetros.
3. Conferir visualmente a página implantada; a ferramenta de navegação
   interrompeu a tentativa por não conseguir confirmar a URL com segurança.
4. Somente após validação científica, definir a variável-alvo e o protocolo
   sem vazamento temporal/espacial. Nenhum alvo binário ou modelo foi produzido.
