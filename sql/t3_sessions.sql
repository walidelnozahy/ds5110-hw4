WITH gaps AS (
  SELECT user_id, timestamp,
         timestamp - LAG(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp) AS gap
  FROM ratings),
flags AS (
  SELECT user_id, timestamp,
         CASE WHEN gap IS NULL OR gap > 1800 THEN 1 ELSE 0 END AS new_session
  FROM gaps),
numbered AS (
  SELECT user_id, timestamp,
         SUM(new_session) OVER (PARTITION BY user_id ORDER BY timestamp
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS session_no
  FROM flags)
SELECT user_id, session_no,
       COUNT(*) AS n_ratings,
       MIN(timestamp) AS start_ts,
       MAX(timestamp) - MIN(timestamp) AS duration_s
FROM numbered
GROUP BY user_id, session_no
ORDER BY user_id, session_no;
