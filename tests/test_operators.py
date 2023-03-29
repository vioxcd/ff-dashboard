import sqlite3
from pathlib import Path

import pytest

from dags.custom.operators import (AnilistFetchMediaDetailsOperator,
                                   AnilistFetchUserFavouritesOperator,
                                   AnilistFetchUserListOperator)

TEST_TASK_ID = "testing_anilist_fetch_user_operator"


@pytest.fixture
def fluff_test_file(tmp_path: Path):
	p = tmp_path / "fluff.test"
	p.write_text("1,vioxcd,5681809")
	return p

@pytest.fixture
def test_db(tmp_path: Path):
	p = tmp_path / "fluff_test.db"
	return p

def test_anilist_fetch_user_operator(fluff_test_file, test_db):
	task = AnilistFetchUserListOperator(
		task_id=TEST_TASK_ID,
		fluff_file=fluff_test_file,
		fluff_db=test_db
	)
	_ = task.execute(context={})

	with sqlite3.connect(test_db) as con:
		cur = con.cursor()
		assert cur.execute("SELECT COUNT(1) FROM users").fetchone()[0] == 1
		assert cur.execute("SELECT COUNT(1) FROM raw_lists").fetchone()[0] > 1

def test_anilist_fetch_favourites_operator(fluff_test_file, test_db):
	task = AnilistFetchUserFavouritesOperator(
		task_id=TEST_TASK_ID,
		fluff_file=fluff_test_file,
		fluff_db=test_db
	)
	_ = task.execute(context={})

	with sqlite3.connect(test_db) as con:
		cur = con.cursor()
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
