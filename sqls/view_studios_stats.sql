-- Studios statistics
-- Studios popularity and their ratings
CREATE VIEW v_studios_stats
AS
WITH
media_scores AS (
  SELECT
    md.*,
    vas.username,
    vas.anichan_score,
    vas.appropriate_score
  FROM v_appropriate_score vas
  JOIN media_details md
  USING(media_id)
  WHERE md.media_type = "ANIME"
	AND studios != ""
),
studio_stats AS (
  SELECT
    studios,
    CAST(AVG(anichan_score) AS INTEGER) AS anichan_avg,
    CAST(AVG(appropriate_score) AS INTEGER) AS ff_avg,
    COUNT(1) AS n
  FROM media_scores
  GROUP BY studios
)
SELECT *,
  DENSE_RANK() OVER (ORDER BY anichan_avg DESC) AS anichan_avg_rank,
  DENSE_RANK() OVER (ORDER BY ff_avg DESC) AS ff_avg_rank,
  DENSE_RANK() OVER (ORDER BY n DESC) AS popularity
FROM studio_stats