#!/bin/sh
set -eu

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
    -v schema_owner_name="$DB_SCHEMA_OWNER_NAME" \
    -v schema_owner_password="$DB_SCHEMA_OWNER_PASSWORD" \
    -v service_account_name="$DB_SERVICE_ACCOUNT_NAME" \
    -v service_account_password="$DB_SERVICE_ACCOUNT_PASSWORD" \
    -v database_name="$DB_NAME" <<'SQL'
CREATE ROLE :"schema_owner_name" LOGIN SUPERUSER PASSWORD :'schema_owner_password';
CREATE ROLE :"service_account_name" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'service_account_password';
CREATE DATABASE :"database_name" OWNER :"schema_owner_name" TEMPLATE template0 ENCODING 'UTF8' LOCALE_PROVIDER builtin LOCALE 'C.UTF-8';
SQL
