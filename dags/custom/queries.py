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