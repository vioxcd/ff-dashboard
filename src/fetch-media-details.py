import sqlite3
import time

import requests

DATABASE_NAME = "fluff.db"


def get_fluff_media():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    media_list_query = cur.execute(
        '''
        SELECT
            DISTINCT media_id, avg_score
        FROM
            v_as_rules
        WHERE
            avg_score >= 80.0
        ORDER BY
            2 DESC
        '''
    )
    return [media_id for (media_id, _) in media_list_query]
 

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
			cover_image_url_md TEXT,
			cover_image_url_lg TEXT,
			cover_image_url_xl TEXT,
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
            category TEXT,
            rank INT
		);
	"""
    cur.execute(query)
    print('Table `media tags` created!')

    cur.execute("DROP TABLE IF EXISTS media_tags_bridge")
    query = """
		CREATE TABLE IF NOT EXISTS media_tags_bridge(
            media_id INT,
            tag_id INT
		);
	"""
    cur.execute(query)
    print('Table `media tags bridge` created!')


def save_media_detail_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    # 16
    query = "INSERT INTO media_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.execute(query, data)
    con.commit()
    print(f'{data[1]} saved!')


def save_media_tags_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO media_tags VALUES (?, ?, ?, ?)"
    cur.executemany(query, data)
    con.commit()
    if data:
        print(f'{data} saved!')


def save_media_tag_bridge_to_db(media_id, tags):
    media_id_tag_id_pairs = [(media_id, tag['id']) for tag in tags]
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO media_tags_bridge VALUES (?, ?)"
    cur.executemany(query, media_id_tag_id_pairs)
    con.commit()
    print(f"{media_id}'s tags saved!")


def fetch_media_details(media_id):
    query = '''
    query ($media_id: Int) {
        Media(id: $media_id) {
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

        if results['errors'][0]['status'] == 429:
            print('Waiting for rate limit to be restored')
            time.sleep(70)

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
        media_id,
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

    for media_id in media_ids:
        data = fetch_media_details(media_id)
        if not data:
            print(f"Error on {media_id}")
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
        tags_ = [list(tag.values()) for tag in new_tags]
        save_media_tags_to_db(tags_ )

        """Update tags list"""
        new_tag_ids = [tag['id'] for tag in new_tags]
        tags.update(new_tag_ids)

        """Save media-tag relationship"""
        save_media_tag_bridge_to_db(media_id, data["Media"]["tags"])