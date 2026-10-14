"""Latihan Pertemuan 2: Python untuk Data Engineering.

Alur latihan:
1. Menyiapkan data transaksi sederhana.
2. Membaca contoh file CSV dan JSON.
3. Membaca dan menginspeksi data.
4. Menggunakan NumPy untuk operasi array dan numerik.
5. Rename kolom.
6. Filter transaksi.
7. Menghitung rata-rata transaksi.
8. Menyimpan hasil transformasi ke CSV.
"""

# Mengimpor Path untuk bekerja dengan lokasi file dan folder.
from pathlib import Path

# Mengimpor NumPy untuk operasi array dan perhitungan angka.
import numpy as np
# Mengimpor Pandas untuk membuat dan mengolah DataFrame.
import pandas as pd


# Menyimpan lokasi folder tempat file script ini berada.
BASE_DIR = Path(__file__).resolve().parent
# Menentukan folder data yang berisi file CSV dan JSON.
DATA_DIR = BASE_DIR / "data"


# Membuat function untuk menghasilkan data transaksi sederhana.
def buat_data_transaksi() -> pd.DataFrame:
    """Menghasilkan dataset transaksi kecil untuk latihan langsung di Python."""
    # Membuat DataFrame dari dictionary berisi nama kolom dan nilai.
    return pd.DataFrame(
        {
            # Membuat kolom ID transaksi.
            "transaction_id": ["TRX-001", "TRX-002", "TRX-003", "TRX-004", "TRX-005"],
            # Membuat kolom nama pelanggan.
            "customer": ["Andi", "Budi", "Citra", "Dewi", "Eka"],
            # Membuat kolom jumlah transaksi.
            "amount": [150000, 75000, 225000, 100000, 350000],
        }
    )


# Membuat function untuk membaca file CSV dan JSON.
def baca_file_csv_json() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Membaca contoh dataset eksternal CSV dan JSON."""
    # Membaca file CSV dari folder data menjadi DataFrame.
    data_csv = pd.read_csv(DATA_DIR / "transaksi.csv")
    # Membaca file JSON dari folder data menjadi DataFrame.
    data_json = pd.read_json(DATA_DIR / "transaksi.json")
    # Mengembalikan dua DataFrame agar dapat digunakan di function lain.
    return data_csv, data_json


# Membuat function untuk rename, filter, dan menghitung data.
def transformasi_data(data: pd.DataFrame) -> tuple[pd.DataFrame, float, int]:
    """Melakukan rename, filter, dan perhitungan numerik dengan NumPy."""
    # Mengganti nama kolom amount menjadi total_transaksi.
    hasil = data.rename(columns={"amount": "total_transaksi"})
    # Memilih transaksi dengan nilai lebih besar dari 100000.
    hasil = hasil[hasil["total_transaksi"] > 100000].copy()
    # Mengubah kolom hasil filter menjadi array NumPy.
    nilai_transaksi = hasil["total_transaksi"].to_numpy()
    # Menghitung nilai rata-rata dari array transaksi.
    rata_rata = float(np.mean(nilai_transaksi))
    # Menghitung total nilai dari array transaksi.
    total = int(np.sum(nilai_transaksi))
    # Mengembalikan data hasil filter, rata-rata, dan total.
    return hasil, rata_rata, total


# Membuat function utama untuk menjalankan seluruh latihan.
def main() -> None:
    """Menjalankan seluruh alur latihan."""
    # Membuat data transaksi langsung dengan Pandas.
    data = buat_data_transaksi()

    # Menampilkan judul bagian data awal.
    print("\n== Data awal dari DataFrame Python ==")
    # Menampilkan isi DataFrame awal.
    print(data)

    # Menampilkan judul bagian pembacaan file.
    print("\n== Contoh membaca file CSV dan JSON ==")
    # Membaca file CSV dan JSON dengan function yang sudah dibuat.
    data_csv, data_json = baca_file_csv_json()
    # Menampilkan label untuk data CSV.
    print("Data CSV:")
    # Menampilkan isi data CSV.
    print(data_csv)
    # Menampilkan label untuk data JSON.
    print("\nData JSON:")
    # Menampilkan isi data JSON.
    print(data_json)

    # Menampilkan judul bagian inspeksi data.
    print("\n== Informasi data awal ==")
    # Menampilkan jumlah baris, nama kolom, dan tipe data.
    data.info()

    # Mengubah kolom amount menjadi array NumPy.
    nilai_transaksi = np.array(data["amount"])
    # Menghitung dan menampilkan total transaksi dengan NumPy.
    print(f"\nTotal dengan NumPy: Rp{np.sum(nilai_transaksi):,.0f}")
    # Menghitung dan menampilkan rata-rata transaksi dengan NumPy.
    print(f"Rata-rata dengan NumPy: Rp{np.mean(nilai_transaksi):,.0f}")

    # Menjalankan function transformasi pada data awal.
    hasil, rata_rata, total = transformasi_data(data)

    # Menampilkan judul bagian hasil transformasi.
    print("\n== Data setelah transformasi ==")
    # Menampilkan DataFrame setelah rename dan filter.
    print(hasil)
    # Menampilkan rata-rata transaksi yang lolos filter.
    print(f"\nRata-rata transaksi yang lolos filter: Rp{rata_rata:,.0f}")
    # Menampilkan total transaksi yang lolos filter.
    print(f"Total transaksi yang lolos filter: Rp{total:,.0f}")

    # Menentukan folder output untuk menyimpan hasil.
    output_dir = BASE_DIR / "output"
    # Membuat folder output jika folder tersebut belum ada.
    output_dir.mkdir(exist_ok=True)
    # Menentukan nama file hasil transformasi.
    output_file = output_dir / "transaksi_terfilter.csv"
    # Menyimpan DataFrame hasil ke file CSV tanpa index tambahan.
    hasil.to_csv(output_file, index=False)
    # Memberi tahu lokasi file hasil kepada pengguna.
    print(f"Hasil tersimpan di: {output_file}")


# Menjalankan function main hanya ketika file dieksekusi langsung.
if __name__ == "__main__":
    main()
