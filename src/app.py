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
	WHERE status = 'COMPLETED' OR (status = 'CURRENT' AND progress >= 5)
	GROUP BY title, media_type
	HAVING COUNT(1) >= 5
	ORDER BY 3 DESC, 4 DESC, 1 DESC
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
