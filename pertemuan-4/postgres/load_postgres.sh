#!/usr/bin/env bash
# Usage: ./load_postgres.sh "postgresql://postgresdev:adminpass123@localhost:5433/nusacode_db" [out_dir]
set -euo pipefail
DSN="${1:?dsn required}"
DIR="${2:-out}"
DIR="$(cd "$DIR" && pwd)"

psql "$DSN" -v ON_ERROR_STOP=1 -f ddl/postgres.sql

TABLES=(locations entity_types entities users activities material_types material_units
        materials entity_activities batches stocks order_types order_statuses
        delivery_types orders order_items transaction_types transaction_reasons transactions)

for t in "${TABLES[@]}"; do
  echo "loading $t"
  psql "$DSN" -v ON_ERROR_STOP=1 -c \
    "\copy bootcamp.$t FROM '$DIR/$t.csv' WITH (FORMAT csv, HEADER true, NULL '')"
done
echo "done"
