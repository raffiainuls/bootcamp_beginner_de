# Dashboard API

Service FastAPI yang membaca tabel silver dan gold ClickHouse untuk menyediakan JSON siap chart. Web dashboard dan dokumentasi OpenAPI disajikan oleh service yang sama.

## URL

- Dashboard: `http://localhost:18080`
- Swagger/OpenAPI: `http://localhost:18080/docs`
- Health check: `http://localhost:18080/api/health`

## Endpoint analitik

| Endpoint | Query analitik | Visual |
|---|---|---|
| `/api/overview` | Jumlah snapshot, unique video, unique channel, views, engagement, top category | KPI cards |
| `/api/category-trends` | Kemunculan kategori berdasarkan hari/bulan | Multi-series line chart |
| `/api/top-channels` | Channel berdasarkan frekuensi trending, rank, dan peak views | Horizontal bar + table |
| `/api/engagement-scatter` | Views, likes, comments, rank, dan engagement per video | Bubble chart |
| `/api/duration-performance` | Average views dan engagement berdasarkan bucket durasi | Bar + line chart |
| `/api/rank-performance` | Average views/engagement berdasarkan kelompok trending rank | Bar chart |
| `/api/seasonal` | Perbandingan Ramadan, pemilu, akhir tahun, dan periode reguler | Horizontal bar chart |

Parameter filter tanggal dan kategori diproses sebagai typed ClickHouse query parameters. Detail SQL berada di `dashboard/app.py`.
