AOTY_2022_QUERY = """
                SELECT
                    award_order, award, media_id, title, anichan_score,
                    ff_score, audience_count, season, season_year, media_type,
                    format, source, studios, is_sequel
                FROM final_aoty_2022
                """

FAVOURITES_P90_QUERY = """
                SELECT
                    name, type, counts, pct_rank
                FROM final_favourites_p90
                """

RANKED_ANIME_QUERY = """
                SELECT *
                FROM final_ranked_anime
                """

RANKED_MANGA_QUERY = """
                SELECT *
                FROM final_ranked_manga
                """

SEASONALS_QUERY = """
                SELECT *
                FROM final_seasonals
                """

POTENTIALS_QUERY = """
                SELECT *
                FROM final_potential
                """