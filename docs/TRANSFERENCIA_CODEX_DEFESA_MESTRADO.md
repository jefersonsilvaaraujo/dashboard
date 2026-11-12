# Plano de transferência para o Codex — Defesa Mestrado

**Projeto:** Dashboard de monitoramento territorial e ambiental da transição Cerrado–Amazônia  
**Pesquisador:** Jeferson Silva Araújo (Jef)  
**Estado do projeto:** 11 de novembro de 2026  
**Ambiente principal:** Windows 11, `D:\mestrado`, Docker Compose, PostgreSQL/PostGIS 17 e Streamlit  
**Objetivo deste documento:** permitir que um agente Codex, operando diretamente no repositório local, assuma a implementação com segurança, sem depender da memória desta conversa.

## 1. Decisão e objetivo principal

O Codex deverá assumir as alterações extensas no código, nas migrações SQL, no Docker e nos testes automatizados. O ChatGPT nesta conversa continuará útil para revisão científica, metodologia, interpretação dos resultados e avaliação das alterações propostas. **Não pressupor que uma nova sessão do Codex tenha acesso completo ao histórico desta conversa ou às decisões não registradas no repositório.** O contexto técnico autoritativo para a implementação é este documento, os arquivos reais do projeto, os dados existentes e as verificações executadas localmente.

**Meta:** fazer a aplicação operar de forma consistente com a seleção territorial definitiva de **255 municípios**, **cinco unidades federativas**, a **Coleção 9 do MapBiomas (1985–2023)** e as fontes complementares PRODES/queimadas, sem misturar silenciosamente universos territoriais ou coleções diferentes.

**Escopo inicial de menor risco:** manter o dashboard legado funcional e trabalhar incrementalmente em módulos/visões independentes para os 255 municípios; só alterar as abas integradas depois de conferir a cobertura territorial de cada fonte e realizar testes de regressão.

## 2. Fatos estabelecidos e verificações concluídas

| Fato | Valor verificado | Evidência ou origem |
| --- | --- | --- |
| Seleção inicial | 268 municípios | `ref.municipio`: 268 registros, todos `area_estudo=true` |
| Seleção definitiva | 255 municípios | GeoPackage do IBGE 2025 e CSVs consolidados |
| Diferença entre seleções | 17 retirados e quatro acrescentados | `FULL OUTER JOIN` PostgreSQL; 21 códigos |
| Período da Coleção 9 | 1985–2023, 39 anos | Auditoria dos 78 CSVs |
| Registros consolidados | 113.364 linhas | Auditoria do ZIP e `COPY 113364` no PostgreSQL |
| Municípios distintos na cobertura | 255 | Conferência SQL após `COMMIT` |
| Anos distintos na cobertura | 39 | Conferência SQL após `COMMIT` |
| Tabela de cobertura | `mapbiomas.cobertura_col9_255` | Criada, carregada e validada |
| Cadastro geográfico independente | `ref.municipio_col9_255` | 255 geometrias em EPSG:4674 |
| Visualização de cobertura | `mapbiomas.vw_cobertura_col9_255` | 113.364 linhas, 255 municípios, 39 anos |
| Visualização territorial | `ref.vw_municipios_col9_255` | Criada e validada |
| Classes sem código na legenda atual | zero | Consulta LEFT JOIN à `mapbiomas.classe` |
| Dashboard legado | preservado | `app.py` e visualizações anteriores não foram substituídos |
| Página provisória Col9 | acessível no localhost | Confirmado pelo pesquisador |

**Atenção:** a presença dos códigos das classes na legenda atual **não comprova equivalência semântica de descrições, cores ou agrupamentos** entre Coleção 9 e Coleção 10/10.1. Validar contra o dicionário oficial da Coleção 9 antes de publicar indicadores derivados.

## 3. Histórico resumido da correção MapBiomas

Os rasters anuais originais foram baixados em preto e branco (classes numéricas, visualização com paleta posterior). Uma auditoria comparou pixels locais contra amostras oficiais no Google Earth Engine das coleções 9, 10 e 10.1. O raster de 2002 foi reconstituído a partir da Coleção 9, na grade original, com 100% de concordância em 11.648 amostras. A equivalência amostral não equivale à inspeção de cada pixel.

A mudança da lista inicial de 268 municípios para a definitiva de 255 não consistiu somente de exclusões: houve **17 saídas e quatro entradas**. Os três municípios maranhenses incorporados estavam sem pixels classificados nos 38 rasters originais, exceto em 2002. Foi exportado do Earth Engine um TIFF complementar de 38 bandas da Coleção 9, para 1985–2023 exceto 2002. O processamento preencheu exclusivamente zeros na área dos três municípios e gerou auditoria por ano. Nos 38 anos, houve **29.268.722 pixels recuperados**, com **19 ocorrências de pixels ainda zerados** na soma das auditorias anuais; nenhuma divergência foi registrada em pixels previamente classificados dos três municípios.

A série completa de 78 arquivos (39 CSVs de cobertura e 39 CSVs de auditoria) foi consolidada em um CSV com 113.364 linhas. A correção foi aplicada às estatísticas sem reescrever os rasters originais. Os GeoTIFFs permanecem como fontes históricas independentes. **Não inferir que os rasters anuais foram todos fisicamente corrigidos.**

### 3.1 Os quatro municípios acrescentados

| Código IBGE | Município | UF |
| --- | --- | --- |
| 2101772 | Bela Vista do Maranhão | MA |
| 2108504 | Pindaré-Mirim | MA |
| 2112274 | Tufilândia | MA |
| 5101837 | Boa Esperança do Norte | MT |

### 3.2 Os 17 códigos retirados da seleção inicial

`1100031, 1501253, 2108454, 2110302, 2111300, 5102504, 5103437, 5103957, 5105234, 5105622, 5106109, 5106174, 5106505, 5106802, 5106828, 5107248, 5107909`.

Todos os quatro códigos acrescentados estão ausentes da tabela legada `ref.municipio` de 268 entradas. Nenhum dos 17 municípios deverá ser apagado automaticamente; há possíveis chaves estrangeiras e histórico PRODES/queimadas.

### 3.3 Ressalva documentada de 2002

Em Buriticupu/MA (código **2102325**, integrante dos 255 municípios), os rasters de 2001 e 2003 apresentam **2.852.945** pixels classificados, enquanto o raster reconstruído de 2002 apresenta **2.865.008**: uma diferença de **12.063 pixels**, aproximadamente 0,42% no município ou 0,00134% do total anual de pixels classificados no conjunto estudado. A causa provável é uma diferença na máscara de cobertura espacial, não uma mudança legítima de classe. Outras diferenças menores aparecem em Urbano Santos e Santo Amaro do Maranhão. Em processamento de **transição pixel a pixel**, tratar zeros como sem dado e comparar apenas pixels válidos nos dois anos. Registrar o episódio na seção metodológica e avaliar a sensibilidade de modelos locais. A diferença não exige interromper análises agregadas, mas não autoriza afirmar que toda transição espacial já está validada.

## 4. Estrutura e caminhos reais do projeto

**Raiz:** `D:\mestrado`.

| Local | Finalidade |
| --- | --- |
| `D:\mestrado\dashboard\app.py` | Aplicação Streamlit principal, legado Coleção 10.1 |
| `D:\mestrado\dashboard\dados.py` | Acesso a banco e CSVs; consultas para todas as abas |
| `D:\mestrado\dashboard\docker-compose.yml` | Serviços `db`, `app`, `etl`; credenciais por `.env` |
| `D:\mestrado\dashboard\pages\01_Colecao_9_255.py` | Nova página independente da Coleção 9; usuário confirmou acesso |
| `D:\mestrado\dashboard\processamento\` | ETL e configuração dos rasters, conforme checkout real |
| `D:\mestrado\dashboard\modelagem\` | Módulos de preparação e modelagem |
| `D:\mestrado\correcao_territorial_255\resultado_20261107_192346\municipios_255_ibge_2025.gpkg` | Referência espacial definitiva, 255 municípios, EPSG:4674 |
| `D:\mestrado\cobertura_col9_255_1985_2023_consolidada.csv` | 113.364 registros, delimitador `;`, UTF-8 com BOM |
| `D:\mestrado\Mapas-Estudo\` | Rasters originais de 1985–2023 |
| `D:\mestrado\Mapas-Estudo\mapbiomas_col9_recuperacao_3municipios_MA.tif` | TIFF complementar de 38 bandas, NÃO um raster anual completo |
| `D:\mestrado\processamento_col9_255_complementado\` | 39 CSVs corrigidos e 39 auditorias anuais |

O ZIP de código recebido continha `app.py`, `dados.py`, `docker-compose.yml`, `banco.py`, `carregar_banco.py`, `config.py`, `mapas.py`, `mapbiomas_col10.py`, `municipios.py`, `painel.py`, `prodes.py`, `queimadas.py` e `modelo_base.py`. Verificar os arquivos correntes no repositório: **o ZIP é um recorte da aplicação e pode estar desatualizado depois da instalação da nova página**. Não assumir que a cópia anexada substitui o checkout real.

## 5. Docker, PostgreSQL e permissões

Contêineres confirmados:

- `dashboard-mestrado-db-1`: imagem `postgis/postgis:17-3.5`, porta local `127.0.0.1:5432`.
- `dashboard-mestrado-app-1`: Streamlit, porta local `127.0.0.1:8501`.

Banco: `dashboard`; administrador: `dashboard_admin`; usuário de aplicação: configurar pelo `APP_DB_USER` do Docker Compose, normalmente `dashboard_app`. **Não registrar ou divulgar senhas**. As variáveis reais são `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `APP_DB_USER`, `APP_DB_PASSWORD` e `PGHOST` etc. Jamais incluir `.env` nos relatórios, commits, patches ou saídas de terminal. O serviço ETL usa volume de dados host montado como leitura e o app é reconstruído por `docker compose up -d --build --no-deps app` na pasta `dashboard`.

Tabelas/vistas importantes do banco:

| Objeto | Condição atual |
| --- | --- |
| `ref.municipio` | 268 municípios legados, `area_estudo=true` para todos |
| `mapbiomas.cobertura` | Cobertura legada; não sobrescrever |
| `mapbiomas.classe` | Legenda atual; códigos Col9 presentes, sem equivalência semântica ainda atestada |
| `mapbiomas.vw_cobertura_municipio` | Vista legada consumida por `dados.carregar_cobertura()` |
| `analise.vw_painel_municipio_ano` | Painel integrado legado, dependente das fontes antigas |
| `mapbiomas.cobertura_col9_255` | Nova tabela de 113.364 linhas |
| `ref.municipio_col9_255` | Nova tabela com 255 geometrias MultiPolygon em EPSG:4674 |
| `mapbiomas.vw_cobertura_col9_255` | Nova vista de cobertura |
| `ref.vw_municipios_col9_255` | Nova vista geográfica |

### 5.1 Colunas da cobertura Col9/255

`cd_mun INTEGER`, `nm_mun TEXT`, `sigla_uf CHAR(2)`, `ano SMALLINT`, `classe_cobertura SMALLINT`, `pixels BIGINT`, `area_ha NUMERIC(18,4)`, `perc_ocupacao NUMERIC(10,4)`. Chave primária composta: `(cd_mun, ano, classe_cobertura)`. Não há chave estrangeira para `ref.municipio` legado.

### 5.2 Comandos de diagnóstico sem escrita

```powershell
$pgUser = docker exec dashboard-mestrado-db-1 printenv POSTGRES_USER
$pgDb = docker exec dashboard-mestrado-db-1 printenv POSTGRES_DB
docker exec dashboard-mestrado-db-1 psql -U $pgUser -d $pgDb -c "SELECT COUNT(*) AS linhas, COUNT(DISTINCT cd_mun) AS municipios, COUNT(DISTINCT ano) AS anos FROM mapbiomas.vw_cobertura_col9_255;"
docker exec dashboard-mestrado-db-1 psql -U $pgUser -d $pgDb -c "SELECT COUNT(*) AS municipios FROM ref.municipio_col9_255;"
```

Esperado: `113364 | 255 | 39` e `255`. A rotina do Codex deve consultar `pg_catalog`, `information_schema`, dependências SQL e `EXPLAIN` antes de migrar o painel integrado.

## 6. Diagnóstico do dashboard legado

No `dados.py` anexo, `USA_BANCO = bool(os.environ.get('PGHOST'))`; a conexão SQLAlchemy usa `postgresql+psycopg://` com variáveis padrão PostgreSQL. `carregar_cobertura()` consulta `mapbiomas.vw_cobertura_municipio`; `carregar_legenda()` consulta `mapbiomas.classe`; `carregar_painel()` consulta `analise.vw_painel_municipio_ano`; `carregar_contornos()` usa `ref.vw_municipio_contorno` e `ref.mv_area_estudo_contorno`; `carregar_municipios()` usa `ref.vw_municipio`; `carregar_focos_pontos()` faz JOIN com `ref.municipio` e aplica `m.area_estudo`. PRODES e queimadas utilizam outras vistas legadas.

No `app.py`, os trechos relevantes incluem:

- Inicialização por `dados.carregar_cobertura()` e merge com legenda.
- Título e caption **Coleção 10.1**; não rotular dados Col9 com esse texto.
- `ANOS_MAPAS = (1985, 2024)`; **2024 não pertence à Coleção 9**.
- Arquivos PNG/PGW de mapas do processamento antigo; não representar imagens Col10 como se fossem Col9.
- Aba `Queimadas` com `dados.carregar_focos_mensais()`, `carregar_municipios()` e `carregar_contornos()` legados.
- Aba `Desmatamento (PRODES)` com `dados.carregar_prodes()`; combina dados com cobertura.
- Aba `Análise Integrada` com `dados.carregar_painel()`; a vista `analise.vw_painel_municipio_ano` alinha mapas do ano civil anterior ao ano PRODES.
- Exportações PDF e componentes derivados contêm referência estática à Coleção 10.1.

**Regra central:** o Codex não deve fazer um `search-and-replace` indiscriminado de `vw_cobertura_municipio` por `vw_cobertura_col9_255`. Há 10 abas interdependentes, com fontes e universos distintos. Toda alteração de universo deve ser explícita, visível na interface e rastreável.

## 7. Plano técnico de execução por fases

### Fase 0 Inventário e controle de versão

1. Inspecionar `git status`, `git branch`, dependências, Dockerfiles, arquivo de rotas, `db/init`, migrações e testes. Se não houver repositório Git, propor inicialização ou cópia recuperável antes de editar; nunca sobrescrever alterações do usuário.
2. Registrar inventário de tabelas e vistas (`pg_catalog`, `information_schema`, `pg_depend`) e permissões dos papéis de aplicação, sem expor credenciais.
3. Inspecionar a página já instalada `pages/01_Colecao_9_255.py`, o `Dockerfile` efetivo do app e sua rota no localhost.
4. Definir um checkpoint não destrutivo (commit no Git ou backup versionado) antes de qualquer migração; não apagar volumes Docker, não executar `docker compose down -v`.
5. Documentar resultado inicial de testes e capturas relevantes (sem senhas).

**Aceite F0:** inventário, dependências e regressões conhecidas registrados; app e banco legados iniciam normalmente.

### Fase 1 Contrato de dados e acesso

1. Criar um contrato explícito de séries: `col9_255_1985_2023`, `legado_10_1` e outras fontes. Expor modo/série por configuração, não via substituição silenciosa.
2. Centralizar consultas em `dados.py` ou módulo novo `dados_col9.py`; usar queries parametrizadas, cache controlado e conversão precisa de `NUMERIC` para números utilizáveis nos gráficos.
3. Criar testes de cobertura: 113.364 linhas, 255 códigos, 39 anos, anos mínima/máxima 1985/2023, chave única e nenhum município faltante em algum ano.
4. Definir nomes canônicos das colunas em Pandas (`CD_MUN`, `NM_MUN`, `SIGLA_UF`, `ano`, `classe_cobertura`, `pixels`, `area_ha`, `perc_ocupacao`); evitar chave implícita por nome.
5. Validar permissões de leitura do `dashboard_app` nas novas views; evitar grants de escrita.
6. Realizar verificação independente da legenda da Coleção 9: código, descrição, grupo, tipo, cor. Persistir versão da legenda e fonte/metadados no banco, se necessário; não assumir que a existência do código resolve todos os significados.

**Aceite F1:** contratos testados e página Col9 consultando apenas a tabela/vista nova; metadados de proveniência disponíveis.

### Fase 2 Página e visualizações Col9/255

1. Evoluir a página isolada, mantendo `app.py` intacto durante os primeiros testes. Filtros: cinco UFs, 255 municípios, 1985–2023, códigos/classes da Coleção 9.
2. Incluir resumo de cobertura, séries de classes, participação percentual, evolução por década, comparação 1985–2023 e exportação de dados filtrados.
3. Reimplementar índices de antropização e vegetação nativa com definições científicas documentadas, baseadas em códigos da Coleção 9; evitar usar apenas strings de grupos da legenda 10.1 sem homologação.
4. Acrescentar mapa geográfico por `ref.vw_municipios_col9_255`; calcular limites/polígonos com simplificação geográfica apenas para visualização, mantendo a geometria original para cálculos. Conferir SRID, validade e ordenação dos municípios.
5. Reconstruir os PNGs/PGWs ou a renderização de mapas temáticos para **1985 e 2023 da Coleção 9**; a imagem colorida é apenas uma interpretação da classe numérica, e não deve ser confundida com dados RGB originais.
6. Prever mensagens claras para dados ausentes, classes raras, município sem amostra, ano sem raster e legenda não homologada.
7. Evitar carregar raster completo de bilhões de pixels em memória no Streamlit; preferir estatísticas prontas do Postgres e leituras de janelas/tiles para visualização local.

**Aceite F2:** todos os gráficos do módulo Col9 utilizam 255 municípios; nenhuma referência a 2024 ou Coleção 10.1 aparece como fonte dos resultados Col9. O app antigo continua funcionando.

### Fase 3 Harmonização PRODES e queimadas

1. Auditar contagens de municípios e cobertura de anos para cada fonte complementar antes de utilizar indicadores com os 255 municípios.
2. Criar vistas `*_255` não destrutivas que usem a seleção definitiva por códigos IBGE. Priorizar `JOIN ref.municipio_col9_255` e evitar dependência da flag `ref.municipio.area_estudo` de 268.
3. Distinguir **município ausente da fonte**, **município presente sem ocorrência** e **valor observado igual a zero**. Não substituir automaticamente ausências por zero.
4. Para os quatro novos municípios, verificar se há dados PRODES/queimadas originalmente recortados pela seleção de 268. Se faltarem, obter dados da fonte primária ou documentar a lacuna; não fabricar valores.
5. Conferir janelas temporais: o ano PRODES de agosto a julho não coincide diretamente com o ano civil MapBiomas. Manter alinhamento temporal explícito e testado nas vistas SQL.
6. Recalcular métricas normalizadas pela área em km² ou hectares com a geometria definitiva; escolher denominadores consistentes e guardar versão do limite territorial.
7. Recriar vizinhanças geográficas a partir da geometria de 255 municípios quando os indicadores exigirem vizinhos; não reutilizar vizinhanças calculadas para a seleção antiga sem auditoria.

**Aceite F3:** cada indicador integrado informa fonte, período, unidade, universo municipal e tratamento de dados ausentes; todos os quatro municípios novos são tratados explicitamente.

### Fase 4 Análise integrada, transições e modelagem

1. Criar vista de painel integrado para 255 municípios independente da `analise.vw_painel_municipio_ano` antiga; preservar a estrutura legada.
2. Recalcular estatísticas de transição entre classes com máscara comum de pixels válidos nos dois anos. Não converter `0`/NoData em classe de mudança.
3. Testar a sensibilidade do intervalo 2001–2003 para Buriticupu e dos demais casos com pequenas diferenças de máscara; apresentar quantidade de pixels elegíveis e excluídos em cada comparação.
4. Estabelecer definições operacionais de vegetação nativa, pastagem, agricultura, mineração, área urbana, corpos d’água e antropização com versão de legenda.
5. Separar indicadores descritivos, explicativos e preditivos. Para RF/XGBoost/SVM, impedir vazamento temporal, validar por município/ano e comparar métricas adequadas (AUC-ROC, PR-AUC, F1, matriz de confusão). Nenhum modelo deve ser declarado validado antes dos testes.
6. Tratar desequilíbrio de classes, correlação espacial e espacialização do risco. Documentar amostragens, semente aleatória, atributos e partições treino/teste.
7. Reproduzir os gráficos e tabelas destinados à dissertação exclusivamente de consultas versionadas e verificáveis.

**Aceite F4:** métricas reproduzíveis, dados de treino/teste rastreáveis, risco de transição artificial controlado e resultados científicos atribuídos à fonte correta.

### Fase 5 Implantação e documentação

1. Adicionar migrações SQL idempotentes ou verificadas por estado, sem `DROP`/`TRUNCATE`/`DELETE` em tabelas legadas.
2. Criar testes unitários de mapeamento de classes, integração SQL e verificações de UI/Streamlit.
3. Separar configuração por ambiente e segredos (`.env` fora do Git); definir políticas de cache e paginação para consultas pesadas.
4. Executar build apenas do serviço `app` quando mudar interface, e ETL apenas quando explicitamente necessário; preservar o volume de banco.
5. Registrar evidências de testes, documentação de execução e comandos seguros de rollback.
6. Atualizar metodologia da dissertação: proveniência, Coleção 9, EPSG, resolução, limites IBGE 2025, amostra de 255, tratamento de NoData, geodesia/área e ressalvas de 2002.

**Aceite F5:** implantação reproduzível em checkout limpo, sem perda da base legada, com procedimentos de reversão verificados.

## 8. Requisitos não funcionais e regras de segurança

| ID | Requisito verificável |
| --- | --- |
| RNF01 | Não executar `docker compose down -v`, `DROP`/`TRUNCATE`/`DELETE` em tabelas legadas ou operações destrutivas sem autorização expressa. |
| RNF02 | Manter uma forma de retornar ao dashboard anterior durante a migração. |
| RNF03 | Utilizar código IBGE `CD_MUN` como identidade; nunca inferir correspondência por nomes similares. |
| RNF04 | Toda fonte e cada gráfico devem declarar coleção, anos e universo municipal. |
| RNF05 | Rasters originais, TIFF complementar e 78 CSVs de auditoria são imutáveis. |
| RNF06 | Nunca expor `.env`, senhas, tokens ou dados pessoais nos logs, relatórios ou commits. |
| RNF07 | Em transições, observar máscara válida comum e rastrear áreas de pixels ausentes. |
| RNF08 | Queries parametrizadas, privilégio mínimo e índices em chaves e geometria. |
| RNF09 | Resultados numéricos e áreas devem manter precisão/CRS; evitar reamostragem bilinear em classes categóricas. |
| RNF10 | Alterações devem vir com testes executados, resultados, limitações e instrução de rollback. |

## 9. Consultas de aceite sugeridas

```sql
-- Integridade da base de cobertura
SELECT COUNT(*) AS linhas, COUNT(DISTINCT cd_mun) AS municipios,
       COUNT(DISTINCT ano) AS anos,
       MIN(ano) AS ano_inicial, MAX(ano) AS ano_final
FROM mapbiomas.vw_cobertura_col9_255;

-- Unicidade das chaves
SELECT cd_mun, ano, classe_cobertura, COUNT(*)
FROM mapbiomas.cobertura_col9_255
GROUP BY 1,2,3 HAVING COUNT(*) > 1;

-- Municipio sem cobertura em algum ano: esperado zero linhas
WITH anos AS (SELECT generate_series(1985,2023) AS ano),
combinacoes AS (SELECT m.cd_mun,a.ano FROM ref.municipio_col9_255 m CROSS JOIN anos a)
SELECT c.cd_mun,c.ano FROM combinacoes c
LEFT JOIN (SELECT DISTINCT cd_mun,ano FROM mapbiomas.cobertura_col9_255) d USING(cd_mun,ano)
WHERE d.cd_mun IS NULL;

-- Confirmar as quatro entradas novas na tabela espacial
SELECT cd_mun,nm_mun,sigla_uf FROM ref.municipio_col9_255
WHERE cd_mun IN (2101772,2108504,2112274,5101837) ORDER BY 1;

-- Conferir o cadastro antigo sem modificá-lo
SELECT COUNT(*), COUNT(*) FILTER (WHERE area_estudo IS TRUE)
FROM ref.municipio;
```

O conjunto de resultados esperado é: `113364 | 255 | 39 | 1985 | 2023`, zero duplicações, zero combinações município–ano ausentes, quatro entradas no novo cadastro e 268 no cadastro legado. Complementar com testes de schema/permissões e revisão semântica de classes.

## 10. Matriz de riscos e mitigação

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Misturar 255 e 268 nas abas | Alto | Contrato de universo por fonte; vistas independentes; testes de contagem |
| Exibir mapa 2024 como Coleção 9 | Alto | Atualizar para mapas Col9 de 1985/2023; legenda explícita |
| Divergência semântica entre classes 9 e 10.1 | Alto | Dicionário oficial versionado e testes de grupos |
| Ausência de PRODES/queimadas nos quatro novos | Alto | Auditoria de cobertura e recuperação específica; usar NA quando necessário |
| Transição artificial em Buriticupu 2002 | Médio localizado | Máscara comum de pixels válidos, sensibilidade e registro metodológico |
| Interrupção do dashboard principal | Médio | Página separada, feature flag e rollback/backup |
| Falhas de permissão no usuário Streamlit | Médio | `GRANT SELECT` apenas nas novas views, sem escrita |
| Desempenho ruim ao carregar rasters | Alto | Pré-agregação em PostgreSQL, índice, cache e consultas por janela |

## 11. Entregáveis solicitados ao Codex

1. Plano de alterações por arquivos, com observação explícita das dependências entre abas.
2. Migrações SQL novas, reversíveis e não destrutivas; nenhuma mutação implícita de `ref.municipio` antigo.
3. Módulos Python/Streamlit revisados com seleção inequívoca da fonte/coleção.
4. Adequação da nova página Col9 com filtros, mapas 1985/2023 e exportações.
5. Vistas/ETL harmonizados para PRODES e queimadas nos 255 municípios, precedidos por auditoria de disponibilidade.
6. Testes de integridade SQL e unidade/integração, com resultados reproduzíveis.
7. Atualização documental de proveniência, metodologia e limitações; log de mudanças.
8. Instruções de implantação com `docker compose` e estratégia de rollback.
9. Relatório final de alterações efetivamente executadas, decisões que dependem do pesquisador e pendências ainda abertas.

## 12. Prompt inicial para entregar ao Codex

> Atue como engenheiro principal do projeto Defesa Mestrado em `D:\mestrado\dashboard`. Leia integralmente o arquivo `TRANSFERENCIA_CODEX_DEFESA_MESTRADO.md` e inspecione o código atual, as migrações SQL, os Dockerfiles, as views e os testes antes de modificar qualquer coisa. O objetivo é evoluir a aplicação Streamlit e PostgreSQL/PostGIS da seleção antiga de 268 municípios/Coleção 10.1 para o estudo definitivo de 255 municípios/Coleção 9 (1985–2023), preservando toda a infraestrutura antiga e os dados já validados. No banco já existem `mapbiomas.cobertura_col9_255`, `ref.municipio_col9_255`, `mapbiomas.vw_cobertura_col9_255` e `ref.vw_municipios_col9_255`; as duas primeiras possuem 113.364 linhas e 255 geometrias, respectivamente. A nova página `pages/01_Colecao_9_255.py` já foi instalada e funciona no localhost. Comece pelas Fases 0 e 1, apresente o diagnóstico e implemente o menor conjunto seguro de mudanças com testes. Não misture fontes/anos/universos, não sobrescreva os 268 municípios legados, não exponha credenciais, não faça migrações destrutivas e não afirme que o raster de 2024 pertence à Coleção 9. Execute testes sempre que possível, relate resultados e só avance para harmonizar PRODES/queimadas após verificar a cobertura territorial das fontes. Divida a implementação em checkpoints claros e documentados.

## 13. Estratégia de colaboração entre ChatGPT e Codex

**Codex:** dono operacional do código, SQL, migrações, testes e Docker quando tiver acesso ao repositório e às permissões apropriadas. **ChatGPT nesta conversa:** apoio à revisão científica, validação metodológica, interpretação das métricas, redação de partes da dissertação e revisão de decisões arquiteturais/relatórios de execução. O pesquisador pode compartilhar saídas, commits e dúvidas entre os dois ambientes. Para garantir continuidade, pedir ao Codex que mantenha no repositório um `docs/DECISOES_DEFESA_MESTRADO.md` com alterações, motivos, resultados dos testes e pendências, evitando depender de memória conversacional.

**Primeira entrega esperada:** inventário/diagnóstico e plano de integração dos dados da Coleção 9 ao painel, não uma substituição integral e precipitada do dashboard legado.
