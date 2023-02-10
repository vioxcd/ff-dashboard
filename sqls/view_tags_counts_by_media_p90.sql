-- Tags total count & percentile (per-media)
CREATE VIEW v_tags_counts_by_media_p90
AS
WITH
tags_count AS (
  SELECT
    name,
    media_type,
    COUNT(1) AS counts
  FROM v_wide_tags
  GROUP BY 1, 2 -- per-media part
),
tags_p90 AS (
  SELECT *,
    1 - PERCENT_RANK()
    OVER(PARTITION BY media_type ORDER BY counts DESC)
    AS pct_rank
  FROM tags_count
)
SELECT *
FROM tags_p90
WHERE pct_rank > .9 -- to get the most popular ones