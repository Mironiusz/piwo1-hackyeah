#!/bin/sh
set -eu
psql --no-psqlrc --set ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres --set owner_name="$DATABASE_OWNER_USER" --set owner_password="$DATABASE_OWNER_PASSWORD" --set service_name="$DATABASE_SERVICE_USER" --set service_password="$DATABASE_SERVICE_PASSWORD" --set database_name="$DATABASE_NAME" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN SUPERUSER PASSWORD %L', :'owner_name', :'owner_password') \gexec
SELECT format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L', :'service_name', :'service_password') \gexec
SELECT format('CREATE DATABASE %I OWNER %I TEMPLATE template0 ENCODING %L LOCALE_PROVIDER builtin LOCALE %L', :'database_name', :'owner_name', 'UTF8', 'C.UTF-8') \gexec
SQL
