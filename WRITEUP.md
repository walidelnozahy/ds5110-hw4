# HW4 write-up

All numbers come from `python run.py all` and are in `output/`.

## T1. A rating in context

### Prediction

- **`t1a_rating_in_context.sql`**: one row per rating, so about 100,000 rows (MovieLens 100k). A window adds the two means as columns but does not merge rows like `GROUP BY` would.
- **`t1b_above_both.sql`**: about 35%. Beating both your own usual rating and the movie's usual rating is harder than beating one. The 20+ share should be a bit higher, because movies with very few ratings make it hard to be above the movie's mean.
- **`t1c_window_rewrite.sql`**: the `genre_means` step and the final join back to it disappear. The window puts the genre mean on each row directly.

### Result

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
