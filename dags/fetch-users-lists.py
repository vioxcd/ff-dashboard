import datetime as dt

from custom.operators import (AnilistDownloadImagesOperator,
                              AnilistFetchMediaDetailsOperator,
                              AnilistFetchUserFavouritesOperator,
                              AnilistFetchUserListOperator)

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator
from airflow.utils.state import State


def skip_if_specified(context):
    task_id = context['task'].task_id
    conf = context['dag_run'].conf or {}
    skip_tasks = conf.get('skip_tasks', [])
    if task_id in skip_tasks:
        ti = context['dag_run'].get_task_instance(task_id)
        ti.set_state(State.SUCCESS)
        raise AirflowException()


default_args = {
    'trigger_rule': 'all_done',  # for skipping tasks
    'pre_execute': skip_if_specified
}

# to skip: go to Airflow's dag detail, click on the ">" and pick trigger w/ config
# insert task_id in the config just like below to skip tasks
# {"skip_tasks": ["fetch_user_favorites"]}

with DAG(
    dag_id="fetch_users_lists",
    description="Fetches users' score format and lists from the Anilist API using a custom operator.",
    start_date=dt.datetime(2023, 3, 30),
    end_date=dt.datetime(2023, 3, 31),
    schedule_interval="@daily",
    default_args=default_args
) as dag:
    start = EmptyOperator(
        task_id='start'
    )

    end = EmptyOperator(
        task_id='end'
    )

    fetch_user_lists = AnilistFetchUserListOperator(
        task_id="fetch_user_lists",
    )

    fetch_user_favorites = AnilistFetchUserFavouritesOperator(
        task_id="fetch_user_favorites",
    )

    fetch_media_details = AnilistFetchMediaDetailsOperator(
        task_id="fetch_media_details",
    )

    download_images = AnilistDownloadImagesOperator(
        task_id="download_images",
    )

    start >> fetch_user_lists >> fetch_user_favorites >> fetch_media_details >> download_images >> end
