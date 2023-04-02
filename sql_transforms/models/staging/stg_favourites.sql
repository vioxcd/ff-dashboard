{{ config(tags="staging") }}

SELECT *
FROM {{ source('ff_anilist', 'favourites') }}
