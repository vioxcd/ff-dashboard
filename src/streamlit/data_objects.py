from dataclasses import dataclass
from enum import Enum


@dataclass
class Ranked:
	ranking: int
	section: str
	media_id: int
	title: str
	media_type: str
	anichan_score: int
	ff_score: int
	audience_count: int
	cover_image_url: str

@dataclass
class AOTY:
	award: int
	award_order: str
	media_id: int
	title: str
	cover_image_url: str

@dataclass
class Favourite:
	item_id: int
	name: str
	type: str
	cover_image_url: str
	audience_count: int
	pct_rank: float

@dataclass
class Media:
	media_id: int
	title: str
	media_type: str
	anichan_score: int
	ff_score: int
	audience_count: int
	cover_image_url: str

class Season(Enum):
	WINTER = 0
	SPRING = 1
	SUMMER = 2
	FALL = 3

@dataclass
class Seasonal:
	season_year: int
	season: Season
	season_code: int
	in_season_rank: int
	media_id: int
	title: str
	media_type: str
	anichan_score: int
	ff_score: int
	audience_count: int
	cover_image_url: str
