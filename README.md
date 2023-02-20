# Fluffy Folks Dashboard

An automated version of `#rankings` channel in Fluffy Folks' discord

Why?  
(1) the manual version seems painful (and not as complete).  
(2) I'm learning about dashboarding stuffs (and pipelines!).

See `FEATURES.md` for details of features, unworked TODOs, and bugs

## Installation

### Some Notes

- I encountered some pip's dependency error when trying to install `jsonschema` which are used by `dbt-core` and `airflow`. Try to install `airflow` first before `dbt-core` (as the former uses `jsonschema` v3, and the latter default to v4.17 but could be made to work with v3)

### Airflow

See [Airflow's Quick Start](https://airflow.apache.org/docs/apache-airflow/stable/start.html)

```bash
# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
export AIRFLOW_HOME="$(pwd)/airflow"

# Install Airflow using the constraints file
AIRFLOW_VERSION=2.5.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example: https://raw.githubusercontent.com/apache/airflow/constraints-2.5.1/constraints-3.7.txt
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# The Standalone command will initialise the database, make a user,
# and start all components for you.
airflow standalone

# Visit localhost:8080 in the browser and use the admin account details
# shown on the terminal to login.
# Enable the example_bash_operator dag in the home page
```
