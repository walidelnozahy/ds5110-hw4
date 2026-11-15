# HW4 write-up

All numbers come from `python run.py all` and are in `output/`.

## T1. A rating in context

### Prediction

- **`t1a_rating_in_context.sql`**: one row per rating, so about 100,000 rows (MovieLens 100k). A window adds the two means as columns but does not merge rows like `GROUP BY` would.
- **`t1b_above_both.sql`**: about 35%. Beating both your own usual rating and the movie's usual rating is harder than beating one. The 20+ share should be a bit higher, because movies with very few ratings make it hard to be above the movie's mean.
- **`t1c_window_rewrite.sql`**: the `genre_means` step and the final join back to it disappear. The window puts the genre mean on each row directly.

### Result

- T1a returned 100,000 rows, one per rating, as predicted.
- T1b: 45,232 of 100,000 ratings are above both means, a share of 0.452. Counting only movies with 20+ ratings, the share is 0.460. I guessed 35%, so I was too low, but the 20+ share was higher as expected.
- T1c returned the same 269 rows as the Week 6 chain (`same_rows: true`).

### Explanation

**Two partitions in one query.** Each `OVER (...)` is its own window. `PARTITION BY user_id` groups the rows by user to get the user's mean, and `PARTITION BY movie_id` groups the same rows by movie to get the movie's mean. Neither one merges rows, so both means just land as new columns on every rating.

**Why a one-rating movie can never be "above both".** If a movie has only one rating, its mean *is* that rating. A rating can't be greater than itself, so it fails the "above the movie's mean" test every time. These ratings still count in the total, so they pull the share down. Movies with only a few ratings have the same problem in a milder way, since one rating has a big effect on their mean. That is why the share goes up from 0.452 to 0.460 once we keep only movies with 20+ ratings.

**What the window replaced in (c).** The `genre_means` step and the final join back to it are gone. The chain needed them because `GROUP BY genre_id` collapses each genre to one row, which loses the movies. To compare each movie with its genre's mean, it had to compute the means in a separate table and join them back to the movie rows. `AVG(movie_mean) OVER (PARTITION BY genre_id)` puts the genre mean on each movie's row directly, so there is nothing to join. The filter still sits one step outside, because a window function can't be used in `WHERE`.

## T2. Top three per occupation

Tie-breaker for the ROW_NUMBER version:

### Prediction

### Result

### Explanation

## T3. Sessions and frames

### Prediction

### Result

### Explanation

## T4. Two indexes for four queries

### Prediction

### Result

### Explanation

## T5. Recommendation
