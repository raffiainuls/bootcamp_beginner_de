-- Skema bootcamp: rantai pasok logistik kesehatan (data fiktif).
-- Bentuk tabel & relasi meniru warehouse produksi, isinya 100% hasil generator.
DROP SCHEMA IF EXISTS bootcamp CASCADE;
CREATE SCHEMA bootcamp;
SET search_path TO bootcamp;

-- ============================ master / referensi ============================
CREATE TABLE locations (
    id          INT PRIMARY KEY,
    name        TEXT NOT NULL,
    level       SMALLINT NOT NULL,          -- 0 provinsi, 1 kab/kota, 2 kecamatan
    parent_id   INT REFERENCES locations(id),
    code        TEXT NOT NULL
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
    entity_type_id   SMALLINT NOT NULL REFERENCES entity_types(id),
    parent_entity_id INT REFERENCES entities(id),
    province_id      INT REFERENCES locations(id),
    regency_id       INT REFERENCES locations(id),
    sub_district_id  INT REFERENCES locations(id),
    address          TEXT,
    lat              NUMERIC(10,6),
    lng              NUMERIC(10,6),
    is_vendor        SMALLINT NOT NULL DEFAULT 0,
    status           SMALLINT NOT NULL DEFAULT 1,
    created_at       TIMESTAMP NOT NULL,
    updated_at       TIMESTAMP NOT NULL
);

CREATE TABLE users (
    id         INT PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    email      TEXT,
    entity_id  INT NOT NULL REFERENCES entities(id),
    role       TEXT,
    status     SMALLINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE activities (
    id         SMALLINT PRIMARY KEY,
    name       TEXT NOT NULL,
    program_id SMALLINT NOT NULL
);

CREATE TABLE material_types (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE material_units (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);

CREATE TABLE materials (
    id                                    INT PRIMARY KEY,
    code                                  TEXT NOT NULL UNIQUE,
    parent_id                             INT REFERENCES materials(id),
    name                                  TEXT NOT NULL,
    material_type_id                      SMALLINT NOT NULL REFERENCES material_types(id),
    unit_of_consumption_id                SMALLINT REFERENCES material_units(id),
    unit_of_distribution_id               SMALLINT REFERENCES material_units(id),
    consumption_unit_per_distribution_unit INT,
    is_temperature_sensitive              SMALLINT NOT NULL DEFAULT 0,
    min_temperature                       NUMERIC(5,2),
    max_temperature                       NUMERIC(5,2),
    is_managed_in_batch                   SMALLINT NOT NULL DEFAULT 0,
    status                                SMALLINT NOT NULL DEFAULT 1,
    created_at                            TIMESTAMP NOT NULL,
    updated_at                            TIMESTAMP NOT NULL
);

CREATE TABLE entity_activities (
    id          INT PRIMARY KEY,
    entity_id   INT NOT NULL REFERENCES entities(id),
    activity_id SMALLINT NOT NULL REFERENCES activities(id),
    start_date  DATE,
    end_date    DATE,
    status      SMALLINT NOT NULL DEFAULT 1,
    created_at  TIMESTAMP NOT NULL,
    UNIQUE (entity_id, activity_id)
);

CREATE TABLE batches (
    id                    INT PRIMARY KEY,
    material_id           INT NOT NULL REFERENCES materials(id),
    code                  TEXT NOT NULL,
    manufacture_entity_id INT REFERENCES entities(id),
    produced_date         DATE,
    expired_date          DATE,
    created_at            TIMESTAMP NOT NULL
);

-- ============================ transaksional ============================
CREATE TABLE stocks (
    id                 INT PRIMARY KEY,
    entity_id          INT NOT NULL REFERENCES entities(id),
    activity_id        SMALLINT NOT NULL REFERENCES activities(id),
    material_id        INT NOT NULL REFERENCES materials(id),
    parent_material_id INT REFERENCES materials(id),
    batch_id           INT REFERENCES batches(id),
    qty_on_hand        BIGINT NOT NULL DEFAULT 0,
    created_at         TIMESTAMP NOT NULL,
    updated_at         TIMESTAMP NOT NULL,
    UNIQUE (entity_id, activity_id, material_id, batch_id)
);

CREATE TABLE order_types    (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE order_statuses (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE delivery_types (id SMALLINT PRIMARY KEY, name TEXT NOT NULL);

CREATE TABLE orders (
    id                INT PRIMARY KEY,
    no_document       TEXT NOT NULL,
    customer_id       INT NOT NULL REFERENCES entities(id),   -- yang meminta
    vendor_id         INT NOT NULL REFERENCES entities(id),   -- yang mengirim
    activity_id       SMALLINT NOT NULL REFERENCES activities(id),
    order_type_id     SMALLINT NOT NULL REFERENCES order_types(id),
    order_status_id   SMALLINT NOT NULL REFERENCES order_statuses(id),
    delivery_type_id  SMALLINT REFERENCES delivery_types(id),
    total_order_items INT NOT NULL DEFAULT 0,
    notes             TEXT,
    created_by        INT REFERENCES users(id),
    updated_by        INT REFERENCES users(id),
    created_at        TIMESTAMP NOT NULL,
    approved_at       TIMESTAMP,
    sent_at           TIMESTAMP,
    received_at       TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL,
    deleted_at        TIMESTAMP
);

CREATE TABLE order_items (
    id                 INT PRIMARY KEY,
    order_id           INT NOT NULL REFERENCES orders(id),
    material_id        INT NOT NULL REFERENCES materials(id),
    parent_material_id INT REFERENCES materials(id),
    qty_requested      BIGINT NOT NULL,
    qty_approved       BIGINT,
    qty_sent           BIGINT,
    created_at         TIMESTAMP NOT NULL,
    updated_at         TIMESTAMP NOT NULL
);

CREATE TABLE transaction_types (
    id        SMALLINT PRIMARY KEY,
    name      TEXT NOT NULL,
    direction SMALLINT NOT NULL            -- +1 menambah stok, -1 mengurangi
);

CREATE TABLE transaction_reasons (
    id                  SMALLINT PRIMARY KEY,
    transaction_type_id SMALLINT NOT NULL REFERENCES transaction_types(id),
    name                TEXT NOT NULL
);

CREATE TABLE transactions (
    id                    BIGINT PRIMARY KEY,
    uuid                  UUID NOT NULL,
    entity_id             INT NOT NULL REFERENCES entities(id),
    companion_entity_id   INT REFERENCES entities(id),  -- lawan transaksi (pemasok/penerima)
    activity_id           SMALLINT NOT NULL REFERENCES activities(id),
    stock_id              INT NOT NULL REFERENCES stocks(id),
    material_id           INT NOT NULL REFERENCES materials(id),
    parent_material_id    INT REFERENCES materials(id),
    batch_id              INT REFERENCES batches(id),
    order_id              INT REFERENCES orders(id),
    transaction_type_id   SMALLINT NOT NULL REFERENCES transaction_types(id),
    transaction_reason_id SMALLINT REFERENCES transaction_reasons(id),
    opening_qty           BIGINT NOT NULL,
    change_qty            BIGINT NOT NULL,   -- bertanda: negatif untuk pengeluaran
    closing_qty           BIGINT NOT NULL,   -- selalu = opening_qty + change_qty
    created_at            TIMESTAMP NOT NULL,
    updated_at            TIMESTAMP NOT NULL
);

-- ============================ index ============================
CREATE INDEX idx_entities_parent   ON entities (parent_entity_id);
CREATE INDEX idx_entities_regency  ON entities (regency_id);
CREATE INDEX idx_stocks_entity_mat ON stocks (entity_id, material_id);
CREATE INDEX idx_orders_customer   ON orders (customer_id, created_at);
CREATE INDEX idx_orders_vendor     ON orders (vendor_id, created_at);
CREATE INDEX idx_tx_created        ON transactions (created_at);
CREATE INDEX idx_tx_entity_created ON transactions (entity_id, created_at);
CREATE INDEX idx_tx_stock          ON transactions (stock_id, created_at);
CREATE INDEX idx_tx_type           ON transactions (transaction_type_id);
