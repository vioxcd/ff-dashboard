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

It's mostly the average ratings of the members (e.g. if you have 3 people, you add them all up and divide by 3) and counting the number of audiences

Other than that, there's the use of 90th percentiles to get the top value

Along with calculation, the data are grouped by certain criteria or filters (this makes it interesting). For example, grouping by seasons would give us `seasonals` and filtering the highest-rated anime that have a 3-4 audiences give us `potentials`

---

##### How is the score calculated? Does it follow Ani-chan or not?

The score is calculated in two ways:  

1. As Ani-chan did, where 5 and 3-stars rating doesn't translate nicely to 100 points (e.g. 5-stars equal 90 points). This is called `anichan_score`  
2. The *correct* score translation where 5-stars *is equal* to 100 points, etc., called `ff_score` (some ratings that uses 100 points before changing to 5-stars are preserved in their points form, e.g. winuyi's Sangatsu II rating is 100, not 90)

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
