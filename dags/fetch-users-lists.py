import datetime as dt

from custom.operators import (AnilistFetchUserFavouritesOperator,
                              AnilistFetchUserListOperator)

from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="fetch_users_lists",
    description="Fetches users' score format and lists from the Anilist API using a custom operator.",
    start_date=dt.datetime(2023, 3, 30),
    end_date=dt.datetime(2023, 3, 31),
    schedule_interval="@daily",
) as dag:
    start = EmptyOperator(
        task_id='start'
    )

    end = EmptyOperator(
        task_id='end'
    )

    # fetch_user_lists = AnilistFetchUserListOperator(
    #     task_id="fetch_user_lists",
    # )

    fetch_user_favorites = AnilistFetchUserFavouritesOperator(
        task_id="fetch_user_favorites",
    )

    # start >> fetch_user_lists >> fetch_user_favorites >> end
    start >> fetch_user_favorites >> end
