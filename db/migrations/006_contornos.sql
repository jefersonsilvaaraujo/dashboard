-- Contornos dos municípios e da área de estudo para desenho em mapas web.
-- A geometria original (até ~80 mil vértices por município, 1,7 milhão no total) é pesada
-- demais para enviar ao navegador; aqui ficam versões simplificadas, derivadas pelo banco.

-- Escala municipal: tolerância de 0,0005° (~55 m), imperceptível num município inteiro.
-- Coluna gerada: recalculada pelo banco sempre que a geometria original muda.
ALTER TABLE ref.municipio
    ADD COLUMN geom_simplificada geometry(MultiPolygon, 4674)
    GENERATED ALWAYS AS (ST_Multi(ST_SimplifyPreserveTopology(geom, 0.0005))) STORED;

COMMENT ON COLUMN ref.municipio.geom_simplificada IS 'Geometria simplificada (tolerância 0,0005°) para desenho em mapas';

-- Contornos em GeoJSON nas escalas municipal e regional (0,004°, ~450 m), com o
-- retângulo envolvente para enquadrar o mapa e escolher os municípios vizinhos
CREATE VIEW ref.vw_municipio_contorno AS
SELECT m.cd_mun,
       m.nome,
       u.sigla                                                               AS sigla_uf,
       ST_AsGeoJSON(m.geom_simplificada, 5)                                  AS geojson,
       ST_AsGeoJSON(ST_SimplifyPreserveTopology(m.geom_simplificada, 0.004), 4) AS geojson_regional,
       ST_XMin(m.geom) AS lon_min, ST_YMin(m.geom) AS lat_min,
       ST_XMax(m.geom) AS lon_max, ST_YMax(m.geom) AS lat_max
FROM ref.municipio m
JOIN ref.uf u USING (cd_uf)
WHERE m.area_estudo;

-- Limite externo da área de estudo. A união leva alguns segundos, por isso é materializada
-- e recalculada a cada carga de municípios. Mantém só o anel externo de cada parte
-- (as frestas entre municípios vizinhos viram buracos na união) e descarta partes < 1 km².
CREATE MATERIALIZED VIEW ref.mv_area_estudo_contorno AS
WITH uniao AS (
    SELECT ST_Union(geom) AS geom FROM ref.municipio WHERE area_estudo
), partes AS (
    SELECT ST_MakePolygon(ST_ExteriorRing((ST_Dump(geom)).geom)) AS geom FROM uniao
)
SELECT ST_AsGeoJSON(ST_SimplifyPreserveTopology(ST_Collect(geom), 0.004), 4) AS geojson,
       ST_XMin(ST_Collect(geom)) AS lon_min, ST_YMin(ST_Collect(geom)) AS lat_min,
       ST_XMax(ST_Collect(geom)) AS lon_max, ST_YMax(ST_Collect(geom)) AS lat_max
FROM partes
WHERE ST_Area(geom::geography) > 1e6;

COMMENT ON MATERIALIZED VIEW ref.mv_area_estudo_contorno IS 'Limite externo da área de estudo (GeoJSON simplificado)';
