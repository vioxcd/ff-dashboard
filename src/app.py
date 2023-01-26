import sqlite3
from collections import namedtuple

import streamlit as st

# Config Layer
st.set_page_config(page_title=":))", layout="wide")

# Data Layer
## Objects
Media = namedtuple("Media", "title type score votes")

## Fetching Data
con = sqlite3.connect('fluff.db')
cur = con.cursor()
media_list_query = cur.execute(
	'''
	SELECT
		title,
		media_type,
		ROUND(AVG(appropriate_score), 2) AS avg_score,
		COUNT(1) AS audience_count
	FROM v_appropriate_score
	WHERE status IN ('COMPLETED', 'CURRENT')
	GROUP BY title, media_type
	HAVING COUNT(1) >= 5
	ORDER BY 3 DESC, 1 DESC
	'''
)

# Logic Layer
## Helper Functions
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

## Variables
media_list: list[Media] = []
for media in media_list_query:
	media_list.append(Media(*media))

anime_list = [media for media in media_list if media.type == "ANIME"]

# Presentation Layer
st.title("Fluffy Folks Ranking Dashboard")

col1, col2, col3 = st.columns([5, 5, 5])

for (media1, media2, media3) in chunks(anime_list[:9], 3):
	with col1:
		col1.write(media1.title)
		col1.write(media1.score)
	with col2:
		col2.write(media2.title)
		col2.write(media1.score)
	with col3:
		col3.write(media3.title)
		col3.write(media1.score)
