-- Test Trigger 1: Update inventory quantity when a sale is made
-- First, check the current quantity
SELECT * FROM inventory_sizes WHERE inventory_id = 1 AND size_id = 1;

-- Insert a new order item
INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status)
VALUES (1, 1, datetime('now'), 15.99, 'Completed');

INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal)
VALUES (last_insert_rowid(), 1, 5, 15.99, 79.95);

-- Check the updated quantity
SELECT * FROM inventory_sizes WHERE inventory_id = 1 AND size_id = 1;

-- Check if a low stock alert was created
SELECT * FROM low_stock_alerts WHERE inventory_id = 1;

-- Test Trigger 2: Log price changes in the inventory
-- Check the current price
SELECT id, item_name, base_price FROM inventory WHERE id = 1;

-- Update the price
UPDATE inventory SET base_price = 17.99 WHERE id = 1;

-- Check the price change log
SELECT * FROM price_change_log WHERE inventory_id = 1;