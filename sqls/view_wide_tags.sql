CREATE VIEW v_wide_tags AS
WITH
filtered_lists AS (
	SELECT
		username,
		media_id,
		title,
		media_type,
		CAST(scores_anichan AS INTEGER) AS scores_anichan,
		CAST(appropriate_score AS INTEGER) AS appropriate_score 
	FROM v_appropriate_score
	WHERE CAST(scores_anichan AS INTEGER) > 0
		AND CAST(appropriate_score AS INTEGER) > 0
),
average_scores AS (
	SELECT
		media_id,
		title,
		media_type,
		CAST(AVG(scores_anichan) AS INTEGER) AS anichan_avg,
		CAST(AVG(appropriate_score) AS INTEGER) AS ff_avg,
		COUNT(1) AS n
	FROM filtered_lists
	GROUP BY title, media_type
	HAVING COUNT(1) > 5
),
tags_info AS (
	SELECT *
	FROM media_tags_bridge
	JOIN media_tags
	USING (tag_id)
),
wide_tags AS (
	SELECT *,
		CASE WHEN INSTR(category, '-') > 0
			THEN SUBSTR(category, 0, INSTR(category, '-'))
			ELSE category
		END AS super_category,
		CASE WHEN INSTR(category, '-') > 0
			THEN SUBSTR(category, INSTR(category, '-') + 1, LENGTH(category))
			ELSE category
		END AS sub_category
	FROM average_scores
	JOIN tags_info
	USING (media_id)
)
SELECT * FROM wide_tags