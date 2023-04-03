DB = fluff.db
export AIRFLOW_HOME := $(shell pwd)/airflow
PREV_AIRFLOW_DAGS_FOLDER := $(AIRFLOW_HOME)/dags
NEW_AIRFLOW_DAGS_FOLDER := $(shell pwd)/dags
EXECUTION_DATE := 04-04-2023
DAG_ID := fetch_anilist_data

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
	test -n $(AIRFLOW_HOME) || (echo "AIRFLOW_HOME is not set" ; exit 1)
	airflow webserver --port 8080 &
	airflow scheduler &

# to pass parameter, do it like `make test-airflow DAG_ID=[dag_id] EXECUTION_DATE=[execution_date]
# https://stackoverflow.com/a/2826178
test-airflow:
	airflow dags test \
		--conf '{"ENVIRONMENT_STATUS": "TESTING"}' \
		$(DAG_ID) \
		$(EXECUTION_DATE)

check-airflow-logs:
	find $(AIRFLOW_HOME)/logs/dag_id=fetch_anilist_data/**/* -name '*.log' | xargs -I {} grep -E "Processed:|Failed:" {} | sort --reverse | uniq

app:
	@echo "Starting streamlit app..."
	streamlit run src/app.py

sql:
	dbt run --project-dir sql_transforms

sql-test:
	dbt test --project-dir sql_transforms

sql-docs:
	dbt docs generate --project-dir sql_transforms
	dbt docs serve --project-dir sql_transforms --port 8081  # 8080 is Airflow's