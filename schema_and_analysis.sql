-- Run using SQLite. The Python pipeline also creates this database/table.
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    purchase_date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    amount REAL NOT NULL
);

-- 1. Total sales by customer
SELECT customer_id, COUNT(DISTINCT transaction_id) AS frequency,
       ROUND(SUM(amount), 2) AS monetary_value
FROM transactions
GROUP BY customer_id
ORDER BY monetary_value DESC;

-- 2. Monthly revenue trend
SELECT substr(purchase_date, 1, 7) AS month,
       ROUND(SUM(amount), 2) AS revenue,
       COUNT(DISTINCT transaction_id) AS transactions
FROM transactions
GROUP BY month
ORDER BY month;

-- 3. Top 10 customers by revenue
SELECT customer_id, ROUND(SUM(amount), 2) AS revenue
FROM transactions
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;

-- 4. RFM base table. Set the analysis date to one day after the latest purchase.
WITH latest AS (
    SELECT date(MAX(purchase_date), '+1 day') AS analysis_date FROM transactions
)
SELECT t.customer_id,
       CAST(julianday(latest.analysis_date) - julianday(MAX(t.purchase_date)) AS INTEGER) AS recency_days,
       COUNT(DISTINCT t.transaction_id) AS frequency,
       ROUND(SUM(t.amount), 2) AS monetary_value
FROM transactions t CROSS JOIN latest
GROUP BY t.customer_id
ORDER BY monetary_value DESC;

-- 5. Average order value by customer
SELECT customer_id,
       ROUND(SUM(amount) * 1.0 / COUNT(DISTINCT transaction_id), 2) AS average_order_value
FROM transactions
GROUP BY customer_id
ORDER BY average_order_value DESC;
