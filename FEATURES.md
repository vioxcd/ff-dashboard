# Features

## Done

|    Part   | Feature                                         | Status | Description                                                                                                                 |
|:---------:|-------------------------------------------------|:------:|-----------------------------------------------------------------------------------------------------------------------------|
|    API    | Fetch `progress`                                |    ✅️   | Needed for rules                                                                                                            |
|    API    | Fetch media `scores`                            |    ✅   |                                                                                                                             |
|    API    | Fetch `rewatch` count                           |    ❌️   | Not many people track their rewatches                                                                                       |
|    Data   | Implement fluff's rules                         |    ✅   | Rules' detail in README                                                                                                     |
| Dashboard | Implement layout as in design                   |    ✅   |                                                                                                                             |
| Dashboard | Anime and Manga tab                             |    ✅   |                                                                                                                             |
| Dashboard | Include animanga with rating below 85           |    ❌️   | As there's no conditional rendering in tabs, all data/images included will result in slower page load. Stick to 85+ for now |
|    Bug    | Username can change; Track user via IDs instead |    ✅   |                                                                                                                             |

## TODOs

- [Refactor] Create object models (class and abstract class?) for every `table create` and `save` method
- [Bug] AOTY should take into account when the series is completed (should be within the same year, or something like that)
- [Bug] AOTY should take `ONA` format into account when deciding best movie. Fetch `episodes` count as some `ONA` has more than 1 episodes
- Add `anichan_score` in the dashboard (as this is what's used in the `#ranking` channel)
- Fetch all image types for various layout uses
- Download all used images in local
- Fetch relationType (non sequel), source, and format for FF's AOTY
- ✨  Fluffy Folks's anime of the year 2022 ✨ tab
- Fetch tags / genre / studio data (there should be a bridge table)
- Tags / genre / studio analysis tab
- Most divisive (highest standard dev) & most differed from AL tab (biggest rating difference between fluff and AL)
- 🏅 90+, 🥈 85+, 🥉 80+ sections (use `expander`)
- Favorites tab (analysis!)
- Redirect to page on link click
- Various way to sort and filter (sort by: most watched, most favorited, most rewatched count. fetch accordingly)
- Track score changes overtime and display who contributed to the change
