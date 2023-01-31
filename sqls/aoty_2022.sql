-- anime of the year: mob psycho iii
WITH
aoty AS (
	SELECT "AOTY" AS award, 1 AS award_order,
		* FROM v_aoty_2022 ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (winter): my dress up darling
aots_winter AS (
	SELECT "AOTS Winter" AS award, 2 AS award_order,
		* FROM v_aoty_2022 WHERE season = "WINTER" ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (spring): kaguya sama: love is war -ultra romantic-
aots_spring AS (
	SELECT "AOTS Spring" AS award, 3 AS award_order,
		* FROM v_aoty_2022 WHERE season = "SPRING" ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (summer): made in abyss: the golden city of the scorching sun
aots_summer AS (
	SELECT "AOTS Summer" AS award, 4 AS award_order,
		* FROM v_aoty_2022 WHERE season = "SUMMER" ORDER BY ff_score DESC LIMIT 1
),
-- anime of the season (fall): mob psycho iii
aots_fall AS (
	SELECT "AOTS Fall" AS award, 5 AS award_order,
		* FROM v_aoty_2022 WHERE season = "FALL" ORDER BY ff_score DESC LIMIT 1
),
-- most popular: bocchi the rock!
most_popular AS (
	SELECT "Most Popular" AS award, 6 AS award_order,
		* FROM v_aoty_2022 ORDER BY audience_count DESC LIMIT 1
),
-- best non-sequel: bocchi the rock!
best_non_sequel AS (
	SELECT "Best Non-Sequel" AS award, 7 AS award_order,
		* FROM v_aoty_2022 WHERE is_sequel = 0 ORDER BY ff_score DESC LIMIT 1
),
-- best original: lycoris recoil
best_original AS (
	SELECT "Best Original" AS award, 8 AS award_order,
		* FROM v_aoty_2022 WHERE source = "ORIGINAL" ORDER BY ff_score DESC LIMIT 1
),
-- best movie: drifting home
best_movie AS (
	SELECT "Best Movie" AS award, 9 AS award_order,
		* FROM v_aoty_2022 WHERE format = "MOVIE" OR (format = "ONA" AND episodes = 1) ORDER BY ff_score DESC LIMIT 1
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