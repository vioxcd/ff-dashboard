-- Place for various utility queries
-- ! NOT TO BE RUN DIRECTLY

-- Rename cover_image column name mistakes
-- probably only ran once (ever)
-- ALTER TABLE media_details RENAME COLUMN cover_image_url_md TO cover_image_url_xl_bak;
-- ALTER TABLE media_details RENAME COLUMN cover_image_url_xl TO cover_image_url_md;
-- ALTER TABLE media_details RENAME COLUMN cover_image_url_xl_bak TO cover_image_url_xl;