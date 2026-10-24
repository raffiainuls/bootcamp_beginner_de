{{ config(
    materialized='table',
    schema='silver',
    engine='MergeTree()',
    order_by='(trending_date, video_id)',
    partition_by='toYYYYMM(trending_date)'
) }}

WITH cleaned AS (
    SELECT
        toDateTimeOrNull(replaceRegexpAll(trending_date, ' UTC$', '')) AS trending_at_utc,
        toDateTimeOrNull(replaceRegexpAll(publish_date, ' UTC$', '')) AS published_at_utc,
        toUInt16OrNull(trending_no) AS trending_rank,
        toUInt16OrNull(category_id) AS category_id,
        nullIf(trim(video_id), '') AS video_id,
        replaceRegexpAll(trim(channel), '[[:space:]]+', ' ') AS channel_name,
        toInt64OrNull(nullIf(trim(comment_count), '')) AS comment_count,
        toInt64OrNull(nullIf(trim(like_count), '')) AS like_count,
        toInt64OrNull(nullIf(trim(view_count), '')) AS view_count,
        trim(title) AS video_title,
        nullIf(replaceRegexpAll(trim(tags), '[[:space:]]+', ' '), '') AS tags,
        toUInt32OrNull(splitByChar(':', duration)[1]) * 3600
            + toUInt32OrNull(splitByChar(':', duration)[2]) * 60
            + toUInt32OrNull(splitByChar(':', duration)[3]) AS duration_seconds
    FROM {{ source('bronze', 'raw_youtube_trending') }}
), categorized AS (
    SELECT
        c.*,
        m.category_name
    FROM cleaned c
    INNER JOIN {{ source('bronze', 'raw_category_master') }} m
        ON c.category_id = toUInt16OrNull(m.category_id)
)
SELECT
    assumeNotNull(video_id) AS video_id,
    assumeNotNull(category_id) AS category_id,
    assumeNotNull(category_name) AS category_name,
    channel_name,
    video_title,
    tags,
    assumeNotNull(addHours(trending_at_utc, 7)) AS trending_at_wib,
    assumeNotNull(addHours(published_at_utc, 7)) AS published_at_wib,
    assumeNotNull(toDate(addHours(trending_at_utc, 7))) AS trending_date,
    assumeNotNull(toDate(addHours(published_at_utc, 7))) AS published_date,
    assumeNotNull(toYear(addHours(trending_at_utc, 7))) AS trending_year,
    assumeNotNull(toMonth(addHours(trending_at_utc, 7))) AS trending_month,
    assumeNotNull(toDayOfWeek(addHours(trending_at_utc, 7))) AS trending_day_of_week,
    trending_rank,
    duration_seconds,
    round(duration_seconds / 60.0, 2) AS duration_minutes,
    coalesce(comment_count, 0) AS comment_count,
    coalesce(like_count, 0) AS like_count,
    view_count,
    round((like_count + comment_count) / nullIf(view_count, 0), 6) AS engagement_rate
FROM categorized
WHERE video_id IS NOT NULL
  AND trending_at_utc IS NOT NULL
  AND published_at_utc IS NOT NULL
  AND view_count >= 0
  AND trending_rank BETWEEN 1 AND 50
