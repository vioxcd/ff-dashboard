import os
import sqlite3
from datetime import datetime
from pathlib import Path

import gspread
from dotenv import load_dotenv
from queries import *


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


def execute_query(db_name, query):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
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

    # `NAME OF SHEETS`: `QUERY`
    queries = {
        "AOTY 2022": AOTY_2022_QUERY,
        "Favourites p90": FAVOURITES_P90_QUERY,
        "Ranked Anime": RANKED_ANIME_QUERY,
        "Ranked Manga": RANKED_MANGA_QUERY,
        "Seasonals": SEASONALS_QUERY,
        "Potentials": POTENTIALS_QUERY,
    }

    for sheet_name, query in queries.items():
        print(f"Inserting {sheet_name}")
        data = execute_query(DATABASE_NAME, query)
        worksheet = sheet.worksheet(sheet_name)
        worksheet.clear()
        worksheet.update(data)

    # last, update info sheet
    sheet_name = "Info"
    worksheet = sheet.worksheet(sheet_name)
    worksheet.clear()
    retrieved_on_message = f'Retrieved on: {get_data_last_retrieved_on(DATABASE_NAME)}'
    exported_on_message = f'Exported on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    worksheet.update(f"A1", retrieved_on_message)
    worksheet.update(f"A2", exported_on_message)

    print("Done!")