-- 1. Top Selling Products by Category
SELECT 'Top Selling Products by Category' AS message;

SELECT
    c.name AS category_name,
    i.item_name,
    SUM(s.quantity) AS total_sold,
    ROUND(SUM(s.total_price), 2) AS total_revenue
FROM
    sales s
JOIN
    inventory i ON s.item_id = i.id
JOIN
    categories c ON i.category_id = c.id
GROUP BY
    c.id, i.id
HAVING
    total_sold > (SELECT AVG(total_sold) FROM (SELECT SUM(quantity) AS total_sold FROM sales GROUP BY item_id))
ORDER BY
    c.name, total_sold DESC;

-- 2. Customer Purchase Frequency
SELECT 'Customer Purchase Frequency Analysis' AS message;

SELECT
    c.id AS customer_id,
    c.name AS customer_name,
    COUNT(o.id) AS total_orders,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    MAX(o.order_date) AS last_order_date,
    ROUND(JULIANDAY('now') - JULIANDAY(MAX(o.order_date))) AS days_since_last_order
FROM
    customers c
LEFT JOIN
    orders o ON c.id = o.customer_id
GROUP BY
    c.id
HAVING
    COUNT(o.id) > 0
ORDER BY
    total_orders DESC, avg_order_value DESC;

-- 3. Inventory Turnover Rate
SELECT 'Inventory Turnover Rate Analysis' AS message;

WITH inventory_sales AS (
    SELECT
        i.id AS item_id,
        i.item_name,
        SUM(COALESCE(s.quantity, 0)) AS total_sold,
        AVG(COALESCE(inv_sizes.quantity, 0)) AS avg_inventory
    FROM
        inventory i
    LEFT JOIN
        sales s ON i.id = s.item_id
    LEFT JOIN
        inventory_sizes inv_sizes ON i.id = inv_sizes.inventory_id
    GROUP BY
        i.id
)
SELECT
    item_id,
    item_name,
    total_sold,
    avg_inventory,
    CASE
        WHEN avg_inventory > 0 THEN ROUND(total_sold / avg_inventory, 2)
        ELSE 0
    END AS turnover_rate
FROM
    inventory_sales
WHERE
    turnover_rate > 0
ORDER BY
    turnover_rate DESC;

-- 4. Employee Sales Performance
SELECT 'Employee Sales Performance Analysis' AS message;

SELECT
    e.id AS employee_id,
    e.name AS employee_name,
    COUNT(o.id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_sales,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    ROUND(SUM(o.total_amount) / COUNT(DISTINCT strftime('%Y-%m', o.order_date)), 2) AS avg_monthly_sales
FROM
    employees e
LEFT JOIN
    orders o ON e.id = o.employee_id
GROUP BY
    e.id
HAVING
    COUNT(o.id) > 0
ORDER BY
    total_sales DESC;

-- 5. Category Performance Over Time
SELECT 'Category Performance Over Time Analysis' AS message;

SELECT
    strftime('%Y-%m', o.order_date) AS month,
    c.name AS category_name,
    COUNT(DISTINCT o.id) AS total_orders,
    SUM(oi.quantity) AS total_items_sold,
    ROUND(SUM(oi.subtotal), 2) AS total_revenue
FROM
    orders o
JOIN
    order_items oi ON o.id = oi.order_id
JOIN
    inventory i ON oi.inventory_id = i.id
JOIN
    categories c ON i.category_id = c.id
GROUP BY
    month, c.id
HAVING
    COUNT(DISTINCT o.id) >= 5
ORDER BY
    month DESC, total_revenue DESC;

-- Optimization: Create indexes for frequently used columns in JOIN and WHERE clauses
CREATE INDEX IF NOT EXISTS idx_sales_item_id ON sales(item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_category_id ON inventory(category_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_employee_id ON orders(employee_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_inventory_id ON order_items(inventory_id);

