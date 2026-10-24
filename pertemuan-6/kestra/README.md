# Kestra — Setup Docker dan Scheduler Pipeline ELT

## Hasil akhir

Kestra dijalankan dengan Docker Compose pada port `8080`. Task pipeline dijalankan oleh Docker Task Runner menggunakan image Python khusus.

```text
Kestra UI/server
       |
       v
Docker Task Runner
       |
       v
nusacodes/p6-elt-runner:local
       |
       v
pertemuan-5/run_pipeline.sh
```

Flow berada di [flows/elt_pipeline.yml](./flows/elt_pipeline.yml).

## Alur eksekusi Kestra dari awal sampai akhir

    1. docker compose up -d
       +--> menjalankan server/UI Kestra pada port 8080

    2. docker build ... pertemuan-6/kestra/Dockerfile
       +--> membuat image nusacodes/p6-elt-runner:local
           +--> COPY . /workspace
           +--> install Python dan dependency Pertemuan 5

    3. Flow YAML di-import ke UI
       +--> Kestra menyimpan flow, task, dan schedule

    4. Execute dari UI atau schedule
       +--> Kestra membaca containerImage pada task
       +--> Docker Task Runner membuat container runner
       +--> container runner menjalankan:
            cd /workspace && bash pertemuan-5/run_pipeline.sh
                 +--> etl_orders.py
                 +--> dbt run
                 +--> dbt test
                 +--> verify_pipeline.py

### Kapan elt_pipeline.yml dan Dockerfile digunakan?

Dockerfile digunakan saat command docker build dijalankan. Hasilnya adalah image runner yang berisi seluruh repository pada /workspace. File YAML tidak otomatis dibaca hanya karena berada di folder lokal; flow harus di-import dan disimpan melalui UI Kestra. Setelah tersimpan, Kestra memakai definisi YAML tersebut ketika flow dieksekusi.

elt_pipeline.yml memberitahu Kestra tiga hal penting:

- task yang harus dijalankan: command bash pertemuan-5/run_pipeline.sh;
- image yang digunakan: nusacodes/p6-elt-runner:local;
- kapan flow berjalan: cron setiap 5 menit dengan timezone Asia/Jakarta.

### Apa yang dijalankan tiap container?

- kestra: server/API/UI dan penyimpanan metadata Kestra.
- nusacodes/p6-elt-runner:local: container task yang dibuat ketika execution berjalan.
- Docker socket /var/run/docker.sock: memberi Kestra kemampuan membuat container runner.
- Database Pertemuan 5 tetap berjalan di host Docker dan diakses runner melalui host.docker.internal.

## 1. Prasyarat

Jalankan dari root repository:

```bash
cd bootcamp_beginner_de
docker --version
docker compose version
docker compose -f pertemuan-5/docker-compose.yml ps
```

PostgreSQL harus tersedia pada `localhost:5433`, ClickHouse pada `localhost:8123`, dan port Kestra `8080` harus kosong.

```bash
lsof -nP -iTCP:8080 -sTCP:LISTEN
```

## 2. File yang digunakan

```text
pertemuan-6/kestra/
├── Dockerfile
├── docker-compose.yml
├── README.md
└── flows/
    └── elt_pipeline.yml
```

- `docker-compose.yml`: Kestra server local, volume, dan Docker socket.
- `Dockerfile`: image task runner Python dan dbt.
- `flows/elt_pipeline.yml`: task dan schedule Kestra.

## 3. Jalankan Kestra UI

Jalankan:

```bash
docker compose -f pertemuan-6/kestra/docker-compose.yml up -d
docker compose -f pertemuan-6/kestra/docker-compose.yml ps
```

Buka [http://localhost:8080](http://localhost:8080).

Validasi:

```bash
curl -I http://localhost:8080
```

## 4. Build image task runner

Build dari root repository:

```bash
docker build \
  -t nusacodes/p6-elt-runner:local \
  -f pertemuan-6/kestra/Dockerfile \
  .
```

Image memasang Python, pandas, psycopg2, clickhouse-connect, dbt-core, dbt-clickhouse, python-dotenv, dan PyYAML.

Periksa image:

```bash
docker image inspect nusacodes/p6-elt-runner:local
```

Kestra menggunakan Docker socket untuk membuat container task. Karena itu Compose memasang `/var/run/docker.sock`.

## 5. Mengapa memakai host.docker.internal?

Task runner berada di container. PostgreSQL dan ClickHouse dipublish ke host.

Dari dalam container:

- `localhost` berarti container tersebut;
- `host.docker.internal` berarti host Docker.

Karena itu environment runner memakai:

```text
PGHOST=host.docker.internal
CH_HOST=host.docker.internal
```

Jangan mengganti nilai tersebut menjadi `localhost`.

## 6. Import flow ke UI

1. Buka menu **Flows**.
2. Klik **Create**.
3. Pilih editor **Code**.
4. Buka file [flows/elt_pipeline.yml](./flows/elt_pipeline.yml).
5. Salin seluruh isi YAML.
6. Paste ke editor Kestra.
7. Klik **Save** atau **Create**.
8. Pastikan namespace `nusacodes.bootcamp` dan ID `pertemuan_6_elt` terlihat.

Isi flow memiliki task:

```yaml
containerImage: nusacodes/p6-elt-runner:local
```

Dan schedule:

```yaml
cron: "*/5 * * * *"
timezone: Asia/Jakarta
```

## 7. Jalankan flow manual

Di halaman flow:

1. Klik **Execute**.
2. Gunakan input default jika diminta.
3. Konfirmasi.
4. Buka **Executions**.
5. Pilih execution terbaru.
6. Buka task `run_elt_pipeline`.
7. Baca log.

Execution sukses jika status flow dan task sukses serta log berisi `VERIFIKASI BERHASIL`.

## 8. Periksa data

```bash
docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query \
  'SELECT count() FROM datamart.mart_daily_orders'
```

Hasil harus lebih besar dari nol.

## 9. Periksa scheduler

Di Kestra UI:

1. Buka flow `pertemuan_6_elt`.
2. Buka bagian **Triggers**.
3. Cari trigger `every_5_minutes`.
4. Pastikan cron `*/5 * * * *`.
5. Pastikan timezone `Asia/Jakarta`.
6. Pastikan trigger tidak disabled.
7. Periksa execution berikutnya.

Untuk kelas, jalankan manual agar tidak perlu menunggu 5 menit.

## 10. Lihat log

```bash
docker compose -f pertemuan-6/kestra/docker-compose.yml logs -f kestra
```

Log task yang detail tersedia pada halaman **Executions**.

## 11. Cleanup

Wajib matikan sebelum selesai:

```bash
docker compose -f pertemuan-6/kestra/docker-compose.yml down
```

Perintah tersebut tidak menghapus volume secara otomatis. Jangan gunakan `down -v` kecuali ingin menghapus metadata Kestra.

Jika image runner tidak akan digunakan lagi:

```bash
docker image rm nusacodes/p6-elt-runner:local
```

## 12. Troubleshooting

## 13. Jika ada update kode

Kestra memakai dua artefak yang berbeda: server Kestra dan image task runner. Kode pipeline berada di image runner, bukan di container server Kestra.

Jika mengubah file berikut:

- pertemuan-5/etl_orders.py
- pertemuan-5/run_pipeline.sh
- model atau macro dbt
- pertemuan-6/kestra/Dockerfile
- requirements.txt

Build ulang image runner dari root repository:

```bash
docker build \
  -t nusacodes/p6-elt-runner:local \
  -f pertemuan-6/kestra/Dockerfile \
  .
```

Tidak perlu menjalankan docker compose down atau restart server Kestra. Execution berikutnya akan membuat task runner baru dari image yang sudah diperbarui.

Jika dependency masih menggunakan cache, build ulang tanpa cache:

```bash
docker build --no-cache \
  -t nusacodes/p6-elt-runner:local \
  -f pertemuan-6/kestra/Dockerfile \
  .
```

Jika mengubah file flows/elt_pipeline.yml, build image saja tidak cukup. Import atau paste ulang flow tersebut di UI Kestra, lalu klik Save atau Update. Alasannya, Kestra menyimpan flow di metadata server setelah flow di-import.

Jika hanya mengubah docker-compose.yml, jalankan:

```bash
docker compose -f pertemuan-6/kestra/docker-compose.yml up -d
```

Tidak perlu menggunakan down -v. Volume kestra_data dan kestra_db menyimpan metadata Kestra.

### Image task tidak ditemukan

```bash
docker build -t nusacodes/p6-elt-runner:local \
  -f pertemuan-6/kestra/Dockerfile .
```

Nama image harus persis `nusacodes/p6-elt-runner:local`.

### UI tidak terbuka

```bash
docker compose -f pertemuan-6/kestra/docker-compose.yml ps
docker compose -f pertemuan-6/kestra/docker-compose.yml logs kestra
```

### Task gagal koneksi database

Pastikan database hidup, port `5433` dan `8123` terbuka, dan runner memakai `host.docker.internal`.

### Flow belum terlihat

Cari namespace `nusacodes.bootcamp` dan ID `pertemuan_6_elt`. Flow harus disimpan/publish sebelum dieksekusi.

## 14. Output peserta

- Screenshot UI.
- Screenshot flow YAML.
- Screenshot trigger schedule.
- Screenshot execution sukses.
- Log berisi `VERIFIKASI BERHASIL`.
- Hasil query datamart.
- Catatan cleanup.

