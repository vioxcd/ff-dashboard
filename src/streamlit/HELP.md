# Answering some Qs

Addressing the next [two question](https://twitter.com/gyrowayne/status/1650007524924604417)

---

##### How does the whole thing work?

The whole thing is something technically called a *data pipeline*. How does it work? It works in several simple steps:

1. Getting the data from the source (Anilist provides this source)
2. Storing the data in my computer (locally)
3. Cleaning the data (for example, transforming Ani-chan rating values as explained below)
4. Doing calculations with the cleaned data (like ranking things)
5. Saving the calculation and exporting the calculation to sheets

Cooking food might be a good analogy: you get the raw ingredients, store it at home, clean the ingredients before you start cooking, make them to an appropriate shape (like, peeling the potato/onion skin), doing stuff with them according to a recipe (it's similar how calculation has its own recipe), and saving the dish to be eaten later.

---

##### How does the ranking got calculated?

It's a two-step process: filter for inclusion and then do a (simple) calculation

The inclusion criteria for ranked series follow the rules in the `#rankings` channel. That is *"count the number of audiences and only include series with an audience count that is at least 20% of fluffs member count"*

Other than the rule used in `#ranking`, several sheets use the 90th or 95th percentile for inclusion criteria, `seasonals` include currently popular ongoing series even if it's unrated, and potentials specifically search for low audience count with high-rating (20% - 1 to 3)

The calculations that are done are simple: either averaging the ratings or counting the audience (the most esoteric one is the `stdev` used in `divisive`)

---

##### How is the score calculated? Does it follow Ani-chan or not?

The score is calculated in two ways:  

1. As Ani-chan did, where 5 and 3-stars rating doesn't translate nicely to 100 points (e.g. 5-stars equal 90 points). This is called `anichan_score`  
2. The *correct* score translation where 5-stars *is equal* to 100 points, etc., called `ff_score`*

*Some ratings that uses 100 points format before changing to 5-stars format are mapped to their currently used points format, e.g. hammz uses 5-stars format and his Chihayafuru rating is 99 previously. His rating is mapped back to 5-stars (99 is 5-stars), and then translated back to 100 points to become 100)

---

##### So, which score format is used where?

As `anichan_score` seems a bit *off*, it's not used except in place where it's obviously displayed, e.g. in the `Anime` and `Manga` tab.  
For ranking others, `ff_score` is used

---

##### What's the mapping for Ani-chan's score?

- 3*    = 100, 60, 35
- 5*    = 90, 70, 50, 40, 10
- 10.0* = x10
- 10*   = x10
- 100   = ...

---

##### What's the rules for picking what's included in these lists?

The rules follows the rules in `#ranking` channel. they are:  

1. Watched by 20% members at minimum (completed or watching by 5th episode)
2. Minimum score of 85 (doesn't apply for some though)
3. Sorted by: score > votes (number of audience) > alphabet
4. ~~Titles are formatted in lowercase English~~ — this doesn't apply!

---

##### Why's there so few entries in the favourites?

It's picked based on **90th percentile!**  
(if it's not there, then probably it's lower than 90th and is not included)

---

##### Any other tab starts from 90th percentile?

The `by_status` (current, planning, dropped) and `divisive` use 90th percentile too!

---

##### How is `divisive` calculated?

It's calculated based on standard deviation of `ff_score` between users

format: `stdev` / `audience_score`

---

##### How is `questionable` calculated?

It's calculated based on the difference of score the user gave vs. `ff_score` (the group average)

format for media: `minority_rating` / `minority_audience_count`

format for users: `user's score` / `score diff against average`

trivia: some people don't have `questionable` ratings (this actually had happened, I only know after someone asked me about it)

---

##### How can I request some additional things or submit a bug if I found some?

DM to me [Twitter](https://twitter.com/vioxcd) 😉️
