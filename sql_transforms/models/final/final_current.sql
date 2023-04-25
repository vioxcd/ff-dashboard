{{ config(
	tags=["final", "dashboard"]
) }}

SELECT
	*
FROM {{ ref('int_media__by_status_join_media') }}
WHERE status = "CURRENT"