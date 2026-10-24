#!/usr/bin/env bash
# Menjalankan script menggunakan Bash.
# Baris ini disebut shebang; sistem akan memilih interpreter Bash.
set -euo pipefail
# Mengaktifkan mode aman:
# -e: script berhenti jika ada command yang gagal.
# -u: error jika memakai variabel yang belum didefinisikan.
# pipefail: error di dalam pipeline command tidak disembunyikan.

# Menentukan folder utama project, yaitu satu level di atas folder script ini.
# dirname "$0" mengambil lokasi file run_pipeline.sh.
# cd ... berpindah sementara ke folder tersebut.
# pwd mengubahnya menjadi absolute path.
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Berpindah ke root project agar semua path berikutnya konsisten.
cd "$ROOT_DIR"

# Menjalankan proses Extract dan Load menggunakan Python.
# Script ini mengambil data dari source lalu memuatnya ke database.
python3 pertemuan-5/etl_orders.py

# Mengecek apakah command dbt tersedia langsung di PATH sistem.
# Output dan error dari pengecekan dibuang karena hanya status exit code yang dibutuhkan.
if command -v dbt >/dev/null 2>&1; then
  # Jika dbt tersedia sebagai command langsung, gunakan command tersebut.
  DBT=(dbt)
else
  # Jika command dbt tidak tersedia, jalankan dbt sebagai module Python.
  DBT=(python3 -m dbt.cli.main)
fi

# Masuk ke folder project dbt hanya untuk command di dalam tanda kurung.
# dbt run menjalankan semua model dbt yang aktif di project.
# --profiles-dir . memberi tahu dbt bahwa profiles.yml berada di folder saat ini.
# Operator && memastikan dbt test hanya dijalankan jika dbt run berhasil.
# dbt test menjalankan seluruh test dbt yang aktif.
(cd pertemuan-5/dbt_project && "${DBT[@]}" run --profiles-dir . && "${DBT[@]}" test --profiles-dir .)

# Menjalankan verifikasi akhir pipeline.
# Script ini memeriksa hasil Extract/Load dan memastikan mart dbt berisi data.
python3 pertemuan-5/verify_pipeline.py
