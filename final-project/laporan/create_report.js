const {
  AlignmentType, BorderStyle, Document, HeadingLevel, PageBreak, Packer,
  Paragraph, ShadingType, Table, TableCell, TableRow, TextRun, WidthType,
} = require('docx');
const fs = require('fs');
const path = require('path');

const out = path.join(__dirname, 'Laporan Tugas Akhir - YouTube Trend Analytics.docx');
const blue = '1F4E79';
const lightBlue = 'D9EAF7';
const cell = (text, bold=false) => new TableCell({
  width: { size: 3000, type: WidthType.DXA },
  shading: { type: ShadingType.CLEAR, fill: bold ? lightBlue : 'FFFFFF' },
  children: [new Paragraph({ children: [new TextRun({ text, bold })] })],
});
const heading = (text, level) => new Paragraph({ heading: level, children: [new TextRun({ text, color: blue })] });
const para = (text) => new Paragraph({ spacing: { after: 100, line: 252 }, children: [new TextRun(text)] });
const bullet = (text) => new Paragraph({ bullet: { level: 0 }, spacing: { after: 40 }, children: [new TextRun(text)] });
const code = (text) => new Paragraph({ style: 'No Spacing', shading: { type: ShadingType.CLEAR, fill: 'F2F2F2' }, children: [new TextRun({ text, font: 'Courier New', size: 16 })] });
const title = new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 2600, after: 300 }, children: [new TextRun({ text: 'YOUTUBE TREND ANALYTICS PIPELINE', bold: true, size: 34, color: blue })] });
const subtitle = new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 2600 }, children: [new TextRun({ text: 'Laporan Tugas Akhir Bootcamp Data Engineer', size: 24 })] });

const children = [
  title, subtitle,
  para('Project ini membangun data platform mini untuk menyediakan data siap analisis. Dataset YouTube Trending dimuat ke ClickHouse, ditransformasikan dengan dbt, diorkestrasi Dagster, disajikan melalui FastAPI, dan divisualisasikan dalam web dashboard interaktif.'),
  new Paragraph({ children: [new PageBreak()] }),
  heading('A. Latar Belakang dan Tujuan', HeadingLevel.HEADING_1),
  para('YouTube menjadi salah satu sumber sinyal tentang minat, budaya digital, dan konsumsi media masyarakat Indonesia. Data trending berbentuk CSV belum langsung siap digunakan karena timestamp masih memiliki suffix UTC, tipe data belum terdefinisi, sebagian metrik kosong, dan kategori masih berupa ID.'),
  para('Tujuan project adalah membangun pipeline ELT yang memuat data/source/youtube_trending_dataset.csv ke ClickHouse, melakukan cleaning dan typing dengan dbt, mengorkestrasi eksekusi dengan Dagster, serta menyediakan data mart untuk trend analysis, creator analytics, engagement research, content strategy, dan cultural insights.'),
  heading('B. Masalah dan Solusi', HeadingLevel.HEADING_1),
  heading('B.1 Masalah', HeadingLevel.HEADING_2),
  ...['Sumber data hanya berupa file CSV.', 'Timestamp UTC belum sesuai kebutuhan analisis WIB.', 'Metrik engagement memiliki nilai kosong.', 'Category ID belum memiliki nama kategori.', 'Satu video dapat muncul pada banyak snapshot trending.', 'Data analyst membutuhkan tabel agregat siap chart.'].map(bullet),
  heading('B.2 Solusi', HeadingLevel.HEADING_2),
  para('Pipeline menerapkan pola ELT: extract dari tiga CSV, load ke bronze dengan kolom String, lalu transform menggunakan dbt. Silver melakukan parsing timestamp, konversi UTC ke WIB, pembersihan teks, casting numerik, perhitungan durasi, validasi, dan join master kategori. Gold menyediakan tabel agregat untuk dashboard.'),
  heading('C. Teknologi dan Tools', HeadingLevel.HEADING_1),
  heading('C.1 Teknologi Utama', HeadingLevel.HEADING_2),
  ...['Python untuk membaca CSV dan load batch.', 'ClickHouse sebagai analytical data warehouse.', 'dbt Core dan dbt-clickhouse untuk transformasi SQL serta testing.', 'Dagster untuk orkestrasi, retry, scheduling, dan monitoring.', 'FastAPI untuk query API analitik.', 'HTML, CSS, JavaScript, dan Chart.js untuk dashboard web.', 'Docker Compose untuk menjalankan seluruh service secara terisolasi.'].map(bullet),
  heading('C.2 Arsitektur Sistem', HeadingLevel.HEADING_2),
  code('Dagster -> Python loader -> bronze -> dbt silver/gold -> tests -> FastAPI -> Web dashboard'),
  para('Semua komponen berada di folder final-project. ClickHouse memakai port 18123/19000, Dagster UI 13000, dan web dashboard 18080.'),
  heading('D. Fitur', HeadingLevel.HEADING_1),
  heading('D.1 Extract dan Load CSV', HeadingLevel.HEADING_2),
  para('ingestion/load_clickhouse.py membaca dataset dan master CSV, membuat database bronze, tabel raw_youtube_trending, raw_category_master, dan raw_season_calendar, lalu memasukkan data. Semua kolom raw disimpan sebagai String untuk menjaga bentuk sumber dan auditability.'),
  heading('D.2 Silver Cleaning dan Standardisasi', HeadingLevel.HEADING_2),
  ...['Menghapus suffix UTC sebelum parsing.', 'Menambahkan 7 jam untuk membentuk waktu WIB.', 'Mengubah rank, category ID, dan metrik menjadi numerik.', 'Mengubah durasi menjadi detik dan menit.', 'Menangani metric kosong dan membersihkan whitespace.', 'Memfilter record invalid dan melakukan enrichment kategori.'].map(bullet),
  heading('D.3 Gold Data Mart', HeadingLevel.HEADING_2),
  new Table({ width: { size: 9000, type: WidthType.DXA }, columnWidths: [3600, 5400], rows: [
    new TableRow({ children: [cell('Tabel', true), cell('Kebutuhan dashboard', true)] }),
    ...[['mart_daily_category_trends','Tren kategori per hari'], ['mart_monthly_content_trends','Perbandingan kategori lintas tahun dan bulan'], ['mart_channel_trends','Ranking channel'], ['mart_seasonal_trends','Ramadan, pemilu, akhir tahun, reguler'], ['mart_content_performance','Views, likes, comments, rank, durasi']].map(([a,b]) => new TableRow({ children: [cell(a), cell(b)] })),
  ]}),
  heading('D.4 Orkestrasi Dagster', HeadingLevel.HEADING_2),
  para('Job youtube_trending_elt_job menjalankan lima tahap berurutan dan hanya melanjutkan jika tahap sebelumnya berhasil.'),
  ...['load_bronze: memuat tiga CSV ke tabel bronze.raw_*.', 'build_silver: menjalankan model dbt silver.', 'build_gold: membangun lima data mart gold.', 'run_data_tests: menjalankan source dan model tests dbt.', 'validate_warehouse: memeriksa row count dan memastikan mart tidak kosong.'].map(bullet),
  para('Setiap tahap mempunyai log sendiri dan retry otomatis maksimal dua kali. Schedule pukul 02.00 WIB tersedia dalam kondisi nonaktif dan dapat diaktifkan melalui Dagster UI.'),
  heading('D.5 API dan Web Dashboard', HeadingLevel.HEADING_2),
  para('FastAPI menyediakan query analitik dengan parameter tanggal dan kategori yang typed. Dashboard web menggunakan endpoint tersebut untuk KPI, tren kategori, ranking creator, engagement scatter, durasi, rank, dan seasonal analysis.'),
  ...['/api/overview: KPI utama dan top category.', '/api/category-trends: line chart harian atau bulanan.', '/api/top-channels: ranking channel.', '/api/engagement-scatter: views, likes, comments, dan rank.', '/api/duration-performance dan /api/rank-performance: content strategy.', '/api/seasonal: cultural moments dan periode reguler.'].map(bullet),
  para('Dashboard menyediakan filter, enam chart, leaderboard, insight otomatis, mode gelap, loading/error state, dan layout responsif. Dashboard tersedia di http://localhost:18080 dan Swagger API di http://localhost:18080/docs.'),
  heading('E. Hasil Pengembangan', HeadingLevel.HEADING_1),
  heading('E.1 Profil Dataset', HeadingLevel.HEADING_2),
  para('Profiling menghasilkan 61.169 record, 23.844 video unik, 3.335 channel, 15 category ID, dan 1.225 tanggal trending. Rentang data adalah 14 Agustus 2022 sampai 4 Maret 2026. Tidak ditemukan duplicate penuh maupun duplicate video_id + trending_date.'),
  ...['comment_count kosong pada 197 record.', 'like_count kosong pada 407 record.', 'tags kosong pada 13.669 record.', 'duration konsisten dalam pola HH:MM:SS.', 'Nilai numerik tersedia tidak negatif dan rank berada di rentang 1–50.'].map(bullet),
  heading('E.2 Output Analitis', HeadingLevel.HEADING_2),
  ...['Tren jumlah kemunculan dan unique video per kategori.', 'Top channel berdasarkan frekuensi trending.', 'Hubungan rank dengan views, likes, comments, dan engagement rate.', 'Perbandingan kategori pada periode khusus dan reguler.', 'Hubungan durasi video dengan views dan engagement.'].map(bullet),
  heading('F. Gambar Pendukung', HeadingLevel.HEADING_1),
  para('Diagram arsitektur pada bagian C.2 dan struktur folder berikut menjadi pendukung implementasi:'),
  code('final-project/\n  data/source/ dan data/master/\n  ingestion/load_clickhouse.py\n  dbt/models/silver/ dan dbt/models/gold/\n  orchestration/definitions.py dan Dockerfile\n  dashboard/app.py, static/, dan Dockerfile\n  scripts/run_pipeline.sh\n  laporan/\n  slides/'),
  heading('G. Tantangan Dalam Pengerjaan', HeadingLevel.HEADING_1),
  para('Tantangan utama adalah menjaga raw data tetap dapat diaudit sekaligus menyediakan data typed. Solusinya adalah memisahkan bronze dan silver. Timestamp dikonversi di silver, nilai kosong ditangani sesuai makna bisnis, dan gold membedakan trending_appearances dari unique_videos.'),
  para('Orkestrasi juga harus mendukung koneksi dari host dan jaringan Docker. Konfigurasi dibuat berbasis environment variable: host menggunakan localhost:18123, sedangkan Dagster menggunakan clickhouse:8123.'),
  para('Dashboard harus tetap aman dan mudah dipahami saat filter berubah. API menggunakan typed ClickHouse query parameters, sedangkan frontend menyediakan loading, empty, dan error states serta tabel data sebagai alternatif chart.'),
  para('Periode Ramadan dan event pemilu menggunakan season_calendar.csv agar mapping dapat ditinjau dan diperbarui sesuai sumber kalender yang disepakati, bukan ditebak hanya dari bulan.'),
  heading('Kesimpulan', HeadingLevel.HEADING_1),
  para('Project ini menghasilkan data platform mini end-to-end yang terisolasi di final-project: pipeline ELT, medallion warehouse, orkestrasi Dagster, FastAPI, dan web dashboard. Analyst dapat mengeksplorasi tren, creator, engagement, strategi konten, dan cultural moments tanpa menulis SQL manual.'),
  heading('Acknowledgement', HeadingLevel.HEADING_1),
  para('Terima kasih kepada Nusacodes dan mentor Bootcamp Data Engineering atas materi Python, ClickHouse, dbt, Docker, Dagster, API, dan praktik pembangunan pipeline data.'),
  heading('Lampiran', HeadingLevel.HEADING_1),
  ...['Source dataset: final-project/data/source/youtube_trending_dataset.csv', 'Master kategori: final-project/data/master/category_master.csv', 'Kalender periode: final-project/data/master/season_calendar.csv', 'Definisi Dagster: final-project/orchestration/definitions.py', 'Slide presentasi: final-project/slides/Automation Scheduling dan Orchestration.pptx', 'Dagster UI: http://localhost:13000', 'Dashboard: http://localhost:18080', 'Swagger API: http://localhost:18080/docs', 'Link GitHub Repository dan LinkedIn: diisi setelah dipublish.'].map(bullet),
];

const doc = new Document({ sections: [{ properties: { page: { margin: { top: 900, right: 1000, bottom: 900, left: 1000 } } }, children }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync(out, buffer));
