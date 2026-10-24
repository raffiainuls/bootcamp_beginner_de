{{ config(materialized='table', schema='gold', engine='MergeTree()', order_by='(trending_date, category_id)', partition_by='toYYYYMM(trending_date)') }}

SELECT
    trending_date,
    category_id,
    any(category_name) AS category_name,
    count() AS trending_appearances,
    uniqExact(video_id) AS unique_videos,
    round(avg(trending_rank), 2) AS average_trending_rank,
    sum(view_count) AS total_views,
    sum(like_count) AS total_likes,
    sum(comment_count) AS total_comments,
    round(avg(duration_minutes), 2) AS average_duration_minutes,
    round(avg(engagement_rate), 6) AS average_engagement_rate
FROM {{ ref('stg_youtube_trending') }}
GROUP BY trending_date, category_id
