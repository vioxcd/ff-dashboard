-- Tags total count & percentile
CREATE VIEW v_tags_counts_p90
AS
WITH
tags_count AS (
  SELECT
    name,
    COUNT(1) AS counts
  FROM v_wide_tags
  GROUP BY 1
),
tags_p90 AS (
  SELECT *,
    1 - PERCENT_RANK()
    OVER(ORDER BY counts DESC)
    AS pct_rank
  FROM tags_count
)
SELECT *
FROM tags_p90
WHERE pct_rank > .9 -- to get the most popular ones