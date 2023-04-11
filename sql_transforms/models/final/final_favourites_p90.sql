{{ config(
	tags=["final", "export", "dashboard"]
) }}

SELECT *
FROM {{ ref('int_favourites__pct_rank') }}
WHERE pct_rank > .9