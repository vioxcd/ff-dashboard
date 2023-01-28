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
            avg_score > 85.0
        ORDER BY
            2 DESC
        '''
    )
    return [media_id for (media_id, _) in media_list_query]
 

def create_table():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()

    query = """
		CREATE TABLE IF NOT EXISTS media_details(
            media_id INT,
			title TEXT,
            season TEXT,
            season_year TEXT,
            type TEXT,
			cover_image_url TEXT,
			banner_image_url TEXT,
            average_score REAL,
            mean_score REAL
		);

	"""
    cur.execute(query)
    print('Table media details created!')


def save_media_detail_to_db(data):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    query = "INSERT INTO media_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.execute(query, data)
    con.commit()
    print(f'{data[1]} saved!')


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
            type,
            coverImage {
    	        extraLarge
            },
            bannerImage,
            averageScore,
            meanScore
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

 
if __name__ == '__main__':
    create_table()

    media_ids = get_fluff_media()

    for media_id in media_ids:
        data = fetch_media_details(media_id)
        if not data:
            print(f"Error on {media_id}")
            continue
        
        # 'media_id', 'title', 'season', 'season_year', 'type',
        # 'cover_image_url', 'banner_image_url', 'average_score', 'mean_score'
        media_detail = data['Media']
        md = (
            media_id,
            media_detail["title"]["english"] or \
                media_detail["title"]["romaji"] or \
                media_detail["title"]["native"],
            media_detail["season"],
            str(media_detail["seasonYear"]),
            media_detail["type"],
            media_detail["coverImage"]["extraLarge"],
            media_detail["bannerImage"],
            media_detail["averageScore"],
            media_detail["meanScore"],
        )

        save_media_detail_to_db(md)
