-- Create a view for sales summary
CREATE VIEW sales_summary AS
SELECT 
    i.category,
    SUM(s.quantity) as total_quantity_sold,
    SUM(s.total_price) as total_revenue,
    AVG(s.total_price / s.quantity) as average_price
FROM 
    sales s
JOIN 
    inventory i ON s.item_id = i.id
GROUP BY 
    i.category;

-- Create a view for inventory status
CREATE VIEW inventory_status AS
SELECT 
    i.id,
    i.item_name,
    i.category,
    SUM(is.quantity) as total_quantity,
    COUNT(DISTINCT is.size) as size_count,
    i.base_price
FROM 
    inventory i
JOIN 
    inventory_sizes is ON i.id = is.inventory_id
GROUP BY 
    i.id, i.item_name, i.category, i.base_price;

-- Create a view for top customers
CREATE VIEW top_customers AS
SELECT 
    c.id,
    c.name,
    COUNT(s.id) as total_purchases,
    SUM(s.total_price) as total_spent
FROM 
    customers c
JOIN 
    sales s ON c.id = s.customer_id
GROUP BY 
    c.id, c.name
ORDER BY 
    total_spent DESC
LIMIT 10;

