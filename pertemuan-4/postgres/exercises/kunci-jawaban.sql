-- Kunci jawaban latihan SQL (PostgreSQL). Jalankan: psql "$DSN" -f exercises/kunci-jawaban.sql
SET search_path TO bootcamp;

-- ============================ LEVEL 1 - SELECT & WHERE ============================

-- 1. Daftar semua fasilitas pelayanan (entity_type_id = 4) di satu provinsi.
SELECT id, code, name, address
FROM entities
WHERE entity_type_id = 4
  AND province_id = 1
ORDER BY name
LIMIT 20;

-- 2. Material rantai dingin yang butuh suhu 2-8 derajat.
SELECT code, name, min_temperature, max_temperature
FROM materials
WHERE is_temperature_sensitive = 1
ORDER BY name;

-- 3. Batch yang sudah kedaluwarsa per 1 Juni 2026.
SELECT b.code AS batch_code, m.name AS material_name, b.expired_date
FROM batches b
JOIN materials m ON m.id = b.material_id
WHERE b.expired_date < DATE '2026-06-01'
ORDER BY b.expired_date;

-- ============================ LEVEL 2 - JOIN ============================

-- 4. Stok on-hand per fasilitas, lengkap dengan nama material dan batch.
SELECT e.name AS entity_name, m.name AS material_name, b.code AS batch_code,
       s.qty_on_hand, b.expired_date
FROM stocks s
JOIN entities e  ON e.id = s.entity_id
JOIN materials m ON m.id = s.material_id
LEFT JOIN batches b ON b.id = s.batch_id
WHERE s.qty_on_hand > 0
ORDER BY e.name, m.name
LIMIT 25;

-- 5. Rantai wilayah: fasilitas -> kabupaten -> provinsi (self join ke locations).
SELECT e.name AS entity_name, reg.name AS regency_name, prov.name AS province_name
FROM entities e
LEFT JOIN locations reg  ON reg.id  = e.regency_id
LEFT JOIN locations prov ON prov.id = e.province_id
WHERE e.entity_type_id = 4
ORDER BY province_name, regency_name, entity_name
LIMIT 25;

-- 6. Hierarki gudang: setiap entitas beserta induk pemasoknya (self join ke entities).
SELECT child.name AS entity_name, et.name AS entity_type_name,
       parent.name AS supplied_by
FROM entities child
JOIN entity_types et ON et.id = child.entity_type_id
LEFT JOIN entities parent ON parent.id = child.parent_entity_id
ORDER BY child.entity_type_id, child.name
LIMIT 25;

-- ============================ LEVEL 3 - AGREGASI ============================

-- 7. Jumlah fasilitas per provinsi.
SELECT prov.name AS province_name, COUNT(*) AS total_facilities
FROM entities e
JOIN locations prov ON prov.id = e.province_id
WHERE e.entity_type_id = 4
GROUP BY prov.name
ORDER BY total_facilities DESC;

-- 8. Total pemakaian (transaction_type_id = 10) per material per bulan.
SELECT DATE_TRUNC('month', t.created_at)::date AS month,
       m.name                                  AS material_name,
       SUM(ABS(t.change_qty))                  AS total_consumed
FROM transactions t
JOIN materials m ON m.id = t.material_id
WHERE t.transaction_type_id = 10
GROUP BY 1, 2
ORDER BY 1, total_consumed DESC
LIMIT 30;

-- 9. Provinsi dengan pemusnahan kedaluwarsa (reason 9) di atas 10.000 dosis.
SELECT prov.name AS province_name, SUM(ABS(t.change_qty)) AS total_expired
FROM transactions t
JOIN entities e     ON e.id = t.entity_id
JOIN locations prov ON prov.id = e.province_id
WHERE t.transaction_reason_id = 9
GROUP BY prov.name
HAVING SUM(ABS(t.change_qty)) > 10000
ORDER BY total_expired DESC;

-- 10. Komposisi transaksi per jenis.
SELECT tt.name AS transaction_type_name, COUNT(*) AS trx_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM transactions t
JOIN transaction_types tt ON tt.id = t.transaction_type_id
GROUP BY tt.name
ORDER BY trx_count DESC;

-- ============================ LEVEL 4 - CTE & SUBQUERY ============================

-- 11. Fill rate pesanan: berapa persen dari yang diminta benar-benar dikirim.
WITH per_order AS (
    SELECT o.id, o.no_document, o.order_status_id,
           SUM(oi.qty_requested)             AS qty_requested,
           SUM(COALESCE(oi.qty_sent, 0))     AS qty_sent
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.no_document, o.order_status_id
)
SELECT os.name AS order_status_name,
       COUNT(*)                                            AS total_orders,
       ROUND(100.0 * SUM(qty_sent) / SUM(qty_requested), 2) AS fill_rate_pct
FROM per_order p
JOIN order_statuses os ON os.id = p.order_status_id
GROUP BY os.name
ORDER BY total_orders DESC;

-- 12. Fasilitas yang belum pernah memesan sama sekali.
SELECT e.code, e.name
FROM entities e
WHERE e.entity_type_id = 4
  AND NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = e.id)
ORDER BY e.name;

-- 13. Material yang pemakaiannya di atas rata-rata semua material.
WITH usage_per_material AS (
    SELECT material_id, SUM(ABS(change_qty)) AS total_used
    FROM transactions
    WHERE transaction_type_id = 10
    GROUP BY material_id
)
SELECT m.name AS material_name, u.total_used
FROM usage_per_material u
JOIN materials m ON m.id = u.material_id
WHERE u.total_used > (SELECT AVG(total_used) FROM usage_per_material)
ORDER BY u.total_used DESC;

-- ============================ LEVEL 5 - WINDOW FUNCTION ============================

-- 14. Tiga fasilitas dengan pemakaian terbesar di setiap provinsi.
WITH usage_per_entity AS (
    SELECT t.entity_id, SUM(ABS(t.change_qty)) AS total_used
    FROM transactions t
    WHERE t.transaction_type_id = 10
    GROUP BY t.entity_id
), ranked AS (
    SELECT prov.name AS province_name, e.name AS entity_name, u.total_used,
           ROW_NUMBER() OVER (PARTITION BY prov.name ORDER BY u.total_used DESC) AS rn
    FROM usage_per_entity u
    JOIN entities e     ON e.id = u.entity_id
    JOIN locations prov ON prov.id = e.province_id
)
SELECT province_name, entity_name, total_used
FROM ranked
WHERE rn <= 3
ORDER BY province_name, total_used DESC;

-- 15. Kartu stok satu stock_id: saldo berjalan dari ledger transaksi.
SELECT t.created_at, tt.name AS transaction_type_name, t.opening_qty, t.change_qty,
       SUM(t.change_qty) OVER (PARTITION BY t.stock_id ORDER BY t.created_at, t.id) AS running_balance
FROM transactions t
JOIN transaction_types tt ON tt.id = t.transaction_type_id
WHERE t.stock_id = (SELECT MIN(stock_id) FROM transactions)
ORDER BY t.created_at, t.id
LIMIT 30;

-- 16. Pertumbuhan pemakaian bulan ke bulan (LAG).
WITH monthly AS (
    SELECT DATE_TRUNC('month', created_at)::date AS month,
           SUM(ABS(change_qty))                  AS total_used
    FROM transactions
    WHERE transaction_type_id = 10
    GROUP BY 1
)
SELECT month, total_used,
       LAG(total_used) OVER (ORDER BY month) AS prev_month,
       ROUND(100.0 * (total_used - LAG(total_used) OVER (ORDER BY month))
             / NULLIF(LAG(total_used) OVER (ORDER BY month), 0), 2) AS growth_pct
FROM monthly
ORDER BY month;

-- ============================ LEVEL 6 - LOGIKA BISNIS ============================

-- 17. Lead time pesanan: berapa hari dari diajukan sampai diterima.
SELECT os.name AS order_status_name,
       COUNT(*) AS total_orders,
       ROUND(AVG(EXTRACT(EPOCH FROM (o.received_at - o.created_at)) / 86400)::numeric, 2) AS avg_lead_time_days
FROM orders o
JOIN order_statuses os ON os.id = o.order_status_id
WHERE o.received_at IS NOT NULL
GROUP BY os.name;

-- 18. Barang dalam perjalanan: sudah dikirim tapi belum diterima.
SELECT o.no_document, v.name AS vendor_name, c.name AS customer_name,
       o.sent_at, SUM(oi.qty_sent) AS qty_in_transit
FROM orders o
JOIN entities v ON v.id = o.vendor_id
JOIN entities c ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
WHERE o.order_status_id = 4
GROUP BY o.no_document, v.name, c.name, o.sent_at
ORDER BY o.sent_at;

-- 19. Stok yang akan kedaluwarsa dalam 90 hari ke depan dan masih bersaldo.
SELECT e.name AS entity_name, m.name AS material_name, b.code AS batch_code,
       b.expired_date, s.qty_on_hand,
       (b.expired_date - DATE '2026-06-30') AS days_to_expiry
FROM stocks s
JOIN batches b   ON b.id = s.batch_id
JOIN materials m ON m.id = s.material_id
JOIN entities e  ON e.id = s.entity_id
WHERE s.qty_on_hand > 0
  AND b.expired_date BETWEEN DATE '2026-06-30' AND DATE '2026-06-30' + 90
ORDER BY b.expired_date
LIMIT 25;

-- 20. UJI INTEGRITAS: saldo stocks harus sama dengan hasil penjumlahan ledger.
--     Query ini harus mengembalikan 0 baris.
WITH ledger AS (
    SELECT stock_id, SUM(change_qty) AS computed_balance
    FROM transactions
    GROUP BY stock_id
)
SELECT s.id, s.qty_on_hand, l.computed_balance
FROM stocks s
JOIN ledger l ON l.stock_id = s.id
WHERE s.qty_on_hand <> l.computed_balance;
