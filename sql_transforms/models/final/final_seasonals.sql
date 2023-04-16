{{ config(
	tags=["final", "export", "dashboard"]
) }}

SELECT *
FROM {{ ref('int_media__seasonals') }}