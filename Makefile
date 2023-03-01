DB = fluff.db
export AIRFLOW_HOME := $(shell pwd)/airflow
PREV_AIRFLOW_DAGS_FOLDER := $(AIRFLOW_HOME)/dags
NEW_AIRFLOW_DAGS_FOLDER := $(shell pwd)/dags

clean:
	rm ff.log fluff.db

setup-airflow:
	@echo $(AIRFLOW_HOME)

	# required airflow initialization
	airflow db init
	airflow users create \
		--username admin \
		--password admin \
		--firstname Airflow \
		--lastname Admin \
		--role Admin \
		--email me@example.com

	# set dags folder
	mkdir -p dags
	sed -i "s|dags_folder = $(PREV_AIRFLOW_DAGS_FOLDER)|dags_folder = $(NEW_AIRFLOW_DAGS_FOLDER)|" airflow/airflow.cfg

	# set timezone
	sed -i 's|default_timezone = utc|default_timezone = Asia/Jakarta|' airflow/airflow.cfg
	sed -i 's|default_ui_timezone = UTC|default_ui_timezone = Asia/Jakarta|' airflow/airflow.cfg

	# set environment variables for the project
	airflow variables set DATABASE_NAME $(DB)

start-airflow:
	airflow webserver --port 8080 &
	airflow scheduler &

redo-db:
	rm fluff.db
	cp fluff.db.bak fluff.db

download-images:
	mkdir -p images
	python3 src/download-images.py

app:
	@echo "Starting streamlit app..."
	streamlit run src/app.py

sql:
	@echo "Setting up views"
	@echo "Dropping..."
	sqlite3 $(DB) < sqls/view_setup_drop.sql

	@echo "Creating appropriate score view..."
	sqlite3 $(DB) < sqls/view_appropriate_score.sql

	@echo "Creating scores defined as rules view..."
	sqlite3 $(DB) < sqls/view_as_rules.sql

	@echo "Creating media lists section and ranking view..."
	sqlite3 $(DB) < sqls/view_media_section_and_ranking.sql

	@echo "Creating AOTY 2022 view..."
	sqlite3 $(DB) < sqls/view_aoty_2022.sql

	@echo "Creating favourites on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_favourites_p90.sql

	@echo "Creating anichan to 3 and 5 score format mapping view..."
	sqlite3 $(DB) < sqls/view_mapping_anichan_to_3_and_5_scores_format.sql

	@echo "Creating buggy users view..."
	sqlite3 $(DB) < sqls/view_buggy_users.sql

	@echo "Adding is_buggy column to users table..."
	sqlite3 $(DB) < sqls/mod_users_is_buggy.sql

	@echo "Update scores to its correct value..."
	sqlite3 $(DB) < sqls/update_score.sql

	@echo "Creating media standard dev. view..."
	sqlite3 $(DB) < sqls/view_media_stddev.sql

	@echo "Creating most divisive media on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_divisive_media_p90.sql

	@echo "Creating most dropped media on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_dropped_media_p90.sql

	@echo "Creating wide media-tags view..."
	sqlite3 $(DB) < sqls/view_wide_tags.sql

	@echo "Creating underrated view..."
	sqlite3 $(DB) < sqls/view_underrated.sql

	@echo "Creating studios statistics view..."
	sqlite3 $(DB) < sqls/view_studios_stats.sql

	@echo "Creating tags 90th percentile statistics view..."
	sqlite3 $(DB) < sqls/view_tags_counts_p90.sql

	@echo "Creating tags per-media 90th percentile statistics view..."
	sqlite3 $(DB) < sqls/view_tags_counts_by_media_p90.sql

	@echo "Creating tags subcategory's ranks view..."
	sqlite3 $(DB) < sqls/view_tags_subcategory_ranked.sql

	@echo "Creating tags subcategory's favourites stats view..."
	sqlite3 $(DB) < sqls/view_tags_subcategory_favorited.sql

	@echo "Done!"
