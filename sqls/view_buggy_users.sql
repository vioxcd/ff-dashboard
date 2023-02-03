-- Lists of possibly affected (buggy) users
-- (those which scores are fetched with default per page argument)
-- it seems that people that are not affected are those with `POINT_100` score format
CREATE VIEW v_buggy_users AS
WITH
buggy_users AS (
	SELECT DISTINCT u.username, u.score_format, 1 AS is_buggy
	FROM v_appropriate_score vas
	JOIN users u
	USING (username)
	WHERE CAST(vas.appropriate_score AS INTEGER) > 100
),
non_buggy_users AS (
	SELECT *, 0 AS is_buggy
	FROM (
		SELECT username, score_format  -- get all users
		FROM users
		EXCEPT
		SELECT username, score_format
		FROM buggy_users
	)
)
SELECT * FROM buggy_users
UNION
SELECT * FROM non_buggy_users
ORDER BY is_buggy