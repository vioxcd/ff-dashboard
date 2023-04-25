{{ config(
	tags=["final", "dashboard"]
) }}

-- Anticipated!
SELECT
	*
FROM {{ ref('int_media__by_status_join_media') }}
WHERE status = "PLANNING"