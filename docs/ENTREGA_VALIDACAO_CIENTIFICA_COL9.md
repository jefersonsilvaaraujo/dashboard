# Checkpoint A/B/C — validação científica e preparação da resposta

11/11/2026. Estado desta entrega:

| Etapa | Executado | Limite/pendência |
|---|---|---|
| A | Desenho e sorteio probabilístico, controles dirigidos, inventário local, aquisição e inspeção de referências públicas, notas por ponto e fichas cegas | Respostas independentes dos 3.744 pontos probabilísticos ainda pendentes; sem estimativa representativa de acurácia ou homologação temática |
| B | 54 combinações de cenários/qualidade/classificação, tabelas por ano/UF/município, casos próximos, exclusões e discordâncias | Sem escolha de tau/A_min; recomendação substantiva final depende da validação temática |
| C | Especificação de dados/relógios/lacunas, índice 255×39 sem Y, partições temporais/LOSO propostas e barreira de disponibilidade | Sem matriz X as-of completa ou treino; vintages históricos e famílias complementares ainda não harmonizados |

Relatórios principais:

- [Validação temática preliminar](RELATORIO_VALIDACAO_TEMATICA_COL9.md).
- [Comparação dos limiares](RELATORIO_COMPARACAO_LIMIARES_COL9.md).
- [Especificação da matriz](ESPECIFICACAO_MATRIZ_TREINAMENTO_COL9.md).

## Arquivos de implementação e documentação

Novos em `processamento/`:

- `cenarios_validacao_col9.py`: cenários A/B/C e elegibilidade específica de cada variante.
- `amostra_tematica_col9.py`: amostragem em dois estágios com probabilidades/pesos.
- `inventariar_referencias_locais_col9.py`: metadados e índices ZIP sem extração.
- `referencias_tematica_col9.py`: STAC, recortes e QA de Sentinel/Landsat; assinatura pública em memória.
- `referencias_fim_ano_col9.py`: complemento novembro/dezembro sem substituir o lote inicial.
- `pranchas_pixel_validacao_col9.py`: footprint nominal Col9 e zoom na imagem de referência.
- `diagnostico_picos_col9.py`: decomposição por classes/UF e controles municipais.
- `respostas_tematica_col9.py`: guarda contra acurácia indevida com não resposta/inspeção dirigida.
- `relatorios_validacao_cientifica_col9.py`: tabelas dos relatórios e notas preliminares explícitas.
- `fechar_checkpoint_validacao_col9.py`: verificação de preservação, manifesto e ZIP novos.

Novos também: `modelagem/contrato_matriz_col9.py`,
`testes/test_validacao_cientifica_col9.py`,
`testes/test_amostragem_tematica_col9_geo.py` e
`referencias/fontes_validacao_cientifica_col9.json`.
Documentação desta entrega, README e diário de decisões atualizados.
`.gitignore`/`.dockerignore` excluem os resultados científicos volumosos do
versionamento/imagem. Nenhum código do app ou ETL legado foi modificado.

## Artefatos ativos e tentativas preservadas

Base nova: `validacao_cientifica_col9/checkpoint_20261111/`.

| Caminho | Conteúdo |
|---|---|
| `limiares/` | medidas contínuas, 54 cenários, agregações, casos próximos e discordâncias |
| `amostragem/` | universo de 9.690 pares, 120 estratos, 234 PSUs probabilísticas, 33 dirigidas, 4.272 pontos e fichas cegas |
| `inventario_mapas_estudo_v2.json` | 161 arquivos, 59 AppleDouble, 21 ZIPs reais, zero falhas reais de cabeçalho/índice |
| `referencias_v2/` | lote público inicial utilizável: 74 recortes |
| `referencias_fim_ano/` | 30 recortes de novembro/dezembro |
| `referencias_historicas_v3/` | 15 recortes históricos recuperados, sobre quatro pontos já selecionados |
| `pranchas_pixel/indice.html` | 42 pranchas com footprint nominal e zoom; não revela classes do mapa |
| `picos/` | classes/UF/ano e séries completas dos cinco municípios prioritários |
| `inspecao_dirigida_notas.csv` | 24 notas preliminares por ID, assistidas por IA, sem rótulo de referência homologado |
| `diagnostico_respostas.json` | 3.744 respostas probabilísticas pendentes; acurácia não calculada |
| `matriz_especificacao_v2/` | 9.945 chaves sem Y, 255 linhas de 2023 sem resposta e partições propostas |
| `preservacao.json`, `ambiente_*.json` | integridade do acervo e versões efetivas |

Os lotes de referência contêm cenas/pontos repetidos; 74+30+15 não é um tamanho
amostral inferencial. O índice inicial não visualiza alguns anos sem recorte;
o lote histórico posterior resolve parte dessas falhas de acesso. A primeira
consulta com ordenação incompatível e tentativas com HTTP 429, o primeiro
inventário que tentou abrir AppleDouble como dados e a primeira especificação
foram preservados. As versões ativas acima são indicadas explicitamente.

## Testes e verificações

- 61 testes principais passaram; três módulos geoespaciais foram ignorados
  nesse ambiente e executados no ambiente apropriado.
- 16 testes geoespaciais passaram. Total: **77 testes distintos**, incluindo
  14 novos. Testes anteriores preservados.
- Cenários verificam AND, igualdade nos limites, denominadores, qualidade,
  D=0, proximidade e aninhamento. Amostragem verifica sementes/ordenação,
  probabilidades, censo, amostragem sem reposição e controles de omissão.
- Contrato verifica 255/39/38, 2023 sem resposta, exclusão de 268, atributos
  proibidos, datas futuras/desconhecidas, fusos, embargo e estado retido.
- As contagens por ano, UF e município foram comparadas às 54 linhas globais.
  Área/estoque principal recalculados conferem com os resultados aprovados.
- Todos os recortes foram adquiridos em arquivos novos; as sequências dirigidas
  e complementos foram inspecionados. As três pranchas críticas de 2023 foram
  reinspecionadas com footprint. Isso não valida respostas dos pontos probabilísticos.

Logs: `docs/evidencias/validacao_regressao_principal_20261111.txt`,
`validacao_regressao_geo_20261111.txt`, `validacao_cenarios_20261111.txt`,
`validacao_amostragem_20261111.txt` e demais logs de referência.

## Preservação e recomendação

Os hashes dos artefatos consolidados e dos checkpoints municipais foram
conferidos durante a execução dos cenários; os 39 rasters mantiveram tamanho
e mtime do manifesto, com abertura somente leitura. App.py e dados.py conservam
os hashes anteriores. Nenhuma migração, escrita de fatos, refresh de view,
recriação/reinício de serviço ou implantação foi feita nesta etapa. Os testes
existentes acessaram o banco apenas para leitura. CSVs e ZIPs anteriores intactos.

Recomenda-se concluir a resposta temática antes de escolher entre A/B/C.
As evidências dirigidas mostram mudanças tardias e casos ainda ambíguos;
não fundamentam uma taxa de acerto do universo. Os atrasos de publicação
impedem declarar o experimento retrospectivo como previsão operacional histórica.
O teste futuro será separado do ajuste, mas sua exploração científica prévia
foi documentada; não será chamado de totalmente cego. A próxima decisão é
científica, não balanceamento de classes. Nenhum modelo definitivo, Y ou
limiar ecológico foi homologado.
