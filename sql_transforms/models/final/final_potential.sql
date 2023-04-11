{{ config(
	tags=["final", "export", "dashboard"]
) }}

SELECT *
FROM {{ ref('int_media__potential') }}
WHERE
	anichan_score >= 80
	OR ff_score >= 80