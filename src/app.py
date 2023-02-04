import sqlite3
from dataclasses import dataclass

import requests
import streamlit as st
from PIL import Image

# Config Layer
st.set_page_config(page_title=":))", layout="wide")

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
	score: int
	audience_count: int
	ranking: int

# Logic Layer
## Helper Functions
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_image(url, title):
	img = Image.open(requests.get(url, stream=True).raw)
	print(f"{title} - {img.size}")
	return img

def crop(min_height, img):
	w, h = img.size
	delta_height = h - min_height
	top_h = 0 + round(delta_height / 2)
	bottom_h = h - round(delta_height / 2)
	return img.crop((0, top_h, w, bottom_h))

def get_media_list(score_type):
	assert score_type in ('Anichan Score', 'Adjusted FF Score'), 'wrong score format'
	query_param = {
		'Anichan Score': 'anichan_score',
		'Adjusted FF Score': 'ff_score'
	}[score_type]

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
			ar.{query_param} AS score,
			ar.audience_count,
			RANK() OVER (PARTITION BY md.type
						ORDER BY ar.{query_param} DESC,
								ar.audience_count DESC,
								md.title DESC
						) AS ranking
		FROM v_as_rules ar
		JOIN media_details md
			USING (media_id)
		ORDER BY
			ar.{query_param} DESC,
			ar.audience_count DESC,
			md.title DESC
		'''
	)


## Fetching Data
con = sqlite3.connect('fluff.db')
cur = con.cursor()

option = st.selectbox(
    'Preferred Score',
    ('Anichan Score', 'Adjusted FF Score'))

st.write('You selected:', option)

## Variables
# """
# ⭐ Fluffy Folks Ranking Inclusion Rules ⭐
# (1) Watched by 5 members at minimum (completed or watching by 5th episode)
# (2) Minimum score of 85
# (3) Sorted by: score > votes (number of audience) > alphabet
# (4) Titles are formatted in lowercase English
# """
media_list: list[Media] = []
for media in get_media_list(option):
	media_list.append(Media(*media))

anime_list: list[Media] = [media for media in media_list \
							if media.media_type == "ANIME" and media.score >= 85.0]
manga_list: list[Media] = [media for media in media_list \
							if media.media_type == "MANGA" and media.score >= 85.0]

# Presentation Layer
st.title("Fluffy Folks Ranking Dashboard")

tab1, tab2 = st.tabs(["Anime", "Manga"])

with tab1:
	with tab1.container():
		for medias in chunks(anime_list[:10], 5):
			images = [get_image(m.cover_image_url, m.title) for m in medias]
			min_height = min([img.size[1] for img in images])
			cropped_images = [crop(min_height, img) for img in images]
			for col, media, img in zip(st.columns(5), medias, cropped_images):
				caption = f"({media.score} | {media.audience_count})"
				col.image(img, caption=caption)
				col.caption(f"<div align='center'>{media.title}</div>", unsafe_allow_html=True)
				col.write("")

with tab2:
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
