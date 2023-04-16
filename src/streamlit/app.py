from data_objects import AOTY, Favourite, Media
from db import (get_anime_ranked, get_aoty_list, get_favourites,
                get_manga_ranked)
from helpers import (chunks, crop, fix_image, get_expanded_sections,
                     get_local_image, get_redirectable_url,
                     make_appropriate_images)

import streamlit as st

# Config Layer
st.set_page_config(page_title="Fluff ~", layout="wide")

## Variables
# """
# ⭐ Fluffy Folks Ranking Inclusion Rules ⭐
# (1) Watched by 5 members at minimum (completed or watching by 5th episode)
# (2) Minimum score of 85
# (3) Sorted by: score > votes (number of audience) > alphabet
# (4) Titles are formatted in lowercase English
# """
anime_ranked = get_anime_ranked()
manga_ranked = get_manga_ranked()

# Presentation Layer
st.title("Fluffy Folks Dashboard 📊")

## Hide expander borders
hide = """
<style>
ul.streamlit-expander {
    border: 0 !important;
</style>
"""
st.markdown(hide, unsafe_allow_html=True)

## Tabs
tabs = ["Favourites", "Awards 2022", "Anime", "Manga", "Help & FAQs"]
favourites_tab, aoty_2022_tab, anime_tab, manga_tab, help_tab = st.tabs(tabs)

with favourites_tab:
	favourites_list = get_favourites()

	# divide favourites by type
	anime_fav: list[Favourite] = []
	manga_fav: list[Favourite]  = []
	characters_fav: list[Favourite]  = []
	staff_fav: list[Favourite]  = []
	studio_fav: list[Favourite]  = []

	for fav in favourites_list:
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
				studio_fav.append(fav)

	ITEM_PER_COLUMN = 5
	msg = "💕️ Top Favourited %s"
	sections = [
		('Anime', anime_fav),
		('Manga', manga_fav),
		('Characters', characters_fav),
		('Staff', staff_fav),
		# ' excluding studios
	]
	for fav_type, fav_list in sections:
		with st.expander(msg % fav_type, expanded=True):
			for favs in chunks(fav_list , ITEM_PER_COLUMN):
				images = [get_local_image(a.cover_image_url, a.name) for a in favs]
				cropped_images = make_appropriate_images(images, _type=fav_type.lower())
				for col, media, img in zip(st.columns(ITEM_PER_COLUMN), favs, cropped_images):
					anchor = get_redirectable_url(media.name, media.item_id, media.type)
					col.image(img, caption=f"({media.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

	with st.expander(msg % 'Studio', expanded=True):
		for favs in chunks(studio_fav , ITEM_PER_COLUMN):
			for col, media in zip(st.columns(ITEM_PER_COLUMN), favs):
				col.caption(f"<div align='center'>{media.name}</div>", unsafe_allow_html=True)
				col.caption(f"<div align='center'>{media.audience_count}</div>", unsafe_allow_html=True)
				col.write("")

with aoty_2022_tab:
	with aoty_2022_tab.container():
		aoty_list = [AOTY(*awardee) for awardee in get_aoty_list()]
		for awardees in chunks(aoty_list, 3):
			images = [get_local_image(a.cover_image_url, a.title) for a in awardees]
			min_height = min([img.size[1] for img in images])
			cropped_images = [crop(min_height, img) for img in images]
			columns = st.columns(5)  # made 5 column, only allocate the middle 3
			for col, awardee, img in zip(columns[1:4], awardees, cropped_images):
				col.image(img)
				col.caption(f"<h3 align='center';>{awardee.award}</h3>", unsafe_allow_html=True)
				col.caption(f"<div align='center'>{awardee.title}</div>", unsafe_allow_html=True)
				col.write("")

with anime_tab:
	for index, (title, is_expanded, media_in_section) in enumerate(get_expanded_sections(anime_ranked)):
		item_per_column = 5 if index == 0 else 8
		with st.expander(title, expanded=is_expanded):
			for animes in chunks(media_in_section, item_per_column):
				images = [get_local_image(a.cover_image_url, a.title) for a in animes]
				cropped_images = make_appropriate_images(images, _type='anime')
				for col, anime, img in zip(st.columns(item_per_column), animes, cropped_images):
					anchor = get_redirectable_url(anime.title, anime.media_id, anime.media_type)
					col.image(img, caption=f"({anime.anichan_score} / {anime.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

# similar to the code above, but this one is for manga
with manga_tab:
	for index, (title, is_expanded, media_in_section) in enumerate(get_expanded_sections(manga_ranked)):
		item_per_column = 5 if index == 0 else 8
		with st.expander(title, expanded=is_expanded):
			for mangas in chunks(media_in_section, item_per_column):
				images = [get_local_image(a.cover_image_url, a.title) for a in mangas]
				cropped_images = make_appropriate_images(images, _type='manga')
				for col, manga, img in zip(st.columns(item_per_column), mangas, cropped_images):
					anchor = get_redirectable_url(manga.title, manga.media_id, manga.media_type)
					col.image(img, caption=f"({manga.anichan_score} / {manga.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

with help_tab:
	help_md_path = "src/streamlit/HELP.md"
	with open(help_md_path, 'r') as f:
		markdown = f.read()
	help_tab.markdown(markdown)
