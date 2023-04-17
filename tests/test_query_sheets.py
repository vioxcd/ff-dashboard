from src.streamlit.sheets import *


def test_all_query_sheet_run_without_errors():
	funcs = [
		get_anime_ranked,
		get_manga_ranked,
		get_aoty_2022,
		get_favourites,
		get_potentials,
		get_seasonals,
		get_divisive,
		get_current,
		get_planning,
		get_dropped,
		get_questionable_per_title,
		get_questionable_per_user
	]

	for f in funcs:
		ret = f()
		assert len(ret) > 0
