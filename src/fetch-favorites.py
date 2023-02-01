import sqlite3
import time

import requests

DATABASE_NAME = "fluff.db"


def get_fluff_users_and_ids():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "SELECT username, id FROM users"
    res = cur.execute(query)
    return res.fetchall()


def create_table():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS favourites")
    query = """
		CREATE TABLE favourites(
			user_id INT,
			name TEXT,
			type TEXT,
			cover_image_url TEXT
		);

	"""
    cur.execute(query)
    print('Table favourites created!')


def save_favourites_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO favourites VALUES (?, ?, ?, ?)"
    cur.executemany(query, data)
    con.commit()
    print('Results saved!')


def get_query(query_type, page, user_id, per_page=50):
	"""
	query_type: queries.keys() -- anime, manga, characters, staff, or studios
	"""
	query_template = '''
	query ($page: Int, $perPage: Int, $id: Int) {
		User(id: $id) {
			favourites {
				%s
			}
		}
	}
	'''
	queries_opts = {
		"anime": '''
			anime(page: $page, perPage: $perPage) {
				nodes {
					title {
						romaji,
						english
					},
					coverImage {
						large
					}
				},
				pageInfo {
					hasNextPage
				}
			}
		''',
		"manga": '''
			manga(page: $page, perPage: $perPage) {
				nodes {
					title {
						romaji,
						english
					},
					coverImage {
						large
					}
				},
				pageInfo {
					hasNextPage
				}
			}
		''',
		"characters": '''
			characters(page: $page, perPage: $perPage) {
				nodes {
					name {
						full
					},
					image {
						large
						medium
					}
				},
				pageInfo {
					hasNextPage
				}
			}
		''',
		"staff": '''
			staff(page: $page, perPage: $perPage) {
				nodes {
					name {
						full
					},
					image {
						large
					}
				},
				pageInfo {
					hasNextPage
				}
			}
		''',
		"studios": '''
			studios(page: $page, perPage: $perPage) {
				nodes {
					name 
				},
				pageInfo {
					hasNextPage
				}
			}
		'''
	}

	query = queries_opts[query_type]
	variables = {
		'page': page,
		'perPage': per_page,
		'id': user_id,
	}
	return {'query': query_template % query, 'variables': variables}


def fetch(params):
    print(f"Requesting {params['variables']}")
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json=params)
    results = response.json()

    # handle rate limit error
    if "errors" in results:
        print(results['errors'][0]['message'])

        if results['errors'][0]['status'] == 429:
            print('Waiting for rate limit to be restored')
            time.sleep(70)

        return None

    return results['data']


def extract_favourites(node, query_type, user_id):
	match query_type:
		case "anime" | "manga":
			return (
				user_id,
				node['title']['english'] or node['title']['romaji'],
				query_type,
				node['coverImage']['large'],
			)
		case "characters" | "staff":
			return (
				user_id,
				node['name']['full'],
				query_type,
				node['image']['large'],
			)
		case "studios":
			return (
				user_id,
				node['name'],
				query_type,
				None,  # studio don't have cover image
			)


if __name__ == "__main__":
	fluff_users_and_ids = get_fluff_users_and_ids()
	create_table()

	for username, user_id in fluff_users_and_ids:
		for query_type in ['anime', 'manga', 'characters', 'staff', 'studios']:
			# loop
			page = 1  # starts from 1
			has_next_page = True
			while has_next_page:
				print(f'Processing {query_type} favourites for {username} on page {page}')

				# one fetch-save cycle
				query_params = get_query(query_type, page, user_id)
				results = fetch(query_params)

				if results:
					fav_items = results['User']['favourites'][query_type]
					has_next_page = fav_items['pageInfo']['hasNextPage']
					page += 1

					data = [extract_favourites(node, query_type, user_id)
							for node in fav_items['nodes']]
					save_favourites_to_db(data)
				
				# sleep for a while to avoid rate_limiting
				time.sleep(1.0)

			print(f'Saving {query_type} favourites for user {username}')
	print('Done!')
