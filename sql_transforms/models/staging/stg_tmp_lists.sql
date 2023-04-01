{{ config(
	materialized="table",
	tags=["staging", "historical", "temporary_table"]
) }}

SELECT * FROM stg_lists