# 🌱 Painel Interativo da Cobertura do Solo - MapBiomas

Este painel interativo desenvolvido em **Python com Streamlit** tem como objetivo permitir a **análise da dinâmica de uso e cobertura do solo** em municípios da fronteira Cerrado-Amazônia, com base nos dados do projeto **MapBiomas** (Coleção 10.1, séries históricas de 1985 a 2024).

## 🔍 Funcionalidades

- Visualização interativa de gráficos por ano, década e classe de cobertura
- Filtros por município, classe de uso do solo e intervalo de anos
- Comparação entre dois anos selecionados
- Cálculo do Índice de Antropização
- Alertas automáticos de perda de vegetação nativa
- Mapas da região de estudo com marcador do município e mapas de uso e cobertura do próprio município (1985 e 2024)
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
| `municipios_base/area_estudo.csv` (opcional) | Lista de `CD_MUN` que define a área de estudo |

```bash
docker compose run --rm etl                               # banco
docker compose run --rm etl python municipios.py          # CSV de municípios
docker compose run --rm etl python mapbiomas_col10.py     # CSVs de cobertura e legenda
docker compose run --rm etl python mapas.py               # mapas PNG
```

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

Os testes verificam que banco e CSVs têm os mesmos dados e que o painel mostra os mesmos indicadores nas duas fontes.

## 🌐 Publicação em servidor

Veja [manual_streamlit_vps.md](manual_streamlit_vps.md).

## 📋 Licença

Este projeto é distribuído sob licença livre para fins acadêmicos e científicos.

## 🙋‍♂️ Autor

[Jeferson Silva (Jef EAD)](https://jefead.com.br)
Desenvolvido como parte de um projeto de pesquisa sobre predição de risco ambiental com Machine Learning.
