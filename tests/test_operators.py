import sqlite3
from pathlib import Path

import pytest

from dags.custom.operators import (AnilistFetchUserFavouritesOperator,
                                   AnilistFetchUserListOperator)

TEST_TASK_ID = "testing_anilist_fetch_user_operator"


@pytest.fixture
def fluff_test_file(tmp_path: Path):
	p = tmp_path / "fluff.test"
	p.write_text("1,vioxcd,5681809")
	return p

@pytest.fixture
def mock_db(tmp_path: Path):
	p = tmp_path / "fluff_test.db"
	return p

def test_anilist_fetch_user_operator(fluff_test_file, mock_db):
	task = AnilistFetchUserListOperator(
		task_id=TEST_TASK_ID,
		fluff_file=fluff_test_file,
		fluff_db=mock_db
	)
	_ = task.execute(context={})

	with sqlite3.connect(mock_db) as con:
		cur = con.cursor()
		assert cur.execute("SELECT COUNT(1) FROM users").fetchone()[0] == 1
		assert cur.execute("SELECT COUNT(1) FROM raw_lists").fetchone()[0] > 1

def test_anilist_fetch_favourites_operator(fluff_test_file, mock_db):
	task = AnilistFetchUserFavouritesOperator(
		task_id=TEST_TASK_ID,
		fluff_file=fluff_test_file,
		fluff_db=mock_db
	)
	_ = task.execute(context={})

	with sqlite3.connect(mock_db) as con:
		cur = con.cursor()
		assert cur.execute("SELECT COUNT(1) FROM favourites").fetchone()[0] > 1
