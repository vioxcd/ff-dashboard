import os
import sqlite3
from pathlib import Path

import gspread
from dotenv import load_dotenv


def get_aoty_2022(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = """
            SELECT
                award_order, award, media_id, title, anichan_score,
                ff_score, audience_count, season, season_year, media_type,
                format, source, studios, is_sequel
            FROM aoty_2022
            """
    res = cur.execute(query)
    columns = [description[0] for description in cur.description]
    rows = [list(row) for row in res.fetchall()]
    return [columns] + rows


def get_top_anime(db_name):
    pass

def get_top_manga(db_name):
    pass


def get_top_seasonals(db_name):
    pass


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
    }

    for sheet_name, query in queries.items():
        print(f"Inserting {sheet_name}")
        data = query(DATABASE_NAME)
        worksheet = sheet.worksheet(sheet_name)
        worksheet.update(data)

    print("Done!")