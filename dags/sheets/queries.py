AOTY_2022_QUERY = """
                SELECT
                    award_order, award, media_id, title, anichan_score,
                    ff_score, audience_count, season, season_year, media_type,
                    format, source, studios, is_sequel
                FROM final_aoty_2022
                """

FAVOURITES_P90_QUERY = """
                SELECT
                    name, type, audience_count, pct_rank
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

CURRENT_QUERY = """
                SELECT *
                FROM final_current
                """

PLANNING_QUERY = """
                SELECT *
                FROM final_planning
                """

DROPPED_QUERY = """
                SELECT *
                FROM final_dropped
                """


DIVISIVE_QUERY = """
                SELECT *
                FROM final_divisive_p90
                """

QUESTIONABLE_PER_USER_QUERY = """
                SELECT
                    username,
                    media_id,
                    title,
                    media_type,
                    mean_score,
                    audience_count,
                    appropriate_score,
                    score_diff,
                    cover_image_url
                FROM final_questionable_per_user
                """

QUESTIONABLE_PER_TITLE_QUERY = """
                SELECT *
                FROM final_questionable_per_title
                """
