import logging
import os
import sqlite3
import sys
from datetime import datetime as dt

import requests
from pyrate_limiter import Duration, Limiter, RequestRate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format("logs", os.path.basename(__file__))),
        logging.StreamHandler(sys.stdout)
    ]
)

DATABASE_NAME = "fluff.db"

# https://anilist.gitbook.io/anilist-apiv2-docs/overview/rate-limiting
minutely_rate = RequestRate(80, Duration.MINUTE)
limiter = Limiter(minutely_rate)


def get_fluff() -> list[tuple[int, str, int]]:
    """Load fluff data (gen, username, and AL ids)"""
    # gen: int, username: str, id: int
    format_fluff = lambda d: (int(d[0]), d[1], int(d[2]))
    with open('fluff', 'r') as f:
        data = [format_fluff(line.rstrip('\n').split(',')) for line in f.readlines()]
        logging.info(f'Fluff: {data}')
    return data


def create_db():
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
    logging.info('Table users created!')

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
    logging.info('Table lists created!')


def save_list_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO lists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.executemany(query, data)
    con.commit()
    logging.info('Results saved!')


def save_user_to_db(id_, username, score_format, gen):
    """Saves username, id_, score_format and gen to db"""
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = f"INSERT INTO users VALUES ('{id_}', '{username}', '{score_format}', '{gen}')"
    cur.execute(query)
    con.commit()
    logging.info(f'{username} info saved!')


def query_score_format(id_: int):
    query = '''
	query ($id: Int) {
		  User(id: $id) {
            id,
            name,
			mediaListOptions {
				scoreFormat
			}
		}
	}
	'''
    variables = {
        'id': id_,
    }
    return {'query': query, 'variables': variables}


def query_list(page, username, per_page):
    # this query has anichan specific score format included
    query = '''
	query ($page: Int, $perPage: Int, $username: String) {
		Page (page: $page, perPage: $perPage) {
			pageInfo {
				hasNextPage
			},
			mediaList(userName: $username) {
				score: score,
				anichan_score: score(format: POINT_100),
				status,
                progress,
                completedAt {
                    year
                    month
                    day
                },
				media {
					id,
					type,
					title {
						english,
						romaji,
						native
					}
				}
			}
		}
	}
	'''
    variables = {
        'page': page,
        'perPage': per_page,
        'username': username,
    }
    return {'query': query, 'variables': variables}


@limiter.ratelimit('identity', delay=True)
def fetch(params):
    """Fetch data, returns Page. Returns None on error"""
    logging.info(f"Requesting {params['variables']}")
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json=params)
    results = response.json()

    # handle rate limit error
    if "errors" in results:
        logging.error(f"Error when fetching {params['variables']}")
        logging.error(results['errors'][0]['message'])
        return None

    return results['data']


if __name__ == "__main__":
    fluffs = get_fluff()

    create_db()

    for gen, username, id_ in fluffs:
        params = query_score_format(id_)
        results = fetch(params)

		# if error happened
        if not results:
            continue

		# check if username is still the same
        if username != results['User']['name']:
            username = results['User']['name']

        score_format = results['User']['mediaListOptions']['scoreFormat']
        save_user_to_db(id_, username, score_format, gen)

        page = 1  # starts from 1
        per_page = 1 if score_format in ('POINT_5', 'POINT_3') else 50
        has_next_page = True
        data = []
        while has_next_page:
            logging.info(f'Processed {username} page {page}')

            # one fetch-save cycle
            params = query_list(page, username, per_page)
            results = fetch(params)

            if results:
                has_next_page = results['Page']['pageInfo']['hasNextPage']
                page += 1

                for media in results['Page']['mediaList']:
                    day = media['completedAt']['day']
                    month = media['completedAt']['month']
                    year = media['completedAt']['year']
                    completed_at = f"{day}-{month}-{year}" if day and month and year else "-"

                    data.append((
                     username,
                     media['score'],
                     media['anichan_score'],
                     media['status'],
                     media['media']['id'],
                     media['media']['type'],
                     media['media']['title']['english'] or \
                      media['media']['title']['romaji'] or \
                      media['media']['title']['native'],
                     media['progress'],
                     completed_at,
                     dt.now().strftime("%Y-%m-%d")  # retrieved_date
                    ))

        save_list_to_db(data)
        logging.info(f'Saving {len(data)} lists for user {username}')

    logging.info('Done!')
