# Pertemuan 2 — Python untuk Data Engineering

## Topik

Python untuk Data Engineering

## Tujuan Pembelajaran

- Memahami peran Python dalam pekerjaan data engineering.
- Mengenal dasar sintaks Python untuk mengolah data.
- Menggunakan Pandas dan NumPy untuk kebutuhan dasar pengolahan data.
- Membaca data dari file CSV dan JSON.
- Melakukan transformasi data sederhana.

## Subtopik / Materi

### 1. Python untuk Data Engineering

Python adalah bahasa pemrograman yang banyak digunakan untuk membaca, mengolah, mentransformasi, dan memindahkan data. Dalam data engineering, Python sering digunakan untuk membuat script ETL, menghubungkan berbagai sumber data, menjalankan validasi, dan mengotomatisasi pekerjaan berulang.

Contoh penggunaan Python:

- Membaca file CSV atau JSON.
- Mengambil data dari API.
- Menghubungkan script ke database.
- Membersihkan dan mentransformasi data.
- Menyimpan hasil pengolahan ke file atau database.

### 2. Dasar Python

- Variabel dan konstanta.
- Tipe data: string, integer, float, boolean, dan `None`.
- List, tuple, dictionary, dan set.
- Operator dan ekspresi.
- Percabangan dengan `if`, `elif`, dan `else`.
- Perulangan dengan `for` dan `while`.
- Function dan parameter.
- Import module.

#### Contoh use case dasar Python di data engineering

Dasar Python dipakai sebelum menggunakan library seperti Pandas atau NumPy. Contohnya:

| Konsep Python | Contoh penggunaan dalam pipeline |
| --- | --- |
| Variabel dan konstanta | Menyimpan nama pipeline, sumber data, dan batas validasi |
| `dict` | Merepresentasikan satu record transaksi |
| `list` | Menyimpan sekumpulan record dalam satu batch |
| `if` | Memeriksa apakah transaksi sudah dibayar |
| `for` | Membaca daftar pelanggan satu per satu |
| Function | Membuat pengecekan transaksi yang dapat dipakai ulang |

Contoh sederhananya adalah mengecek status transaksi sebelum diteruskan ke tahap berikutnya:

```python
transaksi = {"id": "TRX-001", "pelanggan": "Andi", "status": "paid"}

if transaksi["status"] == "paid":
    print("Transaksi sudah dibayar")
else:
    print("Transaksi belum dibayar")
```

Praktik dasar Python ini sengaja dipisahkan dari latihan Pandas, NumPy, CSV, dan JSON agar konsep sintaks dasar dapat dipelajari terlebih dahulu. File latihan menggunakan standard library Python saja dan membahas variabel, list, dictionary, `if`, `for`, dan function melalui contoh transaksi sederhana.

Lihat praktik lengkapnya di:

- [Latihan dasar Python dalam notebook](./latihan_dasar_python.ipynb)
- [Latihan dasar Python dalam script](./latihan_dasar_python.py)

### 3. NumPy dan Pandas

- NumPy sebagai library untuk operasi numerik dan array.
- Pandas sebagai library untuk bekerja dengan data tabular.
- Series dan DataFrame.
- Membaca dan menulis file data.
- Melihat struktur dataset dengan `head()`, `info()`, dan `describe()`.

Contoh praktik NumPy:

```python
import numpy as np

nilai_transaksi = np.array(data["amount"])
total_transaksi = np.sum(nilai_transaksi)
rata_rata_transaksi = np.mean(nilai_transaksi)
```

Pada latihan ini, NumPy digunakan untuk mengubah kolom angka menjadi array dan menghitung total serta rata-rata transaksi.

### 4. Membaca File CSV dan JSON

Sumber data latihan pada sesi ini dapat berupa:

- File CSV dengan `pd.read_csv()`.
- File JSON dengan `pd.read_json()` atau modul bawaan Python.

Hal yang perlu diperhatikan saat membaca data:

- Nama dan tipe kolom.
- Pemisah kolom pada CSV.
- Format tanggal dan angka.
- Struktur JSON.
- Encoding file.

### 5. Transformasi Data Sederhana

- Rename kolom.
- Memilih kolom tertentu.
- Memfilter baris berdasarkan kondisi.
- Membuat kolom baru.
- Menghitung nilai rata-rata.
- Mengurutkan data.
- Menyimpan hasil ke file CSV baru.

Contoh alur transformasi:

```python
import pandas as pd

data = pd.read_csv("transaksi.csv")
data = data.rename(columns={"amount": "total_transaksi"})
data = data[data["total_transaksi"] > 100000]
rata_rata = data["total_transaksi"].mean()
data.to_csv("transaksi_terfilter.csv", index=False)
```

## Perbedaan `.ipynb` dan `.py`

Kedua format ini berisi contoh yang sama, tetapi cara penggunaannya berbeda. Gunakan `.ipynb` untuk belajar dan menjalankan kode per bagian; gunakan `.py` untuk menjalankan script dari awal sampai akhir, misalnya saat membuat proses yang berulang.

### `.ipynb` — Jupyter Notebook

File `.ipynb` menyimpan kode dalam cell, output, markdown, tabel, dan visualisasi dalam satu dokumen interaktif.

Biasanya digunakan untuk:

- Eksplorasi data secara bertahap.
- Menampilkan output setiap potongan kode.
- Menjelaskan proses dengan markdown.
- Praktik belajar dan demo di kelas.
- Membuat analisis yang mudah dibaca.

### `.py` — Python Script

File `.py` menyimpan kode Python sebagai script yang dapat dijalankan dari awal sampai akhir.

Biasanya digunakan untuk:

- Menjalankan proses secara berulang.
- Membuat script ETL.
- Menjalankan pekerjaan melalui terminal atau scheduler.
- Menyusun kode yang lebih terstruktur dan reusable.
- Menggunakan kode sebagai bagian dari aplikasi atau pipeline.

| Aspek | `.ipynb` | `.py` |
|---|---|---|
| Bentuk | Notebook berisi cell kode dan markdown | Script Python biasa |
| Cara menjalankan | Cell dapat dijalankan satu per satu | Umumnya dijalankan dari awal sampai akhir |
| Output | Output tersimpan dan terlihat di notebook | Output biasanya muncul di terminal atau file |
| Kegunaan utama | Eksplorasi, pembelajaran, dan demo | Automasi, ETL, dan production workflow |
| Cocok untuk | Eksperimen interaktif | Proses yang konsisten dan berulang |

Pada repository ini, materi praktik tersedia dalam dua format:

- [Notebook praktik `.ipynb`](./latihan_python_data_engineering.ipynb)
- [Script praktik `.py`](./latihan_python_data_engineering.py)
- [Dataset CSV](./data/transaksi.csv)
- [Dataset JSON](./data/transaksi.json)

Keduanya mengerjakan alur yang sama agar perbedaan format dan kegunaannya dapat dibandingkan secara langsung.

## Output Peserta

- Mengolah data dengan Python.
- Membaca file CSV dan JSON.
- Melakukan transformasi data sederhana.
- Menghasilkan file output dari proses pengolahan data.

## Praktik

1. Menyiapkan Python dan Jupyter Notebook.
2. Membaca dataset CSV.
3. Membaca dataset JSON.
4. Memeriksa isi dan struktur data.
5. Mengubah kolom numerik menjadi array NumPy.
6. Menghitung total dan rata-rata dengan NumPy.
7. Mengubah nama kolom.
8. Memfilter data berdasarkan kondisi.
9. Menyimpan hasil transformasi ke file baru.

## Tugas

Membaca dataset CSV sederhana, kemudian melakukan transformasi berikut:

- Rename kolom.
- Filter data berdasarkan kondisi tertentu.
- Menghitung rata-rata salah satu kolom numerik.
- Menyimpan hasil transformasi sebagai file CSV baru.

## Tools

- Python
- Jupyter Notebook
- Pandas
- NumPy

## Catatan Belajar

> Tambahkan rangkuman materi, contoh kode, dan kendala selama praktik di bagian ini.

## Hasil Praktik

> Tambahkan nama file notebook, script, dataset, dan output latihan di bagian ini.
