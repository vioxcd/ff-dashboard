# TODO

## Niceties

- Docker

## Statistics

- Studios
- Tags
- Genres

## Hard

- modeling: create time dimension table for dynamic up-down indicator (see [utils](./sqls/utils.sql#L284))
- modeling: dynamic `as_rules` (if members are 30, then take 20% of it)
- modeling: `planning` & `current` should have a time-based indicator, e.g. per this retrieve date, this anime is trending etc.
  (caught "trending" phase in data)
- modeling: add scd to favourites table

## Uhhh, no?

- ml: user similarity profile by top 5 and favorites (?)
- ml: recommendation from association rules from socials