import sqlite3
from typing import Optional

from airflow.models import BaseOperator, Variable
from airflow.utils.decorators import apply_defaults
from dags.custom.hooks import AnilistApiHook


class AnilistFetchUserListOperator(BaseOperator):
    """
    Operator that fetches user score_format and media ratings from the Anilist API

    Parameters
    ----------
    fluff_file : str
        path-like string to file containing fluffy folks' data with the format
        of `generation,username,id`
    """
    @apply_defaults
    def __init__(
            self,
            fluff_file: Optional[str] = None,
            fluff_db: Optional[str] = None,
            **kwargs
        ):
        super(AnilistFetchUserListOperator, self).__init__(**kwargs)
        self._fluff_file = fluff_file if fluff_file else 'fluff'
        self._database_name = fluff_db if fluff_db else Variable.get("DATABASE_NAME")
        self.log.info(f"Using {self._database_name}")

    def execute(self, context):
        # load static users data
        fluffs = self._get_fluff()

        # create users and lists table
        self._create_db()
        hooks = AnilistApiHook()

        for gen, username, id_ in fluffs:
            results = hooks.get_user_score_format(id_)
            if not results:  # if error happened
                self.log.error(f"Error when fetching {username} score format")
                continue

            # check if username is still the same
            if username != results['User']['name']:
                self.log.info(f"User's username has changed from {username} to {results['User']['name']}")
                username = results['User']['name']

			# persist user details to db
            score_format = results['User']['mediaListOptions']['scoreFormat']
            self._save_user_to_db(id_, username, score_format, gen)

            # next, prepare to process lists data
            data = hooks.get_user_lists(username)

            if not data:  # in case some error happened
                self.log.error(f"Error encountered. Fetch on {username} is aborted")
                continue
            self._save_list_to_db(data)
            self.log.info(f'Saving {len(data)} lists for user {username}')

        hooks.log_processed_results()
        self.log.info('Done!')

    def _get_fluff(self) -> list[tuple[int, str, int]]:
        """Load fluff data (gen, username, and AL ids)"""
        # gen: int, username: str, id: int
        format_fluff = lambda d: (int(d[0]), str(d[1]), int(d[2]))
        with open(self._fluff_file, 'r') as f:
            data = [format_fluff(line.rstrip('\n').split(','))
                    for line in f.readlines()]
            self.log.info(f'Fluff: {data}')
        return data

    def _create_db(self):
        con = sqlite3.connect(self._database_name)
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

    def _save_user_to_db(self, id_, username, score_format, gen):
        """Saves username, id_, score_format and gen to db"""
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        query = f"INSERT INTO users VALUES ('{id_}', '{username}', '{score_format}', '{gen}')"
        cur.execute(query)
        con.commit()
        self.log.info(f'{username} info saved!')

    def _save_list_to_db(self, data):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        query = "INSERT INTO raw_lists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.executemany(query, data)
        con.commit()
        self.log.info('Results saved!')


class AnilistFetchUserFavouritesOperator(BaseOperator):
    """
    Operator that fetches user's favourites list from the Anilist API

    Parameters
    ----------
    fluff_file : str
        path-like string to file containing fluffy folks' data with the format
        of `generation,username,id`
    """
    @apply_defaults
    def __init__(
            self,
            fluff_file: Optional[str] = None,
            fluff_db: Optional[str] = None,
            **kwargs
        ):
        super(AnilistFetchUserFavouritesOperator, self).__init__(**kwargs)
        self._fluff_file = fluff_file if fluff_file else 'fluff'
        self._database_name = fluff_db if fluff_db else Variable.get("DATABASE_NAME")

    def execute(self, context):
        # load static users data
        fluffs = [(row[1], row[2]) for row in self._get_fluff()]

        # create users and lists table
        self._create_db()
        hooks = AnilistApiHook()

        results = hooks.get_favourites(fluffs)
        self._save_favourites_to_db(results)

        hooks.log_processed_results()
        self.log.info('Done!')

    def _get_fluff(self) -> list[tuple[int, str, int]]:
        """Load fluff data (gen, username, and AL ids)"""
        # gen: int, username: str, id: int
        format_fluff = lambda d: (int(d[0]), str(d[1]), int(d[2]))
        with open(self._fluff_file, 'r') as f:
            data = [format_fluff(line.rstrip('\n').split(','))
                    for line in f.readlines()]
            self.log.info(f'Fluff: {data}')
        return data

    def _create_db(self):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS favourites")

        query = """
            CREATE TABLE favourites(
                user_id INT,
                item_id,
                name TEXT,
                type TEXT,
                cover_image_url TEXT
            );

        """
        cur.execute(query)
        self.log.info('Table favourites created!')

    def _save_favourites_to_db(self, data):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        query = "INSERT INTO favourites VALUES (?, ?, ?, ?, ?)"
        cur.executemany(query, data)
        con.commit()
        self.log.info('Results saved!')