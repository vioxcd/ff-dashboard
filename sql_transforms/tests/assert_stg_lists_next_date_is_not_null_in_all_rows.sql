-- I introduced a bug where `next_date` calculation are shadowed by `next_date` column
-- prevent this kind of things from happening again by a check
SELECT *
FROM (
	SELECT COUNT(next_date) AS next_date_counts
	FROM {{ ref("stg_lists") }}
)
WHERE next_date_counts = 0