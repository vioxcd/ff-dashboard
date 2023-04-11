{{ config(
	tags=["final", "dashboard"]
) }}

SELECT
	*
FROM {{ ref('int_media__by_status') }}
WHERE status = "CURRENT"