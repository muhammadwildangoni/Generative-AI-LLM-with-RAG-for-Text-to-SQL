-- SQLite
SELECT order_id, amount 
FROM orders 
ORDER BY amount DESC 
LIMIT 5;

SELECT c.name, SUM(o.amount) AS total_spent 
FROM orders o 
JOIN customers c ON o.customer_id = c.id 
GROUP BY c.id 
ORDER BY total_spent DESC 
LIMIT 1;

SELECT name FROM customers WHERE id NOT IN (SELECT customer_id FROM orders);

SELECT c.city, SUM(o.amount) AS total_purchase FROM orders o JOIN customers c ON o.customer_id = c.id GROUP BY c.city ORDER BY total_purchase DESC;