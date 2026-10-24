# YouTube Trend Analytics Pipeline

## A. Latar Belakang dan Tujuan

YouTube menjadi salah satu sumber sinyal tentang minat, budaya digital, dan konsumsi media masyarakat Indonesia. Namun, data trending berbentuk CSV belum langsung siap digunakan oleh data analyst karena masih bersifat snapshot, timestamp memakai suffix `UTC`, tipe data belum terdefinisi, metrik numerik memiliki nilai kosong, dan kategori masih berupa ID.

Project ini membangun pipeline ELT terorkestrasi yang memuat dataset `data/source/youtube_trending_dataset.csv` ke ClickHouse, kemudian mentransformasikannya dengan dbt menggunakan medallion architecture. Dagster mengatur dependensi, eksekusi, retry, logging, scheduling, dan validasi setiap tahap. FastAPI menyediakan query analitik sebagai API, sedangkan web dashboard menyajikan hasilnya melalui chart interaktif. Tujuannya adalah menyediakan data terstruktur dan siap digunakan untuk trend analysis, creator analytics, engagement research, content strategy, dan cultural insights.

## B. Masalah dan Solusi

### B.1 Masalah

1. Sumber data hanya berupa file CSV dan belum memiliki data warehouse.
2. Seluruh nilai pada tahap raw perlu dipertahankan untuk audit, tetapi tipe datanya belum siap dianalisis.
3. Kolom timestamp memiliki suffix `UTC`, sedangkan kebutuhan analisis adalah waktu Indonesia Barat (WIB).
4. `comment_count` dan `like_count` memiliki nilai kosong; `tags` juga tidak selalu tersedia.
5. `category_id` belum memiliki nama kategori yang mudah dibaca.
6. Satu video dapat muncul berkali-kali pada tanggal trending yang berbeda sehingga analisis harus membedakan kemunculan trending dan unique video.
7. Data analyst memerlukan tabel agregat yang sederhana untuk chart, bukan hanya tabel snapshot mentah.

### B.2 Solusi

Pipeline menerapkan pola ELT: Extract dari tiga CSV, Load ke ClickHouse bronze dengan seluruh kolom bertipe `String`, lalu Transform menggunakan dbt. Layer silver melakukan parsing timestamp, konversi UTC ke WIB dengan penambahan tujuh jam, pembersihan teks, casting numerik, perhitungan durasi, validasi nilai, dan join master kategori. Layer gold menyediakan tabel agregat harian, bulanan, channel, musim/periode khusus, serta performa konten. Dagster menjalankan seluruh tahap sesuai dependency graph dan menghentikan pipeline jika tahap sebelumnya gagal.

## C. Teknologi dan Tools

### C.1 Teknologi Utama

- **Python**: membaca CSV dan melakukan load batch ke ClickHouse.
- **ClickHouse**: analytical data warehouse untuk menyimpan bronze, silver, dan gold.
- **dbt Core + dbt-clickhouse**: transformasi SQL, dependency graph, dokumentasi, dan data tests.
- **Dagster**: orkestrasi job, observability, retry, schedule, dan monitoring pipeline.
- **FastAPI**: menyediakan endpoint query analitik dari ClickHouse untuk dashboard.
- **HTML, CSS, JavaScript, dan Chart.js**: membangun dashboard web responsif dan chart interaktif.
- **Docker Compose**: menjalankan ClickHouse, Dagster webserver, dan Dagster daemon secara terisolasi.
- **CSV**: sumber data trending, master kategori, dan kalender periode analisis.

### C.2 Arsitektur Sistem

```text
                                Dagster orchestration
                                         │
                                         v
youtube_trending_dataset.csv ─┐    load_bronze
category_master.csv ───────────┼─> Python loader ─> bronze.raw_*
season_calendar.csv ──────────┘                         │
                                                       v
                              build_silver ─> dbt cleaning + typing + enrichment
                                                       │
                                                       v
                              build_gold ─> gold.mart_* dashboard tables
                                                       │
                                                       v
                                 dbt tests ─> warehouse validation
                                                       │
                                                       v
                                  FastAPI query layer ─> Web dashboard
```

Semua komponen berada di folder `final-project`. ClickHouse memakai host port `18123` untuk HTTP dan `19000` untuk native, Dagster UI memakai `13000`, dan web dashboard memakai `18080`, agar tidak bentrok dengan latihan sebelumnya.

## D. Fitur

### D.1 Extract dan Load CSV

`ingestion/load_clickhouse.py` membaca dataset dan master CSV, membuat database `bronze`, membuat tabel dengan prefix `raw_`, mengosongkan isi lama secara terkontrol, lalu memasukkan data. Raw layer mempertahankan bentuk sumber dan menggunakan `String` untuk seluruh kolom.

### D.2 Silver Cleaning dan Standardisasi

- Menghapus suffix ` UTC` sebelum parsing timestamp.
- Menambahkan 7 jam untuk membentuk `trending_at_wib` dan `published_at_wib`.
- Membuat `trending_date`, tahun, bulan, dan hari dalam WIB.
- Mengubah rank, category ID, dan metrik engagement ke tipe numerik.
- Mengubah durasi `HH:MM:SS` menjadi detik dan menit.
- Mengisi metrik kosong dengan nol untuk `comment_count` dan `like_count`.
- Membersihkan whitespace pada channel, title, dan tags tanpa menghapus simbol atau karakter non-Latin yang bermakna.
- Memfilter record yang tidak memiliki video ID/timestamp valid, rank di luar 1–50, atau kategori yang tidak ada di master.

### D.3 Gold Data Mart

| Tabel | Kebutuhan dashboard |
|---|---|
| `gold.mart_daily_category_trends` | Line chart tren kategori per hari |
| `gold.mart_monthly_content_trends` | Perbandingan kategori lintas tahun dan bulan |
| `gold.mart_channel_trends` | Ranking channel berdasarkan frekuensi trending |
| `gold.mart_seasonal_trends` | Perbandingan Ramadan, pemilu, akhir tahun, dan periode reguler |
| `gold.mart_content_performance` | Scatter/relasi views, likes, comments, rank, dan durasi |

### D.4 Orkestrasi Dagster

Job `youtube_trending_elt_job` terdiri dari lima op yang dijalankan berurutan:

1. `load_bronze`: menjalankan Python loader untuk tiga sumber CSV.
2. `build_silver`: menjalankan model dbt pada folder `dbt/models/silver`.
3. `build_gold`: menjalankan lima model dbt pada folder `dbt/models/gold`.
4. `run_data_tests`: menjalankan seluruh source test dan model test dbt.
5. `validate_warehouse`: memeriksa kesesuaian row count bronze, silver, dan fact detail serta memastikan seluruh mart berisi data.

Setiap tahap memiliki log terpisah dan retry otomatis maksimal dua kali. Dagster webserver menyediakan UI pada port `13000`, sedangkan Dagster daemon menangani automation. Schedule harian pukul 02.00 WIB disediakan dalam kondisi nonaktif agar dapat diaktifkan setelah project siap dijalankan otomatis.

### D.5 API dan Web Dashboard

FastAPI menyajikan endpoint typed untuk chart dan filter dashboard. Query membaca tabel `silver.stg_youtube_trending` untuk analisis fleksibel berdasarkan tanggal/kategori serta tabel `gold.mart_seasonal_trends` untuk perbandingan periode khusus.

| Endpoint | Output dashboard |
|---|---|
| `/api/overview` | KPI appearances, unique videos, active channels, views, engagement, top category |
| `/api/category-trends` | Tren kategori harian atau bulanan |
| `/api/top-channels` | Ranking creator berdasarkan kemunculan trending |
| `/api/engagement-scatter` | Hubungan views, likes, comments, rank, dan engagement |
| `/api/duration-performance` | Performa berdasarkan bucket durasi |
| `/api/rank-performance` | Performa berdasarkan kelompok posisi trending |
| `/api/seasonal` | Perbandingan Ramadan, pemilu, akhir tahun, dan periode reguler |

Dashboard web menyediakan filter tanggal, kategori, dan granularitas; KPI cards; enam chart; leaderboard creator; insight otomatis; mode gelap; loading state; error state; serta layout responsif. Dashboard tersedia di `http://localhost:18080` dan Swagger API di `http://localhost:18080/docs`.

## E. Hasil Pengembangan

### E.1 Profil Dataset

Profiling awal menghasilkan 61.169 record, 23.844 video unik, 3.335 channel, 15 category ID, dan 1.225 tanggal trending. Rentang data adalah 14 Agustus 2022 sampai 4 Maret 2026. Dataset tidak memiliki duplicate penuh maupun duplicate `video_id` + `trending_date`.

Temuan kualitas data:

- Seluruh timestamp memiliki suffix `UTC` dan perlu dinormalisasi ke WIB.
- `comment_count` kosong pada 197 record.
- `like_count` kosong pada 407 record.
- `tags` kosong pada 13.669 record; nilai ini dipertahankan sebagai nullable.
- `duration` konsisten dalam pola `HH:MM:SS`.
- Nilai numerik yang tersedia tidak negatif dan rank berada pada rentang 1–50.

### E.2 Output Analitis

Output gold dirancang agar data analyst dapat langsung membuat chart berikut:

1. Tren jumlah kemunculan dan unique video per kategori dari waktu ke waktu.
2. Top channel berdasarkan jumlah kemunculan di trending list.
3. Hubungan trending rank dengan views, likes, comments, dan engagement rate.
4. Perbandingan performa kategori pada Ramadan, masa pemilu, libur akhir tahun, dan periode reguler.
5. Perbandingan durasi video dengan performa views dan engagement.
6. Dashboard interaktif yang memungkinkan analyst mengganti periode dan kategori tanpa menulis SQL ulang.

## F. Gambar Pendukung

Pendukung utama project berupa diagram arsitektur pada bagian C.2 dan struktur folder berikut:

```text
final-project/
├── data/source/youtube_trending_dataset.csv
├── data/master/category_master.csv
├── data/master/season_calendar.csv
├── ingestion/load_clickhouse.py
├── docker-compose.yml
├── dbt/dbt_project.yml dan dbt/profiles.yml
├── dbt/models/silver/ dan dbt/models/gold/
├── orchestration/definitions.py dan orchestration/Dockerfile
├── dashboard/app.py, dashboard/static/, dan dashboard/Dockerfile
├── scripts/run_pipeline.sh
└── laporan/
```

## G. Tantangan Dalam Pengerjaan

Tantangan utama adalah menjaga data raw tetap dapat diaudit sekaligus menyediakan data typed yang siap analisis. Solusinya adalah memisahkan bronze dan silver. Tantangan lain adalah timestamp UTC, nilai kosong, dan kemunculan video yang berulang. Timestamp dikonversi di silver, nilai kosong ditangani sesuai makna bisnis, dan gold membedakan `trending_appearances` dari `unique_videos`.

Tantangan orkestrasi adalah memastikan loader Python dan dbt memakai koneksi yang berbeda saat dijalankan dari host dan dari jaringan Docker. Konfigurasi koneksi dibuat berbasis environment variable: eksekusi host menggunakan `localhost:18123`, sedangkan container Dagster menggunakan service `clickhouse:8123`.

Tantangan dashboard adalah menjaga query tetap aman dan responsif ketika pengguna mengganti tanggal atau kategori. API menggunakan typed ClickHouse query parameters dan hanya mengizinkan nilai granularitas yang telah ditentukan. Frontend menampilkan loading, empty, dan error states sehingga pengguna tidak melihat chart kosong tanpa penjelasan.

Periode Ramadan dan event pemilu tidak boleh ditebak hanya dari bulan. Karena itu, pipeline menggunakan `data/master/season_calendar.csv` sebagai kalender analisis yang dapat ditinjau dan diperbarui oleh analyst sesuai sumber kalender yang disepakati.

## H. Kesimpulan

Project ini menghasilkan data platform mini yang terisolasi dan diorkestrasi Dagster di folder `final-project`, mulai dari file CSV hingga data mart ClickHouse, API analitik, dan web dashboard. Medallion architecture membuat raw data tetap tersedia, proses cleaning terdokumentasi di dbt, dan tabel gold siap digunakan. Dagster membuat setiap tahap dapat dipantau dan divalidasi, sedangkan FastAPI dan dashboard memungkinkan analyst mengeksplorasi insight tanpa menulis query manual.

## Acknowledgement

Terima kasih kepada Nusacodes dan mentor Bootcamp Data Engineering atas materi Python, ClickHouse, dbt, Docker, Dagster, API, dan praktik pembangunan pipeline data.

## Lampiran

- Source dataset: `final-project/data/source/youtube_trending_dataset.csv`
- Master kategori: `final-project/data/master/category_master.csv`
- Kalender periode: `final-project/data/master/season_calendar.csv`
- Definisi Dagster: `final-project/orchestration/definitions.py`
- Dagster UI: `http://localhost:13000`
- Dashboard: `http://localhost:18080`
- Swagger API: `http://localhost:18080/docs`
- Perintah pipeline: `final-project/scripts/run_pipeline.sh`
- Link GitHub Repository: diisi setelah repository dipublish.
- Link Artikel LinkedIn: diisi setelah artikel dipublish.
