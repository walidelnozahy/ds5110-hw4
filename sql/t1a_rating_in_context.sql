SELECT user_id,
       movie_id,
       rating,
       AVG(rating) OVER (PARTITION BY user_id)  AS user_mean, 
       AVG(rating) OVER (PARTITION BY movie_id) AS movie_mean 
FROM ratings;
