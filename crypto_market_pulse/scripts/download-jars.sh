#!/usr/bin/env bash
# Downloads the PostgreSQL JDBC driver needed by PySpark to write to PostgreSQL.
set -e

JAR_DIR="$(dirname "$0")/../spark/jars"
JAR_FILE="$JAR_DIR/postgresql-42.7.1.jar"
JAR_URL="https://jdbc.postgresql.org/download/postgresql-42.7.1.jar"

mkdir -p "$JAR_DIR"

if [ -f "$JAR_FILE" ]; then
    echo "JDBC driver already present: $JAR_FILE"
    exit 0
fi

echo "Downloading PostgreSQL JDBC driver..."
curl -fsSL --ssl-no-revoke -o "$JAR_FILE" "$JAR_URL"
echo "Saved to $JAR_FILE"
