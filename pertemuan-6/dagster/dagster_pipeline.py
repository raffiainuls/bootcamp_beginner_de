"""Dagster wrapper untuk pipeline ELT Pertemuan 5."""
from pathlib import Path
import subprocess
import sys

from dagster import (
    AssetExecutionContext,
    Definitions,
    MaterializeResult,
    asset,
    define_asset_job,
    schedule,
)

ROOT = Path(__file__).resolve().parents[2]


@asset(description="Menjalankan Extract, Load, Transform, dan verifikasi Pertemuan 5")
def elt_pipeline(context: AssetExecutionContext):
    result = subprocess.run(
        ["bash", str(ROOT / "pertemuan-5" / "run_pipeline.sh")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError("Pipeline ELT gagal")
    return MaterializeResult(metadata={"status": "success"})


elt_job = define_asset_job(
    name="elt_pipeline_job",
    selection="elt_pipeline",
)


@schedule(
    cron_schedule="*/5 * * * *",
    job=elt_job,
    execution_timezone="Asia/Jakarta",
)
def elt_pipeline_schedule(_context):
    # Schedule mengembalikan run config biasa; asset dipilih oleh elt_job.
    return {}


defs = Definitions(
    assets=[elt_pipeline],
    jobs=[elt_job],
    schedules=[elt_pipeline_schedule],
)

if __name__ == "__main__" and "--test" in sys.argv:
    print("Definisi Dagster berhasil di-import:", defs)

