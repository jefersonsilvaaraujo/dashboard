-- PRODES: desmatamento por município, bioma e classe; biomas do IBGE como referência.

-- Biomas do IBGE (1:250.000, 2019), o mesmo limite usado pelo PRODES e pelo MapBiomas
CREATE TABLE ref.bioma (
    cd_bioma  smallint PRIMARY KEY CHECK (cd_bioma BETWEEN 1 AND 6),
    nome      text     NOT NULL UNIQUE,
    geom      geometry(MultiPolygon, 4674) NOT NULL CHECK (ST_IsValid(geom)),
    carga_id  integer  NOT NULL REFERENCES ref.carga
);
COMMENT ON TABLE ref.bioma IS 'Biomas do Brasil - IBGE 1:250.000 (2019)';
CREATE INDEX bioma_geom_gix ON ref.bioma USING gist (geom);

CREATE SCHEMA IF NOT EXISTS prodes;
COMMENT ON SCHEMA prodes IS 'Desmatamento - INPE/PRODES';

GRANT USAGE ON SCHEMA prodes TO dashboard_leitura;
ALTER DEFAULT PRIVILEGES IN SCHEMA prodes GRANT SELECT ON TABLES TO dashboard_leitura;

-- Legenda do raster PRODES Brasil
CREATE TABLE prodes.classe (
    classe_id  smallint PRIMARY KEY CHECK (classe_id BETWEEN 0 AND 255),
    rotulo     text     NOT NULL UNIQUE,
    tipo       text     NOT NULL CHECK (tipo IN ('desmatamento', 'residuo', 'hidrografia', 'vegetacao_nativa')),
    ano        smallint CHECK (ano BETWEEN 2000 AND 2100),
    carga_id   integer  NOT NULL REFERENCES ref.carga,
    CONSTRAINT classe_ano_coerente CHECK ((tipo IN ('desmatamento', 'residuo')) = (ano IS NOT NULL))
);
COMMENT ON TABLE prodes.classe IS 'Classes do PRODES: dAAAA (desmatamento do ano PRODES AAAA), rAAAA (resíduo), hidrografia e vegetação nativa';
COMMENT ON COLUMN prodes.classe.ano IS
    'Ano PRODES (ago/AAAA-1 a jul/AAAA). d2000 e d2007 acumulam períodos anteriores; até 2012 a vegetação não florestal foi mapeada a cada dois anos';

-- Área de cada classe por município e bioma (estatística zonal do raster)
CREATE TABLE prodes.area_classe (
    cd_mun     integer          NOT NULL REFERENCES ref.municipio,
    cd_bioma   smallint         NOT NULL REFERENCES ref.bioma,
    classe_id  smallint         NOT NULL REFERENCES prodes.classe,
    area_ha    double precision NOT NULL CHECK (area_ha > 0),
    carga_id   integer          NOT NULL REFERENCES ref.carga,
    PRIMARY KEY (cd_mun, cd_bioma, classe_id)
);
COMMENT ON TABLE prodes.area_classe IS 'Área (ha) de cada classe PRODES na parte do município dentro de cada bioma';
-- Tabela pequena (dezenas de milhares de linhas): a chave primária atende às consultas do painel

-- Visão lida pelo app
CREATE VIEW prodes.vw_area_classe_municipio AS
SELECT a.cd_mun, m.nome AS nm_mun, u.sigla AS sigla_uf, b.nome AS bioma,
       a.classe_id, c.rotulo, c.tipo, c.ano, a.area_ha
FROM prodes.area_classe a
JOIN ref.municipio m USING (cd_mun)
JOIN ref.uf u USING (cd_uf)
JOIN ref.bioma b USING (cd_bioma)
JOIN prodes.classe c USING (classe_id)
WHERE m.area_estudo;
