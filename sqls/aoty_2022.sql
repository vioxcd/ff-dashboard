-- anime of the year: mob psycho iii
-- SELECT * FROM v_aoty_2022 ORDER BY ff_score DESC LIMIT 1

-- anime of the season (winter): my dress up darling
-- SELECT * FROM v_aoty_2022 WHERE season = "WINTER" ORDER BY ff_score DESC LIMIT 1

-- anime of the season (spring): kaguya sama: love is war -ultra romantic-
-- SELECT * FROM v_aoty_2022 WHERE season = "SPRING" ORDER BY ff_score DESC LIMIT 1

-- anime of the season (summer): made in abyss: the golden city of the scorching sun
-- SELECT * FROM v_aoty_2022 WHERE season = "SUMMER" ORDER BY ff_score DESC LIMIT 1

-- anime of the season (fall): mob psycho iii
-- SELECT * FROM v_aoty_2022 WHERE season = "FALL" ORDER BY ff_score DESC LIMIT 1

-- most popular: bocchi the rock!
-- SELECT * FROM v_aoty_2022 ORDER BY audience_count DESC LIMIT 1

-- best non-sequel: bocchi the rock!
-- SELECT * FROM v_aoty_2022 WHERE is_sequel = 0 ORDER BY ff_score DESC LIMIT 1

-- best original: lycoris recoil
-- SELECT * FROM v_aoty_2022 WHERE source = "ORIGINAL" ORDER BY ff_score DESC LIMIT 1

-- best movie: drifting home
-- SELECT * FROM v_aoty_2022 WHERE format = "MOVIE" OR format = "ONA" ORDER BY ff_score DESC LIMIT 1