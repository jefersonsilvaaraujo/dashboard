-- Inventário reproduzível. Executar com psql -X -v ON_ERROR_STOP=1.
-- Nenhuma carga/migração é chamada. Mesmo o administrador fica em READ ONLY.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL statement_timeout = '60s';
\pset pager off
\echo RELACOES
SELECT n.nspname AS esquema, c.relname, c.relkind,
       c.reltuples::bigint AS estimativa, pg_get_userbyid(c.relowner) AS proprietario
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname IN ('ref','mapbiomas','queimadas','prodes','analise','public')
  AND c.relkind IN ('r','v','m') ORDER BY 1,2;
\echo COLUNAS_COL9
SELECT table_schema,table_name,column_name,data_type,udt_name,is_nullable,numeric_precision,numeric_scale
FROM information_schema.columns
WHERE table_name IN ('cobertura_col9_255','municipio_col9_255','vw_cobertura_col9_255','vw_municipios_col9_255')
ORDER BY 1,2,ordinal_position;
\echo DEFINICOES_COL9
SELECT schemaname,viewname,definition FROM pg_views
WHERE viewname IN ('vw_cobertura_col9_255','vw_municipios_col9_255');
\echo CONSTRAINTS_COL9
SELECT conrelid::regclass AS objeto,conname,pg_get_constraintdef(oid) AS definicao
FROM pg_constraint WHERE conrelid IN ('ref.municipio_col9_255'::regclass,'mapbiomas.cobertura_col9_255'::regclass);
\echo INDICES
SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes
WHERE schemaname IN ('ref','mapbiomas','queimadas','prodes','analise') ORDER BY 1,2,3;
\echo DEPENDENCIAS_VIEWS
SELECT DISTINCT nv.nspname||'.'||v.relname AS dependente, nt.nspname||'.'||t.relname AS origem
FROM pg_rewrite r JOIN pg_class v ON v.oid=r.ev_class
JOIN pg_namespace nv ON nv.oid=v.relnamespace
JOIN pg_depend d ON d.classid='pg_rewrite'::regclass AND d.objid=r.oid AND d.refclassid='pg_class'::regclass
JOIN pg_class t ON t.oid=d.refobjid JOIN pg_namespace nt ON nt.oid=t.relnamespace
WHERE nv.nspname IN ('ref','mapbiomas','queimadas','prodes','analise')
AND v.relkind IN ('v','m') AND t.oid<>v.oid ORDER BY 1,2;
\echo PAPEIS_SEM_SEGREDOS
SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolcanlogin,rolconfig
FROM pg_roles WHERE rolname LIKE 'dashboard%' ORDER BY 1;
SELECT pg_get_userbyid(member) AS membro,pg_get_userbyid(roleid) AS grupo FROM pg_auth_members
WHERE pg_get_userbyid(member) LIKE 'dashboard%';
\echo PERMISSOES
SELECT r.rolname,n.nspname||'.'||c.relname AS objeto,
has_schema_privilege(r.oid,n.oid,'USAGE') AS uso_schema,
has_table_privilege(r.oid,c.oid,'SELECT') AS leitura,
has_table_privilege(r.oid,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE') AS alguma_escrita
FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE r.rolname IN ('dashboard_app','dashboard_leitura')
AND n.nspname IN ('ref','mapbiomas','queimadas','prodes','analise') AND c.relkind IN ('r','v','m') ORDER BY 1,2;
\echo MIGRACOES
TABLE public.migracao;
\echo ACEITE_COL9
SELECT count(*) AS linhas,count(DISTINCT cd_mun) AS municipios,count(DISTINCT ano) AS anos,
min(ano) AS inicio,max(ano) AS fim,count(DISTINCT sigla_uf) AS ufs FROM mapbiomas.vw_cobertura_col9_255;
SELECT cd_mun,ano,classe_cobertura,count(*) FROM mapbiomas.cobertura_col9_255 GROUP BY 1,2,3 HAVING count(*)>1;
SELECT m.cd_mun,a.ano FROM ref.municipio_col9_255 m CROSS JOIN generate_series(1985,2023) a(ano)
LEFT JOIN (SELECT DISTINCT cd_mun,ano FROM mapbiomas.cobertura_col9_255) c USING(cd_mun,ano) WHERE c.cd_mun IS NULL;
SELECT count(*) AS municipios,count(*) FILTER(WHERE area_estudo) AS selecionados FROM ref.municipio;
SELECT sigla_uf,count(*) FROM ref.municipio_col9_255 GROUP BY 1 ORDER BY 1;
SELECT ST_SRID(geom),GeometryType(geom),ST_IsValid(geom),count(*) FROM ref.municipio_col9_255 GROUP BY 1,2,3;
SELECT 'entrada' AS diferenca,n.cd_mun FROM ref.municipio_col9_255 n LEFT JOIN ref.municipio l USING(cd_mun) WHERE l.cd_mun IS NULL
UNION ALL SELECT 'saida',l.cd_mun FROM ref.municipio l LEFT JOIN ref.municipio_col9_255 n USING(cd_mun) WHERE n.cd_mun IS NULL ORDER BY 1,2;
\echo FONTES_COMPLEMENTARES
SELECT 'cobertura_legada' AS fonte,count(*) AS linhas,count(DISTINCT cd_mun) AS municipios,min(ano),max(ano) FROM mapbiomas.vw_cobertura_municipio
UNION ALL SELECT 'focos_mensais',count(*),count(DISTINCT cd_mun),min(ano),max(ano) FROM queimadas.vw_focos_municipio_mes
UNION ALL SELECT 'prodes',count(*),count(DISTINCT cd_mun),min(ano),max(ano) FROM prodes.vw_area_classe_municipio
UNION ALL SELECT 'painel_legado',count(*),count(DISTINCT cd_mun),min(ano),max(ano) FROM analise.vw_painel_municipio_ano;
WITH fontes AS (
SELECT 'prodes' AS fonte,cd_mun FROM prodes.area_classe GROUP BY cd_mun
UNION ALL SELECT 'queimadas',cd_mun FROM queimadas.mv_focos_municipio_mes GROUP BY cd_mun)
SELECT f.fonte,count(*) AS presentes_nos_255 FROM fontes f JOIN ref.municipio_col9_255 m USING(cd_mun) GROUP BY 1;
SELECT n.cd_mun,n.nm_mun,
EXISTS(SELECT 1 FROM prodes.area_classe p WHERE p.cd_mun=n.cd_mun) AS tem_prodes,
EXISTS(SELECT 1 FROM queimadas.mv_focos_municipio_mes q WHERE q.cd_mun=n.cd_mun) AS tem_focos
FROM ref.municipio_col9_255 n WHERE cd_mun IN (2101772,2108504,2112274,5101837) ORDER BY 1;
\echo LEGENDA_ATUAL_SEM_HOMOLOGACAO
SELECT DISTINCT c.classe_cobertura,k.nome,k.grupo,k.tipo,k.cor FROM mapbiomas.cobertura_col9_255 c
LEFT JOIN mapbiomas.classe k ON k.classe_id=c.classe_cobertura ORDER BY 1;
\echo EXPLAIN_SEM_EXECUTAR
EXPLAIN SELECT * FROM mapbiomas.vw_cobertura_col9_255 WHERE cd_mun=2102325 AND ano BETWEEN 2001 AND 2003;
EXPLAIN SELECT * FROM analise.vw_painel_municipio_ano WHERE cd_mun=2102325 AND ano BETWEEN 2001 AND 2003;
ROLLBACK;
