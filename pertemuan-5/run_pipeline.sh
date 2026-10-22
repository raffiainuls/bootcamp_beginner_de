#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
python3 pertemuan-5/etl_orders.py
if command -v dbt >/dev/null 2>&1; then
  DBT=(dbt)
else
  DBT=(python3 -m dbt.cli.main)
fi
(cd pertemuan-5/dbt_project && "${DBT[@]}" run --profiles-dir . && "${DBT[@]}" test --profiles-dir .)
python3 pertemuan-5/verify_pipeline.py
