-- Anime under 70 that are rated highly by someone (underrated for them)
-- in rules: user rate > media rate (+ some diff value)
CREATE VIEW v_underrated
AS
WITH
media_scores AS (
  SELECT
    vas.username,
    md.title,
  	md.type,
  	CAST(md.mean_score AS INTEGER) AS mean_score,
    vas.appropriate_score
  FROM v_appropriate_score vas
  JOIN media_details md
  USING(media_id)
  WHERE type = "ANIME"
)
SELECT
  *,
  ABS(mean_score - appropriate_score) AS score_diff
FROM media_scores
WHERE mean_score - appropriate_score < -10
  AND mean_score < 70