import os
import shutil
from datetime import datetime as dt

import requests
from pyrate_limiter import Duration, Limiter, RequestRate

from airflow.hooks.base import BaseHook
from dags.custom.queries import *


class AnilistApiHook(BaseHook):
	"""
	Hook for the Anilist API.

	Abstracts details of the Anilist (GraphQL) API & provides several convenience
	methods for fetching data (e.g. users, media, favourites) from the API. 
	Provides support for adjusting rate limit and handling of pagination
	"""

	URL = 'https://graphql.anilist.co'

	# rate limiter
	_minutely_rate = RequestRate(80, Duration.MINUTE)
	_limiter = Limiter(_minutely_rate)

	def __init__(self):
		super().__init__()
		self._records_counts = {"processed": 0, "failed": 0}

	@_limiter.ratelimit('identity', delay=True)
	def _fetch(self, query_params):
		self.log.info(f"Requesting {query_params['variables']}")

		response = requests.post(self.URL, json=query_params)
		results = response.json()

		# handle rate limit error
		if "errors" in results:
			self.log.error(results['errors'][0]['message'])
			self.log.error(f"Failed: fetch failed with {query_params['variables']}")
			self._records_counts['failed'] += 1
			return None
		self._records_counts['processed'] += 1

		return results['data']

	def log_processed_results(self) -> None:
		self.log.info(f"Processed: {self._records_counts['processed']}")
		self.log.info(f"Failed: {self._records_counts['failed']}")
	
	def get_user_score_format(self, id_: int):
		query_params = self._get_score_format_query(id_)
		return self._fetch(query_params)

	def get_user_lists(self, username: str):
		page = 1
		has_next_page = True
		data = []
		while has_next_page:
			self.log.info(f'Processing {username} page {page}')

			# one fetch-save cycle
			query_params = self._get_list_query(page, username)
			results = self._fetch(query_params)
			if not results:
				self.log.error(f"Error when fetching lists for {username} on page {page}")
				break  # abort fetch for user in case of errors.

			has_next_page = results['Page']['pageInfo']['hasNextPage']
			page += 1

			for media in results['Page']['mediaList']:
				day = media['completedAt']['day']
				month = media['completedAt']['month']
				year = media['completedAt']['year']
				completed_at = f"{day}-{month}-{year}" if day and month and year else "-"

				data.append((
					username,
					media['score'],
					media['anichan_score'],
					media['status'],
					media['media']['id'],
					media['media']['type'],
					media['media']['title']['english'] or \
					media['media']['title']['romaji'] or \
					media['media']['title']['native'],
					media['progress'],
					completed_at,
					dt.now().strftime("%Y-%m-%d")  # retrieved_date
				))
		return data

	def get_media_details(self, media_ids: list[int]):
		tags = set()
		for media_id in media_ids:
			query_params = self._get_media_details_query(media_id)
			data = self._fetch(query_params)

			if not data:
				self.log.error(f"Data not found on {media_id}")
				continue

			# 'media_id', 'title', 'season', 'season_year', 'type',
			# 'format', 'genres', 'cover_image_url_md', 'cover_image_url_lg', 'cover_image_url_xl'
			# 'banner_image_url', 'average_score', 'mean_score' 'source', 'studios', 'is_non_sequel'
			"""Save media details"""
			media_details = self._process_media(data)

			"""Filter unseen tags"""
			new_tags = [tag for tag in data["Media"]["tags"]
						if tag['id'] not in tags]

			"""Save unseen tags"""
			tags_ = [(tag['id'], tag['name'], tag['category']) for tag in new_tags]

			"""Update tags list"""
			new_tag_ids = [tag['id'] for tag in new_tags]
			tags.update(new_tag_ids)

			"""Save media-tag relationship"""
			media_tag_bridges = [(media_id, tag['id'], tag['rank'])
								 for tag in data["Media"]["tags"]]

			yield (media_details, tags_, media_tag_bridges)


	@_limiter.ratelimit('identity', delay=True)
	def get_favourites(self, users: list[tuple[str, int]]):
		data = []

		for username, user_id in users:
			for query_type in ['anime', 'manga', 'characters', 'staff', 'studios']:
				page = 1  # starts from 1
				has_next_page = True
				while has_next_page:
					self.log.info(f'Processing {query_type} favourites for {username} on page {page}')

					# one fetch-save cycle
					query_params = self._get_favourites_query(query_type, page, user_id)
					results = self._fetch(query_params)

					if not results:
						self.log.error(f"Error when fetching favourites {query_type} for {username} on page {page}")
						break

					fav_items = [self._extract_favourites(node, query_type, user_id)
								 for node in results['User']['favourites'][query_type]['nodes']]
					data.extend(fav_items)

					has_next_page = results['User']['favourites'][query_type]['pageInfo']['hasNextPage']
					page += 1

				self.log.info(f'Saving {query_type} favourites for user {username}')

		self.log.info('Done!')
		return data

	@_limiter.ratelimit('identity', delay=True)
	def download_image(self, media, image_folder) -> None:
		(title, media_type, cover_image_url) = media
		media_ident = f"{title}_{media_type}"
		file_name = cover_image_url.split("/")[-1]
		file_path = os.path.join(image_folder, file_name)

		res = requests.get(cover_image_url, stream=True)
		if res.status_code == 200:
			with open(file_path,'wb') as f:
				shutil.copyfileobj(res.raw, f)
			self.log.info(f'{media_ident} sucessfully downloaded: {file_name}')
			self._records_counts["processed"] += 1
		else:
			self.log.error(f"Failed: {media_ident} couldn't be retrieved. url: {cover_image_url}")
			self._records_counts["failed"] += 1

	def _get_score_format_query(self, id_: int):
		variables = {'id': id_}
		return {'query': QUERY_SCORE_FORMAT, 'variables': variables}

	def _get_list_query(self, page: int, username: str, per_page: int = 50):
		variables = {
			'page': page,
			'perPage': per_page,
			'username': username,
		}
		return {'query': QUERY_USERS_MEDIALIST, 'variables': variables}

	def _get_favourites_query(self, query_type: str, page: int, user_id: int, per_page: int = 50):
		query = QUERY_USERS_FAVOURITES_OPTS[query_type]
		variables = {
			'page': page,
			'perPage': per_page,
			'id': user_id,
		}
		return {'query': QUERY_USERS_FAVOURITES_TEMPLATE % query, 'variables': variables}

	def _get_media_details_query(self, media_id: int):
		variables = {'media_id': media_id}
		return {'query': QUERY_MEDIA_DETAILS, 'variables': variables}

	def _extract_favourites(self, node, query_type, user_id):
		match query_type:
			case "anime" | "manga":
				return (
					user_id,
					node['id'],
					node['title']['english'] or node['title']['romaji'],
					query_type,
					node['coverImage']['large'],
				)
			case "characters" | "staff":
				return (
					user_id,
					node['id'],
					node['name']['full'],
					query_type,
					node['image']['large'],
				)
			case "studios":
				return (
					user_id,
					node['id'],
					node['name'],
					query_type,
					None,  # studio don't have cover image
				)

	def _process_media(self, data):
		media_detail = data['Media']

		"""Processing several things"""
		genres = ", ".join(media_detail["genres"])
		studios_list = [studio_info["node"]["name"]
						for studio_info in media_detail["studios"]["edges"]
						if studio_info["isMain"]]
		studios = ", ".join(studios_list)
		is_sequel = any([True
						for relation in media_detail["relations"]["edges"]
						if relation["relationType"] == "PREQUEL"])

		"""Creating object before saving"""
		return (
			media_detail['id'],
			media_detail["title"]["english"] or \
				media_detail["title"]["romaji"] or \
				media_detail["title"]["native"],
			media_detail["season"],
			media_detail["seasonYear"],
			media_detail["episodes"],
			media_detail["type"],
			media_detail["format"],
			genres,
			media_detail["coverImage"]["extraLarge"],
			media_detail["coverImage"]["large"],
			media_detail["coverImage"]["medium"],
			media_detail["bannerImage"],
			media_detail["averageScore"],
			media_detail["meanScore"],
			media_detail["source"],
			studios,
			is_sequel,
		)
