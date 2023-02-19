CREATE VIEW v_aoty_2022
AS
WITH
aoty_2022_rules AS (
	-- this CTE is taken from `as_rules`
	-- the `WHERE` clause is modified with `retrieved_date = "2023-02-01"` to make sure it's getting the correct entries
	SELECT
		media_id,
		title,
		media_type,
		CAST(AVG(anichan_score) AS INTEGER) AS anichan_score,
		CAST(AVG(appropriate_score) AS INTEGER) AS ff_score,
		COUNT(1) AS audience_count
	FROM v_appropriate_score
	WHERE (status = 'COMPLETED' OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5)) -- rules: completed or at least 5 eps progress
		AND CAST(anichan_score AS INTEGER) > 0 -- don't calculate non-rating
		AND CAST(appropriate_score AS INTEGER) > 0 -- don't calculate non-rating
		AND retrieved_date = "2023-02-01" -- retrieve date here
	GROUP BY title, media_type
	HAVING COUNT(1) >= 5 -- rules: minimum watched by 5 members
),
aoty_2022 AS (
  SELECT
    md.*,
    ar.anichan_score,
    ar.ff_score,
    ar.audience_count
  FROM aoty_2022_rules ar
  JOIN media_details md
  USING (media_id)
  WHERE anichan_score >= 80.0
    AND ff_score >= 80.0
    AND md.media_type = 'ANIME'
    AND season_year = 2022
),
aoty AS (
	SELECT "Anime of the Year" AS award, 1 AS award_order,
		* FROM aoty_2022 ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (winter): my dress up darling
aots_winter AS (
	SELECT "Anime of the Season: Winter" AS award, 2 AS award_order,
		* FROM aoty_2022 WHERE season = "WINTER" ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (spring): kaguya sama: love is war -ultra romantic-
aots_spring AS (
	SELECT "Anime of the Season: Spring" AS award, 3 AS award_order,
		* FROM aoty_2022 WHERE season = "SPRING" ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (summer): made in abyss: the golden city of the scorching sun
aots_summer AS (
	SELECT "Anime of the Season: Summer" AS award, 4 AS award_order,
		* FROM aoty_2022 WHERE season = "SUMMER" ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (fall): mob psycho iii
aots_fall AS (
	SELECT "Anime of the Season: Fall" AS award, 5 AS award_order,
		* FROM aoty_2022 WHERE season = "FALL" ORDER BY ff_score DESC LIMIT 1
),
-- most popular: bocchi the rock!
most_popular AS (
	SELECT "Most Popular" AS award, 6 AS award_order,
		* FROM aoty_2022 ORDER BY audience_count DESC LIMIT 1
),
-- best non-sequel: bocchi the rock!
best_non_sequel AS (
	SELECT "Best Non-Sequel" AS award, 7 AS award_order,
		* FROM aoty_2022 WHERE is_sequel = 0 ORDER BY ff_score DESC LIMIT 1
),
-- best original: lycoris recoil
best_original AS (
	SELECT "Best Original" AS award, 8 AS award_order,
		* FROM aoty_2022 WHERE source = "ORIGINAL" ORDER BY ff_score DESC LIMIT 1
),
-- best movie: drifting home
best_movie AS (
	SELECT "Best Movie" AS award, 9 AS award_order,
		* FROM aoty_2022 WHERE format = "MOVIE" OR (format = "ONA" AND episodes = 1) ORDER BY ff_score DESC LIMIT 1
)
SELECT *
FROM (
	SELECT * FROM aoty
	UNION SELECT * FROM aots_winter
	UNION SELECT * FROM aots_spring
	UNION SELECT * FROM aots_summer
	UNION SELECT * FROM aots_fall
	UNION SELECT * FROM most_popular
	UNION SELECT * FROM best_non_sequel
	UNION SELECT * FROM best_original
	UNION SELECT * FROM best_movie
)
ORDER BY award_order