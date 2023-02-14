import sqlite3
from dataclasses import dataclass

import requests
import streamlit as st
from PIL import Image

# Config Layer
st.set_page_config(page_title="FFD :)", layout="wide")

con = sqlite3.connect('fluff.db')
cur = con.cursor()

# Data Layer
## Objects
@dataclass
class Media:
	media_id: int
	title: str
	media_type: str
	cover_image_url: str
	anichan_score: int
	ff_score: int
	audience_count: int
	section: str
	ranking: int

@dataclass
class AOTY:
	award: int
	award_order: str
	media_id: int
	title: str
	cover_image_url: str

@dataclass
class Favorite:
	name: str
	type: str
	cover_image_url: str
	counts: int
	pct_rank: float

# Logic Layer
## Helper Functions
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_image(url, name):
	img = Image.open(requests.get(url, stream=True).raw)
	print(f"{name} - {img.size}")
	return img

def crop(min_height, img):
	w, h = img.size
	delta_height = h - min_height
	top_h = 0 + round(delta_height / 2)
	bottom_h = h - round(delta_height / 2)
	return img.crop((0, top_h, w, bottom_h))

## Fetching Data
def get_media_section_and_ranking() -> list[Media]:
	return [Media(*m) for m in cur.execute('''SELECT * FROM v_media_section_and_ranking''')]

def get_aoty_list():
	return cur.execute('''
		SELECT
			award,
			award_order,
			media_id,
			title,
			cover_image_url_xl AS cover_image_url
		FROM v_aoty_2022
	''')

def get_favorites() -> list[Favorite]:
	return [Favorite(*f) for f in cur.execute('''SELECT * FROM v_favorites_p90''')]

## Variables
# """
# ⭐ Fluffy Folks Ranking Inclusion Rules ⭐
# (1) Watched by 5 members at minimum (completed or watching by 5th episode)
# (2) Minimum score of 85
# (3) Sorted by: score > votes (number of audience) > alphabet
# (4) Titles are formatted in lowercase English
# """
media_ranked = get_media_section_and_ranking()
anime_ranked = [m for m in media_ranked if m.media_type == "ANIME"]
manga_ranked = [m for m in media_ranked if m.media_type == "MANGA"]

# Presentation Layer
st.title("Fluffy Folks Dashboard")

## Hide expander borders
hide = """
<style>
ul.streamlit-expander {
    border: 0 !important;
</style>
"""
st.markdown(hide, unsafe_allow_html=True)

## Tabs
tab0, tab1, tab2, tab3 = st.tabs(["Favorites", "Awards 2022", "Anime", "Manga"])

with tab0:
	favorites_list = get_favorites()

	# divide favorites by type
	anime_fav: list[Favorite] = []
	manga_fav: list[Favorite]  = []
	characters_fav: list[Favorite]  = []
	staff_fav: list[Favorite]  = []
	studios_fav: list[Favorite]  = []

	for fav in favorites_list:
		match fav.type:
			case "anime":
				anime_fav.append(fav)
			case "manga":
				manga_fav.append(fav)
			case "characters":
				characters_fav.append(fav)
			case "staff":
				staff_fav.append(fav)
			case "studios":
				studios_fav.append(fav)

	with st.expander("💕️ Top Favorited Anime", expanded=True):
		for animes in chunks(anime_fav, 5):
			images = [get_image(a.cover_image_url, a.name) for a in animes]
			min_height = min([img.size[1] for img in images])
			cropped_images = [crop(min_height, img) for img in images]
			for col, anime, img in zip(st.columns(5), animes, cropped_images):
				col.image(img, caption=f"({anime.counts})")
				col.caption(f"<div align='center'>{anime.name}</div>", unsafe_allow_html=True)
				col.write("")

with tab1:
	with tab1.container():
		aoty_list = [AOTY(*awardee) for awardee in get_aoty_list()]
		for awardees in chunks(aoty_list, 3):
			images = [get_image(a.cover_image_url, a.title) for a in awardees]
			min_height = min([img.size[1] for img in images])
			cropped_images = [crop(min_height, img) for img in images]
			for col, awardee, img in zip(st.columns(3), awardees, cropped_images):
				col.image(img)
				col.caption(f"<h3 align='center';>{awardee.award}</h3>", unsafe_allow_html=True)
				col.caption(f"<div align='center'>{awardee.title}</div>", unsafe_allow_html=True)
				col.write("")

with tab2:
	section_gold = (anime for anime in anime_ranked if anime.section == "gold")
	section_silver = (anime for anime in anime_ranked if anime.section == "silver")
	section_bronze = (anime for anime in anime_ranked if anime.section == "bronze")

	with st.expander("🏅 90+", expanded=True):
		_, _, _, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
		col4.write(f"<div align='center'>Anichan Score</div>", unsafe_allow_html=True)
		col5.write(f"<div align='center'>Adjusted Score</div>", unsafe_allow_html=True)
		col6.write(f"<div align='center'>Audience</div>", unsafe_allow_html=True)

		st.write("")

		for media in section_gold:
			col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
			col1.write(f"#{media.ranking}")
			col2.image(media.cover_image_url, use_column_width="always")
			col3.write(media.title)
			col4.write(f"<div align='center'>{media.anichan_score}</div>", unsafe_allow_html=True)
			col5.write(f"<div align='center'>{media.ff_score}</div>", unsafe_allow_html=True)
			col6.write(f"<div align='center'>{media.audience_count}</div>", unsafe_allow_html=True)

	with st.expander("🥈 85+"):
		_, _, _, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
		col4.write(f"<div align='center'>Anichan Score</div>", unsafe_allow_html=True)
		col5.write(f"<div align='center'>Adjusted Score</div>", unsafe_allow_html=True)
		col6.write(f"<div align='center'>Audience</div>", unsafe_allow_html=True)

		st.write("")

		for media in section_silver:
			col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
			col1.write(f"#{media.ranking}")
			col2.write("")
			col3.write(media.title)
			col4.write(f"<div align='center'>{media.anichan_score}</div>", unsafe_allow_html=True)
			col5.write(f"<div align='center'>{media.ff_score}</div>", unsafe_allow_html=True)
			col6.write(f"<div align='center'>{media.audience_count}</div>", unsafe_allow_html=True)

	with st.expander("🥉 85"):
		_, _, _, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
		col4.write(f"<div align='center'>Anichan Score</div>", unsafe_allow_html=True)
		col5.write(f"<div align='center'>Adjusted Score</div>", unsafe_allow_html=True)
		col6.write(f"<div align='center'>Audience</div>", unsafe_allow_html=True)

		st.write("")

		for media in section_bronze:
			col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
			col1.write(f"#{media.ranking}")
			col2.write("")
			col3.write(media.title)
			col4.write(f"<div align='center'>{media.anichan_score}</div>", unsafe_allow_html=True)
			col5.write(f"<div align='center'>{media.ff_score}</div>", unsafe_allow_html=True)
			col6.write(f"<div align='center'>{media.audience_count}</div>", unsafe_allow_html=True)

with tab3:
	_, _, _, col4, col5 = st.columns([1, 1, 14, 1, 1])
	col4.write("score")
	col5.write("votes")

	for media in manga_list[:10]:
		col1, col2, col3, col4, col5 = st.columns([1, 1, 14, 1, 1])
		col1.write(f"#{media.ranking}")
		col2.image(media.cover_image_url, use_column_width="always")
		col3.write(media.title)
		col4.write(media.score)
		col5.write(media.audience_count)
