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

app:
	@echo "Starting streamlit app..."
	python3 src/app.py

sql:
	@echo "Setting up views"
	@echo "Dropping..."
	sqlite3 $(DB) < sqls/view_setup_drop.sql

	@echo "Creating appropriate score view..."
	sqlite3 $(DB) < sqls/view_appropriate_score.sql

	@echo "Creating scores defined as rules view..."
	sqlite3 $(DB) < sqls/view_as_rules.sql

	@echo "Creating AOTY 2022 view..."
	sqlite3 $(DB) < sqls/view_aoty_2022.sql

	@echo "Creating favourites on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_favourites_p90.sql

	@echo "Creating favourites on .9 percentile view..."
	sqlite3 $(DB) < sqls/view_mapping_anichan_to_p3p5_scores.sql

	@echo "Done!"
