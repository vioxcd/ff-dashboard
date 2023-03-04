from datetime import datetime as dt

import requests
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

	def fetch_favorites(self, users: list[str]):
		pass

	def get_score_format_query(self, id_: int):
		query = '''
		query ($id: Int) {
			User(id: $id) {
				id,
				name,
				mediaListOptions {
					scoreFormat
				}
			}
		}
		'''
		variables = {
			'id': id_,
		}
		return {'query': query, 'variables': variables}

	def get_list_query(self, page, username, per_page=50):
        # this query has anichan specific score format included
		query = '''
		query ($page: Int, $perPage: Int, $username: String) {
			Page (page: $page, perPage: $perPage) {
				pageInfo {
					hasNextPage
				},
				mediaList(userName: $username) {
					score: score,
					anichan_score: score(format: POINT_100),
					status,
					progress,
					completedAt {
						year
						month
						day
					},
					media {
						id,
						type,
						title {
							english,
							romaji,
							native
						}
					}
				}
			}
		}
		'''
		variables = {
			'page': page,
			'perPage': per_page,
			'username': username,
		}
		return {'query': query, 'variables': variables}
