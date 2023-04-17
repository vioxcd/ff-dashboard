import sqlite3

from src.streamlit.data_objects import (ByStatus, Divisive, Favourite, Media,
                                        QuestionableByTitle,
                                        QuestionableByUser, Ranked, Seasonal)


def get_anime_ranked() -> list[Ranked]:
	con = sqlite3.connect('fluff.db')  # TODO: make proper db connection (.env)
	cur = con.cursor()
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
	return [Ranked(*m) for m in cur.execute(query)]

def get_manga_ranked() -> list[Ranked]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
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
	return [Ranked(*m) for m in cur.execute(query)]

def get_aoty_list():
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
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
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	return [Favourite(*f) for f in cur.execute('''SELECT * FROM final_favourites_p90''')]

def get_potentials() -> list[Media]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	return [Media(*f) for f in cur.execute('''SELECT * FROM final_potential''')]

def get_seasonals() -> list[Seasonal]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	return [Seasonal(*f) for f in cur.execute('''SELECT * FROM final_seasonals''')]

def get_divisive() -> list[Divisive]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	query = '''
		SELECT
			media_id,
			title,
			media_type,
			ff_stddev AS stdev,
			audience_count,
			cover_image_url
		FROM final_divisive_p90
	'''
	return [Divisive(*f) for f in cur.execute(query)]

def get_current() -> list[ByStatus]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	query = '''
		SELECT
			media_id,
			title,
			media_type,
			audience_count,
			cover_image_url
		FROM final_current
	'''
	return [ByStatus(*f) for f in cur.execute(query)]

def get_planning() -> list[ByStatus]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	query = '''
		SELECT
			media_id,
			title,
			media_type,
			audience_count,
			cover_image_url
		FROM final_planning
	'''
	return [ByStatus(*f) for f in cur.execute(query)]

def get_dropped() -> list[ByStatus]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	query = '''
		SELECT
			media_id,
			title,
			media_type,
			audience_count,
			cover_image_url
		FROM final_dropped
	'''
	return [ByStatus(*f) for f in cur.execute(query)]

def get_questionable_per_user() -> list[QuestionableByUser]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	query = '''
		SELECT
			username,
			media_id,
			title,
			media_type,
			appropriate_score AS user_score,
			score_diff,
			cover_image_url
		FROM final_questionable_per_user
	'''
	return [QuestionableByUser(*f) for f in cur.execute(query)]

def get_questionable_per_title() -> list[QuestionableByTitle]:
	con = sqlite3.connect('fluff.db')
	cur = con.cursor()
	query = '''
		SELECT
			media_id,
			title,
			media_type,
			should_be_score,
			audience_count,
			actual_score,
			actual_audience_count,
			cover_image_url
		FROM final_questionable_per_title
	'''
	return [QuestionableByTitle(*f) for f in cur.execute(query)]
