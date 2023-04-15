DB := fluff.db
export AIRFLOW_HOME := $(shell pwd)/airflow
PREV_AIRFLOW_DAGS_FOLDER := $(AIRFLOW_HOME)/dags
NEW_AIRFLOW_DAGS_FOLDER := $(shell pwd)/dags
EXECUTION_DATE := $(shell date +"%Y-%m-%dT%H:%M:%S%z")
DAG_ID := fetch_anilist_data
SAMPLE_DATA_LOADED := 0
SKIP_EXPORT := 0

setup-airflow:
	@echo $(AIRFLOW_HOME)

	# required airflow initialization
	airflow db init
	airflow users create \
		--username airflow \
		--password airflow \
		--firstname Airflow \
		--lastname Admin \
		--role Admin \
		--email me@example.com

	# set dags folder
	sed -i "s|dags_folder = $(PREV_AIRFLOW_DAGS_FOLDER)|dags_folder = $(NEW_AIRFLOW_DAGS_FOLDER)|" airflow/airflow.cfg

	# set timezone
	sed -i 's|default_timezone = utc|default_timezone = Asia/Jakarta|' airflow/airflow.cfg
	sed -i 's|default_ui_timezone = UTC|default_ui_timezone = Asia/Jakarta|' airflow/airflow.cfg

	# don't load examples
	sed -i 's|load_examples = True|load_examples = False|' airflow/airflow.cfg

	# set database connection for the project
	# https://airflow.apache.org/docs/apache-airflow-providers-sqlite/stable/connections/sqlite.html
	# also see: `airflow connections list` | grep sqlite_default`
	# this command might error out if ran twice
	-airflow connections add 'fluff_db' \
		--conn-type 'sqlite' \
		--conn-host "$(shell pwd)/fluff.db"

	-airflow connections add 'fluff_test_db' \
		--conn-type 'sqlite' \
		--conn-host "$(shell pwd)/fluff_test.db"

start-airflow:
	test -n $(AIRFLOW_HOME) || (echo "AIRFLOW_HOME is not set" ; exit 1)
	airflow webserver --port 8080 &
	airflow scheduler &

# to pass parameter, do it like:
# `make test-airflow DAG_ID=[dag_id] EXECUTION_DATE=[execution_date]`
# `make test-airflow DAG_ID=fetch_anilist_data EXECUTION_DATE=$(date +'%d-%m-%Y')`
# https://stackoverflow.com/a/2826178
test-airflow:
	airflow variables set ENVIRONMENT_TYPE TESTING
	airflow dags test \
		$(DAG_ID) \
		$(EXECUTION_DATE)
	airflow variables delete ENVIRONMENT_TYPE

# https://stackoverflow.com/a/59316781
# `make trigger-airflow ENVIRONMENT_TYPE=TESTING`
trigger-airflow:
	airflow dags unpause $(DAG_ID)
	@if [ $(SKIP_EXPORT) = 0 ]; then \
		airflow dags trigger \
			-e $(EXECUTION_DATE) \
			-r "manual__$(EXECUTION_DATE)" \
			$(DAG_ID); \
	else \
		airflow dags trigger \
			-c '{"skip_tasks": ["export_to_sheet"]}' \
			-e $(EXECUTION_DATE) \
			-r "manual__$(EXECUTION_DATE)" \
			$(DAG_ID); \
	fi

stop-airflow:
	-kill -INT \
		$(shell ps -aux | grep '/bin/airflow webserver' | head -n 1 | awk '{print $$2}') \
		$(shell ps -aux | grep '/bin/airflow scheduler' | head -n 1 | awk '{print $$2}')

check-airflow-logs:
	find $(AIRFLOW_HOME)/logs/dag_id=fetch_anilist_data/**/* -name '*.log' | xargs -I {} grep -E "Processed:|Failed:" {} | sort --reverse | uniq

app:
	@echo "Starting streamlit app..."
	streamlit run src/streamlit/app.py

sql:
	dbt run --project-dir sql_transforms

sql-test:
	@if [ $(SAMPLE_DATA_LOADED) = 0 ]; then \
		dbt test --project-dir sql_transforms; \
	else \
		dbt test --project-dir sql_transforms --exclude final_aoty_2022; \
	fi

sql-docs:
	dbt docs generate --project-dir sql_transforms
	dbt docs serve --project-dir sql_transforms --port 8081  # 8080 is Airflow's

load-sample-data:
	sqlite3 $(DB) < $(shell pwd)/samples/dump_for_public.sql

run-export:
	python3 dags/sheets/export.py