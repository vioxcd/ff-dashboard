-- Queries related to underrated view
-- Most underrated per user
WITH numbered_rows AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY username
              ORDER BY score_diff DESC)
              AS user_no
  FROM v_underrated
)
SELECT *
FROM numbered_rows
WHERE user_no = 1
ORDER BY score_diff DESC

-- Top underrated titles
SELECT
  title,
  COUNT(1) AS counts,
  mean_score,
  CAST(AVG(appropriate_score) AS INTEGER) AS avg_score
FROM v_underrated
GROUP BY 1
ORDER BY 2 DESC, 4 DESC

-- Titles with most jarring difference in score
SELECT *
FROM v_underrated
ORDER BY score_diff DESC
LIMIT 10

-- User with most "questionable" ratings
SELECT username, COUNT(1) AS counts
FROM v_underrated
GROUP BY 1
ORDER BY 2 DESC