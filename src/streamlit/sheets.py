import pandas as pd

from src.streamlit.data_objects import (AOTY, ByStatus, Divisive, Favourite,
                                        Potential, QuestionableByTitle,
                                        QuestionableByUser, Ranked, Seasonal)

SHEETS_URL = "https://docs.google.com/spreadsheets/d/1CUSfaHK2nlhUibzl5yADVuSef7hYPdTqOz4yGJSIE54/edit#gid=GID"
SHEETS_GID_KEYS = {
	"AOTY 2022": 0,
	"Favourites p90": 239842297,
	"Ranked Anime": 724123150,
	"Ranked Manga": 1574717606,
	"Seasonals": 739750827,
	"Potentials": 1535595812,
	"Current": 191240988,
	"Planning": 2046264278,
	"Dropped": 26682321,
	"Divisive p90": 313277426,
	"Questionable (titles)": 1613017570,
	"Questionable (users)": 91910980,
}

def get_csv_url(sheets_url: str, gid: int):
	return sheets_url.replace("/edit#gid=", "/export?format=csv&gid=").replace("GID", str(gid))

def load_data(key: str):
	GID = SHEETS_GID_KEYS[key]
	csv_url = get_csv_url(SHEETS_URL, GID)
	return pd.read_csv(csv_url)

def get_anime_ranked() -> list[Ranked]:
	KEY = "Ranked Anime"
	df = load_data(KEY)
	df = df.loc[df.section != '-'].copy()
	cols = [
		"ranking",
		"section",
		"media_id",
		"title",
		"media_type",
		"anichan_score",
		"ff_score",
		"audience_count",
		"cover_image_url"
	]
	return [Ranked(*m) for m in df[cols].values]

def get_manga_ranked() -> list[Ranked]:
	KEY = "Ranked Manga"
	df = load_data(KEY)
	df = df.loc[df.section != '-'].copy()
	cols = [
		"ranking",
		"section",
		"media_id",
		"title",
		"media_type",
		"anichan_score",
		"ff_score",
		"audience_count",
		"cover_image_url"
	]
	return [Ranked(*m) for m in df[cols].values]

def get_aoty_2022() -> list[AOTY]:
	KEY = "AOTY 2022"
	df = load_data(KEY)
	cols = [
		"award",
		"award_order",
		"media_id",
		"title",
		"cover_image_url"
	]
	return [AOTY(*m) for m in df[cols].values]

def get_favourites() -> list[Favourite]:
	KEY = "Favourites p90"
	df = load_data(KEY)
	return [Favourite(*m) for m in df.values]

def get_potentials() -> list[Potential]:
	KEY = "Potentials"
	df = load_data(KEY)
	return [Potential(*m) for m in df.values]

def get_seasonals() -> list[Seasonal]:
	KEY = "Seasonals"
	df = load_data(KEY)
	return [Seasonal(*m) for m in df.values]

def get_divisive() -> list[Divisive]:
	KEY = "Divisive p90"
	df = load_data(KEY)
	cols = [
		"media_id",
		"title",
		"media_type",
		"ff_stddev",
		"audience_count",
		"cover_image_url"
	]
	return [Divisive(*m) for m in df[cols].values]

def get_current() -> list[ByStatus]:
	KEY = "Current"
	df = load_data(KEY)
	cols = [
		"media_id",
		"title",
		"media_type",
		"audience_count",
		"cover_image_url"
	]
	return [ByStatus(*m) for m in df[cols].values]

def get_planning() -> list[ByStatus]:
	KEY = "Planning"
	df = load_data(KEY)
	cols = [
		"media_id",
		"title",
		"media_type",
		"audience_count",
		"cover_image_url"
	]
	return [ByStatus(*m) for m in df[cols].values]

def get_dropped() -> list[ByStatus]:
	KEY = "Dropped"
	df = load_data(KEY)
	cols = [
		"media_id",
		"title",
		"media_type",
		"audience_count",
		"cover_image_url"
	]
	return [ByStatus(*m) for m in df[cols].values]

def get_questionable_per_title() -> list[QuestionableByTitle]:
	KEY = "Questionable (titles)"
	df = load_data(KEY)
	cols = [
		"media_id",
		"title",
		"media_type",
		"should_be_score",
		"audience_count",
		"actual_score",
		"actual_audience_count",
		"cover_image_url"
	]
	return [QuestionableByTitle(*m) for m in df[cols].values]

def get_questionable_per_user() -> list[QuestionableByUser]:
	KEY = "Questionable (users)"
	df = load_data(KEY)
	cols = [
		"username",
		"media_id",
		"title",
		"media_type",
		"appropriate_score",
		"score_diff",
		"cover_image_url"
	]
	return [QuestionableByUser(*m) for m in df[cols].values]
