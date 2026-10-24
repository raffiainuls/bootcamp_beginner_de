# Pertemuan 6 — Orkestrasi Pipeline ELT

## Slide presentasi

- [Pertemuan 6 — Automation, Scheduling, dan Orchestration](./slides/Pertemuan-6-Automation-Scheduling-dan-Orchestration.pptx)

Slide membahas konsep automation, cron dan timezone, perbandingan Dagster–Prefect–Kestra, demo pipeline Pertemuan 5, verifikasi hasil, dan latihan mandiri.

## Tujuan pertemuan

Pada Pertemuan 5 kita sudah membuat pipeline ELT:

```text
PostgreSQL --Extract--> Python --Load--> ClickHouse staging --Transform--> dbt --> datamart
```

Pada pertemuan ini pipeline tersebut dijalankan oleh tiga orchestration tool:

| Tool | Gaya workflow | UI | Dokumentasi |
|---|---|---|---|
| Dagster | Asset-oriented | http://localhost:3000 | [README Dagster](./dagster/README.md) |
| Prefect | Python flow dan deployment | http://localhost:4200 | [README Prefect](./prefect/README.md) |
| Kestra | YAML flow dan task runner | http://localhost:8080 | [README Kestra](./kestra/README.md) |

Semua orchestration dijalankan menggunakan Docker. Python, dbt, server, daemon, dan flow runner tidak perlu di-install di host.

## Gambaran besar: apa yang di-orchestrate?

Orchestrator pada pertemuan ini tidak menggantikan kode ETL dan dbt dari Pertemuan 5. Orchestrator bertugas mengatur kapan pipeline dijalankan, menjalankan command, menyimpan status run, menampilkan log, dan menjalankan schedule.

Pipeline inti tetap berada di file berikut:

    pertemuan-5/etl_orders.py       Extract PostgreSQL lalu Load ke ClickHouse
    pertemuan-5/dbt_project/        Transformasi dbt
    pertemuan-5/verify_pipeline.py  Verifikasi jumlah baris dan datamart
    pertemuan-5/run_pipeline.sh     Urutan eksekusi ketiga bagian di atas

Alur eksekusi akhirnya adalah:

    Scheduler/UI orchestrator
              | memicu run
              v
    Wrapper orchestrator (Dagster asset / Prefect flow / Kestra task)
              | memanggil
              v
    bash pertemuan-5/run_pipeline.sh
              |
              +--> python3 pertemuan-5/etl_orders.py
              +--> dbt run
              +--> dbt test
              +--> python3 pertemuan-5/verify_pipeline.py
              |
              v
    PostgreSQL -> ClickHouse raw -> dbt datamart

Jadi dagster_pipeline.py, prefect_pipeline.py, dan elt_pipeline.yml adalah definisi orkestrasi/wrapper. Ketiganya tidak berisi ulang logic Extract, Load, dan Transform; ketiganya memanggil pipeline Pertemuan 5.

## Kapan file masuk ke Docker?

Pada Dagster dan Prefect, file masuk ke image ketika command docker compose up --build -d dijalankan. Compose memakai root repository sebagai build context, lalu Dockerfile menjalankan COPY . /workspace. Akibatnya folder pertemuan-5 dan pertemuan-6 tersedia di dalam container.

    docker compose up --build
            |
            +--> Docker membaca Dockerfile
            +--> COPY . /workspace
            +--> install requirements dan dependency orchestrator
            +--> membuat image
            +--> menjalankan command service

Pada Kestra ada dua tahap berbeda:

1. docker compose up -d menjalankan server/UI Kestra.
2. docker build ... pertemuan-6/kestra/Dockerfile membuat image runner yang berisi kode pipeline.
3. Flow YAML di-import ke UI Kestra.
4. Saat flow dijalankan, Kestra memakai Docker socket untuk membuat container dari image runner tersebut.
5. Container runner menjalankan bash pertemuan-5/run_pipeline.sh.

Karena itu Kestra memiliki container server dan container task runner yang dibuat saat execution.

## Mengapa pipeline bisa mengakses database?

PostgreSQL dan ClickHouse dari Pertemuan 5 berjalan di Docker Compose terpisah dan port-nya dipublish ke host. Container orchestrator tidak memakai localhost untuk menuju database host. Environment variable diarahkan ke host.docker.internal:

    container orchestrator --host.docker.internal:5433--> PostgreSQL host
    container orchestrator --host.docker.internal:8123--> ClickHouse host

localhost dari dalam container berarti container itu sendiri, bukan laptop dan bukan container database Pertemuan 5.

## Aturan praktik agar resource tidak membengkak

Setiap orchestrator memiliki server, scheduler/daemon, volume metadata, dan image/container sendiri. Menjalankan semuanya sekaligus membuat laptop lebih berat dan dapat menimbulkan konflik port. Karena itu urutannya adalah: nyalakan database, praktikkan satu orchestrator, jalankan verifikasi, lalu docker compose down sebelum pindah ke orchestrator berikutnya.

## Jika ada update kode

Pada setup ini source code tidak di-mount langsung dari laptop ke container. Kode dimasukkan ke image melalui `COPY . /workspace`. Karena itu, perubahan kode tidak otomatis terlihat oleh container yang sedang berjalan.

Gunakan aturan umum berikut:

| Yang diubah | Tindakan |
|---|---|
| Python, shell, SQL, atau dbt model | Build ulang image lalu jalankan kembali service |
| Dockerfile atau `requirements.txt` | Build ulang image; gunakan `--no-cache` jika dependency lama masih terpakai |
| `docker-compose.yml` | Jalankan `up -d` kembali agar konfigurasi diterapkan |
| Volume metadata | Tidak perlu dihapus untuk update kode |
| Database Pertemuan 5 | Kelola dengan Compose Pertemuan 5 secara terpisah |

Jangan langsung memakai `docker compose down -v`. Opsi `-v` menghapus volume metadata orchestrator dan dapat menghilangkan riwayat run, flow, atau konfigurasi yang tersimpan.

Detail per orchestrator tersedia pada bagian update di masing-masing README.

Jalankan hanya satu orchestrator pada satu waktu:

1. Pastikan PostgreSQL dan ClickHouse Pertemuan 5 hidup.
2. Ikuti satu README tool sampai selesai.
3. Jalankan manual run dan verifikasi hasilnya.
4. Matikan tool dengan perintah cleanup di README tersebut.
5. Baru lanjut ke tool berikutnya.

Jangan menjalankan Dagster, Prefect, dan Kestra bersamaan.

## Persiapan bersama

Dari root repository:

```bash
cd bootcamp_beginner_de
docker --version
docker compose version
```

Docker Desktop harus sedang aktif. Pastikan port ini tersedia:

- `3000`: Dagster
- `4200`: Prefect
- `5433`: PostgreSQL Pertemuan 5
- `8080`: Kestra
- `8123`: ClickHouse Pertemuan 5

Cek port jika diperlukan:

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:4200 -sTCP:LISTEN
lsof -nP -iTCP:8080 -sTCP:LISTEN
lsof -nP -iTCP:5433 -sTCP:LISTEN
lsof -nP -iTCP:8123 -sTCP:LISTEN
```

## Menyiapkan database Pertemuan 5

Jalankan database sumber dan target:

```bash
docker compose -f pertemuan-5/docker-compose.yml up -d
docker compose -f pertemuan-5/docker-compose.yml ps
```

Jika database Pertemuan 5 baru dibuat, muat data PostgreSQL:

```bash
python3 pertemuan-4/postgres/load_to_postgres.py \
  --host localhost --port 5433 --user postgresdev --password adminpass123 \
  --dbname nusacode_db --schema bootcamp
```

Uji pipeline tanpa orchestrator:

```bash
bash pertemuan-5/run_pipeline.sh
```

Pipeline siap jika output terakhir berisi `VERIFIKASI BERHASIL`.

## Urutan praktik

1. Baca [README Dagster](./dagster/README.md), lalu matikan:
   ```bash
   docker compose -f pertemuan-6/dagster/docker-compose.yml down
   ```
2. Baca [README Prefect](./prefect/README.md), lalu matikan:
   ```bash
   docker compose -f pertemuan-6/prefect/docker-compose.yml down
   ```
3. Baca [README Kestra](./kestra/README.md), lalu matikan:
   ```bash
   docker compose -f pertemuan-6/kestra/docker-compose.yml down
   ```

## Verifikasi data bersama

```bash
docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query 'SELECT count() FROM datamart.mart_daily_orders'
```

Hasil tidak boleh nol.

## Output peserta

Untuk setiap tool, kumpulkan screenshot UI, satu run manual sukses, bukti log Python/dbt/verifikasi, bukti scheduler aktif, dan catatan cleanup.

## Troubleshooting umum

- Jika port bentrok, cek dengan `lsof` dan jangan mematikan container milik praktik lain tanpa pemeriksaan.
- Jika container orchestration gagal, baca `docker compose logs`.
- Dari dalam container, database harus diakses dengan `host.docker.internal`, bukan `localhost`.
- Jangan menyalakan tiga orchestrator bersamaan.
