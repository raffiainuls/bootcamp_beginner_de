{{ config(materialized='table', schema='gold', engine='MergeTree()', order_by='(season_name, category_id)') }}

WITH tagged AS (
    SELECT
        y.*,
        arrayFirst(
            x -> y.trending_date >= x.2 AND y.trending_date <= x.3,
            s.season_ranges
        ) AS matched_season
    FROM {{ ref('stg_youtube_trending') }} y
    CROSS JOIN (
        SELECT groupArray((season_name, start_date, end_date)) AS season_ranges
        FROM {{ ref('stg_season_calendar') }}
    ) s
)
SELECT
    if(matched_season.1 = '', 'Regular period', matched_season.1) AS season_name,
    category_id,
    any(category_name) AS category_name,
    min(trending_date) AS period_start,
    max(trending_date) AS period_end,
    count() AS trending_appearances,
    uniqExact(video_id) AS unique_videos,
    round(avg(trending_rank), 2) AS average_trending_rank,
    sum(view_count) AS total_views,
    sum(like_count) AS total_likes,
    sum(comment_count) AS total_comments,
    round(avg(engagement_rate), 6) AS average_engagement_rate
FROM tagged
GROUP BY season_name, category_id
