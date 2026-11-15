WITH occ_movie AS (
  SELECT u.occupation, r.movie_id, COUNT(*) AS n, AVG(r.rating) AS mean_rating
  FROM ratings AS r
  JOIN users AS u USING (user_id)
  GROUP BY u.occupation, r.movie_id
  HAVING COUNT(*) >= 20),
ranked AS (
  SELECT occupation, movie_id, n, mean_rating,
         RANK() OVER (PARTITION BY occupation ORDER BY mean_rating DESC) AS pos
  FROM occ_movie)
SELECT occupation, pos, movie_id, title, n, mean_rating
FROM ranked
JOIN movies USING (movie_id)
WHERE pos <= 3
ORDER BY occupation, pos, movie_id;
