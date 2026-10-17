-- Latihan SQL - Bootcamp Data Engineer Pertemuan 4
-- Tulis query-mu di bawah tiap soal. Kunci ada di exercises/kunci-jawaban.sql
SET search_path TO bootcamp;


-- ============================ LEVEL 1 - SELECT & WHERE ============================

-- 1. Daftar semua fasilitas pelayanan (entity_type_id = 4) di satu provinsi.



-- 2. Material rantai dingin yang butuh suhu 2-8 derajat.



-- 3. Batch yang sudah kedaluwarsa per 1 Juni 2026.




-- ============================ LEVEL 2 - JOIN ============================

-- 4. Stok on-hand per fasilitas, lengkap dengan nama material dan batch.



-- 5. Rantai wilayah: fasilitas -> kabupaten -> provinsi (self join ke locations).



-- 6. Hierarki gudang: setiap entitas beserta induk pemasoknya (self join ke entities).




-- ============================ LEVEL 3 - AGREGASI ============================

-- 7. Jumlah fasilitas per provinsi.



-- 8. Total pemakaian (transaction_type_id = 10) per material per bulan.



-- 9. Provinsi dengan pemusnahan kedaluwarsa (reason 9) di atas 10.000 dosis.



-- 10. Komposisi transaksi per jenis.




-- ============================ LEVEL 4 - CTE & SUBQUERY ============================

-- 11. Fill rate pesanan: berapa persen dari yang diminta benar-benar dikirim.



-- 12. Fasilitas yang belum pernah memesan sama sekali.



-- 13. Material yang pemakaiannya di atas rata-rata semua material.




-- ============================ LEVEL 5 - WINDOW FUNCTION ============================

-- 14. Tiga fasilitas dengan pemakaian terbesar di setiap provinsi.



-- 15. Kartu stok satu stock_id: saldo berjalan dari ledger transaksi.



-- 16. Pertumbuhan pemakaian bulan ke bulan (LAG).




-- ============================ LEVEL 6 - LOGIKA BISNIS ============================

-- 17. Lead time pesanan: berapa hari dari diajukan sampai diterima.



-- 18. Barang dalam perjalanan: sudah dikirim tapi belum diterima.



-- 19. Stok yang akan kedaluwarsa dalam 90 hari ke depan dan masih bersaldo.



-- 20. UJI INTEGRITAS: saldo stocks harus sama dengan hasil penjumlahan ledger.



--     Query ini harus mengembalikan 0 baris.
