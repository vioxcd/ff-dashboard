-- setup sql
DROP VIEW IF EXISTS vm_anichan_to_p3p5_scores;
DROP VIEW IF EXISTS v_aoty_2022;
DROP VIEW IF EXISTS v_appropriate_score;
DROP VIEW IF EXISTS v_as_rules;
DROP VIEW IF EXISTS v_favorites_p90;
DROP VIEW IF EXISTS v_buggy_users;
DROP VIEW IF EXISTS v_lists;
DROP VIEW IF EXISTS v_wide_tags;
DROP VIEW IF EXISTS v_media_stddev;
DROP VIEW IF EXISTS v_underrated;
DROP VIEW IF EXISTS v_studios_stats;
ALTER TABLE users DROP COLUMN is_buggy;