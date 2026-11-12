# Diagnóstico da Fase 0 Defesa Mestrado

Inspeção em 11 de novembro de 2026, no checkout `D:\mestrado\dashboard`.
Foram lidos integralmente o plano Markdown solicitado e o conteúdo textual do
anexo `D:\mestrado\TRANSFERENCIA_CODEX_DEFESA_MESTRADO.docx`, incluindo tabelas.
Não havia partes OOXML de notas/comentários adicionais. As orientações do Word
correspondem ao plano; não substituem a solicitação atual nem autorizam exclusões.

## Resultado e limites

A base Col9 existente atende às contagens documentadas. O legado está saudável,
mas a migração científica e operacional ainda não está concluída. PRODES e focos
possuem registros para somente **251 dos 255** municípios; as quatro entradas não
podem ser tratadas como zero. Nenhuma migração, carga, atualização de geometria,
exclusão, substituição de tabela, refresh de materializada ou reprocessamento de
fonte foi executado nesta inspeção.

Evidências reproduzíveis:

- [Inventário de arquivos e tamanhos](evidencias/fase0_arquivos_20261111.csv), sem segredos, ambiente virtual ou arquivos internos do Git.
- [Auditoria SQL](../db/auditoria/fase0.sql), em transação `REPEATABLE READ READ ONLY`, encerrada por `ROLLBACK`.
- [Resultado integral da auditoria](evidencias/fase0_banco_20261111.txt): catálogo, colunas, constraints, índices, dependências, permissões, contagens e EXPLAIN sem ANALYZE.
- [Regressão legada](evidencias/fase0_testes_legado_20261111.txt) e [testes Col9](evidencias/fase1_testes_20261111.txt); o resultado consolidado consta no diário de decisões.

## Controle de versão e checkpoint

Branch inicial: `fase-4-integracao`; HEAD `bdc3348` (modelo de referência).
590 arquivos rastreados. Não havia alteração em arquivo rastreado. Já estavam
sem rastreamento `.vscode/`, o plano em `docs/`, dois documentos em `historico/`
e `pages/01_Colecao_9_255.py`. Esses conteúdos foram preservados; a página foi
copiada antes de editada. Não foi criado commit englobando trabalho do usuário.
Nenhum AGENTS.md foi encontrado no repositório ou nos diretórios ancestrais verificados.

Checkpoint de fontes anterior às edições: 41 entradas no arquivo
`C:\Users\jefsl\AppData\Local\Temp\defesa_mestrado_20261111_f0\fontes_antes.zip`,
com manifesto SHA-256 ao lado. Hash do ZIP:
`6EDB062F9B669E2D1E956AB0A2EC2ED15CAC773A506B788F0F9A3B53C573494B`.
Esse checkpoint é de código, não é backup do PostgreSQL e fica em pasta temporária.
Antes de uma futura migração, criar também backup durável do banco e verificar sua restauração.

Hashes das fontes legadas locais e da imagem em execução, iguais:

| Arquivo | SHA-256 |
|---|---|
| app.py | a71cf9d8ccf45aa52c08cc734093208952b736d49fdbea9842d0d3cdfc1fbc87 |
| dados.py | e7fe3009b1a4b5978499bfe891272c3455e11b0e215f91070f2a9a06d9ba8fba |

## Arquivos e arquitetura

| Área | Conteúdo e função |
|---|---|
| app.py | Streamlit legado, dez abas, gráficos, mapas regionais/municipais, relatório PDF e exportações |
| dados.py | CSV sem PGHOST; PostgreSQL quando PGHOST existe; cache 1h; consultas legadas |
| pages/01_Colecao_9_255.py | Página automática do Streamlit; não há arquivo de rotas separado |
| processamento/ | config, banco, carregar_banco, municipios, mapbiomas_col10, queimadas, prodes, painel, mapas |
| modelagem/ | modelo_base.py e resultados de referência, dependentes do painel legado |
| db/ | init de papéis; sete migrações 001–007; nenhuma migração Col9 no estado inicial |
| testes/ | inicialmente apenas test_paridade.py: paridade CSV/banco, consistência e AppTest legado |
| historico/ e coordenadas/ | seis CSVs históricos e um cadastro CSV; dois Word preexistentes |
| mapas_municipios/ | 536 PNGs, correspondentes ao acervo legado; não usar como mapas Col9 |
| municipios_shapefile/ | três PNGs e três PGWs, anos 1985, 2023 e 2024; presença de 2023 não comprova proveniência Col9 |
| docs/ | plano de transferência e dicionário do painel legado, 4.824 linhas/268 municípios |

Fora do Git, foram conferidas a existência do CSV Col9 consolidado, do GeoPackage
definitivo e de 78 CSVs em `processamento_col9_255_complementado`. Em
`Mapas-Estudo` há 52 TIFFs e outros arquivos: não selecionar rasters apenas por
extensão ou inferir que cada TIFF é um ano completo. Scripts de importação/correção
estão em `D:\mestrado`, fora do checkout. Não foram executados.

## Dependências e Docker

| Lista | Versões declaradas |
|---|---|
| requirements.txt | streamlit 1.66.1; pandas 3.1.0; plotly 7.1.0; kaleido 1.5.0; Pillow 13.0.0; reportlab 5.1.0; SQLAlchemy 2.1.6; psycopg[binary] 3.3.6 |
| requirements-dev.txt | requisitos do app + pytest 9.1.1 |
| processamento/requirements.txt | numpy 2.5.4; pandas 3.1.0; geopandas 1.2.0; pyogrio 0.13.0; shapely 2.2.0; pyproj 3.8.0; rasterio 1.5.2; python-calamine 0.9.0; Pillow 13.0.0; psycopg[binary] 3.3.6; scikit-learn 1.9.1 |

O Python local é 3.14.6, enquanto os Dockerfiles usam 3.12-slim-bookworm. O venv
local tem Streamlit/pandas/Plotly e NumPy nas versões declaradas, mas inicialmente
não tinha SQLAlchemy, psycopg ou pytest. Dependências de teste foram instaladas em
pasta temporária isolada, sem modificar o venv. A imagem em execução confirmou
Streamlit 1.66.1, pandas 3.1.0, NumPy 2.5.4, Plotly 7.1.0, SQLAlchemy 2.1.6 e psycopg 3.3.6.
NumPy e o suporte Parquet são usados pelo app sem pin direto no requirements do
app; auditar a reprodução em imagem limpa na F5, sem atualizar versões por suposição.

| Serviço | Configuração | Estado observado |
|---|---|---|
| db | postgis/postgis:17-3.5; volume dados_postgres; db/init somente leitura; 127.0.0.1:5432 | healthy |
| app | build Dockerfile raiz; usuário Linux painel UID 10001; Chromium para PDF; 127.0.0.1:8501 | healthy |
| etl | perfil etl, Dockerfile processamento; código montado com escrita, fontes /dados:ro; credencial administrativa | não iniciado |

`COPY . .` inclui `pages/` e os novos módulos/referências. Não existe bind mount
do código no app: editar o checkout não altera automaticamente a imagem em execução.
O ignore do Docker exclui fontes de processamento, banco, modelagem, testes e PNG/PGW
regionais de 2023. O ETL tem ignore próprio, copiando só requirements no build.
Segredos são variáveis de ambiente; seus valores não foram registrados.

HTTP observado: `/`, `/Colecao_9_255` e `/_stcore/health` retornaram 200.
O HTML de uma rota Streamlit não comprova a execução da página: a validação
funcional é feita por AppTest. Nenhum serviço precisou ser iniciado/reiniciado para a F0.

## Inventário do banco

24 relações dos esquemas do projeto, além de public.migracao e objetos da extensão
PostGIS em public. Estimativas de pg_class não são contagens exatas; as contagens
abaixo vêm das consultas de agregação executadas.

| Esquema | Tabelas | Views | Views materializadas |
|---|---|---|---|
| ref | carga, uf, municipio, bioma, municipio_col9_255 | vw_municipio, vw_municipio_contorno, vw_municipios_col9_255 | mv_area_estudo_contorno, mv_municipio_vizinho |
| mapbiomas | classe, cobertura, cobertura_col9_255 | vw_cobertura_municipio, vw_cobertura_col9_255 | — |
| queimadas | foco, foco_atributo | vw_focos_municipio_mes | mv_focos_municipio_mes |
| prodes | classe, area_classe | vw_area_classe_municipio | — |
| analise | — | vw_painel_municipio_ano | mv_painel_base |

| Fonte | Linhas | Municípios | Anos |
|---|---:|---:|---|
| cobertura Col9 | 113.364 | 255 | 1985–2023, todos os 39 anos |
| cobertura legada | 126.212 | 268 | 1985–2024 |
| focos mensais legados | 41.367 | 268 | 2003–2025 |
| PRODES por classe/bioma | 9.583 | 268 | classes com ano 2000–2025; não equivale a 26 anos anuais comparáveis |
| painel integrado legado | 4.824 | 268 | 2008–2025 |

Distribuição Col9: MA 95, MT 68, PA 15, RO 5, TO 72. Cadastro legado: 268,
todos area_estudo=true. Diferença territorial confirmada: 17 saídas e quatro entradas,
sem qualquer remoção física. Os códigos 2101772, 2108504, 2112274 e 5101837 não
possuem registros nas tabelas complementares. A presença dos outros 251 não prova
completude temporal nem equivalência dos limites municipais antigos aos de 2025.

A cobertura Col9 tem PK (cd_mun, ano, classe_cobertura), NUMERIC(18,4) para
área e NUMERIC(10,4) para percentual, checks de anos/domínios e nenhuma FK para
o legado. O cadastro Col9 possui área_geom_km2 NUMERIC(16,5), PK e índice GiST.
Todas as 255 geometrias são MULTIPOLYGON válidas em EPSG:4674, mas a validade não
está imposta por CHECK no novo cadastro. A view de cobertura faz JOIN no cadastro
Col9 e usa dele nome/UF; o cadastro geográfico não disponibiliza GeoJSON simplificado.

As sete migrações antigas estão registradas em public.migracao. A criação da Col9
ocorreu por scripts externos ao checkout. Não há carga Col9 associada por FK a
ref.carga; origem e hashes de arquivos deverão ser incorporados sem recarga.

dashboard_app é membro de dashboard_leitura, sem superuser/createdb/createrole,
com default_transaction_read_only=on e timeout 30s. Os dois papéis têm USAGE e
SELECT em todas as relações dos esquemas do projeto, inclusive Col9, e nenhuma
permissão INSERT/UPDATE/DELETE/TRUNCATE nelas. Não foi necessário GRANT.

O EXPLAIN Col9 usa a PK municipal e a PK composta da cobertura. O painel legado
usa sua materializada, janelas temporais e vizinhança: trocar apenas o nome de uma
view não migra esse painel. O catálogo registra 36 pares diretos de dependências.

## Páginas e dependências entre abas

As abas de cobertura e análises do legado dependem de `dados.carregar_cobertura`
e da legenda 10.1. A contagem é de sete abas
MapBiomas mais três integradas: Evolução Temporal, Distribuição Anual, Participação
Percentual, Análise por Década, Comparação Entre Anos, Análises Especiais,
Análises por Estados, Queimadas, Desmatamento (PRODES) e Análise Integrada.
Mapas municipais e PDF também dependem da série legada e das imagens 1985/2024.

Queimadas usa focos mensais/pontos, cadastro e contornos legados; PRODES compara
com a cobertura legada. A Análise Integrada depende de todas as fontes,
materializadas e vizinhança dos 268. O modelo lê o CSV deste painel. A página
Col9 permanece independente e não habilita indicadores integrados para os 255.

## Divergências e riscos confirmados

1. **Reprodução incompleta da Col9:** quatro objetos existem no banco, mas não nas
   migrações do Git; scripts, consolidação e correções estão fora do repositório.
2. **Legenda inicial compartilhada:** 22 códigos observados tinham correspondência,
   mas a classe 6 estava com cor #026975, contra #007785 na
   [referência oficial Col9](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2024/10/Legenda-Colecao-9-LEGEND-CODE_v2.pdf).
   O primeiro incremento passa a usar legenda própria; tipo natural/antrópico não
   está no PDF de códigos e não foi inferido da 10.1.
3. **Validação inicial insuficiente:** a página só verificava totais/extremos,
   não chave, completude município–ano ou identidade dos 255 códigos.
4. **ETL padrão destrutivo:** mapbiomas_col10 e prodes apagam fatos antes de inserir;
   queimadas apaga focos/atributos; municipios atualiza geometrias/flags; mapas.py
   remove PNGs municipais; painel.py sobrescreve CSV/dicionário. Cada carga tem sua
   transação, mas o conjunto do ETL não é uma única transação global.
5. **Identidade por nome na origem legada:** gerar_cobertura faz casamento por nome
   normalizado + UF. Isso não satisfaz a regra de identidade IBGE para a nova série;
   não será reutilizado na Col9.
6. **Harmonização incompleta:** os quatro novos não estão em PRODES/queimadas.
   Filtros JOIN nos 255 sozinhos retornariam 251. COALESCE a zero no painel antigo
   não pode ser transferido ao novo painel sem evidência de observação.
7. **Rasters e geodesia:** PNG 2023 não comprova coleção. Correções estatísticas
   não significam TIFFs anuais corrigidos. O script complementar externo usa Geod
   WGS84, enquanto PRODES usa GRS80; registrar/sensibilizar a diferença e a área
   geográfica de referência antes de harmonizar denominadores, sem recalcular fontes.
8. **Modelagem:** existe HistGradientBoostingRegressor para alvo contínuo e validação
   temporal, não RF/XGBoost/SVM classificadores validados para Col9. MAE/ranking
   do legado não demonstram validação espacial; AUC/F1 requerem outro alvo definido.
9. **Segurança de erro:** a página exibia exceções SQL completas; foi alterada para
   mensagem de conexão sem detalhes internos.

## Sequência de alterações verificáveis

| Checkpoint | Arquivos e ação | Verificação e condição para avançar |
|---|---|---|
| F0 | docs/DIAGNOSTICO_FASE0.md, docs/evidencias/, db/auditoria/fase0.sql | saúde do legado, catálogo/permissões e regressão registrados |
| F1 inicial | contratos_series.py, dados_col9.py, referencias/legenda_col9.*, página isolada, testes | identidade IBGE, 113364/255/39, chave, completude, domínios, precisão, leitura e AppTest |
| F1 conclusão | metadados Col9 versionados e rastreabilidade por hashes; classificação de tipos | conferir todas as classes, denominadores, fonte documental e definição operacional dos índices |
| F2 | página Col9 e módulo de visualização próprio | percentuais/denominadores, décadas, comparação 1985–2023, contornos simplificados; mapas com proveniência Col9 e patch complementar |
| F3 | auditoria por município–ano; novas views *_255 e ETL específico independente | recuperar/reprocessar complementares com limites 2025; distinguir falta, zero observado e nenhuma ocorrência |
| F4 | painel/contiguidade *_255, transições e modelagem independente | máscara válida comum; sensibilidade 2001–2003; partições espaciais/temporais e métricas do alvo definido |
| F5 | migrações verificadas por estado, documentação e build app | backup durável restaurável, checkout limpo, validação em Python 3.12, implantação e retorno ao legado |

As fases posteriores não são aceitas apenas porque há código parcial. A conclusão
da F1 científica e a integração dependem das verificações acima. Não há autorização
implícita para usar o ETL legado ou substituir as tabelas existentes.
