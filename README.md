# 🌱 Painel Interativo da Cobertura do Solo - MapBiomas

Este painel interativo desenvolvido em **Python com Streamlit** tem como objetivo permitir a **análise da dinâmica de uso e cobertura do solo** em municípios da fronteira Cerrado-Amazônia, com base nos dados do projeto **MapBiomas** (Coleção 10.1, séries históricas de 1985 a 2024).

## 🔍 Funcionalidades

- Visualização interativa de gráficos por ano, década e classe de cobertura
- Filtros por município, classe de uso do solo e intervalo de anos
- Comparação entre dois anos selecionados
- Cálculo do Índice de Antropização
- Alertas automáticos de perda de vegetação nativa
- Mapas da região de estudo com marcador do município e mapas de uso e cobertura do próprio município (1985 e 2024)
- Focos de calor do INPE (2003–2025): série anual, sazonalidade, ranking de municípios, intensidade do fogo (FRP), condições do tempo e mapa dos focos
- Desmatamento PRODES por município e bioma (acumulado, série anual 2008–2025, ranking) e comparação com a perda de vegetação nativa do MapBiomas
- Geração de relatório PDF completo com gráficos e mapas

## 🏗 Arquitetura

```
                 ┌──────────────────────────── docker compose ───────────────────────────┐
dados brutos ──► │  etl (processamento/)  ──►  db (PostgreSQL 17 + PostGIS)  ──►  app (Streamlit) │ ──► Apache ──► usuário
(fora do Git)    └──────────────────────────────────────────────────────────────────────┘
```

| Serviço | Papel |
|---|---|
| `db` | PostgreSQL com PostGIS. Esquema versionado em `db/migrations/`. |
| `app` | O painel. Conecta com um usuário **somente leitura** e guarda as consultas em cache. |
| `etl` | Processamento sob demanda: aplica as migrações e carrega os dados no banco. |

As portas são publicadas apenas em `127.0.0.1`; o acesso público passa pelo Apache.

### Banco de dados

| Objeto | Conteúdo |
|---|---|
| `ref.carga` | Proveniência de cada carga: fonte, versão, DOI/URL, hash SHA-256 do arquivo e data |
| `ref.uf` | Unidades da federação (código IBGE) |
| `ref.municipio` | Municípios com polígono (SIRGAS 2000, índice espacial GiST), área oficial, centroide calculado pelo banco e a marca `area_estudo` |
| `mapbiomas.classe` | Legenda oficial: nome, cor, grupo e tipo (natural/antrópico) |
| `mapbiomas.cobertura` | Área (ha) por município, ano e classe |
| `mapbiomas.vw_cobertura_municipio` | Visão lida pelo app; deriva o percentual de ocupação e filtra a área de estudo |
| `ref.vw_municipio` | Municípios da área de estudo com UF e coordenadas do centroide |
| `queimadas.foco` | Focos de calor (ponto, data/hora UTC, bioma, município). O município é o polígono que contém o ponto, calculado no PostGIS. Índices: (município, data), BRIN de data e GiST espacial |
| `queimadas.foco_atributo` | FRP, chuva, dias sem chuva e risco de fogo, quando a fonte oferece (FRP: 2003–2007 e 2015–2024; demais: 2015–2024) |
| `queimadas.mv_focos_municipio_mes` | Agregado mensal por município (view materializada, recalculada a cada carga) |
| `queimadas.vw_focos_municipio_mes` | Agregado mensal da área de estudo, lido pelo app |
| `ref.bioma` | Biomas do IBGE 1:250.000 (2019), com índice espacial |
| `prodes.classe` | Legenda do PRODES: desmatamento por ano (dAAAA), resíduos (rAAAA), hidrografia e vegetação nativa |
| `prodes.area_classe` | Área (ha) de cada classe PRODES por município e bioma |
| `prodes.vw_area_classe_municipio` | Área por classe da área de estudo, lida pelo app |

Princípios adotados: chaves estrangeiras e restrições `CHECK` em todas as tabelas; valores derivados (percentual, centroide) calculados pelo banco em vez de armazenados; cargas em transação única (o painel nunca vê dados pela metade); usuário do app sem permissão de escrita e com tempo-limite de consulta.

Os municípios são identificados pelo código IBGE (`CD_MUN`). No seletor do painel o nome aparece com a UF, pois há homônimos na área de estudo (ex.: Pau D'Arco no PA e no TO).

## 🐳 Como executar (Docker)

Pré-requisito: Docker com Compose.

```bash
cp .env.example .env        # e defina as senhas
docker compose up -d --build
docker compose run --rm etl  # aplica as migrações e carrega os dados
```

Acesse `http://localhost:8501`. O comando do `etl` pode ser repetido sempre que os dados mudarem: ele é idempotente e substitui os dados de forma atômica. O painel guarda as consultas em cache por 1 hora; para ver uma carga nova na hora, reinicie com `docker compose restart app`.

Para conectar o QGIS ou outro cliente ao banco local: `localhost:5432`, banco e usuário definidos no `.env`.

### Sem Docker

Sem as variáveis `PGHOST`/`PGUSER`/`PGPASSWORD`/`PGDATABASE`, o painel lê os CSVs de `historico/` e `coordenadas/`:

```bash
python -m venv venv
venv\Scripts\activate          # Linux: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 🔄 Atualização dos dados

Os dados brutos **não são versionados** e ficam na pasta-mãe do projeto (`MESTRADO_DADOS_HOST` no `.env`):

| Arquivo esperado | Fonte |
|---|---|
| `municipios_base/50km_todosMun.shp` | Limites municipais da área de estudo (IBGE, SIRGAS 2000) |
| `mapbiomas_col10/MAPBIOMAS_BRAZIL-COVERAGE_STATISTICS-COL.10.1-MUNICIPALITIES_STATES_BIOMES.xlsx` | [MapBiomas, estatísticas da Coleção 10.1](https://doi.org/10.58053/MapBiomas/SJZOLT) |
| `mapbiomas_col10/rasters/brazil_coverage_{ano}.tif` (1985 e 2024) | [MapBiomas, rasters anuais da Coleção 10](https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/lulc/coverage/) |
| `queimadas_inpe/focos_br_ref_2003_2025/focos_br_ref_{ano}.zip` | [INPE, focos anuais do satélite de referência](https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/) |
| `queimadas_inpe/focos_qmd_inpe_*/focos_qmd_inpe_*.shp` | Exportações do [BDQueimadas](https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/) com FRP, chuva, dias sem chuva e risco de fogo |
| `desmatamento_prodes/prodes_brasil_2025/prodes_brasil_2025_v20261020.tif` (+ `.qml`) | [INPE/TerraBrasilis, PRODES Brasil](https://terrabrasilis.dpi.inpe.br/downloads/) |
| `biomas_ibge/lm_bioma_250.shp` | [IBGE, Biomas 1:250.000 (2019)](https://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/vetores/) |
| `municipios_base/area_estudo.csv` (opcional) | Lista de `CD_MUN` que define a área de estudo |

```bash
docker compose run --rm etl                               # banco (todas as fontes) e CSV mensal de focos
docker compose run --rm etl python queimadas.py           # só os focos de calor
docker compose run --rm etl python prodes.py              # só o PRODES (~5 min)
docker compose run --rm etl python municipios.py          # CSV de municípios
docker compose run --rm etl python mapbiomas_col10.py     # CSVs de cobertura e legenda
docker compose run --rm etl python mapas.py               # mapas PNG
```

Focos de calor: os atributos dos shapefiles são ligados aos focos por data/hora e coordenadas (todos os registros dos shapefiles encontram seu foco). Valores −999 e fora da faixa física (FRP negativo, dias sem chuva acima de 120, risco fora de 0–1) são tratados como ausentes. O mapa de pontos dos focos só aparece com o banco; no modo CSV o painel usa o agregado mensal.

PRODES: a área de cada classe é somada por município e bioma (interseção calculada no PostGIS) a partir do raster de ~10 m, com a área de cada pixel calculada no elipsoide GRS80 conforme a latitude; a soma das classes de cada município coincide com a área oficial do IBGE. O ano PRODES AAAA vai de agosto de AAAA−1 a julho de AAAA. As classes d2000 a d2007 acumulam o desmatamento anterior à série anual; até 2012 a vegetação não florestal (Cerrado, Pantanal e áreas não florestais da Amazônia) era mapeada a cada dois anos, então anos pares desse período somam dois anos nessas áreas.

Os mapas usam os rasters da Coleção 10 (não há rasters públicos da 10.1); para 1985 e 2024 as áreas por classe diferem menos de 0,1% das estatísticas da Coleção 10.1.

Indicadores derivados da legenda oficial:

- **Vegetação nativa**: classes dos grupos *Floresta* e *Vegetação Herbácea e Arbustiva*.
- **Índice de antropização**: área das classes de tipo *Antrópico* dividida pela área total.

## 🗂 Estrutura de diretórios

```
dashboard/
├── app.py                    # painel
├── dados.py                  # acesso aos dados (PostgreSQL ou CSV)
├── Dockerfile                # imagem do painel
├── docker-compose.yml
├── .env.example
├── db/
│   ├── init/                 # usuário somente leitura do app (criação do banco)
│   └── migrations/           # esquema versionado, aplicado pelo etl
├── processamento/            # ETL: migrações, cargas, CSVs e mapas
├── testes/                   # paridade entre banco e CSVs
├── historico/                # CSVs de cobertura e legenda (gerados)
├── coordenadas/              # CSV de municípios (gerado)
├── municipios_shapefile/     # mapas da região de estudo (gerados)
└── mapas_municipios/         # mapas de cada município (gerados)
```

## ✅ Testes

Com o banco no ar e carregado:

```bash
pip install -r requirements-dev.txt
pytest testes
```

Os testes verificam que banco e CSVs têm os mesmos dados, que o painel mostra os mesmos indicadores nas duas fontes, que a contagem de focos de 2024 confere com a validação independente (51.628 focos) e que a área PRODES de cada município coincide com a área oficial.

## 🌐 Publicação em servidor

Veja [manual_streamlit_vps.md](manual_streamlit_vps.md).

## 📋 Licença

Este projeto é distribuído sob licença livre para fins acadêmicos e científicos.

## 🙋‍♂️ Autor

[Jeferson Silva (Jef EAD)](https://jefead.com.br)
Desenvolvido como parte de um projeto de pesquisa sobre predição de risco ambiental com Machine Learning.
