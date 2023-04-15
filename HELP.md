# Answering some Qs

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

##### What's the rules for picking what's included in these lists?

The rules follows the rules in `#ranking` channel. they are:  

1. Watched by 5 members at minimum (completed or watching by 5th episode)
2. Minimum score of 85 (doesn't apply for some though)
3. Sorted by: score > votes (number of audience) > alphabet
4. ~~Titles are formatted in lowercase English~~ — this doesn't apply!

---

##### Why's there so few entries in the favourites?

It's picked based on **90th percentile!**  
(if it's not there, then probably it's lower than 90th and is not included)

---

##### Any other tab starts from 90th percentile?

The `tags` ones and `studios` use 90th percentile too!

---

##### How is `divisive` calculated?

It's calculated based on standard deviation of `ff_score` between users

---

##### How is `underrated` calculated?

It's calculated based on the difference of score the user gave vs. `ff_score` (the group average)

---

##### How can I request some additional things or submit a bug if I found some?

DM to me [Twitter](https://twitter.com/vioxcd) 😉️
