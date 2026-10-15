# Pertemuan 3 — Data Cleaning & Transformation

## Topik

Data Cleaning & Transformation

## Tujuan Pembelajaran

- Memahami pentingnya membersihkan data sebelum digunakan untuk analisis atau pipeline.
- Mengidentifikasi dan menangani missing values.
- Menyeragamkan format data melalui normalisasi sederhana.
- Mengubah data kategori menjadi bentuk yang dapat diproses oleh sistem.
- Menggabungkan beberapa teknik transformasi melalui data wrangling dengan Pandas.

## Subtopik / Materi

### 1. Pengantar Data Cleaning

Data cleaning adalah proses menemukan dan memperbaiki masalah pada data agar data lebih konsisten, lengkap, dan siap digunakan. Data yang berasal dari aplikasi, file CSV, atau input manual sering memiliki nilai kosong, format yang berbeda, duplikasi, atau penulisan kategori yang tidak seragam.

Contoh masalah yang umum ditemukan:

- Nilai kosong pada kolom penting.
- Spasi tambahan pada teks.
- Huruf besar dan kecil yang tidak konsisten.
- Format tanggal yang berbeda.
- Nilai numerik yang masih terbaca sebagai teks.
- Kategori yang memiliki variasi penulisan, seperti `Jakarta`, `jakarta`, dan ` JAKARTA `.
- Baris duplikat.

Tujuan cleaning bukan mengubah data secara sembarangan, tetapi membuat aturan transformasi yang jelas dan dapat dijelaskan.

### 2. Membuat DataFrame Contoh

Contoh berikut digunakan untuk mempraktikkan seluruh materi pada pertemuan ini:

```python
import pandas as pd

data = pd.DataFrame({
    "nama": ["Andi", "Budi", "Citra", "Dina", "Eko"],
    "kota": [" Jakarta ", "jakarta", None, "Bandung", "Bandung"],
    "kategori": ["Retail", "retail", "Corporate", None, "Corporate"],
    "jumlah": [2, None, 5, 1, 3],
    "harga": [100000, 150000, None, 75000, 200000],
})

data.info()
data.head()
```

Sebelum melakukan transformasi, periksa nama kolom, tipe data, jumlah baris, dan nilai kosong pada setiap kolom.

### 3. Handling Missing Values

Missing values adalah nilai yang tidak tersedia atau tidak tercatat. Pada Pandas, missing values biasanya direpresentasikan sebagai `None` atau `NaN`.

#### Mengidentifikasi missing values

```python
# Jumlah nilai kosong per kolom
data.isna().sum()

# Persentase nilai kosong per kolom
persentase_kosong = data.isna().mean() * 100
persentase_kosong
```

#### Menghapus baris yang kosong

Gunakan `dropna()` jika baris tersebut tidak dapat digunakan tanpa nilai yang hilang.

```python
# Menghapus baris yang memiliki nilai kosong di kolom tertentu
data_bersih = data.dropna(subset=["nama", "kota"])
```

Penghapusan baris perlu dilakukan dengan hati-hati karena dapat mengurangi jumlah data. Pastikan nilai yang dihapus memang tidak dapat diperbaiki atau tidak dibutuhkan.

#### Mengisi missing values

Gunakan `fillna()` jika nilai kosong masih dapat diisi dengan aturan tertentu.

```python
data["kota"] = data["kota"].fillna("Tidak diketahui")
data["kategori"] = data["kategori"].fillna("Tidak diketahui")

# Untuk angka, median sering digunakan agar tidak terlalu dipengaruhi nilai ekstrem
data["jumlah"] = data["jumlah"].fillna(data["jumlah"].median())
data["harga"] = data["harga"].fillna(data["harga"].median())
```

Pilihan penanganan missing values bergantung pada arti kolom dan kebutuhan bisnis:

| Kondisi | Contoh penanganan |
|---|---|
| Baris tidak dapat digunakan tanpa nilai tersebut | Hapus baris dengan `dropna()` |
| Nilai kosong berarti tidak ada informasi | Isi dengan label seperti `Tidak diketahui` |
| Kolom numerik memiliki distribusi yang cukup stabil | Isi dengan rata-rata atau median |
| Nilai dapat diketahui dari baris sebelumnya/berikutnya | Gunakan aturan pengisian berurutan |

### 4. Normalisasi Data

Dalam konteks cleaning, normalisasi adalah proses menyeragamkan format nilai agar data yang memiliki arti sama dapat dikenali sebagai nilai yang sama. Contohnya adalah menghapus spasi, menyeragamkan huruf, dan memperbaiki format teks.

```python
# Menghapus spasi di awal dan akhir, lalu menyeragamkan huruf
data["kota"] = data["kota"].str.strip().str.title()
data["kategori"] = data["kategori"].str.strip().str.title()
```

Setelah transformasi, nilai seperti ` Jakarta ` dan `jakarta` akan menjadi `Jakarta`.

Normalisasi juga dapat digunakan untuk membersihkan kolom numerik yang terbaca sebagai teks:

```python
data["harga"] = pd.to_numeric(data["harga"], errors="coerce")
```

Parameter `errors="coerce"` mengubah nilai yang tidak dapat dikonversi menjadi `NaN`. Setelah itu, nilai tersebut perlu ditangani kembali menggunakan aturan missing values.

### 5. Encoding Data Kategori

Encoding adalah proses mengubah data kategori menjadi bentuk yang lebih mudah diproses oleh program atau sistem analitik.

#### Label encoding sederhana

Untuk kebutuhan transformasi dasar, kategori dapat dipetakan ke angka menggunakan dictionary.

```python
mapping_kategori = {
    "Retail": 1,
    "Corporate": 2,
    "Tidak diketahui": 0,
}

data["kategori_kode"] = data["kategori"].map(mapping_kategori)
```

Mapping perlu dibuat secara eksplisit agar arti setiap angka tetap jelas.

#### One-hot encoding

One-hot encoding membuat satu kolom untuk setiap kategori.

```python
data_encoded = pd.get_dummies(
    data,
    columns=["kategori"],
    prefix="kategori",
    dtype=int,
)
```

Hasilnya dapat berupa kolom seperti `kategori_Corporate` dan `kategori_Retail` dengan nilai `0` atau `1`.

Pemilihan metode encoding bergantung pada tujuan penggunaan data:

| Metode | Hasil | Cocok untuk |
|---|---|---|
| Mapping angka | Satu kolom berisi kode | Kategori sedikit dan mapping memiliki arti jelas |
| One-hot encoding | Satu kolom untuk setiap kategori | Data kategori yang tidak memiliki urutan |

### 6. Data Wrangling

Data wrangling adalah proses menggabungkan beberapa langkah untuk mengubah data mentah menjadi data yang lebih terstruktur dan siap digunakan. Langkahnya dapat meliputi memilih kolom, mengganti nama kolom, memfilter baris, membuat kolom baru, mengurutkan data, dan menghapus duplikasi.

Contoh alur data wrangling:

```python
hasil = data.copy()

# Menyeragamkan teks
hasil["kota"] = hasil["kota"].fillna("Tidak diketahui").str.strip().str.title()
hasil["kategori"] = (
    hasil["kategori"]
    .fillna("Tidak diketahui")
    .str.strip()
    .str.title()
)

# Menangani nilai numerik yang kosong
hasil["jumlah"] = hasil["jumlah"].fillna(hasil["jumlah"].median())
hasil["harga"] = hasil["harga"].fillna(hasil["harga"].median())

# Membuat kolom hasil perhitungan
hasil["total"] = hasil["jumlah"] * hasil["harga"]

# Menghapus duplikasi berdasarkan seluruh kolom
hasil = hasil.drop_duplicates()

# Mengurutkan berdasarkan nilai transaksi terbesar
hasil = hasil.sort_values("total", ascending=False)

hasil.head()
```

Urutan transformasi perlu diperhatikan. Misalnya, kolom numerik sebaiknya dibersihkan dan dikonversi terlebih dahulu sebelum digunakan untuk perhitungan.

### 7. Validasi Setelah Cleaning

Setelah proses cleaning dan transformation, lakukan pemeriksaan ulang untuk memastikan hasilnya sesuai harapan.

```python
hasil.info()
hasil.isna().sum()
hasil.duplicated().sum()
hasil["kategori"].value_counts()
```

Pemeriksaan sederhana yang perlu dilakukan:

- Apakah masih ada missing values pada kolom penting?
- Apakah tipe data sudah sesuai?
- Apakah ada baris duplikat?
- Apakah nilai kategori sudah seragam?
- Apakah hasil perhitungan masuk akal?
- Apakah jumlah baris berubah sesuai dengan aturan yang dibuat?

## Alur Praktik

1. Membaca dataset menggunakan Pandas.
2. Memeriksa struktur data dengan `info()`, `head()`, dan `isna().sum()`.
3. Mengidentifikasi missing values.
4. Memilih strategi untuk menghapus atau mengisi nilai kosong.
5. Membersihkan spasi dan menyeragamkan format teks.
6. Mengubah kolom numerik ke tipe data yang sesuai.
7. Melakukan encoding pada kolom kategori.
8. Membuat kolom hasil transformasi.
9. Menghapus duplikasi dan mengurutkan data.
10. Memvalidasi hasil akhir sebelum data digunakan pada tahap berikutnya.

## Output Peserta

- Dataset yang sudah dibersihkan dari missing values sesuai aturan yang ditentukan.
- Kolom teks dengan format yang lebih konsisten.
- Kolom kategori yang sudah di-encode.
- Dataset hasil wrangling yang siap digunakan untuk proses berikutnya.
- Catatan singkat mengenai aturan cleaning dan transformation yang digunakan.

## Materi Tambahan: Data Platform dan Data Modelling

Materi berikut memperkenalkan konsep yang digunakan ketika data hasil cleaning disimpan, dimodelkan, dan dikonsumsi untuk analisis. Fokusnya adalah memahami fungsi setiap komponen dan trade-off dasarnya, bukan membangun seluruh infrastrukturnya.

### 8. Data Warehouse, Data Lake, dan Data Lakehouse

#### Data Warehouse

Data warehouse adalah sistem penyimpanan terstruktur untuk data yang sudah dibersihkan, terintegrasi, dan siap digunakan untuk analisis. Data biasanya memiliki schema yang jelas, aturan kualitas yang lebih ketat, serta diakses menggunakan SQL.

Karakteristik data warehouse:

- **Format:** data terstruktur sempurna.
- **Skema:** validasi ketat saat penulisan.
- **Fokus:** analitik BI operasional rutin.
- **Karakteristik:** performa query sangat tinggi.
- **Kelemahan:** biaya penyimpanan sangat mahal.

Contoh platform: Snowflake, Google BigQuery, Amazon Redshift, Azure Synapse, dan ClickHouse.

#### Data Lake

Data lake adalah tempat penyimpanan data dalam skala besar yang dapat menampung data terstruktur, semi-terstruktur, maupun tidak terstruktur. Data dapat disimpan dalam bentuk mentah dan baru diberi schema ketika dibaca atau diproses.

Karakteristik data lake:

- **Format:** segala tipe data mentah.
- **Skema:** validasi saat pemuatan.
- **Fokus:** eksplorasi machine learning.
- **Kelemahan:** rawan menjadi rawa data (_data swamp_).

Data lake fleksibel dan relatif murah untuk menyimpan data mentah dalam skala besar, tetapi tetap membutuhkan tata kelola agar data mudah ditemukan, dipahami, dan dipercaya.

#### Data Lakehouse

Data lakehouse menyatukan dunia data lake dan data warehouse. Konsep ini mempertahankan penyimpanan yang murah serta fleksibel, kemudian menambahkan tata kelola dan dukungan transaksi.

Karakteristik data lakehouse:

- **Konsep:** storage murah plus tata kelola.
- **Format:** Apache Iceberg atau Delta Lake.
- **Keamanan:** dukungan penuh transaksi ACID.
- **Hasil:** satu wadah analitik sentral.

| Aspek | Data Warehouse | Data Lake | Data Lakehouse |
|---|---|---|---|
| Tipe data | Terstruktur saja | Semua variasi format | Semua variasi format |
| Skala biaya | Sangat mahal | Sangat terjangkau | Sangat terjangkau |
| Transaksi ACID | Terjamin | Tidak mendukung | Terjamin |
| Performa SQL | Sangat kilat | Sangat lambat | Sangat kilat |
| Dominasi target | BI dan pelaporan | Machine learning | BI dan AI gabungan |

#### Kapan menggunakan masing-masing platform?

- **Pilih warehouse** untuk target dashboard harian dan metrik bisnis krusial.
- **Pilih data lake** untuk menumpuk log mentah dan kebutuhan data science absolut.
- **Pilih lakehouse** untuk integrasi BI dan AI serta efisiensi biaya infrastruktur.

### 9. Snowflake dan Databricks

#### Snowflake

Snowflake adalah penguasa analitik instan dan berbagi data. Snowflake berparadigma gudang data relasional terkelola penuh dengan SQL sebagai antarmuka utama.

Karakteristik Snowflake:

- **Paradigma:** gudang data relasional terkelola penuh.
- **Bahasa utama:** pendekatan antarmuka SQL absolut.
- **Operasional:** bebas konfigurasi infrastruktur klaster.
- **Target pengguna:** analis data dan Business Intelligence.
- **Format terbuka:** mengadopsi Apache Iceberg secara mendalam.

#### Databricks

Databricks adalah pelopor arsitektur data lakehouse terpadu. Platform ini berfokus pada penyatuan danau data berbasis mesin Spark.

Karakteristik Databricks:

- **Paradigma:** penyatuan danau data berbasis mesin Spark.
- **Bahasa utama:** dukungan Python, Scala, R, dan SQL.
- **Keunggulan:** pemrosesan streaming dan komputasi masif.
- **Target pengguna:** ilmuwan data dan rekayasawan data.
- **Format terbuka:** pencipta ekosistem Delta Lake.

Perbandingan singkat:

| Aspek fokus | Snowflake | Databricks |
|---|---|---|
| Pengguna utama | Analis bisnis dan BI | Data scientist dan engineer |
| Kemudahan operasional | Otomatis dan terkelola | Membutuhkan keahlian teknis |
| Kekuatan inti | Kueri SQL interaktif kilat | Pelatihan machine learning |
| Arsitektur dasar | Data warehouse murni | Data lakehouse adaptif |
| Format bawaan | Apache Iceberg (integrasi) | Delta Lake (native) |

Pilih **Snowflake** jika kebutuhan utama adalah pelaporan dasbor BI, tim mayoritas didominasi analis SQL, konfigurasi infrastruktur harus sederhana, atau membutuhkan pembagian data eksternal instan. Pilih **Databricks** jika perlu mengelola pipa data streaming skala masif, fokus pada pelatihan model kecerdasan buatan, tim memiliki keahlian rekayasa perangkat lunak, atau membutuhkan eksekusi kode Python terintegrasi.

### 10. Jenis-Jenis Tabel

Ekosistem tabel data dapat dibedakan berdasarkan fungsi dan karakteristik datanya:

| Jenis tabel | Fungsi utama | Karakteristik data |
|---|---|---|
| Fact table | Menyimpan angka | Banyak baris, sempit |
| Dimension table | Menyimpan teks | Sedikit baris, lebar |
| Bridge table | Menghubungkan M:N | Kumpulan kunci pasangan |
| Junk dimension | Menyimpan status | Kombinasi flag tunggal |
| Aggregate table | Menyimpan rangkuman | Ukuran data terkompresi |

#### Fact Table

Fact table adalah pusat pencatatan nilai transaksi. Ciri utamanya:

- Fokus pada metrik dan menyimpan data angka terhitung.
- Memiliki foreign key yang menghubungkan langsung ke dimensi.
- Memiliki volume baris yang dapat tumbuh sangat besar.

#### Dimension Table

Dimension table menyediakan konteks penyaringan untuk transaksi. Tabel ini berisi atribut teks, struktur kolomnya lebar, dan pertumbuhan jumlah barisnya relatif lambat.

#### Bridge Table

Bridge table menjembatani relasi banyak-ke-banyak (many-to-many). Tabel ini menjadi pemutus konflik relasi, menghubungkan pasangan kunci tanpa merusak granularitas fact table.

#### Junk Dimension

Junk dimension menyederhanakan kumpulan indikator atau flag dengan menggabungkan status transaksi tunggal, mengurangi kolom kunci asing, dan membantu menjaga skema fact table tetap rapi.

#### Aggregate Table

Aggregate table menyimpan hasil agregasi secara otomatis, seperti ringkasan penjualan per hari. Dengan pra-kalkulasi, akses dasbor analitik dapat dipercepat dan beban komputasi memori server dikurangi.

### 11. Pola Data Modelling

Data modelling adalah proses merancang struktur data, hubungan antarentitas, aturan bisnis, dan cara data akan digunakan. Model yang baik membantu menjaga konsistensi serta membuat query lebih mudah dipahami dan dirawat.

#### Star Schema

Star schema digunakan untuk pelaporan penjualan ritel harian dan query dasbor yang cepat karena menerima relasi minimal. Satu fact table dikelilingi oleh beberapa dimension table.

Karakteristiknya:

- Satu fakta dikelilingi dimensi.
- Hanya satu JOIN per dimensi.
- Eksekusi kueri sangat cepat.
- Desainnya intuitif untuk pengguna bisnis.

#### Snowflake Schema

Snowflake schema digunakan untuk database perbankan atau asuransi dengan kapasitas penyimpanan yang sangat terbatas. Dimension dipecah menjadi sub-dimension sehingga data redundan berkurang dan ruang penyimpanan lebih hemat, tetapi kueri menjadi lebih lambat karena membutuhkan banyak JOIN.

#### Galaxy Schema

Galaxy schema digunakan untuk analisis logistik rantai pasok. Model ini melacak produk dari titik perakitan, ke pengiriman, hingga penjualan dan memiliki beberapa fact table yang berbagi dimensi.

Karakteristiknya:

- Konstelasi multi-fakta.
- Berbagi dimensi (_conformed dimensions_).
- Mendukung analisis lintas proses bisnis.
- Desainnya sangat kompleks.

#### One Big Table (OBT)

One Big Table digunakan untuk dasbor analitik _real-time streaming_ di Google BigQuery atau ClickHouse. Semua relasi dimensi disatukan ke satu tabel sehingga tidak membutuhkan operasi JOIN, tetapi konsekuensinya adalah redundansi data yang ekstrem.

Karakteristiknya:

- Denormalisasi absolut tunggal.
- Tanpa operasi JOIN sama sekali.
- Cocok untuk database kolumnar modern.
- Redundansi data ekstrem.

| Skema | Kecepatan kueri | Redundansi data | Kompleksitas desain |
|---|---|---|---|
| Star schema | Tinggi | Sedang | Rendah |
| Snowflake schema | Rendah | Sangat rendah | Sedang |
| Galaxy schema | Sedang | Sedang | Sangat tinggi |
| One Big Table (OBT) | Sangat tinggi | Sangat tinggi | Sangat rendah |

### 12. Medallion Architecture

Medallion Architecture menyusun data ke dalam layer kualitas agar data mentah, data bersih, dan data siap bisnis dapat dipisahkan dengan jelas.

```text
CSV / API → Bronze → Silver → Gold → BI / ML
  sumber      raw       clean     model   konsumsi
```

#### Bronze

Bronze menyimpan hasil _raw ingest_ dengan mempertahankan sumber. Data pada layer ini sedekat mungkin dengan bentuk asalnya agar dapat diaudit atau diproses ulang.

#### Silver

Silver berisi data yang sudah dibersihkan, divalidasi, diintegrasikan, dan distandardisasi. Proses cleaning pada pertemuan ini menjadi fondasi utama untuk layer Silver.

#### Gold

Gold berisi data mart dan agregasi yang siap digunakan oleh dasbor dan machine learning.

Tidak semua pipeline harus memiliki tepat tiga tabel. Yang penting adalah tanggung jawab setiap layer jelas.

#### Quality Gates

Quality gate yang perlu diperiksa pada alur tersebut meliputi **schema**, **missing values**, **duplicate**, **type**, **grain**, dan **join key**.

## Tools

- Python
- Jupyter Notebook
- Pandas

## Catatan Belajar

> Tambahkan rangkuman materi, aturan cleaning yang digunakan, dan kendala selama praktik di bagian ini.

## Hasil Praktik

> Tambahkan nama notebook, dataset sumber, dan file CSV hasil transformasi di bagian ini.
