{{ config(tags="tmp") }}

-- particular interesting detail: the COUNT(1) - 1
-- it covers the use in `as_rules` and `seasonals`
SELECT media_id
FROM {{ ref('stg_lists') }}
GROUP BY media_id, media_type
HAVING COUNT(1) >= (
	SELECT CAST(FLOOR(COUNT(1) * .2) AS INTEGER) - 1
	FROM {{ source('ff_anilist', 'users') }}
)

UNION

SELECT media_id
FROM {{ ref('int_media__by_status') }}

UNION

SELECT media_id
FROM {{ ref('int_media__potential') }}
WHERE anichan_score >= 80 OR ff_score >= 80 -- same as `final_potential`

UNION

SELECT item_id AS media_id
FROM {{ source('ff_anilist', 'favourites') }}
WHERE type IN ("anime", "manga")