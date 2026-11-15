
WITH rated AS (
  SELECT user_id,
         movie_id,
         rating,
         AVG(rating) OVER (PARTITION BY user_id)  AS user_mean,
         AVG(rating) OVER (PARTITION BY movie_id) AS movie_mean,
         COUNT(*)    OVER (PARTITION BY movie_id) AS movie_n
  FROM ratings),
flagged AS (
  SELECT movie_n,
         (rating > user_mean AND rating > movie_mean) AS above_both
  FROM rated)
SELECT COUNT(*)        AS n_ratings,
       SUM(above_both) AS n_above_both,
       AVG(above_both) AS share_above_both,            
       AVG(CASE WHEN movie_n >= 20 THEN above_both END)
         AS share_above_both_20plus
FROM flagged;
