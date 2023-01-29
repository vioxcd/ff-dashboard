-- Table Deduplication SQL

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
