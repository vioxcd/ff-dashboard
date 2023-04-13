{{ config(
	tags=["final", "dashboard"]
) }}

SELECT
	*
FROM {{ ref('int_media__divisive') }}
WHERE pct_rank > .95