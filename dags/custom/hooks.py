from datetime import datetime as dt

import requests
from custom.queries import *
from pyrate_limiter import Duration, Limiter, RequestRate

from airflow.hooks.base import BaseHook


class AnilistApiHook(BaseHook):
	"""
	Hook for the Anilist API.

	Abstracts details of the Anilist (GraphQL) API & provides several convenience
	methods for fetching data (e.g. users, media, favorites) from the API. 
	Provides support for adjusting rate limit and handling of pagination
	"""

	URL = 'https://graphql.anilist.co'

	# rate limiter
	minutely_rate = RequestRate(80, Duration.MINUTE)
	limiter = Limiter(minutely_rate)

	def __init__(self):
		super().__init__()

	@limiter.ratelimit('identity', delay=True)
	def fetch(self, query_params):
		self.log.info(f"Requesting {query_params['variables']}")

		response = requests.post(self.URL, json=query_params)
		results = response.json()

		# handle rate limit error
		if "errors" in results:
			self.log.error(results['errors'][0]['message'])
			return None

		return results['data']
	
	def fetch_user_score_format(self, id_: int):
		query_params = self.get_score_format_query(id_)
		return self.fetch(query_params)

	def fetch_user_lists(self, username: str):
		page = 1
		has_next_page = True
		data = []
		while has_next_page:
			self.log.info(f'Processing {username} page {page}')

			# one fetch-save cycle
			query_params = self.get_list_query(page, username)
			results = self.fetch(query_params)
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

	def fetch_media_details(self, users: list[str]):
		pass

	@limiter.ratelimit('identity', delay=True)
	def fetch_favorites(self, users: list[tuple[str, int]]):
		data = []

		for username, user_id in users:
			for query_type in ['anime', 'manga', 'characters', 'staff', 'studios']:
				page = 1  # starts from 1
				has_next_page = True
				while has_next_page:
					self.log.info(f'Processing {query_type} favourites for {username} on page {page}')

					# one fetch-save cycle
					query_params = self.get_favorites_query(query_type, page, user_id)
					results = self.fetch(query_params)

					if not results:
						self.log.error(f"Error when fetching favorites {query_type} for {username} on page {page}")
						break

					fav_items = [self.extract_favourites(node, query_type, user_id)
								 for node in results['User']['favourites'][query_type]['nodes']]
					data.extend(fav_items)

					has_next_page = results['User']['favourites'][query_type]['pageInfo']['hasNextPage']
					page += 1

				self.log.info(f'Saving {query_type} favourites for user {username}')

		self.log.info('Done!')
		return data


	def get_score_format_query(self, id_: int):
		variables = {'id': id_}
		return {'query': QUERY_SCORE_FORMAT, 'variables': variables}

	def get_list_query(self, page: int, username: str, per_page: int = 50):
		variables = {
			'page': page,
			'perPage': per_page,
			'username': username,
		}
		return {'query': QUERY_USERS_MEDIALIST, 'variables': variables}

	def get_favorites_query(self, query_type: str, page: int, user_id: int, per_page: int = 50):
		query = QUERY_USERS_FAVORITES_OPTS[query_type]
		variables = {
			'page': page,
			'perPage': per_page,
			'id': user_id,
		}
		return {'query': QUERY_USERS_FAVORITES_TEMPLATE % query, 'variables': variables}

	def extract_favourites(self, node, query_type, user_id):
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
