#!/usr/bin/env bash
set -e

# Create the application database (airflow DB already created by POSTGRES_DB env var)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    CREATE DATABASE crypto_pulse OWNER $POSTGRES_USER;
SQL

# Create Silver and Gold schemas inside crypto_pulse
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "crypto_pulse" <<-SQL
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;

    GRANT ALL PRIVILEGES ON SCHEMA silver TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA gold   TO $POSTGRES_USER;
SQL

echo "crypto_pulse database initialized with silver and gold schemas."
