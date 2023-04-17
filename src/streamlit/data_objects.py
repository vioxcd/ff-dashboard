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
class Potential:
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

@dataclass
class Divisive:
	media_id: int
	title: str
	media_type: str
	stdev: int
	audience_count: int
	cover_image_url: str

@dataclass
class ByStatus:
	media_id: int
	title: str
	media_type: str
	audience_count: int
	cover_image_url: str

@dataclass
class QuestionableByUser:
	username: str
	media_id: int
	title: str
	media_type: str
	user_score: int
	score_diff: int
	cover_image_url: str

@dataclass
class QuestionableByTitle:
	media_id: int
	title: str
	media_type: str
	should_be_score: int
	audience_count: int
	actual_score: int
	actual_audience_count: int
	cover_image_url: str
