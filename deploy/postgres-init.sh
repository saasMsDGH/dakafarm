#!/bin/sh
set -eu
# psql lit le mot de passe depuis l'environnement : aucun secret en argument.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<'SQL'
\getenv app_password DAKAFARM_DB_PASSWORD
SELECT format('CREATE ROLE dakafarm LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_password') \gexec
CREATE DATABASE dakafarm OWNER dakafarm;
SQL
