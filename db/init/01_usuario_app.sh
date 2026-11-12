#!/bin/bash
# Executado pelo container do PostgreSQL apenas na criação do banco (volume vazio).
# Cria o usuário de login do app, somente leitura, membro do grupo dashboard_leitura.
# As permissões do grupo sobre as tabelas são concedidas pelas migrações (db/migrations).
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
     -v app_usuario="$APP_DB_USER" -v app_senha="$APP_DB_PASSWORD" <<'EOSQL'
CREATE ROLE dashboard_leitura NOLOGIN;
CREATE ROLE :"app_usuario" LOGIN PASSWORD :'app_senha' IN ROLE dashboard_leitura;

-- Mesmo que o código do app tente escrever, o banco recusa
ALTER ROLE :"app_usuario" SET default_transaction_read_only = on;
-- Nenhuma consulta do painel deve demorar; interrompe consultas presas
ALTER ROLE :"app_usuario" SET statement_timeout = '30s';
EOSQL
