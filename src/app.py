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
		md.*,
		ar.avg_score,
		ar.audience_count,
		RANK() OVER (ORDER BY ar.avg_score DESC, ar.audience_count DESC, md.title DESC) AS ranking
	FROM v_as_rules ar
	JOIN media_details md
		USING (media_id)
	WHERE ar.media_type = 'ANIME'
	ORDER BY
		ar.avg_score DESC,
		ar.audience_count DESC,
		md.title DESC
	LIMIT 10
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

anime_list: list[Media] = [media for media in media_list if media.ff_score >= 85.0]

# Presentation Layer
st.title("Fluffy Folks Ranking Dashboard")

_, _, _, col4, col5 = st.columns([1, 1, 14, 1, 1])
col4.write("score")
col5.write("votes")

for media in anime_list:
	col1, col2, col3, col4, col5 = st.columns([1, 1, 14, 1, 1])
	col1.write(f"#{media.ranking}")
	col2.image(media.cover_image_url, use_column_width="always")
	col3.write(media.title)
	col4.write(media.ff_score)
	col5.write(media.votes)
