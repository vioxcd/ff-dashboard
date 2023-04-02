{{ config(tags='final') }}

SELECT *
FROM {{ ref('int_favourites__pct_rank') }}
WHERE pct_rank > .9