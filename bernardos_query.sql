-- client qui a fait le plus de locations de toute la base

USE dataengineer;

-- Query result : ELEANOR	HUNT	46	17 IMP DES JARDINS	VALLEIRY	74520
SELECT
	c.first_name
	, c.last_name
	, COUNT(rental_id) AS "num_rentals"
	, a.address
	, a.city
	, a.postal_code
	, a.latitude
	, a.longitude
FROM customer c
	LEFT JOIN address a ON c.address_id = a.address_id
	LEFT JOIN rental r ON c.customer_id = r.customer_id
	GROUP BY c.first_name, c.last_name, a.address, a.city, a.postal_code, a.latitude, a.longitude
	ORDER BY COUNT(rental_id) DESC
	LIMIT 1 
    ;