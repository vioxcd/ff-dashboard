-- AOTY 2022 lists is already specified in the discord's #rankings channel.
-- Except some already investigated difference, (e.g. Spring's AoT vs Dress-up Darling & audience counts),
-- this tests ensure that the model generates the correct ordering and statistics
SELECT *
FROM {{ ref("aoty_2022") }}
WHERE
	(award = "Anime of the Year"
		AND
			(title != "Mob Psycho 100 III"
			OR anichan_score != 92
			OR audience_count != 9)
	)
	OR
	(award = "Anime of the Season: Winter"
		AND
			(title != "Attack on Titan Final Season Part 2"
			OR anichan_score != 89
			OR audience_count != 8)
	)
	OR
	(award = "Anime of the Season: Spring"
		AND
			(title != "Kaguya-sama: Love is War -Ultra Romantic-"
			OR anichan_score != 91
			OR audience_count != 16)
	)
	OR
	(award = "Anime of the Season: Summer"
		AND
			(title != "Made in Abyss: The Golden City of the Scorching Sun"
			OR anichan_score != 88
			OR audience_count != 11)
	)
	OR
	(award = "Anime of the Season: Fall"
		AND
			(title != "Mob Psycho 100 III"
			OR anichan_score != 92
			OR audience_count != 9)
	)
	OR
	(award = "Most Popular"
		AND
			(title != "BOCCHI THE ROCK!"
			OR anichan_score != 90
			OR audience_count != 20)
	)
	OR
	(award = "Best Non-Sequel"
		AND
			(title != "BOCCHI THE ROCK!"
			OR anichan_score != 90
			OR audience_count != 20)
	)
	OR
	(award = "Best Original"
		AND
			(title != "Lycoris Recoil"
			OR anichan_score != 83
			OR audience_count != 18)
	)
	OR
	(award = "Best Movie"
		AND
			(title != "Drifting Home"
			OR anichan_score != 81
			OR audience_count != 5)
	)