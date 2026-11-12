-- Referência: controle de cargas, unidades da federação e municípios.

-- Cada carga de dados registra de onde veio (fonte, versão, DOI/URL e hash do arquivo).
-- As tabelas de dados apontam para a carga que as originou.
CREATE TABLE ref.carga (
    carga_id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fonte         text        NOT NULL,
    versao        text,
    referencia    text,
    arquivo       text        NOT NULL,
    sha256        char(64)    NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    registros     integer     NOT NULL CHECK (registros >= 0),
    carregado_em  timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE ref.carga IS 'Proveniência de cada carga de dados (rastreabilidade)';

CREATE TABLE ref.uf (
    cd_uf  smallint PRIMARY KEY CHECK (cd_uf BETWEEN 11 AND 53),
    sigla  char(2)  NOT NULL UNIQUE,
    nome   text     NOT NULL UNIQUE
);
COMMENT ON TABLE ref.uf IS 'Unidades da federação com o código do IBGE';

INSERT INTO ref.uf (cd_uf, sigla, nome) VALUES
    (11, 'RO', 'Rondônia'), (12, 'AC', 'Acre'), (13, 'AM', 'Amazonas'), (14, 'RR', 'Roraima'),
    (15, 'PA', 'Pará'), (16, 'AP', 'Amapá'), (17, 'TO', 'Tocantins'), (21, 'MA', 'Maranhão'),
    (22, 'PI', 'Piauí'), (23, 'CE', 'Ceará'), (24, 'RN', 'Rio Grande do Norte'), (25, 'PB', 'Paraíba'),
    (26, 'PE', 'Pernambuco'), (27, 'AL', 'Alagoas'), (28, 'SE', 'Sergipe'), (29, 'BA', 'Bahia'),
    (31, 'MG', 'Minas Gerais'), (32, 'ES', 'Espírito Santo'), (33, 'RJ', 'Rio de Janeiro'),
    (35, 'SP', 'São Paulo'), (41, 'PR', 'Paraná'), (42, 'SC', 'Santa Catarina'),
    (43, 'RS', 'Rio Grande do Sul'), (50, 'MS', 'Mato Grosso do Sul'), (51, 'MT', 'Mato Grosso'),
    (52, 'GO', 'Goiás'), (53, 'DF', 'Distrito Federal');

CREATE TABLE ref.municipio (
    cd_mun       integer       PRIMARY KEY CHECK (cd_mun BETWEEN 1100000 AND 5399999),
    nome         text          NOT NULL,
    cd_uf        smallint      NOT NULL REFERENCES ref.uf,
    area_km2     numeric(10,3) NOT NULL CHECK (area_km2 > 0),
    area_estudo  boolean       NOT NULL DEFAULT true,
    geom         geometry(MultiPolygon, 4674) NOT NULL CHECK (ST_IsValid(geom)),
    -- Derivado da geometria: calculado pelo banco, nunca diverge do polígono
    centroide    geometry(Point, 4674) GENERATED ALWAYS AS (ST_Centroid(geom)) STORED,
    carga_id     integer       NOT NULL REFERENCES ref.carga,
    -- Os dois primeiros dígitos do código IBGE do município são o código da UF
    CONSTRAINT municipio_uf_coerente CHECK (cd_mun / 100000 = cd_uf),
    CONSTRAINT municipio_nome_uf_unico UNIQUE (cd_uf, nome)
);
COMMENT ON TABLE ref.municipio IS 'Municípios carregados do shapefile da área de estudo (SIRGAS 2000)';
COMMENT ON COLUMN ref.municipio.area_km2 IS 'Área oficial do IBGE';
COMMENT ON COLUMN ref.municipio.area_estudo IS 'Falso para municípios carregados mas fora da área de estudo definida';

-- Índice espacial: base dos cruzamentos ponto-polígono das próximas fases (focos, PRODES)
CREATE INDEX municipio_geom_gix ON ref.municipio USING gist (geom);
CREATE INDEX municipio_cd_uf_idx ON ref.municipio (cd_uf);

-- Visão usada pelo app: municípios da área de estudo com UF e coordenadas do centroide
CREATE VIEW ref.vw_municipio AS
SELECT m.cd_mun,
       m.nome,
       u.sigla           AS sigla_uf,
       m.area_km2,
       ST_Y(m.centroide) AS latitude,
       ST_X(m.centroide) AS longitude
FROM ref.municipio m
JOIN ref.uf u USING (cd_uf)
WHERE m.area_estudo;
