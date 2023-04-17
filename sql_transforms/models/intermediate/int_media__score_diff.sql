{{ config(tags='intermediate') }}

WITH
media_scores AS (
	SELECT
		l.username,
		ar.media_id,
		ar.title,
		ar.media_type,
		CAST(ar.ff_score AS INTEGER) AS mean_score,
		ar.audience_count,
		l.appropriate_score
  	FROM {{ ref('stg_lists') }} l
    	JOIN {{ ref('int_media__as_rules') }} ar
    	USING(media_id)
  	WHERE ar.media_type = "ANIME"
)

SELECT
	*,
	ABS(mean_score - appropriate_score) AS score_diff
FROM media_scores
WHERE
	mean_score - appropriate_score < -10
	AND mean_score < 80