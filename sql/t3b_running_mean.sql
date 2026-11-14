-- T3b. Each user's running mean rating, in time order, computed twice.
-- Required columns: user_id, movie_id, timestamp, rating, run_default, run_rows
--   run_default: AVG(rating) OVER (PARTITION BY user_id ORDER BY timestamp)
--   run_rows:    the same, ORDER BY timestamp, movie_id, with an explicit
--                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW frame
--
-- Prediction (commit before running): the two columns disagree on
-- (no rows / a few rows / many rows), because ______.

-- YOUR QUERY HERE
