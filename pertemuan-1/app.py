import logging
import sys

# konfig logging
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)

# logging.info("===== Memulai Pipeline ====")

# dummy data
data_barang = [
    {"nama": "Buku Tulis", "harga": 5000, "jumlah": 10},
    {"nama": "Pensil", "harga": 2000, "jumlah": 0},
    {"nama": "Keyboard", "harga": 200000, "jumlah": 20},
    {"nama": "Mouse", "harga": 50000, "jumlah": 10}
]

# hitung harga

logging.info("===== Memulai Pipeline ====")


for item, barang in enumerate(data_barang):
    nama = barang.get("nama")
    try:
        harga = barang['harga']
        jumlah = barang['jumlah']
        harga_satuan = int(harga)/int(jumlah)
        
        logging.info(f"SUKSES : {nama} harga {harga_satuan}")

    except ZeroDivisionError:
        logging.warning(f"PEMBERITAHUAN: {nama} jumlah barang 0")

    except TypeError:
        logging.error(f"TIPE DATA SALAH: {nama} harga dan jumlah harus number")

logging.info("===== pipeline selesai ====")

