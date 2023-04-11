-- Place for various utility queries
-- ! NOT TO BE RUN DIRECTLY

-- * Table Deduplication SQL
-- * Run each block below one by one in steps
-- check unique vs. duplicated media
-- SELECT
-- 	COUNT (DISTINCT media_id) AS unique_media_count,
-- 	COUNT (media_id) AS duplicated_media_count
-- FROM
-- 	media_details
-- create backup table with unique media
-- CREATE TABLE media_details_bak AS SELECT * FROM media_details GROUP BY media_id
-- delete table with duplicates
-- DELETE FROM media_details
-- restore item to the original table from backup
-- INSERT INTO media_details
-- SELECT * FROM media_details_bak
-- drop the backup table
-- DROP TABLE media_details_bak


-- * See titles that are not eligible by rules (investigating `as_rules` view)
-- SELECT
--   title,
--   media_type
-- FROM v_appropriate_score
-- WHERE status IN ('COMPLETED', 'CURRENT')
-- GROUP BY title, media_type
-- HAVING COUNT(1) >= 5
-- EXCEPT -- filter clause
-- SELECT
--   title,
--   media_type
-- FROM v_appropriate_score
-- WHERE status = 'COMPLETED' OR (status = 'CURRENT' AND progress >= 5)
-- GROUP BY title, media_type
-- HAVING COUNT(1) >= 5

-- * Rename cover_image column name mistakes
-- probably only ran once (ever)
-- ALTER TABLE media_details RENAME COLUMN cover_image_url_md TO cover_image_url_xl_bak;
-- ALTER TABLE media_details RENAME COLUMN cover_image_url_xl TO cover_image_url_md;
-- ALTER TABLE media_details RENAME COLUMN cover_image_url_xl_bak TO cover_image_url_xl;

-- * Future Use
-- Q: anime under 70/60/50 that are rated highly by someone (user rate > media rate)
--
-- ? it errors out because `mean_score` are not available.
-- Solution: fetch media `mean_score` alongside users' details (lists table)
--
-- SELECT
-- 	username,
-- 	anichan_score,
-- 	appropriate_score
-- FROM v_appropriate_score
-- WHERE media_type = "ANIME"
-- AND mean_score - appropriate_score < 0
-- AND mean_score < 70

-- * Lamfao missing entries
-- trying to recover missing lists and favourites from lamfao's missing account
-- titles that are needed to recover lamfao's missing entries:
-- 		Jibi Eopseo, Manga
-- 		Love Stories, Manga
-- WITH all_non_lamfao_titles AS (
-- 	SELECT name, UPPER(type) AS media_type
-- 	FROM favourites f
-- 	JOIN users u
-- 	ON u.id = f.user_id
-- 	WHERE type IN ("anime", "manga")
-- 		AND username != "lamfao"

-- 	UNION

-- 	SELECT title, media_type
-- 	FROM v_as_rules
-- ),
-- missing_needed_lamfao_titles AS (
-- 	SELECT name, UPPER(type) AS media_type
-- 	FROM favourites f
-- 	JOIN users u
-- 	ON u.id = f.user_id
-- 	WHERE type IN ("anime", "manga")
-- 		AND username = "lamfao"  -- these are lamfao only titles
-- 	EXCEPT
-- 	SELECT * FROM all_non_lamfao_titles
-- ),
-- does_lists_covers_these_titles AS (
-- 	SELECT title, media_type
-- 	FROM lists
-- 	WHERE username != "lamfao"
-- 	GROUP BY 1, 2
-- )
-- SELECT * FROM missing_needed_lamfao_titles
-- EXCEPT
-- SELECT * FROM does_lists_covers_these_titles

-- * Lamfao insert entries
-- INSERT INTO favourites VALUES
-- (5411429, 98478, "March comes in like a lion Season 2", "anime", "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx98478-dF3mpSKiZkQu.jpg"),
-- (5411429, 21710, "Natsume's Book of Friends 5", "anime", "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx21710-Y20fKQviC3hL.jpg"),
-- (5411429, 4181, "Clannad: After Story", "anime", "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx4181-V1LCtX1rJgbR.png"),
-- (5411429, 97986, "Made in Abyss", "anime", "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx97986-pXb9GcQkPDcT.jpg"),
-- (5411429, 55096, "Silver Spoon", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx55096-xdMg0fzQY52d.png"),
-- (5411429, 44483, "Space Brothers", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx44483-wrZppcXvhEfh.jpg"),
-- (5411429, 132288, "Hirayasumi", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx132288-YnkpDO1wNHNM.png"),
-- (5411429, 104998, "Trace: Kasouken Houi Kenkyuuin no Tsuisou", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx104998-LFvSlR3bF2r8.jpg"),
-- (5411429, 31133, "Dorohedoro", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx31133-xhUafoJkW2AZ.png"),
-- (5411429, 31009, "Honey and Clover", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx31009-Gpbp4T7ekBcM.jpg"),
-- (5411429, 86436, "Love Stories", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx86436-WO4OjJFreMJc.png"),
-- (5411429, 74307, "Blank Canvas: My So-Called Artist's Journey", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx74307-femphzZGNGYA.png"),
-- (5411429, 86082, "Delicious in Dungeon", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx86082-it012qMBU8S8.jpg"),
-- (5411429, 87350, "Wake up, Sleeping Beauty", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx87350-MOmoHELzv3uf.png"),
-- (5411429, 34625, "The Summit of the Gods", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx34625-OrkkDW8S3r9y.png"),
-- (5411429, 126986, "Jibi Eopseo", "manga", "https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/bx126986-hgpeh6RNaUpq.jpg"),
-- (5411429, 24311, "Akari Kawamoto", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/24311-WY1Q26PwwJeB.png"),
-- (5411429, 22055, "Tsubasa Hanekawa", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b22055-gMEwJMWVZesx.png"),
-- (5411429, 425, "Ginko", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b425-khK03T5n9Umq.png"),
-- (5411429, 356, "Ayumi Yamada", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b356-UXIjzAnH9IHW.jpg"),
-- (5411429, 67957, "Ayano Tateyama", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b67957-cje7Npn2J7TZ.png"),
-- (5411429, 5756, "Claire Stanfield", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b5756-AO4dD0LGz4fm.png"),
-- (5411429, 6831, "Sanae Furukawa", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b6831-8jUtY6oLk5bp.png"),
-- (5411429, 151351, "Himuro-kun", "characters", "https://s4.anilist.co/file/anilistcdn/character/large/b151351-sCRrYyBxuuRa.png"),
-- (5411429, 97891, "Chica Umino", "staff", "https://s4.anilist.co/file/anilistcdn/staff/large/2891.jpg"),
-- (5411429, 127567, "Ikumi Fukuda", "staff", "https://s4.anilist.co/file/anilistcdn/staff/large/n127567-zOB5DpSvxQsr.jpg"),
-- (5411429, 95600, "Toshiyuki Toyonaga", "staff", "https://s4.anilist.co/file/anilistcdn/staff/large/n95600-giNVqkdeWKuF.png"),
-- (5411429, 104178, "Pyotr Ilyich Tchaikovsky", "staff", "https://s4.anilist.co/file/anilistcdn/staff/large/n104178-XHJqSy8v86Zi.png"),
-- (5411429, 6145, "Science SARU", "studios", ""),
-- (5411429, 44, "Shaft", "studios", "")
-- ;

-- * All unique titles that might get displayed
-- criteria: either they fulfill the rules or are favourited
-- WITH
-- all_titles AS (
--   SELECT title, media_type
--   FROM v_as_rules
--   UNION
--   SELECT name, UPPER(type)
--   FROM favourites
--   WHERE type IN ("anime", "manga")
-- )
-- SELECT title FROM all_titles
-- EXCEPT
-- SELECT title FROM media_details

-- * Should be looked again to investigate what this could be used for
-- ? Is this a kind of "popularity and salience (rank) of tags?"
-- Tags Rank
-- Normalized counts and ranks (divide by max. avg w/ tag_rank)
-- WITH
-- tags_counted_ranked AS (
--  SELECT
--    name,
--    sub_category,
--    COUNT(1) AS counts,
--    CAST(AVG(rank) AS INTEGER) AS tag_rank_avg
--  FROM v_wide_tags
--  GROUP BY 1, 2
-- ),
-- highest_counts AS (
--  SELECT MAX(counts) AS highest_count FROM tags_counted_ranked
-- ),
-- normalize_counts_and_ranks AS (
--  SELECT
--    name,
--    sub_category,
--    ((counts / hc.highest_count) + (tag_rank_avg / 100.0)) / 2 AS normalized_cr
--  FROM tags_counted_ranked, highest_counts hc
-- )
-- SELECT *
-- FROM normalize_counts_and_ranks
-- ORDER BY normalized_cr DESC

-- * Should be looked again to investigate what this could be used for
-- ? Kinda looks the same w/ tags_subcategory_favourited. but it's normalized?
-- Most favourited tags' subcategory, normalized
-- CREATE VIEW v_tags_subcategory_favourited_normalized
-- AS
-- WITH
-- wide_favourite_tags AS (
--   SELECT f.user_id, vwt.*
--   FROM favourites f
--   JOIN v_wide_tags vwt
--   ON f.name = vwt.title
-- ),
-- tags_counted_ranked AS (
--  SELECT
--    name,
--    sub_category,
--    COUNT(1) AS counts,
--    CAST(AVG(rank) AS INTEGER) AS rank_avg
--  FROM wide_favourite_tags
--  GROUP BY 1, 2
-- ),
-- highest_counts AS (
--  SELECT MAX(counts) AS highest_count FROM tags_counted_ranked
-- ),
-- normalized_counts_and_ranks AS (
--  SELECT
--    name,
--    sub_category,
--    counts,
--    rank_avg,
--    ((counts / hc.highest_count) + (rank_avg / 100.0)) / 2 AS normalized_cr
--  FROM tags_counted_ranked, highest_counts hc
-- )
-- SELECT *
-- FROM normalized_counts_and_ranks
-- ORDER BY normalized_cr DESC

-- * The initial mapping of point 3 and 5 scores should've been a table:)
-- CREATE TABLE score_mapping
-- AS
-- SELECT *
-- FROM vm_anichan_to_3_and_5_scores_format_mapping
-- WHERE 0
--
-- INSERT INTO score_mapping
-- SELECT *
-- FROM vm_anichan_to_3_and_5_scores_format_mapping

-- * Adding slowly-changing dimension field to mark historical data
-- * Columns are added for lists (retrieved_date) and users (generation)
-- lists case: the year is ongoing and currently there's an 2022 AOTY that needs to be maintained
-- the data can't be overwritten because it'd change the AOTY lists. therefore, there's a need to
-- maintain historical data, e.g. data before February 2023, in the db.
-- newest entry is from 1st February (see `completedAt` column and check `llure` for example))
-- ALTER TABLE lists
-- ADD COLUMN retrieved_date TEXT;
--
-- Mark all current as from 1 February 2023
-- UPDATE lists
-- SET retrieved_date = "2023-02-01";
-- 
-- * Users case: fluffy folks has new members!
-- make sure they won't change 2022 AOTY lists!!
-- I can actually just use `retrieved time` for their lists to filter for AOTY.
-- but, I'll mark that they're new case in this project via `generation` column just in case
-- ALTER TABLE users
-- ADD COLUMN generation INTEGER;
-- UPDATE users
-- SET generation = 1;
-- 
-- new users are added in fluff.txt

-- * Reload lists to db because there's bug when calculating `next_date`
-- (it's shadowed by the column of the same name)
-- sqlite3 data/fluff_03-2023.db
-- .output data/lists_2023-02.sql
-- .dump lists_2022
-- .output data/lists_2023-03.sql
-- .dump raw_lists
-- .output data/lists_2023-04.sql
-- .dump src_lists
--
-- sed -i 's/lists_2022/raw_lists_02/g' data/lists_2023-02.sql
-- sed -i 's/raw_lists/raw_lists_03/g' data/lists_2023-03.sql
-- sed -i 's/src_lists/raw_lists_04/g' data/lists_2023-04.sql
--
-- .read data/lists_2023-02.sql
-- .read data/lists_2023-03.sql
-- .read data/lists_2023-04.sql
--
-- * Move original fluff.db table
-- ALTER TABLE raw_lists RENAME TO tmp_raw_lists;
-- ALTER TABLE stg_lists RENAME TO tmp_stg_lists;
--
-- * Start operation
-- CREATE TABLE raw_lists AS
-- SELECT u.id AS user_id, rl.*, NULL as next_date
-- FROM users u
-- 	JOIN raw_lists_02 rl
-- 	USING (username)
--
-- `dbt run` / make sql
--
-- * Run the above query for raw_lists_03 and 04 too
--
-- * Query for checking whether it's loaded correctly
-- SELECT COUNT(next_date) FROM stg_lists

-- * Trying to make 🔻 and 🔺 indicator
-- ? idea:
-- ? preserve only the earliest date if record are unchanged in subsequent date.
-- ? this format means unchanged dates applies to later date *until* a change is encountered
-- ' note:
-- ' don't change score when some users change their score;
-- ' change score only when there's additional audience
-- ! Code below is kinda wrong, I guess?
-- ! Rather than putting indicator when score increases, I should've put it when a certain
-- ! *order* changes. **That's why I need to get the ordering right first**
-- WITH
-- all_lists AS (
-- 	SELECT * FROM v_appropriate_score -- ' (1)
-- 	UNION
-- 	SELECT username, score, anichan_score, status, media_id,
-- 		media_type, title, progress, completed_at, retrieved_date,
-- 		user_id AS id, score_format, generation, appropriate_score
-- 	FROM stg_lists
-- ),
-- as_rules AS (
-- 	SELECT
-- 		media_id,
-- 		title,
-- 		media_type,
-- 		CAST(ROUND(AVG(anichan_score)) AS INTEGER) AS anichan_score,
-- 		CAST(ROUND(AVG(appropriate_score)) AS INTEGER) AS ff_score,
-- 		COUNT(1) AS audience_count,
-- 		retrieved_date
-- 	FROM all_lists
-- 	WHERE
-- 		(status = 'COMPLETED' OR (status IN ('CURRENT', 'PAUSED') AND progress >= 5))
-- 		AND anichan_score > 0
-- 		AND appropriate_score > 0
-- 	GROUP BY media_id, media_type, retrieved_date
-- 	HAVING COUNT(1) >= 5
-- ),
-- filter_lists AS (
-- 	-- Filter early to avoid unnecessary calculation
-- 	SELECT *
-- 	FROM as_rules
-- 	WHERE anichan_score >= 85 OR ff_score >= 85
-- ),
-- last_active_group AS (
-- 	-- order by `anichan_score`, as that's what's used in #ranking channels
-- 	SELECT *,
-- 		ROW_NUMBER() OVER (PARTITION BY media_type
-- 						   ORDER BY anichan_score DESC,
-- 									ff_score DESC,
-- 									audience_count DESC,
-- 									title DESC
-- 						   ) AS ranking
-- 	FROM filter_lists
-- 	WHERE retrieved_date = "2023-02-01"
-- ),
-- current_active_group AS (
-- 	SELECT *,
-- 		ROW_NUMBER() OVER (PARTITION BY media_type
-- 						   ORDER BY anichan_score DESC,
-- 									ff_score DESC,
-- 									audience_count DESC,
-- 									title DESC
-- 						   ) AS ranking
-- 	FROM filter_lists
-- 	WHERE retrieved_date = "2023-03-04" -- ' (2)
-- 		AND media_id || '-' || media_type IN
-- 			(SELECT media_id || '-' || media_type FROM last_active_group)
--
-- 	UNION
--
-- 	SELECT *,
-- 		NULL AS ranking
-- 	FROM filter_lists
-- 	WHERE retrieved_date = "2023-03-04" -- ' (2)
-- 	AND media_id || '-' || media_type NOT IN
-- 			(SELECT media_id || '-' || media_type FROM last_active_group)
-- )
-- SELECT
-- 	c.media_id,
-- 	c.title,
-- 	c.media_type,
-- 	c.ranking AS c_rank,
-- 	l.ranking AS l_rank,
-- 	c.audience_count AS c_audience_count,
-- 	l.audience_count AS l_audience_count,
-- 	c.anichan_score AS c_score,
-- 	l.anichan_score AS l_score,
-- 	CASE
-- 		WHEN c.ranking IS NULL THEN "new"
-- 		WHEN c.ranking > l.ranking AND c.anichan_score != l.anichan_score THEN "down"
-- 		WHEN c.ranking < l.ranking AND c.anichan_score != l.anichan_score THEN "up"
-- 		ELSE NULL
-- 	END AS rank_status
-- FROM current_active_group c
-- 	LEFT JOIN last_active_group l
-- 	USING (media_id, media_type)
-- WHERE media_type = "ANIME"
-- ORDER BY c_rank

-- * Fixing missing `user_id`
-- * `user_id` should be present and used in `score_mapping` JOIN
-- * it also should be present initially in `raw_lists` (as username could change)
-- * `user_id` helps for identifying users across time
-- ALTER TABLE score_mapping RENAME TO tmp_score_mapping
--
-- ' add `user_id` to `score_mapping`
-- CREATE TABLE score_mapping AS
-- SELECT user_id, username, score, anichan_score
-- FROM stg_lists
-- WHERE username IN (
--         SELECT username
--         FROM users
--         WHERE score_format IN ("POINT_5", "POINT_3")
-- )
-- GROUP BY 1, 2, 3, 4
--
-- DROP TABLE tmp_score_mapping;
-- DROP VIEW stg_raw_lists
--
-- ALTER TABLE raw_lists RENAME TO tmp_raw_lists;
--
-- ' add `user_id` to `raw_lists`
-- CREATE TABLE "raw_lists"(
-- 			user_id INT,
-- 			username TEXT,
-- 			score TEXT,
-- 			anichan_score TEXT,
-- 			status TEXT,
-- 			media_id INTEGER,
-- 			media_type TEXT,
-- 			title TEXT,
--          progress INTEGER,
--          completed_at TEXT,
-- 			retrieved_date TEXT,
-- 			next_date TEXT
-- )
--
-- INSERT INTO raw_lists
-- SELECT u.id, rl.*
-- FROM users u
-- JOIN tmp_raw_lists rl
-- USING (username)
--
-- DROP TABLE tmp_raw_lists;

-- * Investigating changing user's `score_format` using a new investigation.db
-- * dump commands:
-- CREATE TABLE inv_02_2023 AS SELECT * FROM lists l JOIN users u USING (username) WHERE username IN ('musangkuy', 'chameleon13');
-- sqlite3 fluff_02-2023.db ".dump 'inv_02_2023';" > 02-2023.sql
-- CREATE TABLE inv_04_2023 AS SELECT * FROM stg_lists WHERE username IN ('musangkuy', 'chameleon13');
-- sqlite3 fluff_04-2023.db ".dump 'inv_04_2023';" > 04-2023.sql
--
-- * load commands
-- sqlite3 investigation.db < 02-2023.sql
-- sqlite3 investigation.db < 04-2023.sql