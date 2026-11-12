-- Extensões, esquemas e permissões padrão.
-- Esquemas por tema: ref (referência espacial e controle de cargas) e um por fonte de dados.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS ref;
COMMENT ON SCHEMA ref IS 'Dados de referência (UF, municípios) e controle das cargas de dados';

CREATE SCHEMA IF NOT EXISTS mapbiomas;
COMMENT ON SCHEMA mapbiomas IS 'Cobertura e uso da terra - MapBiomas';

-- Grupo somente leitura usado pelo app (criado também em db/init no primeiro start)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'dashboard_leitura') THEN
        CREATE ROLE dashboard_leitura NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA ref, mapbiomas TO dashboard_leitura;

-- Tabelas e views criadas daqui em diante ficam legíveis para o grupo
ALTER DEFAULT PRIVILEGES IN SCHEMA ref, mapbiomas GRANT SELECT ON TABLES TO dashboard_leitura;
