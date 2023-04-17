from data_objects import (AOTY, ByStatus, Divisive, Favourite, Media,
                          QuestionableByTitle, QuestionableByUser, Seasonal)
from db import (get_anime_ranked, get_aoty_list, get_current, get_divisive,
                get_dropped, get_favourites, get_manga_ranked, get_planning,
                get_potentials, get_questionable_per_title,
                get_questionable_per_user, get_seasonals)
from helpers import (chunks, crop, get_expanded_sections, get_local_image,
                     get_redirectable_url, make_appropriate_images)

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
tabs = ["Favourites", "Awards 2022", "Anime", "Manga", "Seasonals",
		"Potentials", "Divisive",  "By Status", "Questionable", "Help & FAQs"]
favourites_tab, aoty_2022_tab, anime_tab, manga_tab, seasonals_tab, \
	potentials_tab, divisive_tab, by_status_tab, questionable_tab, help_tab = st.tabs(tabs)

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
	fav_sections: list[tuple[str, list[Favourite]]] = [
		('Anime', anime_fav),
		('Manga', manga_fav),
		('Characters', characters_fav),
		('Staff', staff_fav),
		# ' excluding studios
	]
	for fav_type, fav_list in fav_sections:
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
				cropped_images = make_appropriate_images(images)
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
				cropped_images = make_appropriate_images(images)
				for col, manga, img in zip(st.columns(item_per_column), mangas, cropped_images):
					anchor = get_redirectable_url(manga.title, manga.media_id, manga.media_type)
					col.image(img, caption=f"({manga.anichan_score} / {manga.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

with seasonals_tab:
	seasonals = get_seasonals()

	seasons_part: dict[str, list[Seasonal]] = {}
	sub_section = []
	season = seasonals[0].season
	season_year = seasonals[0].season_year
	for media in seasonals:
		if season != media.season or season_year != media.season_year:
			seasons_part[f"{season} {season_year}"] = sub_section
			season = media.season
			season_year = media.season_year
			sub_section = []
		sub_section.append(media)

	ITEM_PER_COLUMN = 5
	for season_year_string, media_in_season in seasons_part.items():
		with st.expander(season_year_string, expanded=True):
			for items in chunks(media_in_season , ITEM_PER_COLUMN):
				images = [get_local_image(a.cover_image_url, a.title) for a in items]
				cropped_images = make_appropriate_images(images)
				for col, media, img in zip(st.columns(ITEM_PER_COLUMN), items, cropped_images):
					anchor = get_redirectable_url(media.title, media.media_id, media.media_type)
					col.image(img, caption=f"({media.ff_score} / {media.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

with potentials_tab:
	potentials = get_potentials()

	anime_pot: list[Media] = [p for p in potentials if p.media_type == "ANIME"]
	manga_pot: list[Media] = [p for p in potentials if p.media_type == "MANGA"]

	ITEM_PER_COLUMN = 5
	msg = "⭐️ Top Potential %s"
	sections: list[tuple[str, list[Media]]] = [
		('Anime', anime_pot),
		('Manga', manga_pot),
	]

	for pot_type, pot_list in sections:
		with st.expander(msg % pot_type, expanded=True):
			for items in chunks(pot_list , ITEM_PER_COLUMN):
				images = [get_local_image(a.cover_image_url, a.title) for a in items]
				cropped_images = make_appropriate_images(images)
				for col, media, img in zip(st.columns(ITEM_PER_COLUMN), items, cropped_images):
					anchor = get_redirectable_url(media.title, media.media_id, media.media_type)
					col.image(img, caption=f"({media.ff_score} / {media.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

with divisive_tab:
	divisives = get_divisive()

	anime_div: list[Divisive] = [x for x in divisives if x.media_type == "ANIME"]
	manga_div: list[Divisive] = [x for x in divisives if x.media_type == "MANGA"]

	ITEM_PER_COLUMN = 5
	msg = "💥️ Top Divisive %s"
	div_sections: list[tuple[str, list[Divisive]]] = [
		('Anime', anime_div),
		('Manga', manga_div),
	]
	for div_type, div_list in div_sections:
		with st.expander(msg % div_type, expanded=True):
			for items in chunks(div_list , ITEM_PER_COLUMN):
				images = [get_local_image(a.cover_image_url, a.title) for a in items]
				cropped_images = make_appropriate_images(images)
				for col, media, img in zip(st.columns(ITEM_PER_COLUMN), items, cropped_images):
					anchor = get_redirectable_url(media.title, media.media_id, media.media_type)
					col.image(img, caption=f"({media.stdev} / {media.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

with by_status_tab:
	followed = get_current()
	anticipated = get_planning()
	dropped = get_dropped()

	anime_fol: list[ByStatus] = [x for x in followed if x.media_type == "ANIME"]
	manga_fol: list[ByStatus] = [x for x in followed if x.media_type == "MANGA"]

	anime_ant: list[ByStatus] = [x for x in anticipated if x.media_type == "ANIME"]
	manga_ant: list[ByStatus] = [x for x in anticipated if x.media_type == "MANGA"]

	anime_drp: list[ByStatus] = [x for x in dropped if x.media_type == "ANIME"]
	manga_drp: list[ByStatus] = [x for x in dropped if x.media_type == "MANGA"]

	ITEM_PER_COLUMN = 5
	msg = "Top %s"
	by_status_sections: list[tuple[str, list[ByStatus]]] = [
		('Followed Anime', anime_fol),
		('Followed Manga', manga_fol),
		('Anticipated Anime', anime_ant),
		('Anticipated Manga', manga_ant),
		('Dropped Anime', anime_drp),
		('Dropped Manga', manga_drp),
	]

	for by_status_type, by_status_list in by_status_sections:
		with st.expander(msg % by_status_type, expanded=True):
			for items in chunks(by_status_list, ITEM_PER_COLUMN):
				images = [get_local_image(a.cover_image_url, a.title) for a in items]
				cropped_images = make_appropriate_images(images)
				for col, media, img in zip(st.columns(ITEM_PER_COLUMN), items, cropped_images):
					anchor = get_redirectable_url(media.title, media.media_id, media.media_type)
					col.image(img, caption=f"({media.audience_count})")
					col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
					col.write("")

with questionable_tab:
	questionable_per_user = get_questionable_per_user()
	questionable_per_title = get_questionable_per_title()

	ITEM_PER_COLUMN = 5

	with st.expander('Questionable per User', expanded=True):
		for items in chunks(questionable_per_user, ITEM_PER_COLUMN):
			images = [get_local_image(a.cover_image_url, a.title) for a in items]
			cropped_images = make_appropriate_images(images)
			for col, media, img in zip(st.columns(ITEM_PER_COLUMN), items, cropped_images):
				anchor = get_redirectable_url(media.title, media.media_id, media.media_type)
				col.image(img, caption=f"{media.username} ({media.user_score} / {media.score_diff})")
				col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
				col.write("")

	with st.expander('Questionable per Title', expanded=True):
		for items in chunks(questionable_per_title, ITEM_PER_COLUMN):
			images = [get_local_image(a.cover_image_url, a.title) for a in items]
			cropped_images = make_appropriate_images(images)
			for col, media, img in zip(st.columns(ITEM_PER_COLUMN), items, cropped_images):
				anchor = get_redirectable_url(media.title, media.media_id, media.media_type)
				col.image(img, caption=f"({media.should_be_score} / {media.audience_count}) - ({media.actual_score} / {media.actual_audience_count})")
				col.caption(f"<div align='center'>{anchor}</div>", unsafe_allow_html=True)
				col.write("")

with help_tab:
	help_md_path = "src/streamlit/HELP.md"
	with open(help_md_path, 'r') as f:
		markdown = f.read()
	help_tab.markdown(markdown)
