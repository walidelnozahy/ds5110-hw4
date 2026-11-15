# HW4 write-up

All numbers come from `python run.py all` and are in `output/`.

## T1. A rating in context

### Prediction

- **`t1a_rating_in_context.sql`**: Bascially for every rating it should return the rating itself (3 columns user_id, movie_id, rating) plus the average rating for that specific user, plus the average rating for that specifci movie for all userss. so 100,000 rows.
- **`t1b_above_both.sql`**: Should return how often does a user give a movie a rating that is higher than both their usual rating and that movie usual ratin.
- **`t1c_window_rewrite.sql`**: Should return movies that are rated at least 0.5 points higher than the average movie rating in their genre, considering only movies with 30+ ratings.

### Result

t1a: 100,000 rows, one per rating.
t1b: 45,232 of 100,000 ratings are above both means. With only movies that have 20+ ratings
t1c: 269 rows

### Explanation
1. Each OVER() is its own window. One groups the rows by user and the other by movie nd both run over the same rows. no row merging
2. If a movie has only one rating, the movie's average is that rating, and a rating can't be higher than itself. but they will still count in tootal
3. It replaced the genre_means step and the join back to it. The old query needed them because GROUP BY genre_id squashes each genre into one row.

## T2. Top three per occupation

### Prediction

- **`t2_top3_row_number.sql`**: This query finds the top 3 movies for each occupation, based on average rating, considering only movies with at least 20 ratings from that occupation.
- **`t2_top3_rank.sql`**: returns more rows than ROW_NUMBER, because RANK() gives tied movies the same rank, so multiple movies can qualify for the top 3.

### Result

- **`t2_top3_row_number.sql`**: 27 rows
- **`t2_top3_rank.sql`**: 28 rows

### Explanation

I see 11 jobs that have no rows at all, because they have too few users for any movie to get 20 ratings. I think I would yse ROW_NUMBER because it always shows at most 3 movies and gives the same result every time.
DENSE_RANK would be right for a rule like "show every movie with one of the 3 best scores". It keeps all ties without skipping numbers. ROW_NUMBER would drop tied movies, and RANK skips a number after a tie, so it can miss the 3rd-best score.

## T3. Sessions and frames

### Prediction

- **`t3_sessions.sql`**: the median session has about 3 ratings, because most people rate a couple of movies, leave, and come back later.

- **`t3b_running_mean.sql`**:  the two columns disagree on no rows, because both are ordered by timestamp, so the running average should come out the same either way.

### Result

- **`t3_sessions.sql`**: 2,793 sessions with a median of 11 ratings each not 3
- **`t3b_running_mean.sql`**: the two columns disagree on 49,787 rows not one

### Explanation

When two ratings have the same timestamp, the second one's gap is 0, so its flag is 0. The default frame adds up all the tied rows at once, but they're zeros, so the sessions come out the same with or without ROWS.  

Someone who takes a break of more than 30 minutes in the middle of rating gets split into two sessions. Two separate visits 20 minutes apart get merged into one. 

Only rows that tie on timestamp with another rating from the same user. The default frame averages in all of the tied ratings at once, while ROWS adds them one by one.

On each user's last rating, both frames include all their ratings, so all 943 users end on the same average. 

## T4. Two indexes for four queries

Indexes: `(movie_id, rating)` and `(timestamp)`.

### Prediction
A_profile: before, it searches with the primary key index but still has to sort. After, the same thingg.

B_movie_page: before, a SCAN of the whole table. After, a SEARCH using the (movie_id, rating) index.
C_recent: before, a SCAN. After, a SEARCH using the (timestamp) index.
D_month: before, a SCAN. After, still a SCAN.
D_rewrite: before, a SCAN. After, a SEARCH using the (timestamp) index.

### Result
A_profile didn't change. It was already finding the user through the primary key index and still sorts their ratings by time. It takes about 0.04 ms either way.
B_movie_page went from reading the whole table to jumping straight to the movie with the new index, from 1.48 ms down to 0.005 ms, about 300 times faster.
C_recent went from reading the whole table to jumping to the time range with the timestamp index, from 1.27 ms to 0.011 ms, about 117 times faster.
D_month still reads every row. Now it reads the smaller index instead of the table, but it's still about 10 ms.
D_rewrite uses the timestamp index to jump to the month, going from 1.94 ms to 0.13 ms, about 15 times faster, and gives the same counts as D_month.
Size: the database grew from 3.63 MB to 6.17 MB, so the two indexes take about 2.5 MB.

### Explanation

These two indexes were picked because B and C were reading the whole table every time, and one index fixes each of them. The (movie_id, rating) index also stores the rating, so B never has to open the table. The (timestamp) index helps C and the D rewrite. A was already fine.

A_profile was already using an index because the primary key (user_id, movie_id) comes with one, and it starts with user_id. But it's sorted by movie, not time, so SQLite still has to sort each user's ratings to get the newest 20. That's the USE TEMP B-TREE line. It's not a big deal, since a user only has about 100 ratings.

D_month stays a SCAN because it turns every timestamp into a month first, so the index is useless there. The rewrite just checks if the timestamp is between two numbers, so it can jump straight to them.

## T5. Recommendation

I'd add two indexes, one on movie and rating and one on the rating time. An index works like the index at the back of a book: the database jumps straight to what it needs instead of reading everything.

They made a big difference. The movie page went from 1.5 ms to 0.005 ms, and "ratings since a date" from 1.3 ms to 0.01 ms. The monthly count got about 15 times faster too, once we asked for a time range instead of a month name.

I'd skip an index for the user profile page. It's already fast at 0.04 ms.

The catch is space. The two indexes added about 2.5 MB, and every new rating has to be saved in three places now, so adding ratings gets a little slower.
