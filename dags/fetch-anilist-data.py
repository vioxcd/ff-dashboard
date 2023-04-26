import datetime as dt
from pathlib import Path

from custom.operators import (AnilistDownloadImagesOperator,
                              AnilistFetchMediaDetailsOperator,
                              AnilistFetchUserFavouritesOperator,
                              AnilistFetchUserListOperator)
from sheets.export import export

from airflow import DAG, configuration
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.utils.state import State

ROOT_DIR = Path(configuration.get_airflow_home()).parent
ENVIRONMENT_TYPE = Variable.get("ENVIRONMENT_TYPE", "DEVELOPMENT")
ENVIRONMENT_CONN_MAPPING = {
    "DEVELOPMENT": 'fluff_db',
    "TESTING": 'fluff_test_db',
}
CONN_ID = ENVIRONMENT_CONN_MAPPING[ENVIRONMENT_TYPE]
DBT_MODEL_TMP_FETCH_MEDIA_DETAILS = 'tmp_fetch_media_details'
DBT_PROJECT_DIR = Variable.get("DBT_PROJECT_DIR", str(ROOT_DIR / "sql_transforms"))
DBT_TARGET_PROFILE = 'test' if ENVIRONMENT_TYPE == "TESTING" else 'dev'


def skip_if_specified(context):
    task_id = context['task'].task_id
    conf = context['dag_run'].conf or {}
    skip_tasks = conf.get('skip_tasks', [])
    if task_id in skip_tasks:
        ti = context['dag_run'].get_task_instance(task_id)
        ti.set_state(State.SUCCESS)
        raise AirflowException()


default_args = {
    'trigger_rule': 'all_success',  # for skipping tasks
    'pre_execute': skip_if_specified,
    'conn_id': CONN_ID,
    'environment_type': ENVIRONMENT_TYPE
}

# to skip: go to Airflow's dag detail, click on the ">" and pick trigger w/ config
# insert task_id in the config just like below to skip tasks
# {"skip_tasks": ["fetch_user_favorites"]}

with DAG(
    dag_id="fetch_anilist_data",
    description="Fetches users' score format, lists, favourites, and all media details from the Anilist API using a custom operator.",
    start_date=dt.datetime(2023, 4, 4),
    end_date=dt.datetime(2023, 4, 9),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    tags=[
        'anilist',
    ],
) as dag:

    start, end = [EmptyOperator(task_id=tid) for tid in ["start", "end"]]

    load_p3p5_score_mapping = SQLExecuteQueryOperator(
        task_id="load_p3p5_score_mapping",
        sql="sqls/mapping_p3p5_score.sql",
        split_statements=True,
        return_last=False,
    )

    fetch_user_lists = AnilistFetchUserListOperator(
        task_id="fetch_user_lists",
    )

    fetch_user_favourites = AnilistFetchUserFavouritesOperator(
        task_id="fetch_user_favourites",
    )

    create_needed_media_details_table = BashOperator(
        task_id='create_needed_media_details_table',
        bash_command=f'''
            dbt run \
                --project-dir {DBT_PROJECT_DIR} \
                --target {DBT_TARGET_PROFILE} \
                --select +{DBT_MODEL_TMP_FETCH_MEDIA_DETAILS}
        '''
    )

    fetch_media_details = AnilistFetchMediaDetailsOperator(
        task_id="fetch_media_details",
    )

    download_images = AnilistDownloadImagesOperator(
        task_id="download_images",
    )

    run_dbt = BashOperator(
        task_id='run_dbt',
        bash_command=f'''
            dbt run \
                --project-dir {DBT_PROJECT_DIR} \
                --target {DBT_TARGET_PROFILE}
        '''
    )

    export_to_sheet = PythonOperator(
        task_id="export_to_sheet",
        python_callable=export,
    )

    chain(start, load_p3p5_score_mapping,
          [fetch_user_lists, fetch_user_favourites], create_needed_media_details_table,
          fetch_media_details, [download_images, run_dbt], export_to_sheet, end
    )
