import os

import requests
from data_objects import Media
from PIL import Image, ImageOps


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_image_from_url(url, name):
	img = Image.open(requests.get(url, stream=True).raw)
	print(f"{name} - {img.size}")
	return img

def get_local_image(url, name):
	IMAGES_FOLDER = os.path.join(os.getcwd(), "images")
	file_name = url.split("/")[-1]
	file_path = os.path.join(IMAGES_FOLDER, file_name)
	img = Image.open(file_path)
	print(f"{name} - {img.size}")
	return img

def resize_with_padding(img, expected_size):
	STREAMLIT_DARK_BACKGROUND_RGB = (14, 17, 23)
	return ImageOps.pad(img, expected_size, color=STREAMLIT_DARK_BACKGROUND_RGB)

def fix_image(img, _type=None):
	w, h = img.size
	NORMAL_ANIME_WIDTH = 460
	STAFF_SIZE_WIDTH = 230
	STAFF_SIZE_HEIGHT = 345
	if _type == "anime" and w < NORMAL_ANIME_WIDTH:
		anime_width_factor = round(NORMAL_ANIME_WIDTH / w, 2)
		factored_h = round(h * anime_width_factor)
		img = resize_with_padding(img, (NORMAL_ANIME_WIDTH, factored_h))
	elif _type == "staff" and w < STAFF_SIZE_WIDTH:
		img = resize_with_padding(img, (STAFF_SIZE_WIDTH, STAFF_SIZE_HEIGHT))
	return img

def crop(min_height, img):
	w, h = img.size
	delta_height = h - min_height
	top_h = 0 + round(delta_height / 2)
	bottom_h = h - round(delta_height / 2)
	return img.crop((0, top_h, w, bottom_h))

# Presentation Functions
def get_expanded_sections(media_ranked: list[Media]) -> list[tuple[str, bool, list[Media]]]:
	section_gold = [media for media in media_ranked if media.section == "gold"]
	section_silver = [media for media in media_ranked if media.section == "silver"]
	section_bronze = [media for media in media_ranked if media.section == "bronze"]
	return [
		("🏅 90+", True, section_gold),
		("🥈 85+", False, section_silver),
		("🥉 85", False, section_bronze),
	]

def get_redirectable_url(content: str, media_id: int, media_type: str) -> str:
	assert media_type.lower() in ('anime', 'manga', 'characters', 'staff'), "incorrect media_type passed"
	url = "https://anilist.co/%s/%s" % (media_type.lower(), media_id)
	return f"""
		<a
			style="color: inherit; text-decoration: none;"
			href="{url}">
			{content}
		</a>
	"""