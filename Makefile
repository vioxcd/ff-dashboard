export AIRFLOW_HOME := $(shell pwd)/airflow
PREV_AIRFLOW_DAGS_FOLDER := $(AIRFLOW_HOME)/dags
NEW_AIRFLOW_DAGS_FOLDER := $(shell pwd)/dags
EXECUTION_DATE := $(shell date +'%d-%m-%Y')
DAG_ID := fetch_anilist_data

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

stop-airflow:
	-kill -INT \
		$(shell ps -aux | grep '/bin/airflow webserver' | head -n 1 | awk '{print $$2}') \
		$(shell ps -aux | grep '/bin/airflow scheduler' | head -n 1 | awk '{print $$2}')

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