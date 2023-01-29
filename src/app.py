import sqlite3
from dataclasses import dataclass

import streamlit as st

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
	avg_score: int
	mean_score: int
	ff_score: float
	votes: int
	ranking: int

## Fetching Data
con = sqlite3.connect('fluff.db')
cur = con.cursor()
media_list_query = cur.execute(
	'''
	SELECT
		title,
		media_type,
		avg_score,
		audience_count
	FROM
		v_as_rules
	ORDER BY 3 DESC, 4 DESC, 1 DESC -- rules
	'''
)

# Logic Layer
## Helper Functions
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

## Variables
# """
# ⭐ Fluffy Folks Ranking Inclusion Rules ⭐
# (1) Watched by 5 members at minimum (completed or watching by 5th episode)
# (2) Minimum score of 85
# (3) Sorted by: score > votes (number of audience) > alphabet
# (4) Titles are formatted in lowercase English
# """
media_list: list[Media] = []
for media in media_list_query:
	media_list.append(Media(*media))

anime_list = [media for media in media_list if media.type == "ANIME" and media.score >= 85.0]

# Presentation Layer
st.title("Fluffy Folks Ranking Dashboard")

c = st.container()
_, _, _, col4 = c.columns([1, 1, 15, 1])
col4.write("score")

for index, media in enumerate(anime_list[:10], start=1):
	sample_image = "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21366-qp94AxKx6ZaM.jpg"
	col1, col2, col3, col4 = st.columns([1, 1, 15, 1])
	col1.write(f"#{index}")
	col2.image(sample_image, use_column_width="always")
	col3.write(media.title)
	col4.write(media.score)
