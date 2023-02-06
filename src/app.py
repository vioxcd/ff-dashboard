import sqlite3
from dataclasses import dataclass

import requests
import streamlit as st
from PIL import Image

# Config Layer
st.set_page_config(page_title=":))", layout="wide")

con = sqlite3.connect('fluff.db')
cur = con.cursor()

# Data Layer
## Objects
@dataclass
class Media:
	media_id: int
	title: str
	season: str
	season_year: int
	media_type: str
	cover_image_url: str
	banner_image_url: str
	average_score: int
	mean_score: int
	anichan_score: int
	ff_score: int
	audience_count: int
	ranking: int

@dataclass
class AOTY:
	award: int
	award_order: str
	media_id: int
	title: str
	cover_image_url: str

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
def get_media_list():
	return cur.execute(
		f'''
		SELECT
			md.media_id,
			md.title,
			md.season,
			md.season_year,
			md.type AS media_type,
			md.cover_image_url_xl AS cover_image_url,
			md.banner_image_url,
			md.average_score,
			md.mean_score,
			ar.anichan_score,
			ar.ff_score,
			ar.audience_count,
			RANK() OVER (PARTITION BY md.type
						ORDER BY ar.anichan_score DESC,
								ar.ff_score DESC,
								ar.audience_count DESC,
								md.title DESC
						) AS ranking
		FROM v_as_rules ar
		JOIN media_details md
			USING (media_id)
		ORDER BY
			ar.anichan_score DESC,
			ar.ff_score DESC,
			ar.audience_count DESC,
			md.title DESC
		'''
	)

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

## Variables
# """
# ⭐ Fluffy Folks Ranking Inclusion Rules ⭐
# (1) Watched by 5 members at minimum (completed or watching by 5th episode)
# (2) Minimum score of 85
# (3) Sorted by: score > votes (number of audience) > alphabet
# (4) Titles are formatted in lowercase English
# """
media_list: list[Media] = []
for media in get_media_list():
	media_list.append(Media(*media))

anime_list: list[Media] = [media for media in media_list \
							if media.media_type == "ANIME" \
								and (media.anichan_score >= 85.0 or media.ff_score >= 85.0)]
manga_list: list[Media] = [media for media in media_list \
							if media.media_type == "MANGA"
								and (media.anichan_score >= 85.0 or media.ff_score >= 85.0)]

# Presentation Layer
st.title("Fluffy Folks Ranking Dashboard")

## Hide expander borders
hide = """
<style>
ul.streamlit-expander {
    border: 0 !important;
</style>
"""
st.markdown(hide, unsafe_allow_html=True)

## Tabs
tab1, tab2, tab3 = st.tabs([ "Awards 2022", "Anime", "Manga"])

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
	section_gold = []
	section_silver = []
	section_bronze = []

	for anime in anime_list:
		if anime.anichan_score >= 90 or anime.ff_score >= 90:
			section_gold.append(anime)
		elif 90 > anime.anichan_score > 85 or 90 > anime.ff_score > 85:
			section_silver.append(anime)
		elif anime.anichan_score == 85 or anime.ff_score == 85:
			section_bronze.append(anime)

	start_rank_gold = 1
	start_rank_silver = 1 + len(section_gold)
	start_rank_bronze = 1 + len(section_silver)

	with st.expander("🏅 90+", expanded=True):
		_, _, _, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
		col4.write(f"<div align='center'>Anichan Score</div>", unsafe_allow_html=True)
		col5.write(f"<div align='center'>Adjusted Score</div>", unsafe_allow_html=True)
		col6.write(f"<div align='center'>Audience</div>", unsafe_allow_html=True)

		st.write("")

		for rank, media in enumerate(section_gold, start=start_rank_gold):
			col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
			col1.write(f"#{rank}")
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

		for rank, media in enumerate(section_silver, start=start_rank_silver):
			col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
			col1.write(f"#{rank}")
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

		for rank, media in enumerate(section_bronze, start=start_rank_bronze):
			col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 9, 2, 2, 2])
			col1.write(f"#{rank}")
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
