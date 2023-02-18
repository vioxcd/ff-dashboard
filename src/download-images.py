import logging
import math
import os
import shutil
import sqlite3
import sys
import time
from dataclasses import dataclass

import requests
from pyrate_limiter import BucketFullException, Duration, Limiter, RequestRate

# / CONFIGS
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format("logs", os.path.basename(__file__))),
        logging.StreamHandler(sys.stdout)
    ]
)

DATABASE_NAME = "fluff.db"
IMAGES_FOLDER = os.path.join(os.getcwd(), "images")

minutely_rate = RequestRate(80, Duration.MINUTE)
limiter = Limiter(minutely_rate)

RETRY_ATTEMPTS = 3  # control variable if BucketFullException is encountered

# / Data Objects
@dataclass
class Media:
    title: str
    media_type: str
    cover_image_url: str

# / Functions
def get_media_lists() -> list[Media]:
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    return [Media(*m) for m in cur.execute('''
        SELECT DISTINCT(title), media_type, cover_image_url_xl FROM media_details
    ''')]


@limiter.ratelimit('identity')
def download_image(media: Media) -> None:
    res = requests.get(media.cover_image_url, stream=True)
    media_ident = f"{media.title}_{media.media_type}"
    file_name = media.cover_image_url.split("/")[-1]
    file_path = os.path.join(IMAGES_FOLDER, file_name)
    if res.status_code == 200:
        with open(file_path,'wb') as f:
            shutil.copyfileobj(res.raw, f)
        logging.info(f'{media_ident} sucessfully downloaded: {file_name}')
    else:
        logging.info(f"{file_name} couldn't be retrieved")


if __name__ == "__main__":
    logging.info(f"Downloading images to {IMAGES_FOLDER}")

    media = get_media_lists()
    for m in media:
        for retries in range(RETRY_ATTEMPTS):
            if retries != 0:
                logging.warning(f"Retrying for {m.title} - {m.media_type}")

            try:
                data = download_image(m)
            except BucketFullException as err:
                logging.error(err)
                logging.error(err.meta_info)
                sleep_for = math.ceil(float(err.meta_info['remaining_time']))
                time.sleep(sleep_for)
            else:
                break

    logging.info("Done!")