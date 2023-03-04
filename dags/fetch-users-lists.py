import datetime as dt

from custom.operators import AnilistFetchUserListOperator

from airflow import DAG

with DAG(
    dag_id="fetch_users_details",
    description="Fetches users' score format and lists from the Anilist API using a custom operator.",
    start_date=dt.datetime(2023, 3, 3),
    end_date=dt.datetime(2023, 3, 4),
    schedule_interval="@daily",
) as dag:
    AnilistFetchUserListOperator(
        task_id="fetch_user_details",
    )
