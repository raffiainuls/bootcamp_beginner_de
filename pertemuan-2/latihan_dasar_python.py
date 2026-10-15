"""Latihan dasar Python untuk pemula.

Contoh use case: mencatat transaksi sederhana dan mengecek transaksi
sebelum diproses oleh pipeline data.
"""


# 1. Variabel dengan beberapa tipe data dasar
# Menyimpan nama pipeline ke dalam variabel berbentuk string.
nama_pipeline = "Pipeline Transaksi"
# Menyimpan jumlah transaksi ke dalam variabel berbentuk integer.
jumlah_transaksi = 3
# Menyimpan status aktif pipeline ke dalam variabel berbentuk boolean.
pipeline_aktif = True

# Menampilkan nama pipeline ke terminal.
print("Nama pipeline:", nama_pipeline)
# Menampilkan jumlah transaksi ke terminal.
print("Jumlah transaksi:", jumlah_transaksi)
# Menampilkan status pipeline ke terminal.
print("Pipeline aktif:", pipeline_aktif)

# 2. List untuk menyimpan beberapa nilai
# Membuat list yang berisi beberapa nama pelanggan.
nama_pelanggan = ["Andi", "Budi", "Citra"]
# Membuat baris kosong agar output lebih mudah dibaca.
print("\nDaftar pelanggan:")
# Mengambil nama pelanggan satu per satu dari dalam list.
for nama in nama_pelanggan:
    # Menampilkan nama pelanggan yang sedang diproses.
    print("-", nama)

# 3. Dictionary untuk menyimpan satu record transaksi
# Membuat dictionary untuk menyimpan satu transaksi.
transaksi = {
    # Menyimpan ID transaksi.
    "id": "TRX-001",
    # Menyimpan nama pelanggan.
    "pelanggan": "Andi",
    # Menyimpan jumlah transaksi dalam bentuk integer.
    "jumlah": 150000,
    # Menyimpan status pembayaran transaksi.
    "status": "paid",
}

# Menampilkan seluruh isi dictionary transaksi.
print("\nSatu transaksi:", transaksi)
# Mengambil dan menampilkan nilai dari key pelanggan.
print("Nama pelanggan:", transaksi["pelanggan"])

# 4. If untuk validasi sederhana
# Memeriksa apakah status transaksi sama dengan paid.
if transaksi["status"] == "paid":
    # Perintah ini dijalankan jika kondisi bernilai benar.
    print("Transaksi sudah dibayar")
else:
    # Perintah ini dijalankan jika kondisi bernilai salah.
    print("Transaksi belum dibayar")

# 5. Function agar aturan dapat digunakan kembali
# Membuat function dengan parameter bernama data.
def cek_transaksi(data):
    # Memeriksa status transaksi yang diterima oleh function.
    if data["status"] == "paid":
        # Mengembalikan teks valid jika transaksi sudah dibayar.
        return "valid"
    # Mengembalikan teks lain jika transaksi belum dibayar.
    return "perlu diperiksa"


# Memanggil function dengan data transaksi sebagai argumen.
print("Hasil pengecekan:", cek_transaksi(transaksi))
