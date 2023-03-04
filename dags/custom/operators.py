import json
import os
import sqlite3
from typing import Optional

from custom.hooks import AnilistApiHook

from airflow.models import BaseOperator, Variable
from airflow.utils.decorators import apply_defaults

# Config
DATABASE_NAME: str = Variable.get("DATABASE_NAME")


class AnilistFetchUserListOperator(BaseOperator):
    """
    Operator that fetches user score_format and media ratings from the Anilist API

    Parameters
    ----------
    conn_id : str
        ID of the connection to use to connect to the Movielens API. Connection
        is expected to include authentication details (login/password) and the
        host that is serving the API.
    output_path : str
        Path to write the fetched ratings to.
    start_date : str
        (Templated) start date to start fetching ratings from (inclusive).
        Expected format is YYYY-MM-DD (equal to Airflow's ds formats).
    end_date : str
        (Templated) end date to fetching ratings up to (exclusive).
        Expected format is YYYY-MM-DD (equal to Airflow's ds formats).
    batch_size : int
        Size of the batches (pages) to fetch from the API. Larger values
        mean less requests, but more data transferred per request.
    """
    @apply_defaults
    def __init__(self, fluff_file: Optional[str] = None, **kwargs):
        super(AnilistFetchUserListOperator, self).__init__(**kwargs)
        self._fluff_file = fluff_file if fluff_file else 'fluff'

    def execute(self, context):
        # load static users data
        fluffs = self.get_fluff()

        # create users and lists table
        self.create_db()
        hooks = AnilistApiHook()

        for gen, username, id_ in fluffs:
            results = hooks.fetch_user_score_format(id_)
            if not results:  # if error happened
                self.log.error(f"Error when fetching {username} score format")
                continue

            # check if username is still the same
            if username != results['User']['name']:
                self.log.info(f"User's username has changed from {username} to {results['User']['name']}")
                username = results['User']['name']

			# persist user details to db
            score_format = results['User']['mediaListOptions']['scoreFormat']
            self.save_user_to_db(id_, username, score_format, gen)

            # next, prepare to process lists data
            data = hooks.fetch_user_lists(username)
            
            if not data:  # in case some error happened
                self.log.error(f"Error encountered. Fetch on {username} is aborted")
                continue
            self.save_list_to_db(data)
            self.log.info(f'Saving {len(data)} lists for user {username}')

        self.log.info('Done!')

    def get_fluff(self) -> list[tuple[int, str, int]]:
        """Load fluff data (gen, username, and AL ids)"""
        # gen: int, username: str, id: int
        format_fluff = lambda d: (int(d[0]), d[1], int(d[2]))
        with open('fluff', 'r') as f:
            data = [format_fluff(line.rstrip('\n').split(','))
                    for line in f.readlines()]
            self.log.info(f'Fluff: {data}')
        return data

    def create_db(self):
        con = sqlite3.connect(DATABASE_NAME)
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS users")
        query = """
            CREATE TABLE users(
                id INT,
                username TEXT,
                score_format TEXT,
                generation INT
            );
        """
        cur.execute(query)
        self.log.info('Table users created!')

        cur.execute("DROP TABLE IF EXISTS raw_lists")
        query = """
            CREATE TABLE raw_lists(
                username TEXT,
                score TEXT,
                anichan_score TEXT,
                status TEXT,
                media_id INTEGER,
                media_type TEXT,
                title TEXT,
                progress INTEGER,
                completed_at TEXT,
                retrieved_date TEXT
            );
        """
        cur.execute(query)
        self.log.info('Table lists created!')

    def save_user_to_db(self, id_, username, score_format, gen):
        """Saves username, id_, score_format and gen to db"""
        con = sqlite3.connect(DATABASE_NAME)
        cur = con.cursor()
        query = f"INSERT INTO users VALUES ('{id_}', '{username}', '{score_format}', '{gen}')"
        cur.execute(query)
        con.commit()
        self.log.info(f'{username} info saved!')

    def save_list_to_db(self, data):
        con = sqlite3.connect(DATABASE_NAME)
        cur = con.cursor()
        query = "INSERT INTO raw_lists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.executemany(query, data)
        con.commit()
        self.log.info('Results saved!')
