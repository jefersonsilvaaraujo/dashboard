# Dicionário de variáveis do painel município x ano

Painel município x ano PRODES com defasagens, vizinhança e alvos do ano seguinte (base para modelagem).

Fonte: `analise.vw_painel_municipio_ano` (gerado por `processamento/painel.py`). 4824 linhas: 268 municípios, anos PRODES 2008 a 2025.

Prefixos: `mb_` MapBiomas (mapa do ano civil anterior), `fq_` focos de calor, `pd_` PRODES, `vz_` média dos municípios vizinhos, `alvo_` variável a prever (ano seguinte).

| Variável | Tipo | Preenchida | Descrição |
|---|---|---|---|
| `cd_mun` | integer | 100% | Código IBGE do município |
| `ano` | smallint | 100% | Ano PRODES AAAA: agosto de AAAA-1 a julho de AAAA |
| `comparavel_prodes` | boolean | 100% | Verdadeiro a partir de 2013, quando o PRODES é anual em toda a área (antes, a vegetação não florestal era mapeada a cada dois anos) |
| `cd_uf` | smallint | 100% | Código IBGE da UF |
| `area_km2` | double precision | 100% | Área oficial do município (km², IBGE) |
| `latitude` | double precision | 100% | Latitude do centroide do município (graus, SIRGAS 2000) |
| `longitude` | double precision | 100% | Longitude do centroide do município (graus, SIRGAS 2000) |
| `pct_amazonia` | double precision | 100% | Percentual da área do município no bioma Amazônia (IBGE 2019) |
| `pct_cerrado` | double precision | 100% | Percentual da área do município no bioma Cerrado (IBGE 2019) |
| `pct_pantanal` | double precision | 100% | Percentual da área do município no bioma Pantanal (IBGE 2019) |
| `bioma_predominante` | text | 100% | Bioma com maior área no município |
| `mb_vegetacao_natural_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): vegetação natural, grupos Floresta e Vegetação Herbácea e Arbustiva (ha) |
| `mb_floresta_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): grupo Floresta (ha) |
| `mb_antropica_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): classes de tipo antrópico (ha) |
| `mb_pastagem_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): pastagem, classe 15 (ha) |
| `mb_soja_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): soja, classe 39 (ha) |
| `mb_lavouras_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): lavouras temporárias e perenes, grupo Agropecuária sem pastagem, silvicultura e mosaico (ha) |
| `mb_urbana_ha` | double precision | 100% | MapBiomas (mapa de AAAA-1): área urbanizada, classe 24 (ha) |
| `mb_indice_antropizacao` | double precision | 100% | MapBiomas (mapa de AAAA-1): área antrópica / área total (%) |
| `mb_variacao_natural_ha` | double precision | 100% | MapBiomas: variação líquida da vegetação natural entre os mapas de AAAA-2 e AAAA-1 (ha; negativo = perda) |
| `fq_focos` | bigint | 100% | Focos de calor no ano PRODES (satélite de referência AQUA) |
| `fq_focos_ago_out` | bigint | 100% | Focos de calor de agosto a outubro (pico da estação seca) dentro do ano PRODES |
| `fq_densidade_focos` | double precision | 100% | Focos de calor no ano PRODES por 1.000 km² |
| `fq_focos_ano_civil` | bigint | 100% | Focos de calor no ano civil AAAA (referência) |
| `fq_frp_medio` | double precision | 65% | FRP médio dos focos do ano PRODES (MW); disponível em 2003-2007 e 2015-2024 |
| `fq_frp_maximo` | real | 65% | FRP máximo dos focos do ano PRODES (MW); disponível em 2003-2007 e 2015-2024 |
| `fq_risco_fogo_medio` | double precision | 59% | Risco de fogo médio no local dos focos (0-1); disponível em 2015-2024 |
| `fq_dias_sem_chuva_medio` | double precision | 59% | Dias sem chuva médios no local dos focos; disponível em 2015-2024 |
| `fq_precipitacao_media` | double precision | 59% | Precipitação média no local e dia dos focos (mm); disponível em 2015-2024 |
| `pd_desmatamento_ha` | double precision | 100% | PRODES: desmatamento do ano (classe dAAAA, ha). Até 2012 a vegetação não florestal soma dois anos nos anos pares |
| `pd_residuo_ha` | double precision | 100% | PRODES: resíduo identificado no ano (classe rAAAA, desmatamento antigo detectado depois, ha) |
| `pd_desmatamento_acumulado_ha` | double precision | 100% | PRODES: desmatamento acumulado até o fim do ano, incluindo resíduos (ha) |
| `pd_vegetacao_nativa_inicio_ha` | double precision | 100% | PRODES: vegetação nativa no início do ano (ha) |
| `pd_vegetacao_nativa_fim_ha` | double precision | 100% | PRODES: vegetação nativa no fim do ano (ha) |
| `pd_taxa_desmatamento` | double precision | 97% | PRODES: desmatamento do ano / vegetação nativa no início do ano (%); nula onde não há vegetação nativa no PRODES (municípios do MA desmatados antes de 2008) |
| `nm_mun` | text | 100% | Nome do município |
| `sigla_uf` | character | 100% | Sigla da UF |
| `pd_desmatamento_ha_lag1` | double precision | 94% | PRODES: desmatamento do ano anterior (ha) |
| `pd_desmatamento_ha_lag2` | double precision | 89% | PRODES: desmatamento de dois anos antes (ha) |
| `pd_desmatamento_ha_mm3` | double precision | 100% | PRODES: média do desmatamento nos últimos 3 anos, incluindo o atual (ha; menos anos no início da série) |
| `fq_focos_lag1` | bigint | 94% | Focos de calor no ano PRODES anterior |
| `fq_focos_lag2` | bigint | 89% | Focos de calor de dois anos PRODES antes |
| `fq_focos_mm3` | double precision | 100% | Média de focos nos últimos 3 anos PRODES, incluindo o atual (menos anos no início da série) |
| `vz_taxa_desmatamento` | double precision | 100% | Média da taxa de desmatamento PRODES dos municípios vizinhos no mesmo ano (%) |
| `vz_densidade_focos` | double precision | 100% | Média da densidade de focos dos municípios vizinhos no mesmo ano (focos por 1.000 km²) |
| `vz_quantidade` | bigint | 100% | Número de municípios vizinhos dentro da área de estudo |
| `alvo_desmatamento_ha_t1` | double precision | 94% | ALVO: desmatamento PRODES no ano seguinte (ha); nulo no último ano |
| `alvo_taxa_desmatamento_t1` | double precision | 92% | ALVO: taxa de desmatamento PRODES no ano seguinte (%); nulo no último ano e onde não há vegetação nativa |
