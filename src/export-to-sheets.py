import os
import sqlite3
from datetime import datetime
from pathlib import Path

import gspread
from dotenv import load_dotenv


def get_data_last_retrieved_on(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT DISTINCT retrieved_date
            FROM stg_lists
            ORDER BY 1 DESC
            LIMIT 1
            """
    res = cur.execute(query)
    last_retrieved_date = res.fetchone()[0]
    return last_retrieved_date


def get_aoty_2022(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT
                award_order, award, media_id, title, anichan_score,
                ff_score, audience_count, season, season_year, media_type,
                format, source, studios, is_sequel
            FROM final_aoty_2022
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


def get_favourites_p90(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT
                name, type, counts, pct_rank
            FROM final_favourites_p90
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


def get_ranked_anime(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT *
            FROM final_ranked_anime
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


def get_ranked_manga(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT *
            FROM final_ranked_manga
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


def get_seasonals(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT *
            FROM final_seasonals
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


def get_potentials(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT *
            FROM final_potential
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


if __name__ == "__main__":
    # load env's variables
    load_dotenv()
    SERVICE_ACCOUNT_CREDENTIALS = Path(os.environ["SERVICE_ACCOUNT_CREDENTIALS"])
    SH_KEY = os.environ["SH_KEY"]
    DATABASE_NAME = os.environ["DATABASE_NAME"]

    # get worksheet
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_CREDENTIALS)
    sheet = gc.open_by_key(SH_KEY)

    # `NAME OF SHEETS`: `METADATA`
    queries = {
        "AOTY 2022": get_aoty_2022,
        "Favourites p90": get_favourites_p90,
        "Ranked Anime": get_ranked_anime,
        "Ranked Manga": get_ranked_manga,
        "Seasonals": get_seasonals,
        "Potentials": get_potentials,
        "Info": get_data_last_retrieved_on,
    }

    for sheet_name, query in queries.items():
        print(f"Inserting {sheet_name}")
        data = query(DATABASE_NAME)
        worksheet = sheet.worksheet(sheet_name)
        worksheet.clear()

        if sheet_name == "Info":
            retrieved_on_message = f'Retrieved on: {data}'
            exported_on_message = f'Exported on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            worksheet.update(f"A1", retrieved_on_message)
            worksheet.update(f"A2", exported_on_message)
        else:
            worksheet.update(data)

    print("Done!")