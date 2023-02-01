import os
import sqlite3
import time

import requests

DATABASE_NAME = "fluff.db"


def get_fluff_users_and_ids():
    with open('fluff', 'r') as f:
        data = list(map(lambda x: x.rstrip('\n').split(','), f.readlines()))
        print(f'Fluff: {data}')
    return data


def create_db():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS users")
    query = """
		CREATE TABLE users(
            id INT,
			username TEXT,
			score_format TEXT
		);

	"""
    cur.execute(query)
    print('Table users created!')

    cur.execute("DROP TABLE IF EXISTS lists")
    query = """
		CREATE TABLE lists(
			username TEXT,
			scores TEXT,
			scores_anichan TEXT,
			status TEXT,
			media_id INTEGER,
			media_type TEXT,
			title TEXT,
            progress INTEGER,
            completed_at TEXT
		);
	"""
    cur.execute(query)
    print('Table lists created!')


def save_list_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO lists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.executemany(query, data)
    con.commit()
    print('Results saved!')


def save_user_to_db(id_, username, score_format):
    """Saves username, id_, and score_format to db"""
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = f"INSERT INTO users VALUES ('{id_}', '{username}',  '{score_format}')"
    cur.execute(query)
    con.commit()
    print(f'{username} info saved!')


def query_score_format(id_):
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


def query_list(page, username, per_page=50):
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


def fetch(params):
    """Fetch data, returns Page. Returns None on error"""
    print(f"Requesting {params['variables']}")
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json=params)
    results = response.json()

    # handle rate limit error
    if "errors" in results:
        print(results['errors']['message'])

        if results['errors']['status'] == 429:
            print('Waiting for rate limit to be restored')
            time.sleep(70)

        return None

    return results['data']


if __name__ == "__main__":
    users_and_ids = get_fluff_users_and_ids()

    create_db()

    for username, id_ in users_and_ids:
        params = query_score_format(id_)
        results = fetch(params)

		# if error happened
        if not results:
            continue

		# check if username is still the same
        if username != results['User']['name']:
            username = results['User']['name']

        score_format = None
        if results:
            score_format = results['User']['mediaListOptions']['scoreFormat']
        save_user_to_db(id_, username, score_format)

        page = 1  # starts from 1
        has_next_page = True
        data = []
        while has_next_page:
            print(f'Processed {username} page {page}')

            # one fetch-save cycle
            params = query_list(page, username)
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
                     completed_at
                    ))

            # sleep for a while to avoid rate_limiting
            time.sleep(1.0)

        save_list_to_db(data)
        print(f'Saving {len(data)} lists for user {username}')

    print('Done!')
