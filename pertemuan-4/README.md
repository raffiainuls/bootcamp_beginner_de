# Pertemuan 4 — SQL untuk Pemula: Rantai Pasok Logistik Kesehatan

## Topik

SQL untuk pemula menggunakan PostgreSQL dan dataset fiktif rantai pasok logistik kesehatan.

Materi ini disusun mengikuti slide [SQL_Pemula_Logistik_Kesehatan_Final.pdf](./SQL_Pemula_Logistik_Kesehatan_Final.pdf). Fokus kelas adalah membaca struktur data dan menulis query dari DDL, `SELECT`, agregasi, `JOIN`, subquery, sampai CTE.

## Hasil Belajar

Setelah menyelesaikan materi ini, peserta diharapkan dapat:

1. Membuat tabel dan memilih tipe data.
2. Menjelaskan primary key, foreign key, dan constraint.
3. Memilih, memfilter, dan mengurutkan baris dengan SQL.
4. Menghitung agregasi dan menggabungkan tabel.
5. Memakai subquery dan CTE untuk query bertahap.

Saran pelaksanaan: dua pertemuan berdurasi sekitar dua jam, termasuk demo dan latihan.

## Bahan Praktik PostgreSQL

Seluruh bahan praktik berada di folder [`postgres/`](./postgres/):

- [Loader PostgreSQL](./postgres/load_to_postgres.py)
- [Loader shell](./postgres/load_postgres.sh)
- [DDL PostgreSQL](./postgres/ddl/postgres.sql)
- [Data CSV](./postgres/out/)
- [Latihan SQL](./postgres/exercises/latihan.sql)
- [Kunci jawaban SQL](./postgres/exercises/kunci-jawaban.sql)

### Menjalankan database

Container PostgreSQL yang digunakan pada repository ini memiliki konfigurasi:

```text
Host     : localhost
Port     : 5433
Database : nusacode_db
User     : postgresdev
Password : adminpass123
Schema   : bootcamp
```

### Menjalankan loader

Loader membuat schema, membuat tabel sesuai DDL, memuat CSV, lalu melakukan validasi. Jalankan dari root project:

```bash
python3 ./pertemuan-4/postgres/load_to_postgres.py
```

Perintah yang sama dapat dijalankan dari folder loader:

```bash
cd pertemuan-4/postgres
python3 load_to_postgres.py
```

Loader memakai default berikut dan dapat dioverride dengan argument atau environment variable:

```bash
export PGHOST=localhost
export PGPORT=5433
export PGDATABASE=nusacode_db
export PGUSER=postgresdev
export PGPASSWORD=adminpass123
```

`load_to_postgres.py` melakukan langkah berikut:

1. Membuka koneksi menggunakan `psycopg2`.
2. Menghapus schema latihan jika sudah ada dengan `DROP SCHEMA ... CASCADE`.
3. Membuat ulang schema dan tabel dari DDL.
4. Membuat primary key, foreign key, unique constraint, index, dan komentar tabel.
5. Memuat CSV dengan `COPY ... FROM STDIN` sesuai urutan dependensi foreign key.
6. Menghitung baris yang berhasil dimuat.
7. Memeriksa foreign key dan konsistensi saldo stok dengan ledger transaksi.
8. Menutup koneksi.

> Perhatian: loader mereset schema `bootcamp`. Gunakan hanya pada lingkungan latihan karena `DROP SCHEMA ... CASCADE` menghapus tabel dan data di dalam schema tersebut.

Setelah proses load selesai, masuk ke database untuk praktik query:

```bash
psql "postgresql://postgresdev:adminpass123@127.0.0.1:5433/nusacode_db"
```

```sql
SET search_path TO bootcamp;

SELECT COUNT(*) FROM entities;
SELECT COUNT(*) FROM transactions;
```

## 1. Database, Schema, Tabel, Kolom, dan Baris

| Istilah | Arti | Contoh pada kelas |
|---|---|---|
| Database | Wadah utama objek PostgreSQL | Database tempat bootcamp dibuat |
| Schema | Namespace di dalam database | `bootcamp` |
| Tabel | Kumpulan baris dengan struktur yang sama | `bootcamp.stocks` |
| Kolom | Atribut dengan tipe data tertentu | `entity_id`, `qty_on_hand` |
| Baris / grain | Satu catatan sesuai detail tabel | Satu catatan stok |

`bootcamp` adalah schema. Perintah berikut memilih urutan schema untuk pencarian nama tabel pada koneksi saat ini:

```sql
SET search_path TO bootcamp;
```

Nama dengan schema eksplisit tetap dapat digunakan:

```sql
SELECT id, name
FROM bootcamp.entities
ORDER BY id;
```

## 2. Kelompok Perintah SQL

| Kelompok | Tujuan | Contoh |
|---|---|---|
| DDL | Mendefinisikan struktur | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` |
| DML | Menambah atau mengubah isi | `INSERT`, `UPDATE`, `DELETE` |
| Query / sering disebut DQL | Membaca data | `SELECT` |
| DCL | Mengatur akses | `GRANT`, `REVOKE` |
| TCL | Mengatur transaksi | `COMMIT`, `ROLLBACK` |

Pengelompokan dapat berbeda antarreferensi. Fokus materi ini adalah DDL dan query `SELECT`.

## 3. Peta Tabel dan Grain Data

### Tabel master dan referensi

| Area | Tabel |
|---|---|
| Wilayah dan fasilitas | `locations`, `entity_types`, `entities` |
| Pengguna dan kegiatan | `users`, `activities`, `entity_activities` |
| Material | `material_types`, `material_units`, `materials`, `batches` |
| Referensi pesanan | `order_types`, `order_statuses`, `delivery_types` |
| Referensi mutasi | `transaction_types`, `transaction_reasons` |

Contoh latihan menggunakan nama dan kolom dari schema `bootcamp`. Nilai pada data mini bersifat fiktif.

### Grain tabel operasional

| Tabel | Makna satu baris | Hal yang perlu diperhatikan |
|---|---|---|
| `stocks` | Satu catatan stok per kombinasi dimensi | `entity`, `activity`, `material`, `batch` |
| `orders` | Satu dokumen permintaan atau pengiriman | `customer` dan `vendor` adalah `entities` |
| `order_items` | Satu baris material dalam pesanan | Satu order dapat memiliki banyak item |
| `transactions` | Satu catatan mutasi stok | `opening + change = closing` menurut komentar DDL |

Snapshot `qty_on_hand` dan akumulasi `change_qty` menjawab pertanyaan yang berbeda. Tentukan grain sebelum menulis agregasi.

## 4. Relasi pada Schema `bootcamp`

| Induk | Anak / kolom referensi | Makna |
|---|---|---|
| `entities.id` | `orders.customer_id` | Fasilitas yang meminta |
| `entities.id` | `orders.vendor_id` | Fasilitas yang mengirim |
| `orders.id` | `order_items.order_id` | Pesanan memiliki 0 sampai banyak item |
| `materials.id` | `stocks.material_id` | Material memiliki banyak catatan stok |
| `stocks.id` | `transactions.stock_id` | Stok memiliki banyak catatan mutasi |
| `entities` dan `activities` | `entity_activities` | Relasi many-to-many |

Setiap foreign key menjaga referensi ID. Foreign key tidak otomatis menjamin semua kombinasi aturan bisnis benar.

## 5. Tipe Data PostgreSQL

| Tipe PostgreSQL | Contoh kolom | Kegunaan |
|---|---|---|
| `SMALLINT` / `INT` | `status`, `entity_id` | Bilangan bulat dengan rentang berbeda |
| `BIGINT` | `qty_on_hand`, `change_qty` | Bilangan bulat untuk kuantitas atau ID besar |
| `TEXT` | `name`, `no_document` | Teks dengan panjang bervariasi |
| `NUMERIC(p,s)` | `lat NUMERIC(10,6)` | Desimal dengan presisi tetap |
| `DATE` / `TIMESTAMP` | `expired_date`, `created_at` | Tanggal dan tanggal-waktu |
| `UUID` | `transactions.uuid` | Identifier berformat UUID |

`TIMESTAMP` pada DDL ini berarti timestamp tanpa zona waktu. `UUID NOT NULL` belum berarti nilainya `UNIQUE`.

## 6. Primary Key, Foreign Key, dan Constraint

### Primary key dan foreign key

| Aspek | Primary key | Foreign key |
|---|---|---|
| Fungsi | Identitas unik baris | Referensi ke baris induk |
| Duplikasi | Tidak boleh berulang | Boleh berulang |
| `NULL` | Tidak boleh | Boleh jika tidak ada `NOT NULL` |
| Contoh | `orders.id` | `orders.customer_id` |

Primary key dapat menggunakan beberapa kolom. Foreign key juga dapat merujuk key gabungan. Pada schema latihan, `order_items.id` adalah primary key dan tidak memakai primary key gabungan `(order_id, material_id)`.

### Constraint dan default

```sql
CREATE TABLE materials (
    id   INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);
```

Constraint yang digunakan pada DDL:

| Constraint | Contoh | Makna |
|---|---|---|
| `PRIMARY KEY` | `transactions.id` | Identitas unik dan tidak `NULL` |
| `FOREIGN KEY` | `stocks.entity_id REFERENCES entities(id)` | Nilai merujuk tabel induk |
| `NOT NULL` | `materials.name` | Nilai wajib tersedia |
| `UNIQUE` | `entities.code` | Nilai tidak boleh duplikat |
| `UNIQUE` gabungan | `UNIQUE (entity_id, activity_id)` | Kombinasi pasangan tidak boleh berulang |
| `DEFAULT` | `qty_on_hand DEFAULT 0` | Nilai awal saat kolom tidak diberikan |

DDL bootcamp belum memiliki `CHECK`. `DEFAULT` memberi nilai awal, tetapi tidak membatasi semua nilai.

### Relasi self-reference

```sql
CREATE TABLE locations (
    id        INT PRIMARY KEY,
    name      TEXT NOT NULL,
    level     SMALLINT NOT NULL,
    parent_id INT REFERENCES locations(id),
    code      TEXT NOT NULL
);
```

`parent_id` menunjuk baris lain pada tabel `locations`. Provinsi dapat memiliki `parent_id` `NULL`. Pada data latihan, `level` berarti 0 provinsi, 1 kabupaten/kota, dan 2 kecamatan.

### Relasi many-to-many

```sql
CREATE TABLE entity_activities (
    id          INT PRIMARY KEY,
    entity_id   INT NOT NULL REFERENCES entities(id),
    activity_id SMALLINT NOT NULL REFERENCES activities(id),
    UNIQUE (entity_id, activity_id)
);
```

Satu fasilitas dapat mengikuti banyak kegiatan dan satu kegiatan dapat diikuti banyak fasilitas. Primary key `id` tetap berbeda dari `UNIQUE` gabungan yang menjaga aturan pasangan.

### Audit aturan bisnis

Komentar pada kolom tidak membuat database melakukan validasi otomatis. Contoh audit:

```sql
SELECT id
FROM transactions
WHERE closing_qty <> opening_qty + change_qty;
```

Usulan constraint tambahan, jika aturan sudah disepakati dan data telah dibersihkan:

```sql
ALTER TABLE transactions
ADD CONSTRAINT chk_qty_balance
CHECK (closing_qty = opening_qty + change_qty);
```

### Perintah perubahan struktur dan isi

| Perintah | Efek | Contoh |
|---|---|---|
| `ALTER TABLE` | Mengubah struktur atau aturan | Menambah constraint |
| `DROP TABLE` | Menghapus tabel dan isinya | `DROP TABLE tabel_demo` |
| `TRUNCATE TABLE` | Mengosongkan seluruh tabel | Tidak memiliki `WHERE` |
| `DELETE FROM` | Menghapus baris sesuai filter | `DELETE ... WHERE id = 1` |

`TRUNCATE` memperhatikan dependensi foreign key. `DROP SCHEMA ... CASCADE` pada loader adalah operasi reset lingkungan latihan, bukan `ON DELETE CASCADE` pada foreign key.

### Referential action

| Aksi | Perilaku saat induk dihapus |
|---|---|
| `NO ACTION` | Menolak jika referensi anak masih melanggar foreign key |
| `RESTRICT` | Menolak penghapusan induk yang masih dirujuk |
| `CASCADE` | Ikut menghapus baris anak |
| `SET NULL` | Mengubah foreign key anak menjadi `NULL` jika diizinkan |

DDL bootcamp tidak mendeklarasikan `ON DELETE CASCADE`.

## 7. Data Mini untuk Memahami Query

Contoh berikut mengikuti data mini pada slide. Angka ini ilustrasi untuk membaca hasil query; hasil pada database kelas mengikuti CSV yang dimuat.

### Fasilitas dan material

| `entities.id` | `entities.name` | `entity_type_id` |
|---:|---|---:|
| 1 | Dinkes Prov | 1 |
| 2 | Dinkes Kab | 2 |
| 3 | PKM Melati | 3 |
| 4 | PKM Mawar | 3 |

| `materials.id` | `materials.name` | `unit` |
|---:|---|---|
| 1000 | Vaksin A | dosis |
| 1001 | Syringe | pcs |
| 1002 | Safety box | box |

### Snapshot stok

| `id` | `entity_id` | `material_id` | `batch_id` | `qty_on_hand` |
|---:|---:|---:|---:|---:|
| 100 | 2 | 1000 | 5000 | 800 |
| 101 | 3 | 1000 | 5000 | 120 |
| 102 | 3 | 1000 | 5001 | 80 |
| 103 | 4 | 1000 | 5001 | 0 |
| 104 | 3 | 1001 | 5002 | 500 |

Semua contoh stok memakai `activity_id = 1`. Saldo Vaksin A di PKM Melati adalah 200 dosis karena dua batch perlu dijumlahkan.

### Pesanan dan item

Pada data mini, `order_status_id` 1 berarti Draft, 2 Dikirim, dan 3 Diterima. Semua laporan mengabaikan soft delete dengan `deleted_at IS NULL`.

## 8. INSERT Data Referensi

Isi tabel induk sebelum tabel anak yang memiliki foreign key:

```sql
INSERT INTO transaction_types
    (id, name, direction)
VALUES
    (1, 'Penerimaan', 1),
    (2, 'Pengeluaran', -1);
```

`transaction_reasons` memerlukan `transaction_type_id` yang sudah tersedia. Pada data generator yang sudah terisi, baca ID dari tabel referensi terlebih dahulu dan jangan menebak arti angka status.

## 9. SELECT Dasar

### Memilih kolom

```sql
SELECT id, name
FROM entities
ORDER BY id;
```

`SELECT` memilih kolom, `FROM` memilih sumber, dan `ORDER BY` menetapkan urutan. `SELECT *` mengambil semua kolom, tetapi pilih kolom yang diperlukan agar maksud query jelas.

### Alias dan kolom hasil perhitungan

```sql
SELECT
    id,
    opening_qty + change_qty AS expected
FROM transactions
WHERE id IN (9001, 9002)
ORDER BY id;
```

`AS` hanya memberi nama pada hasil query. Alias tidak menambah kolom permanen ke tabel. Teks memakai tanda kutip tunggal.

## 10. WHERE dan Filter

### Filter dimensi

```sql
SELECT id, qty_on_hand
FROM stocks
WHERE entity_id = 3
  AND material_id = 1000
  AND activity_id = 1
  AND qty_on_hand > 0
ORDER BY id;
```

Hanya baris dengan kondisi `TRUE` yang lolos. Operator umum adalah `=`, `<>`, `>`, `>=`, `<`, dan `<=`. Filter dimensi menentukan arti jumlah yang akan dihitung.

### AND, OR, NOT, dan tanda kurung

```sql
SELECT id, customer_id AS cust_id
FROM orders
WHERE deleted_at IS NULL
  AND (customer_id = 3 OR customer_id = 4)
  AND NOT (order_status_id = 1)
ORDER BY id;
```

- `AND`: semua syarat harus benar.
- `OR`: minimal satu syarat benar.
- `NOT`: membalik kondisi.
- Prioritas evaluasi: `NOT`, lalu `AND`, lalu `OR`.

### IN, BETWEEN, LIKE, dan ILIKE

```sql
-- Beberapa pilihan nilai
SELECT id, name
FROM entities
WHERE id IN (3, 4);

-- Batas bawah dan atas ikut masuk
SELECT id, qty_on_hand
FROM stocks
WHERE qty_on_hand BETWEEN 1 AND 200;

-- Pencarian pola nama
SELECT id, name
FROM entities
WHERE name ILIKE 'pkm%';
```

`IN` meringkas beberapa `OR`. `BETWEEN` bersifat inklusif. `%` berarti nol atau lebih karakter dan `_` berarti satu karakter. `ILIKE` tidak membedakan huruf besar-kecil pada PostgreSQL.

### NULL dan COALESCE

```sql
SELECT
    id,
    COALESCE(qty_approved, 0) AS approved
FROM order_items
WHERE qty_approved IS NULL
ORDER BY id;
```

Gunakan `IS NULL`, bukan `= NULL`. `COALESCE` memberi nilai pengganti saat menampilkan atau menghitung, tetapi tidak mengubah makna nilai asli `NULL`.

### Filter tanggal

```sql
SELECT id, no_document
FROM orders
WHERE created_at >= TIMESTAMP '2026-02-01'
  AND created_at <  TIMESTAMP '2026-03-01'
  AND deleted_at IS NULL
ORDER BY created_at, id;
```

Pola batas `>=` awal bulan dan `<` awal bulan berikutnya mengambil seluruh Februari tanpa menebak presisi timestamp.

### DISTINCT

```sql
SELECT DISTINCT entity_id
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
ORDER BY entity_id;
```

`DISTINCT` mengevaluasi kombinasi semua kolom yang dipilih. `DISTINCT` bukan pengganti key `JOIN` yang benar dan tidak memperbaiki grain yang keliru.

### ORDER BY dan LIMIT

```sql
SELECT id, qty_on_hand
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
ORDER BY qty_on_hand DESC, id ASC
LIMIT 2;
```

Tanpa `ORDER BY`, urutan hasil tidak dijamin. Gunakan kolom kedua seperti `id` sebagai pemecah seri ketika nilai utama sama.

## 11. Agregasi, GROUP BY, dan HAVING

### Fungsi agregasi

| Fungsi | Kegunaan |
|---|---|
| `COUNT(*)` | Menghitung semua baris |
| `COUNT(column)` | Menghitung nilai non-`NULL` |
| `COUNT(DISTINCT column)` | Menghitung nilai unik non-`NULL` |
| `SUM(column)` | Menjumlahkan nilai |
| `MIN(column)` | Nilai terkecil |
| `MAX(column)` | Nilai terbesar |
| `AVG(column)` | Rata-rata |

```sql
SELECT
    COUNT(*) AS rows,
    SUM(qty_on_hand) AS total,
    MIN(qty_on_hand) AS min_qty,
    MAX(qty_on_hand) AS max_qty,
    AVG(qty_on_hand) AS avg_qty
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1;
```

Rata-rata per baris stok dapat berbeda dari rata-rata per fasilitas karena satu fasilitas dapat memiliki beberapa batch.

### GROUP BY

```sql
SELECT
    entity_id,
    SUM(qty_on_hand) AS total
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
GROUP BY entity_id
ORDER BY entity_id;
```

Aturan aman: kolom di `SELECT` yang tidak menggunakan fungsi agregasi harus ikut berada di `GROUP BY`.

### HAVING

```sql
SELECT
    entity_id,
    SUM(qty_on_hand) AS total
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
GROUP BY entity_id
HAVING SUM(qty_on_hand) >= 200
ORDER BY entity_id;
```

`GROUP BY` membentuk kelompok, `SUM` menghitung saldo per kelompok, dan `HAVING` memilih kelompok dengan total minimal 200. `WHERE SUM(qty_on_hand) >= 200` tidak valid pada query block yang sama.

### WHERE dan HAVING bersama

```sql
SELECT
    entity_id,
    SUM(qty_on_hand) AS total
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
  AND qty_on_hand > 0
GROUP BY entity_id
HAVING SUM(qty_on_hand) >= 200
ORDER BY total DESC, entity_id;
```

`WHERE` menentukan catatan stok yang ikut dihitung. `HAVING` memfilter hasil kelompok. Fasilitas dengan nol stok tidak masuk kelompok karena sudah tersaring di `WHERE`.

### Urutan tulis dan urutan logis

| Urutan logis | Klausa |
|---:|---|
| 1 | `FROM` dan `JOIN` |
| 2 | `WHERE` |
| 3 | `GROUP BY` dan agregasi |
| 4 | `HAVING` |
| 5 | `SELECT`, lalu `DISTINCT` |
| 6 | `ORDER BY` |
| 7 | `LIMIT` |

Ini adalah model untuk memahami hasil query. Optimizer dapat memilih urutan kerja fisik yang berbeda.

### CASE WHEN

```sql
SELECT
    id,
    CASE
        WHEN qty_on_hand = 0 THEN 'Kosong'
        WHEN qty_on_hand < 100 THEN 'Rendah'
        ELSE 'Tersedia'
    END AS label
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
ORDER BY id;
```

Batas 100 pada contoh hanya aturan latihan tingkat baris stok, bukan definisi kecukupan stok produksi.

## 12. JOIN

### Jenis JOIN

| Bentuk JOIN | Baris yang dipertahankan | Contoh |
|---|---|---|
| `INNER JOIN` | Hanya pasangan yang cocok | Stok dengan nama material |
| `LEFT JOIN` | Semua baris tabel kiri | Semua fasilitas, termasuk tanpa order |
| `RIGHT JOIN` | Semua baris tabel kanan | Biasanya dapat ditulis ulang sebagai `LEFT JOIN` |
| `CROSS JOIN` | Semua kombinasi | Fasilitas × kegiatan |
| Self join | Tabel yang sama dengan alias berbeda | Fasilitas dan induknya |

Self join adalah pola memakai tabel yang sama, bukan keyword JOIN tersendiri.

### INNER JOIN

```sql
SELECT o.id, e.name
FROM orders AS o
JOIN entities AS e
    ON e.id = o.customer_id
WHERE o.deleted_at IS NULL
ORDER BY o.id;
```

Pada schema ini tidak ada tabel `customers`. `customer_id` pada `orders` merujuk ke `entities`.

### Dua peran tabel yang sama

```sql
SELECT
    o.id,
    c.name AS customer,
    v.name AS vendor
FROM orders AS o
JOIN entities AS c
    ON c.id = o.customer_id
JOIN entities AS v
    ON v.id = o.vendor_id
WHERE o.id = 201;
```

Alias `c` mewakili peminta dan `v` mewakili pengirim. Nama `vendor_id` menunjukkan peran bisnis, tetapi foreign key tidak memeriksa `is_vendor = 1`.

### LEFT JOIN untuk hasil nol

```sql
SELECT e.id, e.name
FROM entities AS e
LEFT JOIN orders AS o
    ON o.customer_id = e.id
   AND o.deleted_at IS NULL
WHERE o.id IS NULL
ORDER BY e.id;
```

`LEFT JOIN` mempertahankan semua fasilitas. `WHERE o.id IS NULL` memilih fasilitas tanpa order nondeleted sebagai customer.

### Filter pada ON dan WHERE

```sql
SELECT e.id, o.id AS order_id
FROM entities AS e
LEFT JOIN orders AS o
    ON o.customer_id = e.id
   AND o.deleted_at IS NULL
   AND o.received_at IS NOT NULL
WHERE e.id IN (3, 4)
ORDER BY e.id, o.id;
```

Filter `received_at` pada `ON` membatasi pasangan pesanan tanpa membuang fasilitas yang tidak memiliki pasangan. Memindahkan filter tersebut ke `WHERE` akan menghilangkan baris fasilitas tanpa order.

### JOIN beberapa tabel

```sql
SELECT
    e.name,
    SUM(i.qty_sent) AS sent
FROM orders AS o
JOIN entities AS e
    ON e.id = o.customer_id
JOIN order_items AS i
    ON i.order_id = o.id
WHERE o.deleted_at IS NULL
  AND o.activity_id = 1
  AND i.material_id = 1000
GROUP BY e.id, e.name
ORDER BY sent DESC NULLS LAST, e.id;
```

`qty_sent` berasal dari `order_items`. Jumlah terkirim bukan jumlah diterima karena schema tidak memiliki `qty_received` pada `order_items`.

### Risiko JOIN: baris dapat bertambah

```sql
SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT o.id) AS orders
FROM orders AS o
JOIN order_items AS i
    ON i.order_id = o.id
WHERE o.deleted_at IS NULL;
```

Satu order dapat memiliki beberapa item. Setelah join, `COUNT(*)` menghitung baris hasil join, bukan jumlah order unik. Hindari menjumlahkan kolom order setelah join ke item tanpa memahami grain.

### LEFT JOIN dan COUNT

```sql
SELECT
    e.name,
    COUNT(o.id) AS total
FROM entities AS e
LEFT JOIN orders AS o
    ON o.customer_id = e.id
   AND o.deleted_at IS NULL
GROUP BY e.id, e.name
ORDER BY e.id;
```

Gunakan `COUNT(o.id)` untuk hasil nol. `COUNT(*)` tetap menghitung baris placeholder dari outer join.

### UNION dan UNION ALL

```sql
SELECT name AS label
FROM entities
WHERE id IN (3, 4)

UNION ALL

SELECT name AS label
FROM entities
WHERE id = 3

ORDER BY label;
```

`UNION ALL` menumpuk baris dan mempertahankan duplikasi. `UNION` menghapus duplikasi. Jumlah kolom harus sama dan tipe datanya kompatibel. JOIN mencocokkan baris, sedangkan UNION menumpuk hasil query.

## 13. Subquery

Subquery adalah query di dalam query lain.

| Bentuk | Lokasi umum | Tujuan |
|---|---|---|
| Scalar | `SELECT` atau pembanding `WHERE` | Stok di atas rata-rata |
| Set | `IN` / `NOT IN` | Fasilitas yang memiliki stok |
| Derived table | `FROM` | Memfilter hasil agregasi |
| Correlated | Merujuk kolom query luar | Material tanpa stok |

Jumlah baris dan kolom subquery harus sesuai dengan tempat pemakaiannya.

### Scalar subquery

```sql
SELECT id, qty_on_hand
FROM stocks
WHERE material_id = 1000
  AND activity_id = 1
  AND qty_on_hand > (
      SELECT AVG(qty_on_hand)
      FROM stocks
      WHERE material_id = 1000
        AND activity_id = 1
  )
ORDER BY id;
```

Subquery menghasilkan satu nilai agregat. Query luar mencari baris yang lebih besar dari nilai tersebut. Dimensi dan grain query luar harus sama dengan subquery.

### Subquery IN

```sql
SELECT id, name
FROM entities
WHERE id IN (
    SELECT entity_id
    FROM stocks
    WHERE material_id = 1000
      AND activity_id = 1
      AND qty_on_hand > 0
)
ORDER BY id;
```

`IN` memeriksa keanggotaan ID. Beberapa batch dalam subquery tidak menggandakan baris fasilitas.

### EXISTS dan correlated subquery

```sql
SELECT m.id, m.name
FROM materials AS m
WHERE NOT EXISTS (
    SELECT 1
    FROM stocks AS s
    WHERE s.material_id = m.id
)
ORDER BY m.id;
```

Subquery merujuk `m.id` dari query luar. `NOT EXISTS` mencari material tanpa satu pun catatan stok. Tidak memiliki catatan stok berbeda dari memiliki catatan dengan saldo nol.

### NULL pada NOT IN

```sql
SELECT 1002 NOT IN (1000, 1001, NULL) AS result;
```

Hasilnya `NULL` atau `UNKNOWN`. `WHERE` hanya meloloskan kondisi `TRUE`. Jika daftar dapat mengandung `NULL`, `NOT EXISTS` sering lebih jelas untuk mencari baris tanpa pasangan.

### Derived table

```sql
SELECT x.entity_id, x.total
FROM (
    SELECT
        entity_id,
        SUM(qty_on_hand) AS total
    FROM stocks
    WHERE material_id = 1000
      AND activity_id = 1
    GROUP BY entity_id
) AS x
WHERE x.total >= 200
ORDER BY x.entity_id;
```

Query di dalam `FROM` menghasilkan sumber bernama `x`. Query luar dapat memfilter `total` karena kolom tersebut sudah menjadi output query block sebelumnya.

## 14. CTE

CTE atau Common Table Expression memberi nama pada tahap query dan berlaku hanya dalam satu statement.

```sql
WITH stock_summary AS (
    SELECT
        entity_id,
        SUM(qty_on_hand) AS total
    FROM stocks
    WHERE material_id = 1000
      AND activity_id = 1
    GROUP BY entity_id
)
SELECT entity_id, total
FROM stock_summary
WHERE total >= 200
ORDER BY entity_id;
```

Hasilnya sama dengan derived table sebelumnya, tetapi tahapnya lebih mudah dibaca. CTE bukan tabel permanen dan tidak otomatis lebih cepat.

### Beberapa CTE

```sql
WITH eligible AS (
    SELECT id, customer_id
    FROM orders
    WHERE deleted_at IS NULL
      AND activity_id = 1
), sent_qty AS (
    SELECT
        o.customer_id,
        SUM(i.qty_sent) AS sent
    FROM eligible AS o
    JOIN order_items AS i
        ON i.order_id = o.id
    WHERE i.material_id = 1000
    GROUP BY o.customer_id
)
SELECT customer_id, sent
FROM sent_qty
WHERE sent >= 200
ORDER BY sent DESC, customer_id;
```

Antar-CTE dipisahkan dengan koma. Tahap pertama memilih order relevan, tahap kedua menghitung jumlah terkirim, dan query utama memilih total minimal 200.

## 15. Memilih JOIN, Subquery, atau CTE

| Pilihan | Paling membantu ketika | Hal yang diperiksa |
|---|---|---|
| JOIN | Perlu kolom dari beberapa sumber | Kardinalitas dan duplikasi |
| `IN` / `EXISTS` | Perlu memeriksa keanggotaan atau keberadaan | `NULL` dan korelasi |
| Derived table | Hasil query langsung menjadi sumber | Alias dan grain hasil |
| CTE | Query memiliki beberapa tahap bernama | Scope dan rencana eksekusi |

Pilih bentuk yang jelas dan benar. Bandingkan performa dengan `EXPLAIN` pada database target.

## 16. Kesalahan Umum

| Gejala | Kemungkinan penyebab | Pemeriksaan |
|---|---|---|
| `Unknown column` | Memakai nama kolom dari contoh lama | Gunakan `qty_on_hand`, `qty_sent`, `created_at` sesuai schema |
| Hasil nol terlalu besar | `COUNT(*)` setelah `LEFT JOIN` | Gunakan `COUNT(o.id)` |
| Jumlah membesar | Join stok ke mutasi atau order ke item | Periksa grain dan kardinalitas |
| Status keliru | Menebak arti ID numerik | Join ke tabel referensi |
| Jumlah mencampur unit | Menjumlahkan dosis dan pcs | Filter material atau unit yang sebanding |
| Pesanan terhapus ikut laporan | Soft delete belum difilter | Tambahkan `deleted_at IS NULL` |

Satu angka yang valid secara SQL belum tentu menjawab pertanyaan bisnis dengan benar.

## 17. Bonus: Index dan EXPLAIN

```sql
EXPLAIN
SELECT id, change_qty
FROM transactions
WHERE entity_id = 3
  AND created_at >= TIMESTAMP '2026-02-01'
  AND created_at <  TIMESTAMP '2026-03-01';
```

`EXPLAIN` menampilkan rencana query. Index dapat membantu pencarian, tetapi optimizer tetap dapat memilih scan tabel. Data mini terlalu kecil untuk menilai performa produksi.

PostgreSQL tidak otomatis membuat index untuk setiap foreign key. Primary key dan unique constraint memiliki index pendukung.

## 18. Bonus: Hierarki Fasilitas

```sql
SELECT
    e.name AS child,
    p.name AS parent
FROM entities AS e
LEFT JOIN entities AS p
    ON p.id = e.parent_entity_id
WHERE e.id IN (3, 4)
ORDER BY e.id;
```

Self join membaca satu tingkat induk. Penelusuran banyak tingkat dapat memakai `WITH RECURSIVE`.

## 19. Bonus: Audit Konsistensi Referensi

Foreign key terpisah hanya memastikan setiap ID memiliki pasangan. Query berikut mencari dimensi transaksi yang berbeda dari dimensi `stock_id`:

```sql
SELECT t.id
FROM transactions AS t
JOIN stocks AS s
    ON s.id = t.stock_id
WHERE t.entity_id <> s.entity_id
   OR t.material_id <> s.material_id
   OR t.activity_id <> s.activity_id
   OR t.batch_id IS DISTINCT FROM s.batch_id;
```

`IS DISTINCT FROM` membandingkan nilai dengan aman ketika salah satunya `NULL`.

## 20. Bonus: Batch Mendekati Kedaluwarsa

```sql
SELECT s.id, b.expired_date
FROM stocks AS s
JOIN batches AS b
    ON b.id = s.batch_id
WHERE s.material_id = 1000
  AND s.activity_id = 1
  AND s.qty_on_hand > 0
  AND b.expired_date >= DATE '2026-06-01'
  AND b.expired_date <  DATE '2026-07-01'
ORDER BY b.expired_date, s.id;
```

Rentang tersebut adalah contoh laporan untuk batch yang kedaluwarsa pada Juni 2026. Ambang “mendekati kedaluwarsa” harus ditentukan oleh aturan bisnis.

## 21. Peta Penyusunan Query

| Pertanyaan | Konsep atau klausa |
|---|---|
| Satu baris hasil mewakili apa? | Grain, key, dan satuan |
| Data berasal dari tabel mana? | `FROM` dan `JOIN` |
| Baris mana yang dihitung? | `WHERE` dan filter soft delete |
| Ringkasan per apa? | `GROUP BY` dan agregat |
| Kelompok mana yang tampil? | `HAVING` |
| Bagaimana bentuk keluaran? | `SELECT`, `ORDER BY`, `LIMIT` |
| Perlu beberapa tahap? | Subquery atau CTE |

Bedakan saldo, mutasi neto, jumlah terkirim, dan jumlah diterima saat menetapkan metrik.

## 22. Latihan

Kerjakan latihan pada [postgres/exercises/latihan.sql](./postgres/exercises/latihan.sql) langsung di database `bootcamp`.

### Latihan 1: SELECT dan filter

1. Tampilkan fasilitas yang namanya diawali `PKM`, urutkan nama A–Z.
2. Cari stok material `1000` dan activity `1` dengan quantity 1 sampai 200.
3. Cari `order_items` yang `qty_approved` belum tersedia.
4. Ambil dua pesanan nondeleted terbaru berdasarkan `created_at` dan `id`.

### Latihan 2: GROUP BY dan HAVING

1. Hitung pesanan nondeleted per `order_status_id`.
2. Hitung pesanan nondeleted per `customer_id`, lalu tampilkan customer dengan lebih dari satu pesanan.
3. Hitung saldo material `1000` pada activity `1` per `entity_id`.
4. Jelaskan mengapa `WHERE SUM(qty_on_hand) > 200` tidak valid untuk agregasi langsung.

### Latihan akhir: laporan stok dan distribusi

1. Tampilkan semua fasilitas beserta jumlah order nondeleted sebagai customer, termasuk fasilitas dengan nol order.
2. Hitung `qty_sent` material `1000` pada activity `1` per customer dari order nondeleted dan tampilkan total minimal 200.
3. Cari material yang tidak memiliki catatan `stocks` dengan `NOT EXISTS`.
4. Tulis ulang soal nomor 2 memakai CTE dan bandingkan hasilnya.

## Output Peserta

- Schema PostgreSQL `bootcamp` yang berhasil dimuat.
- Pemahaman tentang grain, primary key, foreign key, dan constraint.
- File query atau notebook berisi latihan `SELECT`, filter, agregasi, `JOIN`, subquery, dan CTE.
- Penjelasan singkat tentang tabel sumber, kolom penghubung, grain, dan filter yang digunakan.
- Hasil query yang dapat dijelaskan secara bisnis, bukan hanya valid secara sintaks.

## Referensi

- Slide: [SQL_Pemula_Logistik_Kesehatan_Final.pdf](./SQL_Pemula_Logistik_Kesehatan_Final.pdf)
- [Loader PostgreSQL](./postgres/load_to_postgres.py)
- [DDL PostgreSQL](./postgres/ddl/postgres.sql)
- [Latihan SQL](./postgres/exercises/latihan.sql)
- [Kunci jawaban SQL](./postgres/exercises/kunci-jawaban.sql)
- [Dokumentasi PostgreSQL](https://www.postgresql.org/docs/current/)
- Materi sebelumnya: [Pertemuan 3 — Data Cleaning & Transformation](../pertemuan-3/README.md)
- Materi berikutnya: [Pertemuan 5 — Data Pipeline Automation](../pertemuan-5/README.md)
