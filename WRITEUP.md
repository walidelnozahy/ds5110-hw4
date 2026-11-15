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
