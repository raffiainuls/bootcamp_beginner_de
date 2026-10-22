# Pertemuan 5 — ETL Sederhana dengan Python dan Transformasi dbt

## Topik

Membangun pipeline dari PostgreSQL ke ClickHouse:

```text
PostgreSQL --Extract--> Python --Load--> ClickHouse staging --Transform--> dbt --> datamart
```

Python mengambil data dan memuatnya ke staging. Transformasi analitik dilakukan oleh dbt di ClickHouse. Pola ini disebut **ELT** (Extract, Load, Transform), dan merupakan praktik yang baik untuk mengenalkan pipeline secara bertahap.

## Slide Presentasi

- [Pertemuan 5 — ETL Python dan Transformasi dbt](./slides/Pertemuan-5-ETL-Python-dan-dbt.pptx)

## Hasil Belajar

Peserta dapat:

1. Menjelaskan Extract, Load, dan Transform.
2. Menjalankan PostgreSQL dan ClickHouse dengan Docker Compose.
3. Membaca `bootcamp.orders` dari PostgreSQL menggunakan Python.
4. Memuat data raw ke `staging.raw_orders` di ClickHouse.
5. Membuat model staging dan datamart dengan dbt.
6. Menguji dan menjalankan ulang pipeline tanpa duplikasi.

## Prasyarat

- Git, Docker Desktop, dan Python 3.9+
- Repository sudah di-clone
- Data CSV Pertemuan 4 pada `pertemuan-4/postgres/out/`

Jalankan semua perintah dari root repository.

## 1. Siapkan lingkungan

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp pertemuan-5/.env.example pertemuan-5/.env
docker compose -f pertemuan-5/docker-compose.yml up -d
docker compose -f pertemuan-5/docker-compose.yml ps
```

Konfigurasi: PostgreSQL `localhost:5433`, database `nusacode_db`, schema `bootcamp`; ClickHouse `localhost:8123`, user `clickhousedev`, password `adminpass123`.

## 2. Siapkan sumber PostgreSQL

Loader memakai DDL dan CSV dari Pertemuan 4. Loader mereset schema `bootcamp`, jadi gunakan hanya untuk database latihan:

```bash
python3 pertemuan-4/postgres/load_to_postgres.py \
  --host localhost --port 5433 \
  --user postgresdev --password adminpass123 \
  --dbname nusacode_db --schema bootcamp
```

Pastikan sumber berisi order:

```bash
docker compose -f pertemuan-5/docker-compose.yml exec postgres \
  psql -U postgresdev -d nusacode_db \
  -c 'SELECT count(*) AS jumlah_order FROM bootcamp.orders;'
```

## 3. Extract dan Load dengan Python — dua versi

Tersedia dua versi script. Jalankan versi pemula terlebih dahulu agar alurnya mudah diikuti. Setelah itu gunakan versi rapi untuk melihat pola yang lebih siap dipelihara.

### Versi 1 — pemula-friendly

File: [`etl_orders_beginner.py`](./etl_orders_beginner.py)

Script ini sengaja ditulis lurus dari atas ke bawah:

```bash
python3 pertemuan-5/etl_orders_beginner.py
```

Hal yang akan terlihat langsung di kode:

1. Koneksi PostgreSQL ditulis dengan nilai hardcoded.
2. Query tabel `bootcamp.orders` ditulis langsung.
3. DDL ClickHouse ditulis langsung di dalam script.
4. Data di-`TRUNCATE`, kemudian dimuat ke `staging.raw_orders`.

Versi ini cocok untuk demo pertama karena peserta dapat membaca urutan Extract → Load tanpa harus memahami function, YAML, atau environment variable.

### Versi 2 — rapi dan configurable

File utama: [`etl_orders.py`](./etl_orders.py)

```bash
python3 pertemuan-5/etl_orders.py
```

Versi ini memakai:

- `pertemuan-5/.env`: kredensial dan host koneksi.
- [`config.yml`](./config.yml): daftar tabel sumber, kolom yang diambil, kolom pengurutan, dan target table.
- Folder [`schema/`](./schema/): DDL ClickHouse per tabel yang dibaca dan dijalankan oleh script.
- function terpisah untuk membaca config, membaca schema, extract, dan load.

Contoh konfigurasi yang tersedia:

```yaml
tables:
  - source_table: bootcamp.orders
    columns:
      - id
      - no_document
    order_by: id
    target_database: staging
    target_table: raw_orders
    schema_file: schema/clickhouse_raw_orders.sql

  - source_table: bootcamp.entities
    columns:
      - id
      - code
      - name
    order_by: id
    target_database: staging
    target_table: raw_entities
    schema_file: schema/clickhouse_raw_entities.sql
```

Script akan melakukan loop untuk setiap item di `tables`. Jadi untuk menambah tabel baru:

1. Tambahkan satu item baru di `config.yml`.
2. Cantumkan kolom sumber dan `order_by`.
3. Buat file DDL ClickHouse baru di folder `schema/`.
4. Isi `schema_file` dengan path file DDL tersebut.

Setelah itu, nama tabel dan query tidak perlu ditulis ulang di kode Python. DDL juga tidak ditulis di script.

> Jangan commit file `.env`. Gunakan `.env.example` sebagai template. Nilai pada contoh ini hanya kredensial database latihan lokal.

### Memeriksa hasil Load

```bash
docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query \
  'SELECT count() AS jumlah_raw FROM staging.raw_orders;'

docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query \
  'SELECT count() AS jumlah_raw FROM staging.raw_entities;'
```

## 4. Transformasi dengan dbt dari awal

### 4.1 Apa yang dilakukan dbt?

Pada pipeline ini Python hanya melakukan Extract dan Load:

```text
PostgreSQL bootcamp.orders
        |
        | Python Extract + Load
        v
ClickHouse staging.raw_orders
        |
        | dbt Transform
        v
ClickHouse staging.stg_orders
        |
        | dbt Transform + agregasi
        v
ClickHouse datamart.mart_daily_orders
```

dbt membaca file SQL model, mengatur urutan dependensi dari `ref()`, lalu menjalankan SQL tersebut di ClickHouse. Peserta tidak perlu menulis `CREATE TABLE` untuk model datamart secara manual.

### 4.2 Inisialisasi project dbt

Jika membuat project baru dari folder kosong, jalankan:

```bash
mkdir -p latihan-dbt
cd latihan-dbt
dbt init dbt_clickhouse_project
```

Perintah `dbt init` membuat project awal dan biasanya meminta nama profile. Untuk repository ini, project dbt sudah disiapkan di `pertemuan-5/dbt_project/`, sehingga jangan menjalankan `dbt init` lagi di dalam folder tersebut. Gunakan struktur yang sudah ada sebagai hasil inisialisasi project.

### 4.3 Struktur folder dan file dbt

Buat struktur berikut jika memulai dari project kosong:

```text
dbt_project/
├── dbt_project.yml
├── profiles.yml
├── macros/
│   └── generate_schema_name.sql
└── models/
    ├── sources.yml
    ├── stg_orders.sql
    └── mart_daily_orders.sql
```

Folder `target/` dan `logs/` akan dibuat otomatis oleh dbt. Folder tersebut tidak perlu dibuat atau di-commit.

### 4.4 File `dbt_project.yml`

File ini adalah identitas dan konfigurasi utama project dbt:

```yaml
name: dbt_clickhouse_project
version: '1.0.0'
config-version: 2
profile: dbt_clickhouse_project
model-paths: [models]
models:
  dbt_clickhouse_project:
    +materialized: view
```

Penjelasan singkat:

- `name`: nama project.
- `profile`: nama koneksi yang dicari di `profiles.yml`.
- `model-paths`: folder tempat model SQL dan source YAML.
- `materialized: view`: default model dibuat sebagai view, kecuali diubah oleh model tertentu.

### 4.5 File `profiles.yml`

File ini berisi koneksi dbt ke ClickHouse. Pada latihan ini file diletakkan lokal di `pertemuan-5/dbt_project/` dan selalu dipanggil dengan `--profiles-dir .`.

```yaml
dbt_clickhouse_project:
  target: dev
  outputs:
    dev:
      type: clickhouse
      schema: default
      host: localhost
      port: 8123
      user: clickhousedev
      password: adminpass123
      secure: false
      threads: 2
```

Nilai `user` dan `password` harus sama dengan konfigurasi ClickHouse pada Docker Compose. Untuk project nyata, jangan menyimpan password langsung di repository.

### 4.6 File `models/sources.yml`

Source memberi nama resmi untuk tabel yang sudah dimuat oleh Python. Source bukan tabel baru; source hanya memberi tahu dbt lokasi tabel yang akan dibaca.

```yaml
version: 2
sources:
  - name: staging
    schema: staging
    tables:
      - name: raw_orders
        columns:
          - name: id
            tests: [unique, not_null]
```

Dengan definisi ini, SQL dapat memanggil tabel menggunakan:

```sql
{{ source('staging', 'raw_orders') }}
```

Test `unique` dan `not_null` memastikan `id` order tidak kosong dan tidak duplikat.

### 4.7 File `models/stg_orders.sql`

Model staging membaca source lalu merapikan nama kolom dan tipe tanggal:

```sql
{{ config(materialized='view', schema='staging') }}

SELECT
    id AS order_id,
    no_document,
    customer_id,
    vendor_id,
    total_order_items,
    toDate(created_at) AS order_date
FROM {{ source('staging', 'raw_orders') }}
```

Model ini menghasilkan view `staging.stg_orders` di ClickHouse.

### 4.8 File `models/mart_daily_orders.sql`

Model mart membaca model staging dengan `ref()`, kemudian melakukan agregasi harian:

```sql
{{ config(materialized='table', schema='datamart') }}

SELECT
    order_date,
    count() AS total_orders,
    sum(total_order_items) AS total_items_ordered,
    uniqExact(customer_id) AS unique_customers
FROM {{ ref('stg_orders') }}
GROUP BY order_date
ORDER BY order_date
```

Karena memakai `ref('stg_orders')`, dbt tahu bahwa `stg_orders` harus dibuat lebih dahulu. Model ini menghasilkan tabel `datamart.mart_daily_orders`.

### 4.9 File macro `macros/generate_schema_name.sql`

ClickHouse memakai konsep database sebagai tempat tabel. Macro ini membuat nilai `schema: staging` dan `schema: datamart` digunakan apa adanya, bukan diubah menjadi nama seperti `default_staging`.

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

Tanpa macro ini, konfigurasi default dbt dapat menghasilkan nama database yang tidak sesuai dengan query verifikasi tutorial.

### 4.10 Jalankan dbt secara bertahap

Pastikan Python Extract/Load sudah dijalankan terlebih dahulu. Kemudian:

```bash
cd pertemuan-5/dbt_project

# Memeriksa file project dan koneksi ClickHouse
dbt debug --profiles-dir .

# Melihat model yang terdeteksi tanpa menjalankan SQL
dbt ls --profiles-dir .

# Membuat view staging dan tabel mart
dbt run --profiles-dir .

# Menjalankan test source
dbt test --profiles-dir .

cd ../..
```

Urutan yang diharapkan:

1. `dbt debug` menampilkan `All checks passed!`.
2. `dbt run` membuat `staging.stg_orders` dan `datamart.mart_daily_orders` tanpa error.
3. `dbt test` menampilkan dua test `PASS` untuk `raw_orders.id`.

Cek hasil transformasi langsung di ClickHouse:

```bash
docker compose -f pertemuan-5/docker-compose.yml exec clickhouse \
  clickhouse-client --query \
  'SELECT * FROM datamart.mart_daily_orders ORDER BY order_date LIMIT 10;'
```

## 5. Jalankan dan verifikasi end-to-end

`run_pipeline.sh` memakai versi rapi (`etl_orders.py`) karena script tersebut membaca konfigurasi dari `.env`, `config.yml`, dan file schema.

```bash
chmod +x pertemuan-5/run_pipeline.sh
./pertemuan-5/run_pipeline.sh
python3 pertemuan-5/verify_pipeline.py
```

Output akhir harus menunjukkan jumlah `PostgreSQL orders` sama dengan `ClickHouse staging`, jumlah `ClickHouse mart` lebih dari 0, dan `VERIFIKASI BERHASIL`.

## 6. Simulasi scheduling manual

```bash
while true; do
  ./pertemuan-5/run_pipeline.sh
  sleep 3600
done
```

Hentikan dengan `Ctrl+C`. Untuk latihan, ubah `sleep 3600` menjadi `sleep 60`. Jangan gunakan loop ini di database produksi.

## Troubleshooting

Jika port bermasalah, periksa atau matikan stack latihan:

```bash
docker compose -f pertemuan-5/docker-compose.yml ps
docker compose -f pertemuan-5/docker-compose.yml down
```

Jika `dbt` tidak ditemukan, aktifkan `.venv` dan jalankan `python -m pip install -r requirements.txt`.

## Tugas

1. Tambahkan `order_status_id` pada extract dan staging.
2. Buat model dbt yang menghitung order per `order_status_id`.
3. Tambahkan satu dbt test yang relevan.
4. Lampirkan screenshot output `dbt test` dan hasil datamart.

## Struktur file

```text
pertemuan-5/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── config.yml
├── etl_orders_beginner.py
├── etl_orders.py
├── schema/
│   ├── clickhouse_raw_orders.sql
│   └── clickhouse_raw_entities.sql
├── run_pipeline.sh
├── verify_pipeline.py
└── dbt_project/
    ├── dbt_project.yml
    ├── profiles.yml
    ├── macros/
    │   └── generate_schema_name.sql
    └── models/
        ├── sources.yml
        ├── stg_orders.sql
        └── mart_daily_orders.sql
```
