# Dagster — Setup Docker dan Scheduler Pipeline ELT

## Hasil akhir

Dua container Dagster dijalankan melalui Docker Compose:

| Container | Fungsi | Port |
|---|---|---|
| `dagster-webserver` | UI dan API Dagster | `3000` |
| `dagster-daemon` | Menjalankan scheduler | tidak dipublish |

Pipeline dijalankan oleh asset `elt_pipeline` di [dagster_pipeline.py](./dagster_pipeline.py).

## Alur eksekusi Dagster dari awal sampai akhir

    docker compose up --build -d
            |
            +--> build image dari root repository
            |    Dockerfile: COPY . /workspace
            |
            +--> dagster-webserver membaca workspace.yaml
            |         |
            |         +--> import dagster_pipeline.py
            |
            +--> dagster-daemon membaca schedule setiap saat
                      |
                      +--> setiap 5 menit memicu asset elt_pipeline
                                |
                                +--> subprocess menjalankan
                                     bash /workspace/pertemuan-5/run_pipeline.sh
                                          |
                                          +--> etl_orders.py
                                          +--> dbt run
                                          +--> dbt test
                                          +--> verify_pipeline.py

### Kapan dagster_pipeline.py diambil?

File tersebut masuk ke image saat proses build melalui COPY . /workspace, bukan saat user menekan Materialize. Setelah container hidup, webserver dan daemon meng-import file itu melalui workspace.yaml. Saat tombol Materialize ditekan atau schedule aktif, Dagster menjalankan function elt_pipeline() dari file tersebut. Function itu membuat subprocess untuk menjalankan run_pipeline.sh.

Dengan kata lain:

- dagster_pipeline.py adalah aturan Dagster: asset, schedule, log, dan pemanggilan command.
- run_pipeline.sh adalah pipeline kerja sebenarnya dari Pertemuan 5.
- etl_orders.py, dbt, dan verify_pipeline.py adalah proses ELT yang dikerjakan oleh subprocess.

### Apa yang dijalankan tiap container?

- dagster-webserver menyediakan UI/API pada port 3000 dan membaca definisi asset dari workspace.
- dagster-daemon memantau schedule dan membuat run ketika waktunya tiba.
- Keduanya menggunakan image yang sama dan memiliki akses ke folder /workspace.
- Database tetap berada pada stack Pertemuan 5; Dagster mengaksesnya melalui host.docker.internal.

## 1. Prasyarat

Jalankan dari root repository:

```bash
cd bootcamp_beginner_de
docker --version
docker compose version
docker compose -f pertemuan-5/docker-compose.yml ps
```

PostgreSQL harus tersedia pada `localhost:5433`, ClickHouse pada `localhost:8123`, dan port Dagster `3000` harus kosong.

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

Tidak perlu menginstall Dagster, Python, atau dbt di host.

## 2. File yang digunakan

```text
pertemuan-6/dagster/
├── Dockerfile
├── dagster.yaml
├── workspace.yaml
├── dagster_pipeline.py
└── docker-compose.yml
```

- `Dockerfile`: image Python, dependency Pertemuan 5, dbt, Dagster, dan webserver.
- `dagster_pipeline.py`: asset dan schedule.
- `workspace.yaml`: lokasi definisi asset.
- `dagster.yaml`: storage metadata dan konfigurasi daemon.
- `docker-compose.yml`: webserver dan daemon.

Asset Dagster memanggil `pertemuan-5/run_pipeline.sh`. Jadi kode ETL dan dbt tetap berasal dari Pertemuan 5.

## 3. Build dan jalankan container

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml up --build -d
docker compose -f pertemuan-6/dagster/docker-compose.yml ps
```

Hasil yang diharapkan:

```text
dagster-webserver   Up
dagster-daemon      Up
```

Jika daemon berhenti:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml logs dagster-daemon
```

## 4. Buka UI

Buka [http://localhost:3000](http://localhost:3000).

1. Buka **Assets**.
2. Pastikan `elt_pipeline` terlihat.
3. Buka asset tersebut.
4. Pastikan schedule tersedia.
5. Validasi endpoint:
   ```bash
   curl -I http://localhost:3000
   ```

## 5. Jalankan pipeline manual

Di UI:

1. Klik **Assets**.
2. Pilih `elt_pipeline`.
3. Klik **Materialize**.
4. Buka **Runs**.
5. Buka run terbaru.
6. Baca log asset.

Run sukses jika terdapat `RUN_SUCCESS` dan log pipeline berisi `VERIFIKASI BERHASIL`.

Alternatif melalui CLI container:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml exec dagster-webserver \
  dagster asset materialize \
  --select elt_pipeline \
  -f /workspace/pertemuan-6/dagster/dagster_pipeline.py
```

## 6. Periksa hasil data

```bash
docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query \
  'SELECT count() FROM datamart.mart_daily_orders'
```

Hasil harus lebih besar dari nol. Pipeline juga memeriksa jumlah orders, entities, hasil dbt, dan data mart.

## 7. Periksa scheduler

Container `dagster-daemon` harus tetap berstatus `Up`.

Di UI:

1. Buka **Automation** atau **Schedules**.
2. Cari schedule asset `elt_pipeline`.
3. Pastikan aktif.
4. Pastikan cron `*/5 * * * *`.
5. Jika tidak ingin menunggu 5 menit, gunakan manual materialize.

Lihat log daemon:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml logs -f dagster-daemon
```

## 8. Cleanup

Wajib matikan sebelum lanjut ke Prefect:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml down
docker compose -f pertemuan-6/dagster/docker-compose.yml ps
```

Jangan gunakan `down -v` kecuali ingin menghapus metadata Dagster.

## 9. Troubleshooting

## 10. Jika ada update kode

Dagster menggunakan `COPY . /workspace` ketika image dibuat. Jadi perubahan pada file berikut tidak otomatis masuk ke container yang sedang berjalan:

- `pertemuan-5/etl_orders.py`
- `pertemuan-5/run_pipeline.sh`
- model atau macro dbt
- `pertemuan-6/dagster/dagster_pipeline.py`
- `workspace.yaml`

Setelah mengubah file tersebut, build ulang dan jalankan service:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml up --build -d
```

Perintah tersebut akan membuat ulang image dan container `dagster-webserver` serta `dagster-daemon`. Setelah itu cek:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml ps
```

Jika perubahan hanya pada `docker-compose.yml`, jalankan:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml up -d
```

Jika dependency atau Dockerfile bermasalah karena cache, gunakan:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml build --no-cache
docker compose -f pertemuan-6/dagster/docker-compose.yml up -d
```

Tidak perlu menghapus volume `dagster_home`. Volume tersebut menyimpan metadata Dagster, bukan source code pipeline.

### UI tidak terbuka

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml ps
docker compose -f pertemuan-6/dagster/docker-compose.yml logs dagster-webserver
```

### Daemon berhenti

Pastikan `dagster.yaml` termount dan workspace tersedia:

```bash
docker compose -f pertemuan-6/dagster/docker-compose.yml logs dagster-daemon
```

### Database tidak terhubung

Dari dalam container, gunakan `host.docker.internal` untuk PostgreSQL dan ClickHouse. Jangan gunakan `localhost`.

## 11. Output peserta

- Screenshot UI.
- Screenshot asset.
- Screenshot run sukses.
- Screenshot schedule aktif.
- Log berisi `RUN_SUCCESS` dan `VERIFIKASI BERHASIL`.

