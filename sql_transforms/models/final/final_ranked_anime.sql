{{ config(
	tags=["final", "export"]
) }}

SELECT *
FROM {{ ref('int_media__section_and_ranking') }}
WHERE media_type == "ANIME"