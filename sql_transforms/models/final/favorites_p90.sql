{{ config(tags='final') }}

SELECT *
FROM {{ ref('int_favorites__pct_rank') }}
WHERE pct_rank > .9