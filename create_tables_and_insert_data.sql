-- This SQL script defines a database schema for a retail or inventory management system.
-- It includes tables for customers, categories, suppliers, inventory, sizes, employees, shifts, orders, and order items.
-- Each table is designed with appropriate constraints and relationships to ensure data integrity.

-- Create tables

-- Inserting sample data into the Inventory table
INSERT INTO inventory (item_name, category, base_price, description, item_details)
VALUES
('Classic T-Shirt', 'T-Shirts', 19.99, 'A comfortable, everyday t-shirt', '<colors><color name="White"/><color name="Black"/><color name="Gray"/></colors>'),
('Slim Fit Jeans', 'Jeans', 49.99, 'Modern slim fit jeans', '<colors><color name="Blue"/><color name="Black"/></colors>'),
('Summer Dress', 'Dresses', 39.99, 'Light and breezy summer dress', '<colors><color name="Floral"/><color name="Yellow"/><color name="Pink"/></colors>'),
('Hooded Sweatshirt', 'Sweaters', 29.99, 'Cozy hooded sweatshirt for cool days', '<colors><color name="Navy"/><color name="Red"/><color name="Green"/></colors>'),
('Cargo Shorts', 'Shorts', 34.99, 'Versatile cargo shorts with multiple pockets', '<colors><color name="Khaki"/><color name="Olive"/><color name="Gray"/></colors>'),
('Formal Blazer', 'Suits', 89.99, 'Elegant blazer for formal occasions', '<colors><color name="Black"/><color name="Navy"/><color name="Gray"/></colors>'),
('Running Shoes', 'Accessories', 79.99, 'Lightweight running shoes for optimal performance', '<colors><color name="Black/White"/><color name="Blue/Orange"/><color name="Gray/Yellow"/></colors>');

-- Inserting sample data into the Inventory Sizes table
INSERT INTO inventory_sizes (inventory_id, size, quantity)
VALUES
(1, 'S', 50),(1, 'M', 75),(1, 'L', 60),(1, 'XL', 40),(2, '30', 40),(2, '32', 50),(2, '34', 45),(2, '36', 35),(3, 'S', 30),
(3, 'M', 40),(3, 'L', 35),(4, 'S', 25),(4, 'M', 35),(4, 'L', 30),(4, 'XL', 20),(5, '30', 30),(5, '32', 40),(5, '34', 35),
(5, '36', 25),(6, '38', 20),(6, '40', 25),(6, '42', 20),(6, '44', 15),(7, '8', 15),(7, '9', 20),(7, '10', 25),(7, '11', 20),
(7, '12', 15);

-- Inserting sample data into the Sales table
INSERT INTO sales (item_id, quantity, total_price, date)
VALUES
(1, 2, 39.98, '2023-06-01 10:30:00'),(2, 1, 49.99, '2023-06-02 14:45:00'),(3, 1, 39.99, '2023-06-03 11:15:00'),
(4, 1, 29.99, '2023-06-04 16:20:00'),(5, 2, 69.98, '2023-06-05 13:10:00'),(6, 1, 89.99, '2023-06-06 15:30:00'),
(7, 1, 79.99, '2023-06-07 12:45:00'),(1, 3, 59.97, '2023-06-08 10:00:00'),(2, 2, 99.98, '2023-06-09 17:30:00'),
(3, 2, 79.98, '2023-06-10 14:15:00');

-- Inserting sample data into the Customers table
INSERT INTO customers (name, email, phone)
VALUES
('John Doe', 'john.doe@email.com', '555-1234'),
('Jane Smith', 'jane.smith@email.com', '555-5678'),
('Bob Johnson', 'bob.johnson@email.com', '555-9876'),
('Alice Williams', 'alice.williams@email.com', '555-4321'),
('Charlie Brown', 'charlie.brown@email.com', '555-8765'),
('Diana Miller', 'diana.miller@email.com', '555-2345'),
('Edward Davis', 'edward.davis@email.com', '555-7890');

-- Inserting sample data into the Employees table
INSERT INTO employees (name, position, hire_date, salary)
VALUES
('Alice Brown', 'Store Manager', '2022-01-15', 50000.00),
('Charlie Davis', 'Sales Associate', '2022-03-01', 30000.00),
('Eva Wilson', 'Cashier', '2022-05-10', 28000.00),
('Frank Thomas', 'Assistant Manager', '2022-02-20', 40000.00),
('Grace Lee', 'Sales Associate', '2022-04-05', 30000.00),
('Henry Martinez', 'Inventory Specialist', '2022-06-15', 32000.00),
('Ivy Chen', 'Customer Service Representative', '2022-07-01', 29000.00);

-- Inserting sample data into the Item Images table
-- Note: In a real scenario, you would store the actual image data as a BLOB
-- Here, we're using placeholder text to represent image data
INSERT INTO item_images (inventory_id, image_data)
VALUES
(1, 'IMAGE_DATA_FOR_CLASSIC_TSHIRT'),
(2, 'IMAGE_DATA_FOR_SLIM_FIT_JEANS'),
(3, 'IMAGE_DATA_FOR_SUMMER_DRESS'),
(4, 'IMAGE_DATA_FOR_HOODED_SWEATSHIRT'),
(5, 'IMAGE_DATA_FOR_CARGO_SHORTS'),
(6, 'IMAGE_DATA_FOR_FORMAL_BLAZER'),
(7, 'IMAGE_DATA_FOR_RUNNING_SHOES');

------------------- SUPPORTING TABLES ----------------------
-- Supporting table: Categories
INSERT INTO categories (category_name, description)
VALUES
('T-Shirts', 'Casual short-sleeved shirts'),
('Jeans', 'Denim pants in various styles'),
('Dresses', 'One-piece garments for women'),
('Sweaters', 'Warm upper body garments'),
('Shorts', 'Short pants for casual wear'),
('Suits', 'Formal wear for professional settings'),
('Accessories', 'Additional items to complement outfits');

-- Supporting table: Suppliers
INSERT INTO suppliers (supplier_name, contact_person, email, phone)
VALUES
('FashionWholesale Inc.', 'Mark Johnson', 'mark@fashionwholesale.com', '555-0001'),
('TextileMasters Ltd.', 'Sarah Lee', 'slee@textilemasters.com', '555-0002'),
('TrendySupplies Co.', 'Alex Wong', 'awong@trendysupplies.com', '555-0003'),
('EcoFabrics Group', 'Emma Green', 'egreen@ecofabrics.com', '555-0004'),
('GlobalThreads Inc.', 'Carlos Rodriguez', 'crodriguez@globalthreads.com', '555-0005');

-- Supporting table: Orders (for inventory restocking)
INSERT INTO orders (supplier_id, order_date, total_amount, status)
VALUES
(1, '2023-05-15', 5000.00, 'Delivered'),
(2, '2023-05-20', 3500.00, 'In Transit'),
(3, '2023-05-25', 4200.00, 'Processing'),
(4, '2023-05-30', 2800.00, 'Delivered'),
(5, '2023-06-05', 3900.00, 'Processing');

-- Supporting table: Order_Items
INSERT INTO order_items (order_id, inventory_id, quantity, unit_price)
VALUES
(1, 1, 100, 10.00),
(1, 2, 50, 30.00),
(2, 3, 75, 20.00),
(2, 4, 60, 15.00),
(3, 5, 80, 20.00),
(3, 6, 40, 50.00),
(4, 7, 50, 40.00),
(4, 1, 100, 10.00),
(5, 2, 60, 30.00),
(5, 3, 70, 20.00);

-- Supporting table: Promotions
INSERT INTO promotions (promo_code, discount_percent, start_date, end_date, description)
VALUES
('SUMMER10', 10, '2023-06-01', '2023-08-31', 'Summer season 10% off'),
('NEWCUST20', 20, '2023-01-01', '2023-12-31', '20% off for new customers'),
('FLASH25', 25, '2023-07-01', '2023-07-03', 'Flash sale 25% off'),
('LOYALTY15', 15, '2023-01-01', '2023-12-31', '15% off for loyalty program members'),
('HOLIDAY30', 30, '2023-12-15', '2023-12-25', 'Holiday season 30% off');

-----------------------------------------------------------
-- Customers table: Stores customer information.
CREATE TABLE customers (
    id INTEGER PRIMARY KEY, -- Unique identifier for each customer
    name TEXT NOT NULL, -- Customer's full name
    email TEXT UNIQUE, -- Customer's email address, must be unique
    phone TEXT, -- Customer's phone number
    address TEXT, -- Customer's address
    registration_date DATE -- Date when the customer registered
);

-- Categories table: Stores product categories.
CREATE TABLE categories (
    id INTEGER PRIMARY KEY, -- Unique identifier for each category
    name TEXT NOT NULL, -- Name of the category
    description TEXT -- Description of the category
);

-- Suppliers table: Stores supplier information.
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY, -- Unique identifier for each supplier
    name TEXT NOT NULL, -- Name of the supplier
    contact_person TEXT, -- Contact person at the supplier
    email TEXT, -- Supplier's email address
    phone TEXT, -- Supplier's phone number
    address TEXT -- Supplier's address
);

-- Inventory table: Stores product information.
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY, -- Unique identifier for each inventory item
    item_name TEXT NOT NULL, -- Name of the item
    category_id INTEGER, -- Foreign key referencing the category of the item
    supplier_id INTEGER, -- Foreign key referencing the supplier of the item
    base_price REAL, -- Base price of the item
    description TEXT, -- Description of the item
    added_date DATE, -- Date when the item was added to inventory
    FOREIGN KEY (category_id) REFERENCES categories (id), -- Enforces referential integrity with categories table
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id) -- Enforces referential integrity with suppliers table
);

-- Sizes table: Stores available sizes for inventory items.
CREATE TABLE sizes (
    id INTEGER PRIMARY KEY, -- Unique identifier for each size
    size_name TEXT NOT NULL -- Name of the size (e.g., Small, Medium)
);

-- Inventory_sizes table: Links inventory items to their available sizes and quantities.
CREATE TABLE inventory_sizes (
    id INTEGER PRIMARY KEY, -- Unique identifier for each inventory-size relationship
    inventory_id INTEGER, -- Foreign key referencing the inventory item
    size_id INTEGER, -- Foreign key referencing the size
    quantity INTEGER, -- Quantity of the item available in this size
    FOREIGN KEY (inventory_id) REFERENCES inventory (id), -- Enforces referential integrity with inventory table
    FOREIGN KEY (size_id) REFERENCES sizes (id) -- Enforces referential integrity with sizes table
);

-- Employees table: Stores employee information.
CREATE TABLE employees (
    id INTEGER PRIMARY KEY, -- Unique identifier for each employee
    name TEXT NOT NULL, -- Employee's full name
    position TEXT, -- Employee's job position
    hire_date DATE, -- Date when the employee was hired
    salary REAL, -- Employee's salary
    email TEXT, -- Employee's email address
    phone TEXT -- Employee's phone number
);

-- Shifts table: Stores employee shift information.
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY, -- Unique identifier for each shift
    employee_id INTEGER, -- Foreign key referencing the employee
    shift_date DATE, -- Date of the shift
    start_time TIME, -- Start time of the shift
    end_time TIME, -- End time of the shift
    FOREIGN KEY (employee_id) REFERENCES employees (id) -- Enforces referential integrity with employees table
);

-- Orders table: Stores order information.
CREATE TABLE orders (
    id INTEGER PRIMARY KEY, -- Unique identifier for each order
    customer_id INTEGER, -- Foreign key referencing the customer who placed the order
    employee_id INTEGER, -- Foreign key referencing the employee who processed the order
    order_date DATETIME, -- Date and time when the order was placed
    total_amount REAL, -- Total amount of the order
    status TEXT, -- Status of the order (e.g., Completed, Processing)
    FOREIGN KEY (customer_id) REFERENCES customers (id), -- Enforces referential integrity with customers table
    FOREIGN KEY (employee_id) REFERENCES employees (id) -- Enforces referential integrity with employees table
);

-- Order_items table: Stores individual items within an order.
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY, -- Unique identifier for each order item
    order_id INTEGER, -- Foreign key referencing the order
    inventory_id INTEGER, -- Foreign key referencing the inventory item
    quantity INTEGER, -- Quantity of the item ordered
    unit_price REAL, -- Price per unit of the item
    subtotal REAL, -- Subtotal for the item (quantity * unit_price)
    FOREIGN KEY (order_id) REFERENCES orders (id), -- Enforces referential integrity with orders table
    FOREIGN KEY (inventory_id) REFERENCES inventory (id) -- Enforces referential integrity with inventory table
);

-- Insert at least 5 records into each table

-- Insert sample customer records
INSERT INTO customers (name, email, phone, address, registration_date) VALUES
('John Doe', 'john@example.com', '555-1234', '123 Main St, City', '2023-01-01'),
('Jane Smith', 'jane@example.com', '555-5678', '456 Elm St, Town', '2023-01-15'),
('Bob Johnson', 'bob@example.com', '555-9876', '789 Oak St, Village', '2023-02-01'),
('Alice Brown', 'alice@example.com', '555-4321', '321 Pine St, County', '2023-02-15'),
('Charlie Wilson', 'charlie@example.com', '555-8765', '654 Maple St, State', '2023-03-01');

-- Insert sample category records
INSERT INTO categories (name, description) VALUES
('Shirts', 'All types of shirts'),
('Pants', 'All types of pants'),
('Dresses', 'All types of dresses'),
('Shoes', 'All types of footwear'),
('Accessories', 'Belts, hats, and other accessories');

-- Insert sample supplier records
INSERT INTO suppliers (name, contact_person, email, phone, address) VALUES
('Fashion Wholesale', 'Tom Smith', 'tom@fashionwholesale.com', '555-1111', '100 Fashion Ave, Style City'),
('Trendy Textiles', 'Sarah Johnson', 'sarah@trendytextiles.com', '555-2222', '200 Fabric Lane, Textile Town'),
('Chic Distributors', 'Mike Brown', 'mike@chicdistributors.com', '555-3333', '300 Elegance Road, Chic City'),
('Glamour Goods', 'Emily Davis', 'emily@glamourgoods.com', '555-4444', '400 Glitter Street, Sparkle Town'),
('Style Suppliers', 'David Wilson', 'david@stylesuppliers.com', '555-5555', '500 Couture Court, Fashion Falls');

-- Insert sample inventory records
INSERT INTO inventory (item_name, category_id, supplier_id, base_price, description, added_date) VALUES
('Blue T-Shirt', 1, 1, 15.99, 'Comfortable cotton t-shirt', '2023-03-15'),
('Black Jeans', 2, 2, 39.99, 'Classic black denim jeans', '2023-03-16'),
('Floral Dress', 3, 3, 49.99, 'Summer floral print dress', '2023-03-17'),
('Running Shoes', 4, 4, 79.99, 'High-performance running shoes', '2023-03-18'),
('Leather Belt', 5, 5, 24.99, 'Genuine leather belt', '2023-03-19');

-- Insert sample size records
INSERT INTO sizes (size_name) VALUES
('Small'),
('Medium'),
('Large'),
('X-Large'),
('One Size');

-- Insert sample inventory_sizes records
INSERT INTO inventory_sizes (inventory_id, size_id, quantity) VALUES
(1, 1, 50),
(1, 2, 50),
(2, 2, 30),
(2, 3, 30),
(3, 1, 20),
(3, 2, 20),
(4, 2, 25),
(4, 3, 25),
(5, 5, 40);

-- Insert sample employee records
INSERT INTO employees (name, position, hire_date, salary, email, phone) VALUES
('Emma Davis', 'Store Manager', '2022-01-01', 60000, 'emma@store.com', '555-1212'),
('Michael Lee', 'Sales Associate', '2022-02-15', 35000, 'michael@store.com', '555-2323'),
('Sarah Johnson', 'Cashier', '2022-03-01', 30000, 'sarah@store.com', '555-3434'),
('David Brown', 'Inventory Specialist', '2022-04-15', 40000, 'david@store.com', '555-4545'),
('Lisa Chen', 'Assistant Manager', '2022-05-01', 50000, 'lisa@store.com', '555-5656');

-- Insert sample shift records
INSERT INTO shifts (employee_id, shift_date, start_time, end_time) VALUES
(1, '2023-05-01', '09:00', '17:00'),
(2, '2023-05-01', '10:00', '18:00'),
(3, '2023-05-01', '11:00', '19:00'),
(4, '2023-05-02', '09:00', '17:00'),
(5, '2023-05-02', '10:00', '18:00');

-- Insert sample order records
INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status) VALUES
(1, 2, '2023-05-01 10:30:00', 55.98, 'Completed'),
(2, 3, '2023-05-01 14:45:00', 79.99, 'Completed'),
(3, 4, '2023-05-02 11:15:00', 49.99, 'Processing'),
(4, 5, '2023-05-02 16:00:00', 104.98, 'Completed'),
(5, 1, '2023-05-03 13:30:00', 24.99, 'Processing');

-- Insert sample order_items records
INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES
(1, 1, 2, 15.99, 31.98),
(1, 5, 1, 24.99, 24.99),
(2, 4, 1, 79.99, 79.99),
(3, 3, 1, 49.99, 49.99),
(4, 2, 2, 39.99, 79.98),
(4, 5, 1, 24.99, 24.99),
(5, 5, 1, 24.99, 24.99);