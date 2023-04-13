{{ config(
	tags=["final", "dashboard"]
) }}

SELECT *
FROM {{ ref('int_media__title_diff') }}
WHERE audience_count > 3