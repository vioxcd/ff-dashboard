import sqlite3

from data_objects import Favourite, Media

con = sqlite3.connect('fluff.db')  # TODO: make proper db connection (.env)
cur = con.cursor()

def get_anime_ranked() -> list[Media]:
	query = '''
		SELECT
			ranking,
			section,
			media_id,
			title,
			media_type,
			anichan_score,
			ff_score,
			audience_count,
			cover_image_url
		FROM final_ranked_anime
		WHERE section != '-'
	'''
	# TODO: create Anime and Manga dataclass
	# season,
	# season_year,
	# format,
	return [Media(*m) for m in cur.execute(query)]

def get_manga_ranked() -> list[Media]:
	query = '''
		SELECT
			ranking,
			section,
			media_id,
			title,
			media_type,
			anichan_score,
			ff_score,
			audience_count,
			cover_image_url
		FROM final_ranked_manga
		WHERE section != '-'
	'''
	# source,
	return [Media(*m) for m in cur.execute(query)]

def get_aoty_list():
	return cur.execute('''
		SELECT
			award,
			award_order,
			media_id,
			title,
			cover_image_url_xl AS cover_image_url
		FROM final_aoty_2022
	''')

def get_favourites() -> list[Favourite]:
	return [Favourite(*f) for f in cur.execute('''SELECT * FROM final_favourites_p90''')]
