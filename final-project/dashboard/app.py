"""FastAPI backend and static web host for the analytics dashboard."""

import os
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

import clickhouse_connect
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app = FastAPI(
    title="YouTube Trend Intelligence API",
    description="Query API for the Indonesia YouTube trending analytics dashboard.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@lru_cache(maxsize=1)
def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "18123")),
        username=os.getenv("CLICKHOUSE_USER", "clickhousedev"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "adminpass123"),
        # The dashboard loads several charts concurrently. A generated
        # ClickHouse session ID only permits one active query, so sharing that
        # session made the other chart requests fail with HTTP 503.
        autogenerate_session_id=False,
    )


def result_as_dicts(result):
    return [dict(zip(result.column_names, row)) for row in result.result_rows]


def execute(sql, parameters=None):
    try:
        return result_as_dicts(get_client().query(sql, parameters=parameters or {}))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"ClickHouse query failed: {exc}") from exc


def where_clause(start_date, end_date, category_id, alias=""):
    prefix = f"{alias}." if alias else ""
    clauses = [
        f"{prefix}trending_date >= {{start_date:Date}}",
        f"{prefix}trending_date <= {{end_date:Date}}",
    ]
    parameters = {"start_date": start_date, "end_date": end_date}
    if category_id is not None:
        clauses.append(f"{prefix}category_id = {{category_id:UInt16}}")
        parameters["category_id"] = category_id
    return " AND ".join(clauses), parameters


def validate_range(start_date, end_date):
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")


@app.get("/", include_in_schema=False)
def dashboard_page():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    rows = execute("SELECT version() AS clickhouse_version, now() AS checked_at")
    return {"status": "ok", **rows[0]}


@app.get("/api/filters")
def filters():
    date_range = execute(
        """SELECT min(trending_date) AS min_date, max(trending_date) AS max_date
        FROM silver.stg_youtube_trending"""
    )[0]
    categories = execute(
        """SELECT category_id, any(category_name) AS category_name
        FROM silver.stg_youtube_trending
        GROUP BY category_id
        ORDER BY category_name"""
    )
    return {**date_range, "categories": categories}


@app.get("/api/overview")
def overview(
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None,
):
    validate_range(start_date, end_date)
    where, params = where_clause(start_date, end_date, category_id)
    summary = execute(
        f"""SELECT
            count() AS trending_appearances,
            uniqExact(video_id) AS unique_videos,
            uniqExact(channel_name) AS unique_channels,
            sum(view_count) AS total_views,
            round(avg(engagement_rate) * 100, 2) AS average_engagement_pct
        FROM silver.stg_youtube_trending
        WHERE {where}""",
        params,
    )[0]
    top_category = execute(
        f"""SELECT any(category_name) AS category_name, count() AS appearances
        FROM silver.stg_youtube_trending
        WHERE {where}
        GROUP BY category_id
        ORDER BY appearances DESC
        LIMIT 1""",
        params,
    )
    summary["top_category"] = top_category[0]["category_name"] if top_category else "—"
    return summary


@app.get("/api/category-trends")
def category_trends(
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None,
    granularity: Literal["day", "month"] = "month",
):
    validate_range(start_date, end_date)
    where, params = where_clause(start_date, end_date, category_id, "y")
    period = "toDate(y.trending_date)" if granularity == "day" else "toStartOfMonth(y.trending_date)"
    rows = execute(
        f"""WITH top_categories AS (
            SELECT category_id
            FROM silver.stg_youtube_trending y
            WHERE {where}
            GROUP BY category_id
            ORDER BY count() DESC
            LIMIT 5
        )
        SELECT
            {period} AS period,
            y.category_id,
            any(y.category_name) AS category_name,
            count() AS appearances,
            uniqExact(y.video_id) AS unique_videos,
            round(avg(y.engagement_rate) * 100, 2) AS average_engagement_pct
        FROM silver.stg_youtube_trending y
        WHERE {where}
          AND y.category_id IN top_categories
        GROUP BY period, y.category_id
        ORDER BY period, category_name""",
        params,
    )
    return {"granularity": granularity, "data": rows}


@app.get("/api/top-channels")
def top_channels(
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None,
    limit: int = Query(default=10, ge=5, le=25),
):
    validate_range(start_date, end_date)
    where, params = where_clause(start_date, end_date, category_id)
    params["limit"] = limit
    return execute(
        f"""SELECT
            channel_name,
            count() AS trending_appearances,
            uniqExact(video_id) AS unique_videos,
            round(avg(trending_rank), 2) AS average_rank,
            max(view_count) AS peak_views,
            round(avg(engagement_rate) * 100, 2) AS average_engagement_pct
        FROM silver.stg_youtube_trending
        WHERE {where}
        GROUP BY channel_name
        ORDER BY trending_appearances DESC, peak_views DESC
        LIMIT {{limit:UInt16}}""",
        params,
    )


@app.get("/api/engagement-scatter")
def engagement_scatter(
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None,
    limit: int = Query(default=180, ge=50, le=500),
):
    validate_range(start_date, end_date)
    where, params = where_clause(start_date, end_date, category_id)
    params["limit"] = limit
    return execute(
        f"""SELECT
            video_id,
            any(video_title) AS video_title,
            any(channel_name) AS channel_name,
            any(category_name) AS category_name,
            max(view_count) AS views,
            max(like_count) AS likes,
            max(comment_count) AS comments,
            min(trending_rank) AS best_rank,
            any(duration_minutes) AS duration_minutes,
            round(max(engagement_rate) * 100, 2) AS engagement_pct
        FROM silver.stg_youtube_trending
        WHERE {where}
        GROUP BY video_id
        ORDER BY views DESC
        LIMIT {{limit:UInt16}}""",
        params,
    )


@app.get("/api/duration-performance")
def duration_performance(
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None,
):
    validate_range(start_date, end_date)
    where, params = where_clause(start_date, end_date, category_id)
    return execute(
        f"""SELECT
            multiIf(
                duration_minutes < 3, '< 3 min',
                duration_minutes < 6, '3–6 min',
                duration_minutes < 12, '6–12 min',
                duration_minutes < 20, '12–20 min',
                '20+ min'
            ) AS duration_bucket,
            count() AS appearances,
            round(avg(view_count), 0) AS average_views,
            round(avg(engagement_rate) * 100, 2) AS average_engagement_pct,
            round(avg(trending_rank), 2) AS average_rank
        FROM silver.stg_youtube_trending
        WHERE {where}
        GROUP BY duration_bucket
        ORDER BY indexOf(['< 3 min', '3–6 min', '6–12 min', '12–20 min', '20+ min'], duration_bucket)""",
        params,
    )


@app.get("/api/rank-performance")
def rank_performance(
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None,
):
    validate_range(start_date, end_date)
    where, params = where_clause(start_date, end_date, category_id)
    return execute(
        f"""SELECT
            multiIf(
                trending_rank <= 10, '1–10',
                trending_rank <= 20, '11–20',
                trending_rank <= 30, '21–30',
                trending_rank <= 40, '31–40',
                '41–50'
            ) AS rank_bucket,
            count() AS appearances,
            round(avg(view_count), 0) AS average_views,
            round(avg(like_count), 0) AS average_likes,
            round(avg(comment_count), 0) AS average_comments,
            round(avg(engagement_rate) * 100, 2) AS average_engagement_pct
        FROM silver.stg_youtube_trending
        WHERE {where}
        GROUP BY rank_bucket
        ORDER BY indexOf(['1–10', '11–20', '21–30', '31–40', '41–50'], rank_bucket)""",
        params,
    )


@app.get("/api/seasonal")
def seasonal(category_id: Optional[int] = None):
    category_filter = ""
    params = {}
    if category_id is not None:
        category_filter = "WHERE category_id = {category_id:UInt16}"
        params["category_id"] = category_id
    return execute(
        f"""SELECT
            season_name,
            sum(trending_appearances) AS trending_appearances,
            sum(unique_videos) AS unique_videos,
            sum(total_views) AS total_views,
            round(avg(average_engagement_rate) * 100, 2) AS average_engagement_pct
        FROM gold.mart_seasonal_trends
        {category_filter}
        GROUP BY season_name
        ORDER BY trending_appearances DESC""",
        params,
    )
