{{ config(tags='intermediate') }}

SELECT
	title,
	CAST(AVG(appropriate_score) AS INTEGER) AS should_be_score,
	COUNT(1) AS audience_count,
	mean_score AS actual_score,
	audience_count AS actual_audience_count
FROM {{ ref('int_media__score_diff') }}
GROUP BY title
ORDER BY audience_count DESC, should_be_score DESC