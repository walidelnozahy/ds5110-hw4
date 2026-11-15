WITH movie_stats AS (                 
  SELECT movie_id, AVG(rating) AS movie_mean
  FROM ratings
  GROUP BY movie_id
  HAVING COUNT(*) >= 30),
movie_genre AS (                      
  SELECT mg.genre_id,
         s.movie_id,
         s.movie_mean,
         AVG(s.movie_mean) OVER (PARTITION BY mg.genre_id) AS genre_mean
  FROM movie_stats AS s
  JOIN movie_genres AS mg USING (movie_id))
SELECT genre_id, movie_id, movie_mean, genre_mean
FROM movie_genre                      
WHERE movie_mean >= genre_mean + 0.5;
