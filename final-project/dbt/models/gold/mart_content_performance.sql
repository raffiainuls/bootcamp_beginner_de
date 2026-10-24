{{ config(materialized='table', schema='gold', engine='MergeTree()', order_by='(trending_date, video_id)') }}

SELECT
    trending_date,
    video_id,
    category_id,
    category_name,
    channel_name,
    video_title,
    trending_rank,
    duration_seconds,
    duration_minutes,
    view_count,
    like_count,
    comment_count,
    engagement_rate,
    round(view_count / nullIf(trending_rank, 0), 2) AS views_per_rank_point
FROM {{ ref('stg_youtube_trending') }}
