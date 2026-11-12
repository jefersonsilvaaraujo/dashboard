-- Tabela integrada município x ano (MapBiomas, focos de calor e PRODES) para análise e modelagem.
--
-- Unidade de tempo: ano PRODES AAAA = agosto de AAAA-1 a julho de AAAA.
-- Para evitar que variáveis explicativas "vejam" o período previsto, as variáveis MapBiomas da
-- linha AAAA vêm do mapa de AAAA-1 (situação no início do ano PRODES).

CREATE SCHEMA IF NOT EXISTS analise;
COMMENT ON SCHEMA analise IS 'Bases integradas para análise e modelagem';

GRANT USAGE ON SCHEMA analise TO dashboard_leitura;
ALTER DEFAULT PRIVILEGES IN SCHEMA analise GRANT SELECT ON TABLES TO dashboard_leitura;

-- Municípios vizinhos (até ~110 m de distância: o shapefile tem pequenas frestas entre limites)
CREATE MATERIALIZED VIEW ref.mv_municipio_vizinho AS
SELECT a.cd_mun, b.cd_mun AS cd_mun_vizinho
FROM ref.municipio a
JOIN ref.municipio b ON a.cd_mun <> b.cd_mun AND ST_DWithin(a.geom_simplificada, b.geom_simplificada, 0.001)
WHERE a.area_estudo AND b.area_estudo;

CREATE UNIQUE INDEX mv_municipio_vizinho_pk ON ref.mv_municipio_vizinho (cd_mun, cd_mun_vizinho);
COMMENT ON MATERIALIZED VIEW ref.mv_municipio_vizinho IS 'Pares de municípios vizinhos da área de estudo';

-- Base anual: uma linha por município e ano PRODES
CREATE MATERIALIZED VIEW analise.mv_painel_base AS
WITH anos AS (
    SELECT generate_series(2008, (SELECT max(ano) FROM prodes.classe WHERE tipo = 'desmatamento'))::smallint AS ano
),
grade AS (
    SELECT m.cd_mun, m.cd_uf, m.area_km2::double precision AS area_km2,
           ST_Y(m.centroide) AS latitude, ST_X(m.centroide) AS longitude, a.ano
    FROM ref.municipio m CROSS JOIN anos a
    WHERE m.area_estudo
),
mapbiomas AS (  -- mapa do ano civil AAAA-1, ligado ao ano PRODES AAAA
    SELECT c.cd_mun, (c.ano + 1)::smallint AS ano,
           coalesce(sum(c.area_ha) FILTER (WHERE k.grupo IN ('Floresta', 'Vegetação Herbácea e Arbustiva')), 0) AS natural_ha,
           coalesce(sum(c.area_ha) FILTER (WHERE k.grupo = 'Floresta'), 0)                        AS floresta_ha,
           coalesce(sum(c.area_ha) FILTER (WHERE k.tipo = 'Antrópico'), 0)                        AS antropica_ha,
           coalesce(sum(c.area_ha) FILTER (WHERE c.classe_id = 15), 0)                            AS pastagem_ha,
           coalesce(sum(c.area_ha) FILTER (WHERE c.classe_id = 39), 0)                            AS soja_ha,
           coalesce(sum(c.area_ha) FILTER (WHERE k.grupo = 'Agropecuária' AND c.classe_id NOT IN (9, 15, 21)), 0) AS lavouras_ha,
           coalesce(sum(c.area_ha) FILTER (WHERE c.classe_id = 24), 0)                            AS urbana_ha,
           sum(c.area_ha)                                                                         AS total_ha
    FROM mapbiomas.cobertura c
    JOIN mapbiomas.classe k USING (classe_id)
    GROUP BY 1, 2
),
mapbiomas_variacao AS (  -- variação da vegetação natural em relação ao mapa anterior
    SELECT *, natural_ha - lag(natural_ha) OVER (PARTITION BY cd_mun ORDER BY ano) AS variacao_natural_ha
    FROM mapbiomas
),
focos AS (  -- focos no ano PRODES (agosto de AAAA-1 a julho de AAAA)
    SELECT f.cd_mun,
           (extract(year FROM (f.data_hora AT TIME ZONE 'UTC') - interval '7 months') + 1)::smallint AS ano,
           count(*)                                                                               AS focos,
           count(*) FILTER (WHERE extract(month FROM f.data_hora AT TIME ZONE 'UTC') IN (8, 9, 10)) AS focos_ago_out,
           avg(a.frp)            AS frp_medio,
           max(a.frp)            AS frp_maximo,
           avg(a.risco_fogo)     AS risco_fogo_medio,
           avg(a.dias_sem_chuva)::double precision AS dias_sem_chuva_medio,  -- avg(smallint) seria numeric
           avg(a.precipitacao)   AS precipitacao_media
    FROM queimadas.foco f
    LEFT JOIN queimadas.foco_atributo a USING (foco_id)
    GROUP BY 1, 2
),
focos_civil AS (
    SELECT cd_mun, ano, sum(focos) AS focos FROM queimadas.mv_focos_municipio_mes GROUP BY 1, 2
),
prodes_ano AS (
    SELECT a.cd_mun, c.ano,
           coalesce(sum(a.area_ha) FILTER (WHERE c.tipo = 'desmatamento'), 0) AS desmatamento_ha,
           coalesce(sum(a.area_ha) FILTER (WHERE c.tipo = 'residuo'), 0)      AS residuo_ha
    FROM prodes.area_classe a
    JOIN prodes.classe c USING (classe_id)
    WHERE c.ano IS NOT NULL
    GROUP BY 1, 2
),
prodes_nativa_final AS (  -- vegetação nativa no fim da série PRODES
    SELECT a.cd_mun, sum(a.area_ha) AS nativa_ha
    FROM prodes.area_classe a
    JOIN prodes.classe c USING (classe_id)
    WHERE c.tipo = 'vegetacao_nativa'
    GROUP BY 1
),
prodes_estado AS (
    SELECT g.cd_mun, g.ano,
           -- Vegetação nativa no fim do ano = a do fim da série + o que foi suprimido depois
           coalesce(n.nativa_ha, 0) + coalesce((SELECT sum(p.desmatamento_ha + p.residuo_ha) FROM prodes_ano p
                                   WHERE p.cd_mun = g.cd_mun AND p.ano > g.ano), 0)      AS nativa_fim_ha,
           coalesce(n.nativa_ha, 0) + coalesce((SELECT sum(p.desmatamento_ha + p.residuo_ha) FROM prodes_ano p
                                   WHERE p.cd_mun = g.cd_mun AND p.ano >= g.ano), 0)     AS nativa_inicio_ha,
           coalesce((SELECT sum(p.desmatamento_ha + p.residuo_ha) FROM prodes_ano p
                     WHERE p.cd_mun = g.cd_mun AND p.ano <= g.ano), 0)                    AS acumulado_ha
    FROM grade g
    LEFT JOIN prodes_nativa_final n USING (cd_mun)
),
bioma_area AS (
    SELECT a.cd_mun, b.nome, sum(a.area_ha) AS area_ha
    FROM prodes.area_classe a
    JOIN ref.bioma b USING (cd_bioma)
    GROUP BY 1, 2
),
biomas AS (
    SELECT cd_mun,
           100 * sum(area_ha) FILTER (WHERE nome = 'Amazônia') / sum(area_ha) AS pct_amazonia,
           100 * sum(area_ha) FILTER (WHERE nome = 'Cerrado')  / sum(area_ha) AS pct_cerrado,
           100 * sum(area_ha) FILTER (WHERE nome = 'Pantanal') / sum(area_ha) AS pct_pantanal,
           (array_agg(nome ORDER BY area_ha DESC))[1]                         AS bioma_predominante
    FROM bioma_area
    GROUP BY 1
)
SELECT g.cd_mun,
       g.ano,
       (g.ano >= 2013)                                       AS comparavel_prodes,
       g.cd_uf,
       g.area_km2,
       g.latitude,
       g.longitude,
       coalesce(bi.pct_amazonia, 0)                          AS pct_amazonia,
       coalesce(bi.pct_cerrado, 0)                           AS pct_cerrado,
       coalesce(bi.pct_pantanal, 0)                          AS pct_pantanal,
       bi.bioma_predominante,
       -- MapBiomas (mapa de AAAA-1)
       mb.natural_ha                                         AS mb_vegetacao_natural_ha,
       mb.floresta_ha                                        AS mb_floresta_ha,
       mb.antropica_ha                                       AS mb_antropica_ha,
       mb.pastagem_ha                                        AS mb_pastagem_ha,
       mb.soja_ha                                            AS mb_soja_ha,
       mb.lavouras_ha                                        AS mb_lavouras_ha,
       mb.urbana_ha                                          AS mb_urbana_ha,
       100 * mb.antropica_ha / mb.total_ha                   AS mb_indice_antropizacao,
       mb.variacao_natural_ha                                AS mb_variacao_natural_ha,
       -- Focos de calor
       coalesce(fq.focos, 0)                                 AS fq_focos,
       coalesce(fq.focos_ago_out, 0)                         AS fq_focos_ago_out,
       1000 * coalesce(fq.focos, 0) / g.area_km2             AS fq_densidade_focos,
       coalesce(fc.focos, 0)                                 AS fq_focos_ano_civil,
       fq.frp_medio                                          AS fq_frp_medio,
       fq.frp_maximo                                         AS fq_frp_maximo,
       fq.risco_fogo_medio                                   AS fq_risco_fogo_medio,
       fq.dias_sem_chuva_medio                               AS fq_dias_sem_chuva_medio,
       fq.precipitacao_media                                 AS fq_precipitacao_media,
       -- PRODES
       coalesce(pa.desmatamento_ha, 0)                       AS pd_desmatamento_ha,
       coalesce(pa.residuo_ha, 0)                            AS pd_residuo_ha,
       pe.acumulado_ha                                       AS pd_desmatamento_acumulado_ha,
       pe.nativa_inicio_ha                                   AS pd_vegetacao_nativa_inicio_ha,
       pe.nativa_fim_ha                                      AS pd_vegetacao_nativa_fim_ha,
       CASE WHEN pe.nativa_inicio_ha > 0
            THEN 100 * coalesce(pa.desmatamento_ha, 0) / pe.nativa_inicio_ha END AS pd_taxa_desmatamento
FROM grade g
LEFT JOIN biomas bi USING (cd_mun)
LEFT JOIN mapbiomas_variacao mb USING (cd_mun, ano)
LEFT JOIN focos fq USING (cd_mun, ano)
LEFT JOIN focos_civil fc USING (cd_mun, ano)
LEFT JOIN prodes_ano pa USING (cd_mun, ano)
LEFT JOIN prodes_estado pe USING (cd_mun, ano);

CREATE UNIQUE INDEX mv_painel_base_pk ON analise.mv_painel_base (cd_mun, ano);

COMMENT ON MATERIALIZED VIEW analise.mv_painel_base IS
    'Município x ano PRODES (ago/AAAA-1 a jul/AAAA): MapBiomas (mapa de AAAA-1), focos de calor e PRODES';
COMMENT ON COLUMN analise.mv_painel_base.cd_mun IS 'Código IBGE do município';
COMMENT ON COLUMN analise.mv_painel_base.ano IS 'Ano PRODES AAAA: agosto de AAAA-1 a julho de AAAA';
COMMENT ON COLUMN analise.mv_painel_base.comparavel_prodes IS 'Verdadeiro a partir de 2013, quando o PRODES é anual em toda a área (antes, a vegetação não florestal era mapeada a cada dois anos)';
COMMENT ON COLUMN analise.mv_painel_base.cd_uf IS 'Código IBGE da UF';
COMMENT ON COLUMN analise.mv_painel_base.area_km2 IS 'Área oficial do município (km², IBGE)';
COMMENT ON COLUMN analise.mv_painel_base.latitude IS 'Latitude do centroide do município (graus, SIRGAS 2000)';
COMMENT ON COLUMN analise.mv_painel_base.longitude IS 'Longitude do centroide do município (graus, SIRGAS 2000)';
COMMENT ON COLUMN analise.mv_painel_base.pct_amazonia IS 'Percentual da área do município no bioma Amazônia (IBGE 2019)';
COMMENT ON COLUMN analise.mv_painel_base.pct_cerrado IS 'Percentual da área do município no bioma Cerrado (IBGE 2019)';
COMMENT ON COLUMN analise.mv_painel_base.pct_pantanal IS 'Percentual da área do município no bioma Pantanal (IBGE 2019)';
COMMENT ON COLUMN analise.mv_painel_base.bioma_predominante IS 'Bioma com maior área no município';
COMMENT ON COLUMN analise.mv_painel_base.mb_vegetacao_natural_ha IS 'MapBiomas (mapa de AAAA-1): vegetação natural, grupos Floresta e Vegetação Herbácea e Arbustiva (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_floresta_ha IS 'MapBiomas (mapa de AAAA-1): grupo Floresta (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_antropica_ha IS 'MapBiomas (mapa de AAAA-1): classes de tipo antrópico (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_pastagem_ha IS 'MapBiomas (mapa de AAAA-1): pastagem, classe 15 (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_soja_ha IS 'MapBiomas (mapa de AAAA-1): soja, classe 39 (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_lavouras_ha IS 'MapBiomas (mapa de AAAA-1): lavouras temporárias e perenes, grupo Agropecuária sem pastagem, silvicultura e mosaico (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_urbana_ha IS 'MapBiomas (mapa de AAAA-1): área urbanizada, classe 24 (ha)';
COMMENT ON COLUMN analise.mv_painel_base.mb_indice_antropizacao IS 'MapBiomas (mapa de AAAA-1): área antrópica / área total (%)';
COMMENT ON COLUMN analise.mv_painel_base.mb_variacao_natural_ha IS 'MapBiomas: variação líquida da vegetação natural entre os mapas de AAAA-2 e AAAA-1 (ha; negativo = perda)';
COMMENT ON COLUMN analise.mv_painel_base.fq_focos IS 'Focos de calor no ano PRODES (satélite de referência AQUA)';
COMMENT ON COLUMN analise.mv_painel_base.fq_focos_ago_out IS 'Focos de calor de agosto a outubro (pico da estação seca) dentro do ano PRODES';
COMMENT ON COLUMN analise.mv_painel_base.fq_densidade_focos IS 'Focos de calor no ano PRODES por 1.000 km²';
COMMENT ON COLUMN analise.mv_painel_base.fq_focos_ano_civil IS 'Focos de calor no ano civil AAAA (referência)';
COMMENT ON COLUMN analise.mv_painel_base.fq_frp_medio IS 'FRP médio dos focos do ano PRODES (MW); disponível em 2003-2007 e 2015-2024';
COMMENT ON COLUMN analise.mv_painel_base.fq_frp_maximo IS 'FRP máximo dos focos do ano PRODES (MW); disponível em 2003-2007 e 2015-2024';
COMMENT ON COLUMN analise.mv_painel_base.fq_risco_fogo_medio IS 'Risco de fogo médio no local dos focos (0-1); disponível em 2015-2024';
COMMENT ON COLUMN analise.mv_painel_base.fq_dias_sem_chuva_medio IS 'Dias sem chuva médios no local dos focos; disponível em 2015-2024';
COMMENT ON COLUMN analise.mv_painel_base.fq_precipitacao_media IS 'Precipitação média no local e dia dos focos (mm); disponível em 2015-2024';
COMMENT ON COLUMN analise.mv_painel_base.pd_desmatamento_ha IS 'PRODES: desmatamento do ano (classe dAAAA, ha). Até 2012 a vegetação não florestal soma dois anos nos anos pares';
COMMENT ON COLUMN analise.mv_painel_base.pd_residuo_ha IS 'PRODES: resíduo identificado no ano (classe rAAAA, desmatamento antigo detectado depois, ha)';
COMMENT ON COLUMN analise.mv_painel_base.pd_desmatamento_acumulado_ha IS 'PRODES: desmatamento acumulado até o fim do ano, incluindo resíduos (ha)';
COMMENT ON COLUMN analise.mv_painel_base.pd_vegetacao_nativa_inicio_ha IS 'PRODES: vegetação nativa no início do ano (ha)';
COMMENT ON COLUMN analise.mv_painel_base.pd_vegetacao_nativa_fim_ha IS 'PRODES: vegetação nativa no fim do ano (ha)';
COMMENT ON COLUMN analise.mv_painel_base.pd_taxa_desmatamento IS 'PRODES: desmatamento do ano / vegetação nativa no início do ano (%); nula onde não há vegetação nativa no PRODES (municípios do MA desmatados antes de 2008)';

-- Visão final: base + defasagens, médias móveis, vizinhança e variáveis-alvo do ano seguinte
CREATE VIEW analise.vw_painel_municipio_ano AS
SELECT b.*,
       m.nome                                                             AS nm_mun,
       u.sigla                                                            AS sigla_uf,
       lag(b.pd_desmatamento_ha, 1) OVER w                               AS pd_desmatamento_ha_lag1,
       lag(b.pd_desmatamento_ha, 2) OVER w                               AS pd_desmatamento_ha_lag2,
       avg(b.pd_desmatamento_ha) OVER (w ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS pd_desmatamento_ha_mm3,
       lag(b.fq_focos, 1) OVER w                                         AS fq_focos_lag1,
       lag(b.fq_focos, 2) OVER w                                         AS fq_focos_lag2,
       (avg(b.fq_focos) OVER (w ROWS BETWEEN 2 PRECEDING AND CURRENT ROW))::double precision AS fq_focos_mm3,
       vz.vz_taxa_desmatamento,
       vz.vz_densidade_focos,
       vz.vz_quantidade,
       lead(b.pd_desmatamento_ha) OVER w                                 AS alvo_desmatamento_ha_t1,
       lead(b.pd_taxa_desmatamento) OVER w                               AS alvo_taxa_desmatamento_t1
FROM analise.mv_painel_base b
JOIN ref.municipio m USING (cd_mun)
JOIN ref.uf u ON u.cd_uf = b.cd_uf
LEFT JOIN LATERAL (
    SELECT avg(n.pd_taxa_desmatamento) AS vz_taxa_desmatamento,
           avg(n.fq_densidade_focos)   AS vz_densidade_focos,
           count(*)                    AS vz_quantidade
    FROM ref.mv_municipio_vizinho v
    JOIN analise.mv_painel_base n ON n.cd_mun = v.cd_mun_vizinho AND n.ano = b.ano
    WHERE v.cd_mun = b.cd_mun
) vz ON true
WINDOW w AS (PARTITION BY b.cd_mun ORDER BY b.ano);

COMMENT ON VIEW analise.vw_painel_municipio_ano IS
    'Painel município x ano PRODES com defasagens, vizinhança e alvos do ano seguinte (base para modelagem)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.nm_mun IS 'Nome do município';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.sigla_uf IS 'Sigla da UF';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.pd_desmatamento_ha_lag1 IS 'PRODES: desmatamento do ano anterior (ha)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.pd_desmatamento_ha_lag2 IS 'PRODES: desmatamento de dois anos antes (ha)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.pd_desmatamento_ha_mm3 IS 'PRODES: média do desmatamento nos últimos 3 anos, incluindo o atual (ha; menos anos no início da série)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.fq_focos_lag1 IS 'Focos de calor no ano PRODES anterior';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.fq_focos_lag2 IS 'Focos de calor de dois anos PRODES antes';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.fq_focos_mm3 IS 'Média de focos nos últimos 3 anos PRODES, incluindo o atual (menos anos no início da série)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.vz_taxa_desmatamento IS 'Média da taxa de desmatamento PRODES dos municípios vizinhos no mesmo ano (%)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.vz_densidade_focos IS 'Média da densidade de focos dos municípios vizinhos no mesmo ano (focos por 1.000 km²)';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.vz_quantidade IS 'Número de municípios vizinhos dentro da área de estudo';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.alvo_desmatamento_ha_t1 IS 'ALVO: desmatamento PRODES no ano seguinte (ha); nulo no último ano';
COMMENT ON COLUMN analise.vw_painel_municipio_ano.alvo_taxa_desmatamento_t1 IS 'ALVO: taxa de desmatamento PRODES no ano seguinte (%); nulo no último ano e onde não há vegetação nativa';
