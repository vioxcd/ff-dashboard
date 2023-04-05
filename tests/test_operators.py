import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from airflow.models.dag import DAG
from dags.custom.operators import (AnilistDownloadImagesOperator,
                                   AnilistFetchMediaDetailsOperator,
                                   AnilistFetchUserFavouritesOperator,
                                   AnilistFetchUserListOperator)

TEST_TASK_ID = "testing_anilist_fetch_user_operator"


@pytest.fixture
def test_dag():
	return DAG(
        dag_id="test_dag",
        default_args={
			"owner": "me",
			"start_date": datetime(2022, 1, 1),
			'conn_id': 'fluff_test_db',
			'environment_type': 'TESTING'
		},
    )

@pytest.fixture
def fluff_test_file(tmp_path: Path):
	p = tmp_path / "fluff.test"
	p.write_text("1,vioxcd,5681809")
	return p

@pytest.fixture
def test_db(tmp_path: Path):
	p = tmp_path / "fluff_test.db"
	return p

@pytest.fixture
def tmp_image_folder(tmp_path: Path):
	d = tmp_path / "images"
	d.mkdir()
	return d

def test_anilist_fetch_user_operator(test_dag, fluff_test_file):
	task = AnilistFetchUserListOperator(
		task_id=TEST_TASK_ID,
		dag=test_dag,
		fluff_file=fluff_test_file,
	)
	_ = task.execute(context={})

	cur = task._db_hook.get_cursor()
	assert cur.execute("SELECT COUNT(1) FROM users").fetchone()[0] == 1
	assert cur.execute("SELECT COUNT(1) FROM raw_lists").fetchone()[0] > 1

def test_anilist_fetch_favourites_operator(test_dag, fluff_test_file):
	task = AnilistFetchUserFavouritesOperator(
		task_id=TEST_TASK_ID,
		fluff_file=fluff_test_file,
		dag=test_dag,
	)
	_ = task.execute(context={})

	cur = task._db_hook.get_cursor()
	assert cur.execute("SELECT COUNT(1) FROM favourites").fetchone()[0] > 1

def test_anilist_fetch_media_details_operator(test_db):
	with sqlite3.connect(test_db) as con:
		cur = con.cursor()
		cur.execute("CREATE TABLE favourites (item_id INT, type TEXT)")
		cur.execute("INSERT INTO favourites VALUES (20698, 'anime')")
		cur.execute("CREATE TABLE v_as_rules (media_id INT, type TEXT)")
		cur.execute("INSERT INTO v_as_rules  VALUES (20698, 'anime')")

	task = AnilistFetchMediaDetailsOperator(
		task_id=TEST_TASK_ID,
		fluff_db=test_db
	)
	_ = task.execute(context={})

	with sqlite3.connect(test_db) as con:
		cur = con.cursor()
		assert cur.execute("SELECT COUNT(1) FROM media_details").fetchone()[0] > 0
		assert cur.execute("SELECT COUNT(1) FROM media_tags").fetchone()[0] > 0
		assert cur.execute("SELECT COUNT(1) FROM media_tags_bridge").fetchone()[0] > 0

def test_download_images_operator(tmp_image_folder: Path, test_db):
	image_url = 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/small/bx20698-YZIYor2zW3Ta.png'
	with sqlite3.connect(test_db) as con:
		cur = con.cursor()
		cur.execute('''
			CREATE TABLE media_details (
				title TEXT,
				media_type TEXT,
				cover_image_url_xl TEXT
			)
		''')
		cur.execute('''
			INSERT INTO media_details VALUES
				('My Teen Romantic Comedy SNAFU TOO!', 'ANIME', '%s')
		''' % image_url)

	task = AnilistDownloadImagesOperator(
		task_id=TEST_TASK_ID,
		fluff_db=test_db,
		image_folder=str(tmp_image_folder)
	)
	_ = task.execute(context={})

	f = tmp_image_folder / image_url.split("/")[-1]
	assert f.exists()