DB = fluff.db

all:
	@echo "Fetching fluff's scores..."
	python3 src/fetch-users-details.py

	@echo "Fetching media details..."
	python3 src/fetch-media-details.py

	@echo "Fetching fluff's favorites..."
	python3 src/fetch-favorites.py

clean:
	rm ff.log fluff.db

redo-db:
	rm fluff.db
	cp fluff.db.bak fluff.db

download-images:
	mkdir -p images
	python3 src/download-images.py

app:
	@echo "Starting streamlit app..."
	streamlit run src/app.py

sql:
	@echo "Setting up views"
	@echo "Dropping..."
	sqlite3 $(DB) < sqls/view_setup_drop.sql

	@echo "Creating appropriate score view..."
	sqlite3 $(DB) < sqls/view_appropriate_score.sql

	@echo "Creating anichan to 3 and 5 score format mapping view..."
	sqlite3 $(DB) < sqls/view_mapping_anichan_to_3_and_5_scores_format.sql

	@echo "Creating buggy users view..."
	sqlite3 $(DB) < sqls/view_buggy_users.sql

	@echo "Adding is_buggy column to users table..."
	sqlite3 $(DB) < sqls/mod_users_is_buggy.sql

	@echo "Update scores to its correct value..."
	sqlite3 $(DB) < sqls/update_score.sql

	@echo "Creating scores defined as rules view..."
	sqlite3 $(DB) < sqls/view_as_rules.sql

	@echo "Creating media lists section and ranking view..."
	sqlite3 $(DB) < sqls/view_media_section_and_ranking.sql

	@echo "Creating AOTY 2022 view..."
	sqlite3 $(DB) < sqls/view_aoty_2022.sql

	@echo "Creating favourites on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_favourites_p90.sql

	@echo "Creating media standard dev. view..."
	sqlite3 $(DB) < sqls/view_media_stddev.sql

	@echo "Creating most divisive media on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_divisive_media_p90.sql

	@echo "Creating most dropped media on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_dropped_media_p90.sql

	@echo "Creating wide media-tags view..."
	sqlite3 $(DB) < sqls/view_wide_tags.sql

	@echo "Creating underrated view..."
	sqlite3 $(DB) < sqls/view_underrated.sql

	@echo "Creating studios statistics view..."
	sqlite3 $(DB) < sqls/view_studios_stats.sql

	@echo "Creating tags 90th percentile statistics view..."
	sqlite3 $(DB) < sqls/view_tags_counts_p90.sql

	@echo "Creating tags per-media 90th percentile statistics view..."
	sqlite3 $(DB) < sqls/view_tags_counts_by_media_p90.sql

	@echo "Creating tags subcategory's ranks view..."
	sqlite3 $(DB) < sqls/view_tags_subcategory_ranked.sql

	@echo "Creating tags subcategory's favourites stats view..."
	sqlite3 $(DB) < sqls/view_tags_subcategory_favorited.sql

	@echo "Done!"
