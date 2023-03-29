QUERY_SCORE_FORMAT = '''
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

# this query has anichan specific score format included
QUERY_USERS_MEDIALIST = '''
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

QUERY_USERS_FAVOURITES_TEMPLATE = '''
query ($page: Int, $perPage: Int, $id: Int) {
	User(id: $id) {
		favourites {
			%s
		}
	}
}
'''

QUERY_USERS_FAVOURITES_OPTS = {
	"anime": '''
		anime(page: $page, perPage: $perPage) {
			nodes {
				id,
				title {
					romaji,
					english
				},
				coverImage {
					large
				}
			},
			pageInfo {
				hasNextPage
			}
		}
	''',
	"manga": '''
		manga(page: $page, perPage: $perPage) {
			nodes {
				id,
				title {
					romaji,
					english
				},
				coverImage {
					large
				}
			},
			pageInfo {
				hasNextPage
			}
		}
	''',
	"characters": '''
		characters(page: $page, perPage: $perPage) {
			nodes {
				id,
				name {
					full
				},
				image {
					large
					medium
				}
			},
			pageInfo {
				hasNextPage
			}
		}
	''',
	"staff": '''
		staff(page: $page, perPage: $perPage) {
			nodes {
				id,
				name {
					full
				},
				image {
					large
				}
			},
			pageInfo {
				hasNextPage
			}
		}
	''',
	"studios": '''
		studios(page: $page, perPage: $perPage) {
			nodes {
				id,
				name
			},
			pageInfo {
				hasNextPage
			}
		}
	'''
}


QUERY_MEDIA_DETAILS = '''
query ($media_id: Int) {
	Media(id: $media_id) {
		id,
		title {
			english,
			native,
			romaji
		},
		season,
		seasonYear,
		episodes,
		type,
		format,
		genres,
		coverImage {
			extraLarge,
			large,
			medium
		},
		bannerImage,
		averageScore,
		meanScore,
		source,
		studios {
			edges {
				isMain
				node {
					id,
					name,
					isAnimationStudio
				}
			}
		},
		tags {
			id,
			name,
			category,
			rank
		},
		relations {
			edges {
				node {
					id,
					title {
					romaji
					english
					native
					userPreferred
					}
				},
				relationType
			}
		}
	}
}
'''