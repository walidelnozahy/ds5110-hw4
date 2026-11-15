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

Tie-breaker for the ROW_NUMBER version: ___

### Prediction

- **`t2_top3_row_number.sql`**: This query finds the top 3 movies for each occupation, based on average rating, considering only movies with at least 20 ratings from that occupation.
- **`t2_top3_rank.sql`**: returns more rows than ROW_NUMBER, because RANK() gives tied movies the same rank, so multiple movies can qualify for the top 3.

### Result

- **`t2_top3_row_number.sql`**: 27 rows
- **`t2_top3_rank.sql`**: 28 rows

### Explanation

I see 11 jobs that have no rows at all, because they have too few users for any movie to get 20 ratings. I think I would yse ROW_NUMBER because it always shows at most 3 movies and gives the same result every time.

## T3. Sessions and frames

### Prediction

### Result

### Explanation

## T4. Two indexes for four queries

### Prediction

### Result

### Explanation

## T5. Recommendation
