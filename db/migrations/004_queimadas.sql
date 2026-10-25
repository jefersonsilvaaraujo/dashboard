-- Queimadas: focos de calor do INPE (satélite de referência) e seus agregados.

CREATE SCHEMA IF NOT EXISTS queimadas;
COMMENT ON SCHEMA queimadas IS 'Focos de calor - INPE/BDQueimadas';

GRANT USAGE ON SCHEMA queimadas TO dashboard_leitura;
ALTER DEFAULT PRIVILEGES IN SCHEMA queimadas GRANT SELECT ON TABLES TO dashboard_leitura;

-- Um registro por foco detectado dentro de um município carregado em ref.municipio.
CREATE TABLE queimadas.foco (
    foco_id    uuid        PRIMARY KEY,
    id_bdq     bigint      NOT NULL UNIQUE,
    data_hora  timestamptz NOT NULL,
    satelite   text        NOT NULL,
    bioma      text        NOT NULL CHECK (bioma IN ('Amazônia', 'Caatinga', 'Cerrado', 'Mata Atlântica', 'Pampa', 'Pantanal')),
    cd_mun     integer     NOT NULL REFERENCES ref.municipio,
    geom       geometry(Point, 4674) NOT NULL,
    carga_id   integer     NOT NULL REFERENCES ref.carga
);
COMMENT ON TABLE queimadas.foco IS 'Focos de calor do satélite de referência; município definido pelo polígono que contém o ponto';
COMMENT ON COLUMN queimadas.foco.data_hora IS 'Passagem do satélite (o INPE publica em UTC)';
COMMENT ON COLUMN queimadas.foco.bioma IS 'Bioma informado pelo INPE';

-- Consultas do painel: focos de um município num período
CREATE INDEX foco_mun_data_idx ON queimadas.foco (cd_mun, data_hora);
-- Consultas por período em toda a área; a carga insere em ordem de data, o que torna o BRIN compacto e eficiente
CREATE INDEX foco_data_brin ON queimadas.foco USING brin (data_hora);
-- Cruzamentos espaciais (ex.: focos dentro de polígonos de desmatamento)
CREATE INDEX foco_geom_gix ON queimadas.foco USING gist (geom);
CREATE INDEX foco_carga_idx ON queimadas.foco (carga_id);

-- Atributos disponíveis só em parte da série (shapefiles do BDQueimadas):
-- FRP em 2003-2007 e 2015-2024; chuva, dias sem chuva e risco de fogo em 2015-2024.
CREATE TABLE queimadas.foco_atributo (
    foco_id         uuid     PRIMARY KEY REFERENCES queimadas.foco ON DELETE CASCADE,
    frp             real     CHECK (frp >= 0),
    precipitacao    real     CHECK (precipitacao >= 0),
    dias_sem_chuva  smallint CHECK (dias_sem_chuva BETWEEN 0 AND 120),
    risco_fogo      real     CHECK (risco_fogo BETWEEN 0 AND 1),
    carga_id        integer  NOT NULL REFERENCES ref.carga
);
COMMENT ON TABLE queimadas.foco_atributo IS 'Atributos complementares do foco, quando disponíveis na fonte';
COMMENT ON COLUMN queimadas.foco_atributo.frp IS 'Potência radiativa do fogo (MW)';
COMMENT ON COLUMN queimadas.foco_atributo.precipitacao IS 'Precipitação no dia (mm)';
CREATE INDEX foco_atributo_carga_idx ON queimadas.foco_atributo (carga_id);

-- Agregado mensal por município, recalculado ao final de cada carga.
-- Materializado porque o painel lê todos os municípios a cada sessão.
CREATE MATERIALIZED VIEW queimadas.mv_focos_municipio_mes AS
SELECT f.cd_mun,
       extract(year  FROM f.data_hora AT TIME ZONE 'UTC')::smallint AS ano,
       extract(month FROM f.data_hora AT TIME ZONE 'UTC')::smallint AS mes,
       count(*)::integer                         AS focos,
       count(a.frp)::integer                     AS focos_com_frp,
       avg(a.frp)::double precision              AS frp_medio,
       max(a.frp)::double precision              AS frp_maximo,
       avg(a.precipitacao)::double precision     AS precipitacao_media,
       avg(a.dias_sem_chuva)::double precision   AS dias_sem_chuva_medio,  -- avg(smallint) seria numeric
       avg(a.risco_fogo)::double precision       AS risco_fogo_medio
FROM queimadas.foco f
LEFT JOIN queimadas.foco_atributo a USING (foco_id)
GROUP BY 1, 2, 3;

CREATE UNIQUE INDEX mv_focos_municipio_mes_pk ON queimadas.mv_focos_municipio_mes (cd_mun, ano, mes);

-- Visão lida pelo app: área de estudo, com nome do município e UF
CREATE VIEW queimadas.vw_focos_municipio_mes AS
SELECT q.cd_mun, m.nome AS nm_mun, u.sigla AS sigla_uf, q.ano, q.mes, q.focos,
       q.focos_com_frp, q.frp_medio, q.frp_maximo,
       q.precipitacao_media, q.dias_sem_chuva_medio, q.risco_fogo_medio
FROM queimadas.mv_focos_municipio_mes q
JOIN ref.municipio m USING (cd_mun)
JOIN ref.uf u USING (cd_uf)
WHERE m.area_estudo;
