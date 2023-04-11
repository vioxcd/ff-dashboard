{{ config(
	tags=["final", "dashboard"]
) }}

-- Anticipated!
SELECT
	*
FROM {{ ref('int_media__by_status') }}
WHERE status = "PLANNING"