import math
import sqlite3
import time

import requests
from pyrate_limiter import BucketFullException, Duration, Limiter, RequestRate

DATABASE_NAME = "fluff.db"

# https://anilist.gitbook.io/anilist-apiv2-docs/overview/rate-limiting
minutely_rate = RequestRate(80, Duration.MINUTE)
limiter = Limiter(minutely_rate)

RETRY_ATTEMPTS = 3  # control variable if BucketFullException is encountered


def get_fluff_media():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    return list(cur.execute('''
        SELECT media_id
        FROM v_as_rules
        UNION
        SELECT item_id
        FROM favourites
        WHERE type IN ("anime", "manga")
    '''))


def create_table():
    con = sqlite3.connect(DATABASE_NAME)
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
            type TEXT,
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
    print('Table `media details` created!')

    cur.execute("DROP TABLE IF EXISTS media_tags")
    query = """
		CREATE TABLE IF NOT EXISTS media_tags(
            tag_id INT,
            name TEXT,
            category TEXT
		);
	"""
    cur.execute(query)
    print('Table `media tags` created!')

    cur.execute("DROP TABLE IF EXISTS media_tags_bridge")
    query = """
		CREATE TABLE IF NOT EXISTS media_tags_bridge(
            media_id INT,
            tag_id INT,
            rank INT
		);
	"""
    cur.execute(query)
    print('Table `media tags bridge` created!')


def save_media_detail_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    # 17
    query = "INSERT INTO media_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.execute(query, data)
    con.commit()
    print(f'{data[1]} saved!')


def save_media_tags_to_db(tags):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO media_tags VALUES (?, ?, ?)"
    cur.executemany(query, tags)
    con.commit()
    if tags:
        print(f'{tags} saved!')


def save_media_tag_bridge_to_db(media_id, tags):
    media_tag_bridges = [(media_id, tag['id'], tag['rank']) for tag in tags]
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO media_tags_bridge VALUES (?, ?, ?)"
    cur.executemany(query, media_tag_bridges)
    con.commit()
    print(f"{media_id}'s tags saved!")


@limiter.ratelimit('identity')
def fetch_media_details(media_id):
    query = '''
    query ($media_id: Int) {
        Media(id: $media_id) {
            id,
            title {
                english,
                native,
                romaji
            },
            season,
            seasonYear,
            episodes,
            type,
            format,
            genres,
            coverImage {
    	        extraLarge,
                large,
                medium
            },
            bannerImage,
            averageScore,
            meanScore,
            source,
            studios {
                edges {
                    isMain
                    node {
                        id,
                        name,
                        isAnimationStudio
                    }
                }
            },
            tags {
                id,
                name,
                category,
                rank
            },
            relations {
                edges {
                    node {
                        id,
                        title {
                        romaji
                        english
                        native
                        userPreferred
                        }
                    },
                    relationType
                }
            }
        }
    }
    '''
    params = {'query': query, 'variables': {'media_id': media_id}}
    url = 'https://graphql.anilist.co'

    response = requests.post(url, json=params)
    results = response.json()

    # handle rate limit error
    if "errors" in results:
        print(results['errors'][0]['message'])
        return None

    return results['data']


def process_media(data):
    media_detail = data['Media']
    
    """Processing several things"""
    genres = ", ".join(media_detail["genres"])
    studios_list = [studio_info["node"]["name"]
                    for studio_info in media_detail["studios"]["edges"]
                    if studio_info["isMain"]]
    studios = ", ".join(studios_list)
    is_sequel = any([True
                    for relation in media_detail["relations"]["edges"]
                    if relation["relationType"] == "PREQUEL"])

    """Creating object before saving"""
    return (
        media_detail['id'],
        media_detail["title"]["english"] or \
            media_detail["title"]["romaji"] or \
            media_detail["title"]["native"],
        media_detail["season"],
        media_detail["seasonYear"],
        media_detail["episodes"],
        media_detail["type"],
        media_detail["format"],
        genres,
        media_detail["coverImage"]["extraLarge"],
        media_detail["coverImage"]["large"],
        media_detail["coverImage"]["medium"],
        media_detail["bannerImage"],
        media_detail["averageScore"],
        media_detail["meanScore"],
        media_detail["source"],
        studios,
        is_sequel,
    )
 

if __name__ == '__main__':
    create_table()
    media_ids = get_fluff_media()
    tags = set()

    print(f"Processing {len(media_ids)} items")

    for media_id in media_ids:
        data = None

        for retries in range(RETRY_ATTEMPTS):
            if retries != 0:
                print(f"Retrying for {media_id}")

            try:
                data = fetch_media_details(media_id)
            except BucketFullException as err:
                print(err)
                print(err.meta_info)
                sleep_for = math.ceil(float(err.meta_info['remaining_time']))
                time.sleep(sleep_for)
            else:
                break

        if not data:
            print(f"Data not found on {media_id}")
            continue
        
        # 'media_id', 'title', 'season', 'season_year', 'type',
        # 'format', 'genres', 'cover_image_url_md', 'cover_image_url_lg', 'cover_image_url_xl'
        # 'banner_image_url', 'average_score', 'mean_score' 'source', 'studios', 'is_non_sequel'
        """Save media details"""
        media_details = process_media(data)
        save_media_detail_to_db(media_details)

        """Filter unseen tags"""
        new_tags = [tag for tag in data["Media"]["tags"]
                    if tag['id'] not in tags]

        """Save unseen tags"""

        tags_ = [(tag['id'], tag['name'], tag['category']) for tag in new_tags]
        save_media_tags_to_db(tags_ )

        """Update tags list"""
        new_tag_ids = [tag['id'] for tag in new_tags]
        tags.update(new_tag_ids)

        """Save media-tag relationship"""
        save_media_tag_bridge_to_db(media_id, data["Media"]["tags"])
