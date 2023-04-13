# Fluffy Folks Dashboard

An end-to-end pipeline and dashboard of Fluffy Folks' statistics!

This pipeline:

1. Fetches and stores the historical FF's data from Anilist

2. Calculates [many interesting statistics](#statistics) that can be viewed from a dashboard

3. Periodically exports a version of `#rankings` channel content (from Fluffy Folks' discord) to accessible sheets

4. Created using `Airflow`, `dbt`, and `streamlit`

## Why?

1. The statistics seems super interesting!

2. Manual data aggregation in `#rankings` channel seems painful and not as complete

3. I'm learning about pipelines, SQLs, and dashboarding stuffs

See `FEATURES.md` for details of features, unworked TODOs, and bugs

## Installation & Usage

Moved to its own [file](./INSTALLATION.md)

## Some Notes

- Most of the commands I use are recorded in the [Makefile](./Makefile).

- Some custom terminal stuff that is quite useful

  ```bash
  # Use below command to setup Airflow's command-line autocompletion
  eval "$(register-python-argcomplete airflow)"

  # Silence SQLAlchemy deprecation warning
  # https://stackoverflow.com/a/75109965
  export SQLALCHEMY_SILENCE_UBER_WARNING=1
  ```

- I encountered some pip's dependency error when trying to install `jsonschema` which are used by `dbt-core` and `airflow`. Try to install `airflow` first before `dbt-core` (as the former uses `jsonschema` v3, and the latter default to v4.17 but could be made to work with v3)

## Statistics

| Aspects                | Description |
| -----------            | ----------- |
| AOTY 2022              | Anime of the year; best of several pre-defined categories   |
| Favourites             | Top favourited anime, manga, characters, staff, and studio   |
| Ranked Anime           | Ranked anime based on aggregated ratings    |
| Ranked Manga           | Ranked manga based on aggregated ratings    |
| Potentials             | Titles that have potentials to be included in ranked    |
| Seasonals              | Ranked anime but it's viewed from within season perspective   |
| Planning (anticipated) | Most planned series   |
| Dropped                | Most dropped series   |
| Current (followed)     | Most followed series (currently watched)   |
| Divisive               | Most divisive series (high [stdev](https://en.wikipedia.org/wiki/Standard_deviation))   |
| Questionable           | Most questionable ratings and titles (e.g. high score given for low rated title)   |

## Caveats

A note for my future-self as well!

- Be careful when testing stuff! make sure the `ENVIRONMENT_TYPE` are according to what you're going to be doing, e.g. when you trying to test and there's error when running the command, the env-vars might not be *unset*, and from that point on, it might cause bugs in your dag runs when you're actually don't want to test
