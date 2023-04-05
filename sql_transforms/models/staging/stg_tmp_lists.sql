{{ config(
	materialized="table",
	tags=["staging", "historical", "temporary_table"]
) }}

--
-- START CUSTOM CTE
-- the CTEs below will not run in initial data load
-- ref: https://discourse.getdbt.com/t/writing-packages-when-a-source-table-may-or-may-not-exist/1487

{%- set source_relation = adapter.get_relation(
      database=source('ff_anilist', 'raw_lists').database,
      schema=source('ff_anilist', 'raw_lists').schema,
      identifier='stg_lists') -%}

{% set table_exists=source_relation is not none %}

{% if table_exists %}

SELECT * FROM stg_lists

{% else %}

SELECT
	NULL AS user_id,
	NULL AS username,
	NULL AS score_format,
	NULL AS generation,
	NULL AS score,
	NULL AS anichan_score,
	NULL AS appropriate_score,
	NULL AS status,
	NULL AS media_id,
	NULL AS media_type,
	NULL AS title,
	NULL AS progress,
	NULL AS completed_at,
	NULL AS retrieved_date,
	NULL AS next_date
-- this means there will be zero rows
WHERE FALSE

{% endif %}

-- END CUSTOM CTE
--
