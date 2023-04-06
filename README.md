# Fluffy Folks Dashboard

An end-to-end pipeline and dashboard of Fluffy Folks' statistics!

This pipeline:

1. Fetches and stores the historical FF's data from Anilist

2. Calculates [many interesting statistics](#statistics) that can be viewed from a dashboard

3. *(WIP)* Periodically exports a version of `#rankings` channel content (from Fluffy Folks' discord) to accessible sheets

4. Created using `Airflow`, `dbt`, and `streamlit`

## Why?

1. the statistics seems super interesting!

2. manual data aggregation in `#rankings` channel seems painful and not as complete

3. I'm learning about pipelines, SQLs, and dashboarding stuffs

See `FEATURES.md` for details of features, unworked TODOs, and bugs

## Installation & Usage

1. Install packages

    `pip install -r requirements.txt`

2. Export default Airflow's home directory

   `export AIRFLOW_HOME="$(pwd)/airflow"`

3. Setup Airflow, set users, config, and default connections

    `make setup-airflow`

4. Start Airflow's webserver and scheduler

    `make start-airflow`

5. Navigate to [fetch-anilist-data.py](./dags/fetch-anilist-data.py#L54) to configure `start_date` and `end_date` param

    (try today as start date and a week from now as end date. this steps make sure the dag can run within a given date!)

6. Go to `localhost:8080` to access Airflow's UI page. Use `airflow` as username and password.

7. Search for the dags using tags `anilist` (it could be the only one there) and unpause it by clicking the left-most switch button if it's not green (warning: unpausing the dag would run the whole data fetching pipeline! skip to point 11 to test the pipeline instead).

    Then, you can click the option in the right-hand side of the table and click "trigger dag" option to run the dag manually

    Alternatively, you can see point 10 where the dag are triggered from the cli

8. Click the dag name `fetch-anilist-data` and explore the dag!

9. Bring back down the webserver and scheduler

    `make stop-airflow`

10. The dag can also be triggered to run from the command-line

    `make trigger-airflow  # run the whole dags`

    see next point if you don't want to run the whole dags!

11. For testing simple dag runs

    `make test-airflow`

12. There's two database that could be created in the root folder, `fluff.db` or `fluff_test.db`. Both can be opened using the `sqlite3` [command-line tool](https://www.sqlite.org/download.html) or database browser, such as [DB Browser for SQLite](https://sqlitebrowser.org/)

13. To load sample data without running the whole dag (this would drop previously made database)

    `make load-sample-data`

14. To run `dbt` models. (caveat: you should setup your [profiles.yml](https://docs.getdbt.com/docs/core/connection-profiles) beforehand). Inspect the result run in the database afterwards

    `make sql`

15. To test the model run correctly

    `make sql-test`

16. To see `dbt` docs

    `make sql-docs`

17. Finally, to see the `streamlit` app

    `make app`

### Some Notes

- Most of the commands I use are recorded in the [Makefile](./Makefile).

- Some custom terminal stuff that is quite useful

  ```bash
  # Use below command to setup Airflow's command-line autocompletion
  eval "$(register-python-argcomplete airflow)"

  # Silence SQLAlchemy deprecation warning
  # https://stackoverflow.com/a/75109965
  export SQLALCHEMY_SILENCE_UBER_WARNING=1
  ```

- I encountered some pip's dependency error when trying to install `jsonschema` which are used by `dbt-core` and `airflow`. Try to install `airflow` first before `dbt-core` (as the former uses `jsonschema` v3, and the latter default to v4.17 but could be made to work with v3)

## Statistics

Work in progress!

## Caveats

A note for my future-self as well!

- Be careful when testing stuff! make sure the `ENVIRONMENT_TYPE` are according to what you're going to be doing, e.g. when you trying to test and there's error when running the command, the env-vars might not be *unset*, and from that point on, it might cause bugs in your dag runs when you're actually don't want to test
