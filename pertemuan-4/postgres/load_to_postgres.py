#!/usr/bin/env python3
"""Buat skema di PostgreSQL lalu muat semua CSV hasil generator.py ke dalamnya.

Semua tabel dibuat lengkap dengan PRIMARY KEY dan FOREIGN KEY, jadi diagram relasi
di DBeaver (Database Navigator -> tabel -> tab "ER Diagram") langsung menampilkan
garis antar tabel tanpa perlu digambar manual.

Contoh pakai:
    python3 load_to_postgres.py
    python3 load_to_postgres.py --host localhost --port 5433 \
                                --user postgresdev --password adminpass123 \
                                --dbname nusacode_db --csv-dir out
"""
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import psycopg2
except ImportError:
    sys.exit("psycopg2 belum terpasang. Jalankan: pip install psycopg2-binary")


# --------------------------------------------------------------------------- #
# DDL: dijalankan lebih dulu, sebelum satu baris data pun masuk.
# Setiap kolom *_id yang menunjuk tabel lain dibuat sebagai FOREIGN KEY supaya
# relasinya terbaca oleh tool diagram.
# --------------------------------------------------------------------------- #
DDL = """
DROP SCHEMA IF EXISTS {schema} CASCADE;
CREATE SCHEMA {schema};
SET search_path TO {schema};

-- ============================== master / referensi ==============================
CREATE TABLE locations (
    id        INT PRIMARY KEY,
    name      TEXT NOT NULL,
    level     SMALLINT NOT NULL,                 -- 0 provinsi, 1 kab/kota, 2 kecamatan
    parent_id INT,
    code      TEXT NOT NULL,
    CONSTRAINT fk_locations_parent FOREIGN KEY (parent_id) REFERENCES locations (id)
);

CREATE TABLE entity_types (
    id   SMALLINT PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT NOT NULL
);

CREATE TABLE entities (
    id               INT PRIMARY KEY,
    code             TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    entity_type_id   SMALLINT NOT NULL,
    parent_entity_id INT,                        -- gudang pemasok di atasnya
    province_id      INT,
    regency_id       INT,
    sub_district_id  INT,
    address          TEXT,
    lat              NUMERIC(10,6),
    lng              NUMERIC(10,6),
    is_vendor        SMALLINT NOT NULL DEFAULT 0,
    status           SMALLINT NOT NULL DEFAULT 1,
    created_at       TIMESTAMP NOT NULL,
    updated_at       TIMESTAMP NOT NULL,
    CONSTRAINT fk_entities_type     FOREIGN KEY (entity_type_id)   REFERENCES entity_types (id),
    CONSTRAINT fk_entities_parent   FOREIGN KEY (parent_entity_id) REFERENCES entities (id),
    CONSTRAINT fk_entities_province FOREIGN KEY (province_id)      REFERENCES locations (id),
    CONSTRAINT fk_entities_regency  FOREIGN KEY (regency_id)       REFERENCES locations (id),
    CONSTRAINT fk_entities_subdist  FOREIGN KEY (sub_district_id)  REFERENCES locations (id)
);

CREATE TABLE users (
    id         INT PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    email      TEXT,
    entity_id  INT NOT NULL,
    role       TEXT,
    status     SMALLINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_users_entity FOREIGN KEY (entity_id) REFERENCES entities (id)
);

CREATE TABLE activities (
    id         SMALLINT PRIMARY KEY,
    name       TEXT NOT NULL,
    program_id SMALLINT NOT NULL
);

CREATE TABLE material_types (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE material_units (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);

CREATE TABLE materials (
    id                                     INT PRIMARY KEY,
    code                                   TEXT NOT NULL UNIQUE,
    parent_id                              INT,          -- material induk
    name                                   TEXT NOT NULL,
    material_type_id                       SMALLINT NOT NULL,
    unit_of_consumption_id                 SMALLINT,
    unit_of_distribution_id                SMALLINT,
    consumption_unit_per_distribution_unit INT,
    is_temperature_sensitive               SMALLINT NOT NULL DEFAULT 0,
    min_temperature                        NUMERIC(5,2),
    max_temperature                        NUMERIC(5,2),
    is_managed_in_batch                    SMALLINT NOT NULL DEFAULT 0,
    status                                 SMALLINT NOT NULL DEFAULT 1,
    created_at                             TIMESTAMP NOT NULL,
    updated_at                             TIMESTAMP NOT NULL,
    CONSTRAINT fk_materials_parent FOREIGN KEY (parent_id)               REFERENCES materials (id),
    CONSTRAINT fk_materials_type   FOREIGN KEY (material_type_id)        REFERENCES material_types (id),
    CONSTRAINT fk_materials_uoc    FOREIGN KEY (unit_of_consumption_id)  REFERENCES material_units (id),
    CONSTRAINT fk_materials_uod    FOREIGN KEY (unit_of_distribution_id) REFERENCES material_units (id)
);

CREATE TABLE entity_activities (
    id          INT PRIMARY KEY,
    entity_id   INT NOT NULL,
    activity_id SMALLINT NOT NULL,
    start_date  DATE,
    end_date    DATE,
    status      SMALLINT NOT NULL DEFAULT 1,
    created_at  TIMESTAMP NOT NULL,
    CONSTRAINT uq_entity_activities UNIQUE (entity_id, activity_id),
    CONSTRAINT fk_ea_entity   FOREIGN KEY (entity_id)   REFERENCES entities (id),
    CONSTRAINT fk_ea_activity FOREIGN KEY (activity_id) REFERENCES activities (id)
);

CREATE TABLE batches (
    id                    INT PRIMARY KEY,
    material_id           INT NOT NULL,
    code                  TEXT NOT NULL,
    manufacture_entity_id INT,
    produced_date         DATE,
    expired_date          DATE,
    created_at            TIMESTAMP NOT NULL,
    CONSTRAINT fk_batches_material FOREIGN KEY (material_id)           REFERENCES materials (id),
    CONSTRAINT fk_batches_producer FOREIGN KEY (manufacture_entity_id) REFERENCES entities (id)
);

-- ================================ transaksional ================================
CREATE TABLE stocks (
    id                 INT PRIMARY KEY,
    entity_id          INT NOT NULL,
    activity_id        SMALLINT NOT NULL,
    material_id        INT NOT NULL,
    parent_material_id INT,
    batch_id           INT,
    qty_on_hand        BIGINT NOT NULL DEFAULT 0,
    created_at         TIMESTAMP NOT NULL,
    updated_at         TIMESTAMP NOT NULL,
    CONSTRAINT uq_stocks UNIQUE (entity_id, activity_id, material_id, batch_id),
    CONSTRAINT fk_stocks_entity    FOREIGN KEY (entity_id)          REFERENCES entities (id),
    CONSTRAINT fk_stocks_activity  FOREIGN KEY (activity_id)        REFERENCES activities (id),
    CONSTRAINT fk_stocks_material  FOREIGN KEY (material_id)        REFERENCES materials (id),
    CONSTRAINT fk_stocks_parentmat FOREIGN KEY (parent_material_id) REFERENCES materials (id),
    CONSTRAINT fk_stocks_batch     FOREIGN KEY (batch_id)           REFERENCES batches (id)
);

CREATE TABLE order_types    (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE order_statuses (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE delivery_types (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);

CREATE TABLE orders (
    id                INT PRIMARY KEY,
    no_document       TEXT NOT NULL,
    customer_id       INT NOT NULL,                -- entitas yang meminta
    vendor_id         INT NOT NULL,                -- entitas yang mengirim
    activity_id       SMALLINT NOT NULL,
    order_type_id     SMALLINT NOT NULL,
    order_status_id   SMALLINT NOT NULL,
    delivery_type_id  SMALLINT,
    total_order_items INT NOT NULL DEFAULT 0,
    notes             TEXT,
    created_by        INT,
    updated_by        INT,
    created_at        TIMESTAMP NOT NULL,
    approved_at       TIMESTAMP,
    sent_at           TIMESTAMP,
    received_at       TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL,
    deleted_at        TIMESTAMP,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)      REFERENCES entities (id),
    CONSTRAINT fk_orders_vendor   FOREIGN KEY (vendor_id)        REFERENCES entities (id),
    CONSTRAINT fk_orders_activity FOREIGN KEY (activity_id)      REFERENCES activities (id),
    CONSTRAINT fk_orders_type     FOREIGN KEY (order_type_id)    REFERENCES order_types (id),
    CONSTRAINT fk_orders_status   FOREIGN KEY (order_status_id)  REFERENCES order_statuses (id),
    CONSTRAINT fk_orders_delivery FOREIGN KEY (delivery_type_id) REFERENCES delivery_types (id),
    CONSTRAINT fk_orders_cby      FOREIGN KEY (created_by)       REFERENCES users (id),
    CONSTRAINT fk_orders_uby      FOREIGN KEY (updated_by)       REFERENCES users (id)
);

CREATE TABLE order_items (
    id                 INT PRIMARY KEY,
    order_id           INT NOT NULL,
    material_id        INT NOT NULL,
    parent_material_id INT,
    qty_requested      BIGINT NOT NULL,
    qty_approved       BIGINT,
    qty_sent           BIGINT,
    created_at         TIMESTAMP NOT NULL,
    updated_at         TIMESTAMP NOT NULL,
    CONSTRAINT fk_oi_order     FOREIGN KEY (order_id)           REFERENCES orders (id),
    CONSTRAINT fk_oi_material  FOREIGN KEY (material_id)        REFERENCES materials (id),
    CONSTRAINT fk_oi_parentmat FOREIGN KEY (parent_material_id) REFERENCES materials (id)
);

CREATE TABLE transaction_types (
    id        SMALLINT PRIMARY KEY,
    name      TEXT NOT NULL,
    direction SMALLINT NOT NULL                   -- +1 menambah stok, -1 mengurangi
);

CREATE TABLE transaction_reasons (
    id                  SMALLINT PRIMARY KEY,
    transaction_type_id SMALLINT NOT NULL,
    name                TEXT NOT NULL,
    CONSTRAINT fk_reasons_type FOREIGN KEY (transaction_type_id) REFERENCES transaction_types (id)
);

CREATE TABLE transactions (
    id                    BIGINT PRIMARY KEY,
    uuid                  UUID NOT NULL,
    entity_id             INT NOT NULL,
    companion_entity_id   INT,                    -- lawan transaksi (pemasok / penerima)
    activity_id           SMALLINT NOT NULL,
    stock_id              INT NOT NULL,
    material_id           INT NOT NULL,
    parent_material_id    INT,
    batch_id              INT,
    order_id              INT,
    transaction_type_id   SMALLINT NOT NULL,
    transaction_reason_id SMALLINT,
    opening_qty           BIGINT NOT NULL,
    change_qty            BIGINT NOT NULL,        -- bertanda: negatif untuk pengeluaran
    closing_qty           BIGINT NOT NULL,        -- selalu = opening_qty + change_qty
    created_at            TIMESTAMP NOT NULL,
    updated_at            TIMESTAMP NOT NULL,
    CONSTRAINT fk_tx_entity    FOREIGN KEY (entity_id)             REFERENCES entities (id),
    CONSTRAINT fk_tx_companion FOREIGN KEY (companion_entity_id)   REFERENCES entities (id),
    CONSTRAINT fk_tx_activity  FOREIGN KEY (activity_id)           REFERENCES activities (id),
    CONSTRAINT fk_tx_stock     FOREIGN KEY (stock_id)              REFERENCES stocks (id),
    CONSTRAINT fk_tx_material  FOREIGN KEY (material_id)           REFERENCES materials (id),
    CONSTRAINT fk_tx_parentmat FOREIGN KEY (parent_material_id)    REFERENCES materials (id),
    CONSTRAINT fk_tx_batch     FOREIGN KEY (batch_id)              REFERENCES batches (id),
    CONSTRAINT fk_tx_order     FOREIGN KEY (order_id)              REFERENCES orders (id),
    CONSTRAINT fk_tx_type      FOREIGN KEY (transaction_type_id)   REFERENCES transaction_types (id),
    CONSTRAINT fk_tx_reason    FOREIGN KEY (transaction_reason_id) REFERENCES transaction_reasons (id)
);

-- ==================================== index ====================================
CREATE INDEX idx_entities_parent    ON entities (parent_entity_id);
CREATE INDEX idx_entities_regency   ON entities (regency_id);
CREATE INDEX idx_stocks_entity_mat  ON stocks (entity_id, material_id);
CREATE INDEX idx_orders_customer    ON orders (customer_id, created_at);
CREATE INDEX idx_orders_vendor      ON orders (vendor_id, created_at);
CREATE INDEX idx_tx_created         ON transactions (created_at);
CREATE INDEX idx_tx_entity_created  ON transactions (entity_id, created_at);
CREATE INDEX idx_tx_stock           ON transactions (stock_id, created_at);
CREATE INDEX idx_tx_type            ON transactions (transaction_type_id);

-- ================================== keterangan =================================
COMMENT ON TABLE locations           IS 'Wilayah berjenjang: provinsi, kabupaten/kota, kecamatan';
COMMENT ON TABLE entities            IS 'Gudang, fasilitas pelayanan, dan distributor';
COMMENT ON TABLE activities          IS 'Program/kegiatan; stok selalu dipisah per program';
COMMENT ON TABLE materials           IS 'Produk; parent_id menunjuk material induk';
COMMENT ON TABLE batches             IS 'Nomor batch beserta tanggal kedaluwarsa';
COMMENT ON TABLE stocks              IS 'Saldo per kombinasi entitas, program, material, batch';
COMMENT ON TABLE orders              IS 'Permintaan barang dari entitas hilir ke hulu';
COMMENT ON TABLE order_items         IS 'Rincian material pada tiap permintaan';
COMMENT ON TABLE transactions        IS 'Buku besar mutasi stok; opening_qty + change_qty = closing_qty';
"""

# Urutan muat penting: tabel yang dirujuk harus terisi lebih dulu.
TABLES = [
    "locations", "entity_types", "entities", "users", "activities",
    "material_types", "material_units", "materials", "entity_activities",
    "batches", "stocks", "order_types", "order_statuses", "delivery_types",
    "orders", "order_items", "transaction_types", "transaction_reasons",
    "transactions",
]


def build_dsn(args):
    if args.dsn:
        return args.dsn
    return (
        "host={} port={} dbname={} user={} password={}"
        .format(args.host, args.port, args.dbname, args.user, args.password)
    )


def create_schema(conn, schema):
    print("membuat skema '{}' beserta relasinya...".format(schema))
    with conn.cursor() as cur:
        cur.execute(DDL.format(schema=schema))
    conn.commit()
    print("  skema siap")


def load_csv(conn, schema, csv_dir):
    total = 0
    for table in TABLES:
        path = os.path.join(csv_dir, table + ".csv")
        if not os.path.exists(path):
            print("  {:<22} DILEWATI (file tidak ada)".format(table))
            continue
        with open(path, "r", encoding="utf-8") as fh:
            header = fh.readline().strip()
            fh.seek(0)
            sql = (
                "COPY {}.{} ({}) FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')"
                .format(schema, table, header)
            )
            with conn.cursor() as cur:
                cur.copy_expert(sql, fh)
                cur.execute("SELECT count(*) FROM {}.{}".format(schema, table))
                n = cur.fetchone()[0]
        conn.commit()
        total += n
        print("  {:<22} {:>9,} baris".format(table, n))
    print("total {:,} baris dimuat".format(total))


def verify(conn, schema):
    """Cek relasi terpasang dan saldo stok cocok dengan buku besar transaksi."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM information_schema.table_constraints "
            "WHERE constraint_schema = %s AND constraint_type = 'FOREIGN KEY'",
            (schema,),
        )
        fk_count = cur.fetchone()[0]

        cur.execute(
            "SELECT count(*) FROM {s}.stocks s "
            "JOIN (SELECT stock_id, sum(change_qty) AS saldo "
            "      FROM {s}.transactions GROUP BY stock_id) l ON l.stock_id = s.id "
            "WHERE s.qty_on_hand <> l.saldo".format(s=schema)
        )
        mismatch = cur.fetchone()[0]

    print("\npemeriksaan")
    print("  foreign key terpasang   : {}".format(fk_count))
    print("  selisih stok vs ledger  : {} (harus 0)".format(mismatch))
    if mismatch:
        print("  PERINGATAN: data tidak konsisten, cek ulang CSV-nya")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", help="connection string utuh; kalau diisi, opsi host/user diabaikan")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", default=os.environ.get("PGPORT", "5433"))
    ap.add_argument("--dbname", default=os.environ.get("PGDATABASE", "nusacode_db"))
    ap.add_argument("--user", default=os.environ.get("PGUSER", "postgresdev"))
    ap.add_argument("--password", default=os.environ.get("PGPASSWORD", "adminpass123"))
    ap.add_argument("--schema", default="bootcamp")
    ap.add_argument(
        "--csv-dir",
        dest="csv_dir",
        default=None,
        help="folder CSV; default: out/ di folder script ini",
    )
    args = ap.parse_args()

    csv_dir = args.csv_dir or os.path.join(SCRIPT_DIR, "out")
    if not os.path.isdir(csv_dir) and not os.path.isabs(csv_dir):
        script_relative_dir = os.path.join(SCRIPT_DIR, csv_dir)
        if os.path.isdir(script_relative_dir):
            csv_dir = script_relative_dir

    if not os.path.isdir(csv_dir):
        sys.exit("folder CSV tidak ditemukan: {}".format(csv_dir))

    conn = psycopg2.connect(build_dsn(args))
    try:
        create_schema(conn, args.schema)
        print("memuat CSV dari '{}'...".format(csv_dir))
        load_csv(conn, args.schema, csv_dir)
        verify(conn, args.schema)
    finally:
        conn.close()
    print("\nselesai. Di DBeaver: buka skema '{}' -> klik kanan -> View Diagram".format(args.schema))


if __name__ == "__main__":
    main()
