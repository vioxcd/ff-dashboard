# Installation & Usage

1. Install packages

    `pip install -r requirements.txt`

2. Export default Airflow's home directory

   `export AIRFLOW_HOME="$(pwd)/airflow"`

3. Setup Airflow, set users, config, and default connections. Also, set the proper variables for exporting in `.env` file (follow the `.env.example` file)

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

    `make trigger-airflow SKIP_EXPORT=1  # skip export`

    see next point if you don't want to run the whole dags!

11. For testing simple dag runs

    `make test-airflow`

12. There's two database that could be created in the root folder, `fluff.db` or `fluff_test.db`. Both can be opened using the `sqlite3` [command-line tool](https://www.sqlite.org/download.html) or database browser, such as [DB Browser for SQLite](https://sqlitebrowser.org/)

13. To load sample data without running the whole dag (this would drop previously made database)

    `make load-sample-data`

14. To run `dbt` models. (don't forget to look at the setup of your [profiles.yml](./sql_transforms/profiles.yml)). Inspect the result run in the database afterwards

    `make sql`

15. To test the model run correctly

    `make sql-test SAMPLE_DATA_LOADED=1`

16. To see `dbt` docs

    `make sql-docs`

17. Finally, to see the `streamlit` app

    `make app`

18. If you set `SH_KEY` in `.env` file, it would also be filled with data now
