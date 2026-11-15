SELECT user_id, movie_id, timestamp, rating,
       AVG(rating) OVER (PARTITION BY user_id ORDER BY timestamp) AS run_default,
       AVG(rating) OVER (PARTITION BY user_id ORDER BY timestamp, movie_id
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS run_rows
FROM ratings;
