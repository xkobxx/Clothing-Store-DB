-- Create a virtual table for inventory status
CREATE VIEW inventory_status AS
SELECT 
    i.id,
    i.item_name,
    c.category_name,
    i.base_price,
    SUM(is.quantity) as total_quantity,
    CASE 
        WHEN SUM(is.quantity) = 0 THEN 'Out of Stock'
        WHEN SUM(is.quantity) < 10 THEN 'Low Stock'
        ELSE 'In Stock'
    END as stock_status
FROM 
    inventory i
JOIN 
    categories c ON i.category_id = c.id
JOIN 
    inventory_sizes is ON i.id = is.inventory_id
GROUP BY 
    i.id;

-- Create a virtual table for sales summary
CREATE VIEW sales_summary AS
SELECT 
    s.id as sale_id,
    i.item_name,
    s.quantity,
    s.total_price,
    s.date,
    c.name as customer_name
FROM 
    sales s
JOIN 
    inventory i ON s.item_id = i.id
LEFT JOIN 
    customers c ON s.customer_id = c.id;

-- Create a virtual table for top selling items
CREATE VIEW top_selling_items AS
SELECT 
    i.id,
    i.item_name,
    c.category_name,
    SUM(s.quantity) as total_quantity_sold,
    SUM(s.total_price) as total_revenue
FROM 
    sales s
JOIN 
    inventory i ON s.item_id = i.id
JOIN 
    categories c ON i.category_id = c.id
GROUP BY 
    i.id
ORDER BY 
    total_quantity_sold DESC
LIMIT 10;

