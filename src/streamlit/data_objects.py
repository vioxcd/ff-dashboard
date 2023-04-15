from dataclasses import dataclass


@dataclass
class Media:
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
	counts: int
	pct_rank: float
