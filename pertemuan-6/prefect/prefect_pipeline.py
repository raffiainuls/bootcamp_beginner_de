"""Prefect wrapper untuk pipeline ELT Pertemuan 5."""
from pathlib import Path
import subprocess
import sys

from prefect import flow, task

ROOT = Path(__file__).resolve().parents[2]


@task(retries=1, retry_delay_seconds=10, log_prints=True)
def run_elt_pipeline() -> str:
    result = subprocess.run(
        ["bash", str(ROOT / "pertemuan-5" / "run_pipeline.sh")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Pipeline ELT gagal")
    return "success"


@flow(name="pertemuan-6-elt", log_prints=True)
def elt_flow() -> str:
    return run_elt_pipeline()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        elt_flow.serve(
            name="pertemuan-6-elt",
            cron="*/15 * * * *",
            pause_on_shutdown=False,
        )
    else:
        print(elt_flow())

