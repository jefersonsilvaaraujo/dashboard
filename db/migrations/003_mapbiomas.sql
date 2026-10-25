-- MapBiomas: legenda das classes e cobertura por município, ano e classe.

CREATE TABLE mapbiomas.classe (
    classe_id  smallint PRIMARY KEY CHECK (classe_id BETWEEN 0 AND 255),
    nome       text     NOT NULL UNIQUE,
    cor        char(7)  NOT NULL CHECK (cor ~ '^#[0-9a-f]{6}$'),
    grupo      text     NOT NULL,
    tipo       text     NOT NULL CHECK (tipo IN ('Natural', 'Antrópico', 'Natural ou Antrópico', 'Não observado')),
    carga_id   integer  NOT NULL REFERENCES ref.carga
);
COMMENT ON TABLE mapbiomas.classe IS 'Legenda oficial da coleção (nome, cor, grupo de nível 1 e tipo natural/antrópico)';

-- Tabela de fatos: uma linha por município, ano e classe com área > 0.
-- O percentual de ocupação não é armazenado; é derivado na view a partir da área do município.
CREATE TABLE mapbiomas.cobertura (
    cd_mun     integer          NOT NULL REFERENCES ref.municipio,
    ano        smallint         NOT NULL CHECK (ano BETWEEN 1985 AND 2100),
    classe_id  smallint         NOT NULL REFERENCES mapbiomas.classe,
    area_ha    double precision NOT NULL CHECK (area_ha > 0),
    carga_id   integer          NOT NULL REFERENCES ref.carga,
    PRIMARY KEY (cd_mun, ano, classe_id)
);
COMMENT ON TABLE mapbiomas.cobertura IS 'Área (ha) de cada classe por município e ano';

-- A chave primária atende às consultas por município; este índice atende às consultas
-- por classe ao longo dos anos (ex.: área urbanizada por estado) e à chave estrangeira.
CREATE INDEX cobertura_classe_ano_idx ON mapbiomas.cobertura (classe_id, ano);
CREATE INDEX cobertura_carga_idx ON mapbiomas.cobertura (carga_id);

-- Visão lida pelo app, no mesmo formato do antigo estatisticas_coverage_historico.csv
CREATE VIEW mapbiomas.vw_cobertura_municipio AS
SELECT c.cd_mun,
       m.nome                                AS nm_mun,
       u.sigla                               AS sigla_uf,
       c.ano,
       c.classe_id                           AS classe_cobertura,
       c.area_ha,
       c.area_ha / m.area_km2::double precision AS perc_ocupacao  -- (ha / (km² * 100)) * 100
FROM mapbiomas.cobertura c
JOIN ref.municipio m USING (cd_mun)
JOIN ref.uf u USING (cd_uf)
WHERE m.area_estudo;
