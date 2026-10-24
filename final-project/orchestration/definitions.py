"""Dagster orchestration for the YouTube Trending final project."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import clickhouse_connect
from dagster import (
    DefaultScheduleStatus,
    Definitions,
    In,
    Out,
    RetryPolicy,
    ScheduleDefinition,
    job,
    op,
)


PROJECT_DIR = Path(__file__).resolve().parents[1]
DBT_DIR = PROJECT_DIR / "dbt"
RETRY_POLICY = RetryPolicy(max_retries=2, delay=10)


def run_command(context, command):
    """Run a command while forwarding stdout and stderr to Dagster logs."""
    context.log.info("Running: %s", " ".join(command))
    process = subprocess.Popen(
        command,
        cwd=PROJECT_DIR,
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    if process.stdout:
        for line in process.stdout:
            context.log.info(line.rstrip())
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"Command failed with exit code {return_code}: {' '.join(command)}")


def dbt_command(*arguments):
    executable = shutil.which("dbt")
    if executable:
        return [executable, *arguments]
    return [sys.executable, "-m", "dbt.cli.main", *arguments]


@op(out=Out(str), retry_policy=RETRY_POLICY, tags={"layer": "bronze"})
def load_bronze(context):
    """Extract CSV sources and load all columns as String into bronze.raw_* tables."""
    run_command(context, [sys.executable, str(PROJECT_DIR / "ingestion" / "load_clickhouse.py")])
    context.add_output_metadata({"database": "bronze", "source": "CSV files"})
    return "bronze_loaded"


@op(ins={"upstream": In(str)}, out=Out(str), retry_policy=RETRY_POLICY, tags={"layer": "silver"})
def build_silver(context, upstream):
    """Run dbt cleaning, type conversion, WIB conversion, and category enrichment."""
    context.log.info("Upstream status: %s", upstream)
    run_command(
        context,
        dbt_command(
            "run",
            "--project-dir",
            str(DBT_DIR),
            "--profiles-dir",
            str(DBT_DIR),
            "--select",
            "path:models/silver",
        ),
    )
    context.add_output_metadata({"database": "silver", "models": 2})
    return "silver_built"


@op(ins={"upstream": In(str)}, out=Out(str), retry_policy=RETRY_POLICY, tags={"layer": "gold"})
def build_gold(context, upstream):
    """Build dashboard-ready marts in the ClickHouse gold database."""
    context.log.info("Upstream status: %s", upstream)
    run_command(
        context,
        dbt_command(
            "run",
            "--project-dir",
            str(DBT_DIR),
            "--profiles-dir",
            str(DBT_DIR),
            "--select",
            "path:models/gold",
        ),
    )
    context.add_output_metadata({"database": "gold", "models": 5})
    return "gold_built"


@op(ins={"upstream": In(str)}, out=Out(str), retry_policy=RETRY_POLICY, tags={"quality": "dbt"})
def run_data_tests(context, upstream):
    """Run source and model data-quality tests after all transformations finish."""
    context.log.info("Upstream status: %s", upstream)
    run_command(
        context,
        dbt_command(
            "test",
            "--project-dir",
            str(DBT_DIR),
            "--profiles-dir",
            str(DBT_DIR),
        ),
    )
    return "tests_passed"


@op(ins={"upstream": In(str)}, tags={"quality": "warehouse"})
def validate_warehouse(context, upstream):
    """Validate row flow and ensure every dashboard mart contains data."""
    context.log.info("Upstream status: %s", upstream)
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "18123")),
        username=os.getenv("CLICKHOUSE_USER", "clickhousedev"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "adminpass123"),
    )

    tables = {
        "bronze.raw_youtube_trending": None,
        "silver.stg_youtube_trending": None,
        "gold.mart_daily_category_trends": None,
        "gold.mart_monthly_content_trends": None,
        "gold.mart_channel_trends": None,
        "gold.mart_seasonal_trends": None,
        "gold.mart_content_performance": None,
    }
    for table in tables:
        tables[table] = client.query(f"SELECT count() FROM {table}").result_rows[0][0]

    source_rows = tables["bronze.raw_youtube_trending"]
    if source_rows != tables["silver.stg_youtube_trending"]:
        raise RuntimeError("Bronze and silver row counts do not match")
    if source_rows != tables["gold.mart_content_performance"]:
        raise RuntimeError("Silver and content performance row counts do not match")
    empty_tables = [table for table, count in tables.items() if count == 0]
    if empty_tables:
        raise RuntimeError(f"Empty warehouse tables: {', '.join(empty_tables)}")

    context.add_output_metadata(tables)
    context.log.info("Warehouse validation passed for %s source rows", source_rows)


@job(description="Orchestrates the YouTube Trending ELT pipeline from CSV to gold marts.")
def youtube_trending_elt_job():
    validate_warehouse(run_data_tests(build_gold(build_silver(load_bronze()))))


daily_youtube_trending_schedule = ScheduleDefinition(
    name="daily_youtube_trending_schedule",
    job=youtube_trending_elt_job,
    cron_schedule="0 2 * * *",
    execution_timezone="Asia/Jakarta",
    default_status=DefaultScheduleStatus.STOPPED,
)


defs = Definitions(
    jobs=[youtube_trending_elt_job],
    schedules=[daily_youtube_trending_schedule],
)


if __name__ == "__main__":
    print("Dagster definitions loaded:", youtube_trending_elt_job.name)
