# Prefect — Setup Docker dan Scheduler Pipeline ELT

## Hasil akhir

Prefect dijalankan menggunakan dua container:

| Container | Fungsi | Port |
|---|---|---|
| `prefect-server` | API, metadata, dan UI | `4200` |
| `prefect-flow` | Flow Python dan deployment scheduler | tidak dipublish |

Pipeline didefinisikan di [prefect_pipeline.py](./prefect_pipeline.py).

## Alur eksekusi Prefect dari awal sampai akhir

    docker compose up --build -d
            |
            +--> build image dari root repository
            |    Dockerfile: COPY . /workspace
            |
            +--> prefect-server menjalankan API/UI port 4200
            |
            +--> prefect-flow menjalankan
                 python /workspace/pertemuan-6/prefect/prefect_pipeline.py --serve
                        |
                        +--> mendaftarkan flow dan deployment ke server
                        +--> menunggu schedule setiap 15 menit
                        +--> menerima run dari UI/CLI/schedule
                                  |
                                  +--> task run_elt_pipeline()
                                       |
                                       +--> bash /workspace/pertemuan-5/run_pipeline.sh
                                            +--> etl_orders.py
                                            +--> dbt run
                                            +--> dbt test
                                            +--> verify_pipeline.py

### Kapan prefect_pipeline.py digunakan?

File tersebut sudah berada di dalam image sejak proses docker compose up --build menjalankan COPY . /workspace. File kemudian dipakai ketika container prefect-flow menjalankan command python pertemuan-6/prefect/prefect_pipeline.py --serve.

Mode --serve tidak langsung menjalankan ETL. Mode ini mendaftarkan flow pertemuan-6-elt, membuat deployment dengan cron */15 * * * *, lalu menjaga worker tetap hidup untuk mengambil pekerjaan dari Prefect server. ETL baru dijalankan ketika deployment dipicu.

### Apa yang dijalankan tiap container?

- prefect-server: API, penyimpanan metadata, dan UI pada port 4200.
- prefect-flow: proses Python yang mendaftarkan deployment dan menunggu pekerjaan.
- run_elt_pipeline() adalah task Prefect yang memanggil run_pipeline.sh menggunakan subprocess.
- Database tetap berasal dari stack Pertemuan 5 dan diakses melalui host.docker.internal.

### Mengapa flow tidak berisi ulang kode ETL?

Karena Prefect hanya menjadi pengatur eksekusi. Decorator flow dan task menambahkan metadata, retry, status, dan log. Logic Extract, Load, Transform, serta verifikasi tetap satu sumber di Pertemuan 5 sehingga hasilnya sama ketika dijalankan langsung atau melalui Prefect.

## 1. Prasyarat

Jalankan dari root repository:

```bash
cd bootcamp_beginner_de
docker --version
docker compose version
docker compose -f pertemuan-5/docker-compose.yml ps
```

PostgreSQL harus tersedia pada `localhost:5433`, ClickHouse pada `localhost:8123`, dan port Prefect `4200` harus kosong.

```bash
lsof -nP -iTCP:4200 -sTCP:LISTEN
```

Tidak perlu menginstall Prefect, Python, atau dbt di host.

## 2. File yang digunakan

```text
pertemuan-6/prefect/
├── Dockerfile
├── docker-compose.yml
└── prefect_pipeline.py
```

- `Dockerfile`: image Prefect Python 3.11 dan dependency pipeline.
- `prefect_pipeline.py`: task, flow, retry, dan deployment.
- `docker-compose.yml`: server dan flow scheduler.

Alur:

```text
Prefect deployment scheduler
          |
          v
pertemuan-6-elt flow
          |
          v
run_elt_pipeline task
          |
          v
pertemuan-5/run_pipeline.sh
```

## 3. Build dan jalankan container

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml up --build -d
docker compose -f pertemuan-6/prefect/docker-compose.yml ps
```

Compose akan menunggu API server sehat sebelum menyalakan flow container.

Hasil yang diharapkan:

```text
prefect-server   Up (healthy)
prefect-flow     Up
```

Jika flow berhenti:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml logs prefect-flow
```

## 4. Buka UI

Buka [http://localhost:4200](http://localhost:4200).

Validasi API:

```bash
curl -fsS http://localhost:4200/api/health
```

Output:

```text
true
```

Di UI buka **Flows** dan **Deployments**. Pastikan flow/deployment `pertemuan-6-elt` terlihat.

## 5. Jalankan deployment dari UI

1. Buka **Deployments**.
2. Pilih deployment `pertemuan-6-elt`.
3. Klik **Run**.
4. Gunakan parameter default.
5. Buka **Flow Runs**.
6. Pilih run terbaru.
7. Buka log task `run_elt_pipeline`.

Run sukses jika statusnya **Completed** dan log berisi `VERIFIKASI BERHASIL`.

## 6. Jalankan deployment dari CLI container

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml exec prefect-flow \
  prefect deployment run 'pertemuan-6-elt/pertemuan-6-elt'
```

Lihat log:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml logs -f prefect-flow
```

Output sukses:

```text
Finished in state Completed()
VERIFIKASI BERHASIL
```

## 7. Periksa hasil data

```bash
docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query \
  'SELECT count() FROM datamart.mart_daily_orders'
```

Hasil harus lebih besar dari nol. Dataset latihan yang berhasil biasanya menunjukkan:

- PostgreSQL orders: 2.020 baris;
- ClickHouse raw orders: 2.020 baris;
- PostgreSQL entities: 142 baris;
- ClickHouse raw entities: 142 baris;
- datamart daily orders: 348 baris.

## 8. Periksa scheduler dan retry

Di UI:

1. Buka deployment `pertemuan-6-elt`.
2. Pastikan schedule aktif.
3. Pastikan cron `*/15 * * * *`.
4. Pastikan deployment tidak paused.
5. Buka riwayat flow runs.
6. Untuk menguji retry, kegagalan task akan dicoba ulang satu kali karena kode memakai `retries=1`.

Container `prefect-flow` harus tetap `Up` karena proses `flow.serve` melakukan polling deployment.

## 9. Cleanup

Wajib matikan sebelum lanjut ke Kestra:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml down
docker compose -f pertemuan-6/prefect/docker-compose.yml ps
```

Jangan gunakan `down -v` kecuali ingin menghapus metadata Prefect.

## 10. Troubleshooting

## 11. Jika ada update kode

Prefect menjalankan prefect_pipeline.py dari image yang dibuat dengan COPY . /workspace. Perubahan pada file berikut membutuhkan build ulang:

- pertemuan-5/etl_orders.py
- pertemuan-5/run_pipeline.sh
- model atau macro dbt
- pertemuan-6/prefect/prefect_pipeline.py
- requirements.txt

Jalankan:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml up --build -d
```

Perintah tersebut memperbarui image dan menjalankan kembali prefect-server serta prefect-flow. Periksa bahwa deployment terdaftar:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml ps
docker compose -f pertemuan-6/prefect/docker-compose.yml logs prefect-flow
```

Jika hanya mengubah docker-compose.yml, gunakan:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml up -d
```

Jika perubahan dependency belum terlihat karena cache:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml build --no-cache
docker compose -f pertemuan-6/prefect/docker-compose.yml up -d
```

Tidak perlu menghapus volume prefect_data. Volume tersebut menyimpan metadata Prefect, bukan source code.

### Flow gagal koneksi saat startup

Compose sudah memakai healthcheck. Periksa:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml logs prefect-server
docker compose -f pertemuan-6/prefect/docker-compose.yml logs prefect-flow
```

Restart:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml down
docker compose -f pertemuan-6/prefect/docker-compose.yml up -d
```

### UI kosong

Pastikan `prefect-flow` berstatus `Up`. Deployment dibuat oleh flow container, bukan host.

### UI menampilkan Unable to connect to Prefect server

Pastikan browser memakai http://localhost:4200, bukan hostname Docker prefect-server:4200. Hostname prefect-server hanya dapat digunakan oleh container lain dalam network Compose.

Compose memisahkan dua alamat:

- PREFECT_SERVER_UI_API_URL=http://localhost:4200/api untuk browser di host;
- PREFECT_API_URL=http://prefect-server:4200/api untuk flow container.

Periksa konfigurasi yang dibaca UI:

```bash
curl http://localhost:4200/ui-settings
```

Nilai api_url harus menunjuk ke http://localhost:4200/api. Jika baru mengubah Compose, jalankan:

```bash
docker compose -f pertemuan-6/prefect/docker-compose.yml up -d
```

### Database tidak terhubung

Dari dalam container gunakan `host.docker.internal`, bukan `localhost`.

## 12. Output peserta

- Screenshot UI.
- Screenshot flow/deployment.
- Screenshot run berstatus Completed.
- Screenshot schedule aktif.
- Log berisi `VERIFIKASI BERHASIL`.
- Catatan retry dan cleanup.

