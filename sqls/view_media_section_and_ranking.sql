-- Media lists that are ready to be displayed, complete with sections and rankings
-- This view follows `as_rules` and takes into account sections & ranking (which previously are written in python, but now moved to SQL)
CREATE VIEW v_media_section_and_ranking
AS
WITH
get_media_lists AS (
	SELECT
		md.media_id,
		md.title,
		md.type AS media_type,
		md.cover_image_url_xl AS cover_image_url,
		ar.anichan_score,
		ar.ff_score,
		ar.audience_count
	FROM v_as_rules ar
	JOIN media_details md
		USING (media_id)
),
get_sections AS (
	SELECT *,
		CASE
			WHEN anichan_score >= 90 OR ff_score >= 90
				THEN "gold"
			WHEN (anichan_score > 85 AND anichan_score < 90)
				OR (ff_score > 85 AND ff_score < 90)
				THEN "silver"
			WHEN anichan_score = 85 OR ff_score = 85
				THEN "bronze"
			ELSE "-"
		END AS section
	FROM get_media_lists
),
get_sections_rank AS (
	SELECT *,	
		ROW_NUMBER() OVER (PARTITION BY media_type
							ORDER BY
								CASE section
									WHEN "gold" THEN 0
									WHEN "silver" THEN 1
									WHEN "bronze" THEN 2
									ELSE 3
								END,
								anichan_score DESC,
								ff_score DESC,
								audience_count DESC,
								title DESC
							) AS ranking
	FROM get_sections
)
SELECT *
FROM get_sections_rank
WHERE section != "-"
ORDER BY ranking