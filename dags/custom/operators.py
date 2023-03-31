import sqlite3
from pathlib import Path
from typing import Optional

from airflow import configuration
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
    fluff_db : str
        path-like string to sqlite3 db
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

        cur.execute("DROP TABLE IF EXISTS src_lists")
        query = """
            CREATE TABLE src_lists(
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

        query = "INSERT INTO src_lists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
    fluff_db : str
        path-like string to sqlite3 db
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
                item_id INT,
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


class AnilistFetchMediaDetailsOperator(BaseOperator):
    """
    Operator that fetches media list from the Anilist API

    Parameters
    ----------
    fluff_db : str
        path-like string to sqlite3 db
    """
    @apply_defaults
    def __init__(
            self,
            fluff_db: Optional[str] = None,
            **kwargs
        ):
        super(AnilistFetchMediaDetailsOperator, self).__init__(**kwargs)
        self._database_name = fluff_db if fluff_db else Variable.get("DATABASE_NAME")

    def execute(self, context):
        # load static users data
        media_ids = self._get_fluff_media()
        self.log.info(f"Processing {len(media_ids)} items")

        # create users and lists table
        self._create_db()
        hooks = AnilistApiHook()

        for (media_details, tags_, media_tag_bridges) in hooks.get_media_details(media_ids):
            self._save_media_detail_to_db(media_details)
            self._save_media_tags_to_db(tags_ )
            self._save_media_tag_bridge_to_db(media_tag_bridges)

        hooks.log_processed_results()
        self.log.info('Done!')

    def _get_fluff_media(self) -> list[int]:
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        return [media_id for (media_id,) in cur.execute('''
            SELECT media_id
            FROM v_as_rules
            UNION
            SELECT item_id
            FROM favourites
            WHERE type IN ("anime", "manga")
        ''')]

    def _create_db(self):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS media_details")
        # genres and studios are comma-separated list represented in string
        query = """
            CREATE TABLE IF NOT EXISTS media_details(
                media_id INT,
                title TEXT,
                season TEXT,
                season_year INT,
                episodes INT,
                media_type TEXT,
                format TEXT,
                genres TEXT,
                cover_image_url_xl TEXT,
                cover_image_url_lg TEXT,
                cover_image_url_md TEXT,
                banner_image_url TEXT,
                average_score REAL,
                mean_score REAL,
                source TEXT,
                studios TEXT,
                is_sequel BOOLEAN
            );
        """
        cur.execute(query)
        self.log.info('Table `media details` created!')

        cur.execute("DROP TABLE IF EXISTS media_tags")
        query = """
            CREATE TABLE IF NOT EXISTS media_tags(
                tag_id INT,
                name TEXT,
                category TEXT
            );
        """
        cur.execute(query)
        self.log.info('Table `media tags` created!')

        cur.execute("DROP TABLE IF EXISTS media_tags_bridge")
        query = """
            CREATE TABLE IF NOT EXISTS media_tags_bridge(
                media_id INT,
                tag_id INT,
                rank INT
            );
        """
        cur.execute(query)
        self.log.info('Table `media tags bridge` created!')

    def _save_media_detail_to_db(self, data):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        # 17
        query = "INSERT INTO media_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(query, data)
        con.commit()
        self.log.info(f'{data[1]} saved!')

    def _save_media_tags_to_db(self, tags):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        query = "INSERT INTO media_tags VALUES (?, ?, ?)"
        cur.executemany(query, tags)
        con.commit()
        if tags:
            self.log.info(f'{tags} saved!')


    def _save_media_tag_bridge_to_db(self, media_tag_bridges):
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        query = "INSERT INTO media_tags_bridge VALUES (?, ?, ?)"
        cur.executemany(query, media_tag_bridges)
        con.commit()


class AnilistDownloadImagesOperator(BaseOperator):
    """
    Operator that download images hosted from the Anilist API

    Parameters
    ----------
    fluff_db : str
        path-like string to sqlite3 db
    image_folder : str
        path-like string to folder that stores the images output
    """
    @apply_defaults
    def __init__(
            self,
            fluff_db: Optional[str] = None,
            image_folder : Optional[str] = None,
            **kwargs
        ):
        super(AnilistDownloadImagesOperator, self).__init__(**kwargs)
        self._database_name = fluff_db if fluff_db else Variable.get("DATABASE_NAME")
        self._output_path = Path(image_folder) if image_folder else Path(configuration.get_airflow_home()).parent / "images"

    def execute(self, context):
        existing_images = self._get_existing_images()
        media = [m for m in self._get_media_lists()
                 if m[2].split("/")[-1] not in existing_images]

        # ' check if environment is currently in testing
        if context.get('params', {}).get("ENVIRONMENT_STATUS") == "TESTING":
            media = media[:1]  # only take one sample

        self.log.info(f"Existing images: {len(existing_images)} items")
        self.log.info(f"Processing {len(media)} items")

        hooks = AnilistApiHook()
        self.log.info(f"Downloading images to {self._output_path}")
        self._output_path.mkdir(exist_ok=True)

        for m in media:
            hooks.download_image(m, self._output_path.absolute())

        hooks.log_processed_results()
        self.log.info('Done!')

    def _get_media_lists(self) -> list[tuple[str, str, str]]:
        con = sqlite3.connect(self._database_name)
        cur = con.cursor()
        return [m for m in cur.execute('''
            SELECT DISTINCT(title), media_type, cover_image_url_xl FROM media_details
        ''')]

    def _get_existing_images(self) -> set[str]:
        return set([file_.name for file_ in Path(self._output_path).iterdir()])
