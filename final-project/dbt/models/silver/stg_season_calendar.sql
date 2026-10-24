{{ config(materialized='table', schema='silver', engine='MergeTree()', order_by='(start_date, end_date)') }}

WITH parsed AS (
    SELECT
        trim(season_name) AS season_name,
        toDateOrNull(start_date) AS start_date,
        toDateOrNull(end_date) AS end_date,
        trim(notes) AS notes
    FROM {{ source('bronze', 'raw_season_calendar') }}
)
SELECT
    season_name,
    assumeNotNull(start_date) AS start_date,
    assumeNotNull(end_date) AS end_date,
    notes
FROM parsed
WHERE start_date IS NOT NULL
  AND end_date IS NOT NULL
