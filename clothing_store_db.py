import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from tkinter.ttk import Notebook
import tkinter.scrolledtext as scrolledtext

from inventory_utils import create_reorder_log_table, check_and_reorder_inventory
from triggers import create_triggers


class ClothingStoreDB:
    def __init__(self, master):
        self.db_path = "clothing_store.db"
        self.master = master
        self.master.title("Clothing Store Database")
        self.master.geometry("800x600")

        try:
            self.conn = sqlite3.connect(self.db_path)
            self.create_tables()
            create_triggers(self.conn)  # Create triggers after tables are created
            create_reorder_log_table(self.db_path)  # Create reorder_log table
            self.create_widgets()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.master.destroy()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Create tables
        tables = [
            ('''CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                registration_date DATE
            )'''),
            ('''CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )'''),
            ('''CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT
            )'''),
            ('''CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                category_id INTEGER,
                supplier_id INTEGER,
                base_price REAL,
                description TEXT,
                added_date DATE,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )'''),
            ('''CREATE TABLE IF NOT EXISTS sizes (
                id INTEGER PRIMARY KEY,
                size_name TEXT NOT NULL
            )'''),
            ('''CREATE TABLE IF NOT EXISTS inventory_sizes (
                id INTEGER PRIMARY KEY,
                inventory_id INTEGER,
                size_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                FOREIGN KEY (size_id) REFERENCES sizes (id)
            )'''),
            ('''CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                hire_date DATE,
                salary REAL,
                email TEXT,
                phone TEXT
            )'''),
            ('''CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                shift_date DATE,
                start_time TIME,
                end_time TIME,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )'''),
            ('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                employee_id INTEGER,
                order_date DATETIME,
                total_amount REAL,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )'''),
            ('''CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                inventory_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                subtotal REAL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (inventory_id) REFERENCES inventory (id)
            )''')
        ]

        for table in tables:
            cursor.execute(table)

        # Create views
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS sales_summary AS
        SELECT 
            o.id AS order_id,
            c.name AS customer_name,
            e.name AS employee_name,
            o.order_date,
            o.total_amount,
            o.status,
            GROUP_CONCAT(i.item_name || ' (' || oi.quantity || ')') AS items
        FROM 
            orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN employees e ON o.employee_id = e.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN inventory i ON oi.inventory_id = i.id
        GROUP BY 
            o.id
        ''')

        cursor.execute('''
CREATE VIEW IF NOT EXISTS inventory_status AS
SELECT 
    i.id AS inventory_id,
    i.item_name,
    c.name AS category,
    s.name AS supplier,
    i.base_price,
    SUM(is_.quantity) AS total_quantity,
    GROUP_CONCAT(sz.size_name || ': ' || is_.quantity) AS size_breakdown
FROM 
    inventory i
    JOIN categories c ON i.category_id = c.id
    JOIN suppliers s ON i.supplier_id = s.id
    JOIN inventory_sizes is_ ON i.id = is_.inventory_id
    JOIN sizes sz ON is_.size_id = sz.id
GROUP BY 
    i.id
''')

        self.conn.commit()

        # Insert sample data (only if tables are empty)
        if not cursor.execute("SELECT * FROM customers").fetchone():
            self.insert_sample_data(cursor)

    def insert_sample_data(self, cursor):
        # Insert sample data for each table
        sample_data = [
            ("INSERT INTO customers (name, email, phone, address, registration_date) VALUES (?, ?, ?, ?, ?)",
             [('John Doe', 'john@example.com', '555-1234', '123 Main St, City', '2023-01-01'),
              ('Jane Smith', 'jane@example.com', '555-5678', '456 Elm St, Town', '2023-01-15'),
              ('Bob Johnson', 'bob@example.com', '555-9876', '789 Oak St, Village', '2023-02-01'),
              ('Alice Brown', 'alice@example.com', '555-4321', '321 Pine St, County', '2023-02-15'),
              ('Charlie Wilson', 'charlie@example.com', '555-8765', '654 Maple St, State', '2023-03-01')]),

            ("INSERT INTO categories (name, description) VALUES (?, ?)",
             [('Shirts', 'All types of shirts'),
              ('Pants', 'All types of pants'),
              ('Dresses', 'All types of dresses'),
              ('Shoes', 'All types of footwear'),
              ('Accessories', 'Belts, hats, and other accessories')]),

            ("INSERT INTO suppliers (name, contact_person, email, phone, address) VALUES (?, ?, ?, ?, ?)",
             [('Fashion Wholesale', 'Tom Smith', 'tom@fashionwholesale.com', '555-1111', '100 Fashion Ave, Style City'),
              ('Trendy Textiles', 'Sarah Johnson', 'sarah@trendytextiles.com', '555-2222',
               '200 Fabric Lane, Textile Town'),
              ('Chic Distributors', 'Mike Brown', 'mike@chicdistributors.com', '555-3333',
               '300 Elegance Road, Chic City'),
              (
              'Glamour Goods', 'Emily Davis', 'emily@glamourgoods.com', '555-4444', '400 Glitter Street, Sparkle Town'),
              ('Style Suppliers', 'David Wilson', 'david@stylesuppliers.com', '555-5555',
               '500 Couture Court, Fashion Falls')]),

            (
            "INSERT INTO inventory (item_name, category_id, supplier_id, base_price, description, added_date) VALUES (?, ?, ?, ?, ?, ?)",
            [('Blue T-Shirt', 1, 1, 15.99, 'Comfortable cotton t-shirt', '2023-03-15'),
             ('Black Jeans', 2, 2, 39.99, 'Classic black denim jeans', '2023-03-16'),
             ('Floral Dress', 3, 3, 49.99, 'Summer floral print dress', '2023-03-17'),
             ('Running Shoes', 4, 4, 79.99, 'High-performance running shoes', '2023-03-18'),
             ('Leather Belt', 5, 5, 24.99, 'Genuine leather belt', '2023-03-19')]),

            ("INSERT INTO sizes (size_name) VALUES (?)",
             [('Small',), ('Medium',), ('Large',), ('X-Large',), ('One Size',)]),

            ("INSERT INTO inventory_sizes (inventory_id, size_id, quantity) VALUES (?, ?, ?)",
             [(1, 1, 50), (1, 2, 50), (2, 2, 30), (2, 3, 30), (3, 1, 20),
              (3, 2, 20), (4, 2, 25), (4, 3, 25), (5, 5, 40)]),

            ("INSERT INTO employees (name, position, hire_date, salary, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
             [('Emma Davis', 'Store Manager', '2022-01-01', 60000, 'emma@store.com', '555-1212'),
              ('Michael Lee', 'Sales Associate', '2022-02-15', 35000, 'michael@store.com', '555-2323'),
              ('Sarah Johnson', 'Cashier', '2022-03-01', 30000, 'sarah@store.com', '555-3434'),
              ('David Brown', 'Inventory Specialist', '2022-04-15', 40000, 'david@store.com', '555-4545'),
              ('Lisa Chen', 'Assistant Manager', '2022-05-01', 50000, 'lisa@store.com', '555-5656')]),

            ("INSERT INTO shifts (employee_id, shift_date, start_time, end_time) VALUES (?, ?, ?, ?)",
             [(1, '2023-05-01', '09:00', '17:00'),
              (2, '2023-05-01', '10:00', '18:00'),
              (3, '2023-05-01', '11:00', '19:00'),
              (4, '2023-05-02', '09:00', '17:00'),
              (5, '2023-05-02', '10:00', '18:00')]),

            ("INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
             [(1, 2, '2023-05-01 10:30:00', 55.98, 'Completed'),
              (2, 3, '2023-05-01 14:45:00', 79.99, 'Completed'),
              (3, 4, '2023-05-02 11:15:00', 49.99, 'Processing'),
              (4, 5, '2023-05-02 16:00:00', 104.98, 'Completed'),
              (5, 1, '2023-05-03 13:30:00', 24.99, 'Processing')]),

            ("INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
             [(1, 1, 2, 15.99, 31.98),
              (1, 5, 1, 24.99, 24.99),
              (2, 4, 1, 79.99, 79.99),
              (3, 3, 1, 49.99, 49.99),
              (4, 2, 2, 39.99, 79.98),
              (4, 5, 1, 24.99, 24.99),
              (5, 5, 1, 24.99, 24.99)])
        ]

        for query, data in sample_data:
            cursor.executemany(query, data)

        self.conn.commit()

    def create_widgets(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs
        self.customers_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.employees_tab = ttk.Frame(self.notebook)
        self.sales_tab = ttk.Frame(self.notebook)
        self.views_tab = ttk.Frame(self.notebook)
        self.insights_tab = ttk.Frame(self.notebook)  # New tab for business insights
        self.schema_explanation_tab = ttk.Frame(self.notebook)  # Added tab for schema explanation

        self.notebook.add(self.customers_tab, text="Customers")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.employees_tab, text="Employees")
        self.notebook.add(self.sales_tab, text="Sales")
        self.notebook.add(self.views_tab, text="Views")
        self.notebook.add(self.insights_tab, text="Business Insights")  # Add the new tab
        self.notebook.add(self.schema_explanation_tab, text="Schema Explanation")  # Add schema explanation tab

        # Create widgets for each tab
        self.create_customers_widgets()
        self.create_inventory_widgets()
        self.create_employees_widgets()
        self.create_sales_widgets()
        self.create_views_widgets()
        self.create_insights_widgets()  # Create widgets for the new tab
        self.create_schema_explanation_widgets()  # Create widgets for schema explanation

    def create_customers_widgets(self):
        # Customer input fields
        ttk.Label(self.customers_tab, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.customer_name = ttk.Entry(self.customers_tab)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.customers_tab, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.customer_email = ttk.Entry(self.customers_tab)
        self.customer_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.customers_tab, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.customer_phone = ttk.Entry(self.customers_tab)
        self.customer_phone.grid(row=2, column=1, padx=5, pady=5)

        # Add customer button
        ttk.Button(self.customers_tab, text="Add Customer", command=self.add_customer).grid(row=3, column=0,
                                                                                            columnspan=2, pady=10)

        # Customer list
        self.customer_tree = ttk.Treeview(self.customers_tab, columns=("ID", "Name", "Email", "Phone"), show="headings")
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Name")
        self.customer_tree.heading("Email", text="Email")
        self.customer_tree.heading("Phone", text="Phone")
        self.customer_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Populate customer list
        self.populate_customer_list()

    def create_inventory_widgets(self):
        # Inventory input fields
        ttk.Label(self.inventory_tab, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.item_name = ttk.Entry(self.inventory_tab)
        self.item_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.item_category = ttk.Entry(self.inventory_tab)
        self.item_category.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Size:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.item_size = ttk.Entry(self.inventory_tab)
        self.item_size.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Price:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.item_price = ttk.Entry(self.inventory_tab)
        self.item_price.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.inventory_tab, text="Quantity:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.item_quantity = ttk.Entry(self.inventory_tab)
        self.item_quantity.grid(row=4, column=1, padx=5, pady=5)

        # Add item button
        ttk.Button(self.inventory_tab, text="Add Item", command=self.add_inventory_item).grid(row=5, column=0,
                                                                                              columnspan=2, pady=10)

        # Inventory list
        self.inventory_tree = ttk.Treeview(self.inventory_tab,
                                           columns=("ID", "Name", "Category", "Size", "Price", "Quantity"),
                                           show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Size", text="Size")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # Add a new button for checking and reordering inventory
        self.reorder_button = ttk.Button(self.inventory_tab, text="Check and Reorder Inventory",
                                         command=self.check_and_reorder)
        self.reorder_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Populate inventory list
        self.populate_inventory_list()

    def create_employees_widgets(self):
        # Employee input fields
        ttk.Label(self.employees_tab, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.employee_name = ttk.Entry(self.employees_tab)
        self.employee_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.employees_tab, text="Position:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.employee_position = ttk.Entry(self.employees_tab)
        self.employee_position.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.employees_tab, text="Hire Date:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.employee_hire_date = ttk.Entry(self.employees_tab)
        self.employee_hire_date.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.employees_tab, text="Salary:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.employee_salary = ttk.Entry(self.employees_tab)
        self.employee_salary.grid(row=3, column=1, padx=5, pady=5)

        # Add employee button
        ttk.Button(self.employees_tab, text="Add Employee", command=self.add_employee).grid(row=4, column=0,
                                                                                            columnspan=2, pady=10)

        # Employee list
        self.employee_tree = ttk.Treeview(self.employees_tab, columns=("ID", "Name", "Position", "Hire Date", "Salary"),
                                          show="headings")
        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.heading("Position", text="Position")
        self.employee_tree.heading("Hire Date", text="Hire Date")
        self.employee_tree.heading("Salary", text="Salary")
        self.employee_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Populate employee list
        self.populate_employee_list()

    def create_sales_widgets(self):
        # Sales input fields
        ttk.Label(self.sales_tab, text="Customer ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.sale_customer_id = ttk.Entry(self.sales_tab)
        self.sale_customer_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sales_tab, text="Item ID:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.sale_item_id = ttk.Entry(self.sales_tab)
        self.sale_item_id.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.sales_tab, text="Quantity:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.sale_quantity = ttk.Entry(self.sales_tab)
        self.sale_quantity.grid(row=2, column=1, padx=5, pady=5)

        # Add sale button
        ttk.Button(self.sales_tab, text="Add Sale", command=self.add_sale).grid(row=3, column=0, columnspan=2, pady=10)

        # Sales list
        self.sales_tree = ttk.Treeview(self.sales_tab,
                                       columns=("ID", "Customer", "Item", "Quantity", "Total Price", "Date"),
                                       show="headings")
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Customer", text="Customer")
        self.sales_tree.heading("Item", text="Item")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Total Price", text="Total Price")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Populate sales list
        self.populate_sales_list()

    def create_views_widgets(self):
        # Create a notebook for different views
        self.views_notebook = ttk.Notebook(self.views_tab)
        self.views_notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs for each view
        self.sales_summary_tab = ttk.Frame(self.views_notebook)
        self.inventory_status_tab = ttk.Frame(self.views_notebook)

        self.views_notebook.add(self.sales_summary_tab, text="Sales Summary")
        self.views_notebook.add(self.inventory_status_tab, text="Inventory Status")

        # Sales Summary View
        self.sales_summary_tree = ttk.Treeview(self.sales_summary_tab,
                                               columns=(
                                               "Order ID", "Customer", "Employee", "Date", "Total", "Status", "Items"),
                                               show="headings")
        self.sales_summary_tree.heading("Order ID", text="Order ID")
        self.sales_summary_tree.heading("Customer", text="Customer")
        self.sales_summary_tree.heading("Employee", text="Employee")
        self.sales_summary_tree.heading("Date", text="Date")
        self.sales_summary_tree.heading("Total", text="Total")
        self.sales_summary_tree.heading("Status", text="Status")
        self.sales_summary_tree.heading("Items", text="Items")
        self.sales_summary_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Inventory Status View
        self.inventory_status_tree = ttk.Treeview(self.inventory_status_tab,
                                                  columns=("ID", "Item", "Category", "Supplier", "Price", "Total Qty",
                                                           "Size Breakdown"),
                                                  show="headings")
        self.inventory_status_tree.heading("ID", text="ID")
        self.inventory_status_tree.heading("Item", text="Item")
        self.inventory_status_tree.heading("Category", text="Category")
        self.inventory_status_tree.heading("Supplier", text="Supplier")
        self.inventory_status_tree.heading("Price", text="Price")
        self.inventory_status_tree.heading("Total Qty", text="Total Qty")
        self.inventory_status_tree.heading("Size Breakdown", text="Size Breakdown")
        self.inventory_status_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons to refresh the views
        ttk.Button(self.sales_summary_tab, text="Refresh", command=self.populate_sales_summary).pack(pady=10)
        ttk.Button(self.inventory_status_tab, text="Refresh", command=self.populate_inventory_status).pack(pady=10)

        # Populate the views
        self.populate_sales_summary()
        self.populate_inventory_status()

    def create_insights_widgets(self):
        # Create a notebook for different insights
        self.insights_notebook = ttk.Notebook(self.insights_tab)
        self.insights_notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs for each insight
        self.bestsellers_tab = ttk.Frame(self.insights_notebook)
        self.top_customers_tab = ttk.Frame(self.insights_notebook)
        self.restock_tab = ttk.Frame(self.insights_notebook)
        self.employee_performance_tab = ttk.Frame(self.insights_notebook)
        self.monthly_sales_tab = ttk.Frame(self.insights_notebook)

        self.insights_notebook.add(self.bestsellers_tab, text="Top 5 Bestsellers")
        self.insights_notebook.add(self.top_customers_tab, text="Top Customers")
        self.insights_notebook.add(self.restock_tab, text="Restock Needed")
        self.insights_notebook.add(self.employee_performance_tab, text="Employee Performance")
        self.insights_notebook.add(self.monthly_sales_tab, text="Monthly Sales")

        # Create Treeview widgets for each insight
        self.create_bestsellers_widget()
        self.create_top_customers_widget()
        self.create_restock_widget()
        self.create_employee_performance_widget()
        self.create_monthly_sales_widget()

    def create_bestsellers_widget(self):
        columns = ("Item Name", "Category", "Total Sold", "Total Revenue")
        self.bestsellers_tree = self.create_treeview(self.bestsellers_tab, columns)
        self.bestsellers_tree.pack(expand=True, fill="both", padx=10, pady=10)
        ttk.Button(self.bestsellers_tab, text="Refresh", command=self.populate_bestsellers).pack(pady=10)

    def create_top_customers_widget(self):
        columns = ("Name", "Email", "Total Spent", "Order Count", "Avg Order Value")
        self.top_customers_tree = self.create_treeview(self.top_customers_tab, columns)
        self.top_customers_tree.pack(expand=True, fill="both", padx=10, pady=10)
        ttk.Button(self.top_customers_tab, text="Refresh", command=self.populate_top_customers).pack(pady=10)

    def create_restock_widget(self):
        columns = ("Item Name", "Category", "Supplier", "Total Quantity")
        self.restock_tree = self.create_treeview(self.restock_tab, columns)
        self.restock_tree.pack(expand=True, fill="both", padx=10, pady=10)
        ttk.Button(self.restock_tab, text="Refresh", command=self.populate_restock_needed).pack(pady=10)

    def create_employee_performance_widget(self):
        columns = ("Employee Name", "Total Orders", "Total Sales", "Avg Order Value")
        self.employee_performance_tree = self.create_treeview(self.employee_performance_tab, columns)
        self.employee_performance_tree.pack(expand=True, fill="both", padx=10, pady=10)
        ttk.Button(self.employee_performance_tab, text="Refresh", command=self.populate_employee_performance).pack(
            pady=10)

    def create_monthly_sales_widget(self):
        columns = ("Month", "Total Orders", "Total Revenue", "Avg Order Value")
        self.monthly_sales_tree = self.create_treeview(self.monthly_sales_tab, columns)
        self.monthly_sales_tree.pack(expand=True, fill="both", padx=10, pady=10)
        ttk.Button(self.monthly_sales_tab, text="Refresh", command=self.populate_monthly_sales).pack(pady=10)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        return tree

    def populate_bestsellers(self):
        query = """
        SELECT 
            i.item_name,
            c.name AS category,
            SUM(oi.quantity) AS total_sold,
            SUM(oi.subtotal) AS total_revenue
        FROM 
            order_items oi
        JOIN 
            inventory i ON oi.inventory_id = i.id
        JOIN 
            categories c ON i.category_id = c.id
        GROUP BY 
            i.id
        HAVING 
            total_sold > 0
        ORDER BY 
            total_sold DESC
        LIMIT 5;
        """
        self.populate_treeview(self.bestsellers_tree, query)
        messagebox.showinfo("Info", "Top 5 bestselling items have been updated.")

    def populate_top_customers(self):
        query = """
        SELECT 
            c.name,
            c.email,
            SUM(o.total_amount) AS total_spent,
            COUNT(o.id) AS order_count,
            AVG(o.total_amount) AS avg_order_value
        FROM 
            customers c
        JOIN 
            orders o ON c.id = o.customer_id
        GROUP BY 
            c.id
        HAVING 
            total_spent > (SELECT AVG(total_amount) FROM orders)
        ORDER BY 
            total_spent DESC;
        """
        self.populate_treeview(self.top_customers_tree, query)
        messagebox.showinfo("Info", "Top customers list has been updated.")

    def populate_restock_needed(self):
        query = """
SELECT 
    i.item_name,
    c.name AS category,
    s.name AS supplier,
    SUM(is_.quantity) AS total_quantity
FROM 
    inventory i
JOIN 
    categories c ON i.category_id =c.id
JOIN 
    suppliers s ON i.supplier_id = s.id
JOIN 
    inventory_sizes is_ ON i.id = is_.inventory_id
GROUPBY 
    i.id
HAVING 
    total_quantity < 20
ORDER BY 
    total_quantity ASC;
"""
        self.populate_treeview(self.restock_tree, query)
        messagebox.showinfo("Info", "Items needing restocking have been updated.")

    def populate_employee_performance(self):
        query = """
        SELECT 
            e.name AS employee_name,
            COUNT(o.id) AS total_orders,
            SUM(o.total_amount) AS total_sales,
            AVG(o.total_amount) AS avg_order_value
        FROM 
            employees e
        LEFT JOIN 
            orders o ON e.id = o.employee_id
        GROUP BY 
            e.id
        HAVING 
            total_orders > 0
        ORDER BY 
            total_sales DESC;
        """
        self.populate_treeview(self.employee_performance_tree, query)
        messagebox.showinfo("Info", "Employee performance data has been updated.")

    def populate_monthly_sales(self):
        query = """
        SELECT 
            strftime('%Y-%m', o.order_date) AS month,
            COUNT(o.id) AS total_orders,
            SUM(o.total_amount) AS total_revenue,
            AVG(o.total_amount) AS avg_order_value
        FROM 
            orders o
        GROUP BY 
            month
        ORDER BY 
            month DESC;
        """
        self.populate_treeview(self.monthly_sales_tree, query)
        messagebox.showinfo("Info", "Monthly sales report has been updated.")

    def populate_treeview(self, tree, query):
        tree.delete(*tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    def execute_query(self, query, parameters=None):
        try:
            cursor = self.conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return None

    def add_customer(self):
        name = self.customer_name.get()
        email = self.customer_email.get()
        phone = self.customer_phone.get()

        if name and email and phone:
            query = "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)"
            cursor = self.execute_query(query, (name, email, phone))
            if cursor:
                self.populate_customer_list()
                self.clear_customer_fields()
        else:
            messagebox.showerror("Error", "Please fill in all fields")

    def add_inventory_item(self):
        name = self.item_name.get()
        category = self.item_category.get()
        size = self.item_size.get()
        price = self.item_price.get()
        quantity = self.item_quantity.get()

        if name and category and size and price and quantity:
            cursor = self.execute_query("INSERT INTO inventory (item_name, category_id, base_price) VALUES (?, ?, ?)",
                                        (name, category, float(price)))
            if cursor:
                inventory_id = cursor.lastrowid
                cursor = self.execute_query(
                    "INSERT INTO inventory_sizes (inventory_id, size_id, quantity) VALUES (?, ?, ?)",
                    (inventory_id, size, int(quantity)))
                if cursor:
                    self.populate_inventory_list()
                    self.clear_inventory_fields()
        else:
            messagebox.showerror("Error", "Please fill in all fields")

    def add_employee(self):
        name = self.employee_name.get()
        position = self.employee_position.get()
        hire_date = self.employee_hire_date.get()
        salary = self.employee_salary.get()

        if name and position and hire_date and salary:
            cursor = self.execute_query("INSERT INTO employees (name, position, hire_date, salary) VALUES (?, ?, ?, ?)",
                                        (name, position, hire_date, float(salary)))
            if cursor:
                self.populate_employee_list()
                self.clear_employee_fields()
        else:
            messagebox.showerror("Error", "Please fill in all fields")

    def add_sale(self):
        customer_id = self.sale_customer_id.get()
        item_id = self.sale_item_id.get()
        quantity = self.sale_quantity.get()

        if customer_id and item_id and quantity:
            cursor = self.execute_query("SELECT base_price FROM inventory WHERE id = ?", (item_id,))
            if cursor:
                item_price = cursor.fetchone()
                if item_price:
                    total_price = float(item_price[0]) * int(quantity)
                    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    cursor = self.execute_query(
                        "INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
                        (int(customer_id), 1, sale_date, total_price, 'Completed'))
                    if cursor:
                        order_id = cursor.lastrowid
                        cursor = self.execute_query(
                            "INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                            (order_id, int(item_id), int(quantity), float(item_price[0]), total_price))
                        if cursor:
                            cursor = self.execute_query(
                                "UPDATE inventory_sizes SET quantity = quantity - ? WHERE inventory_id = ?",
                                (int(quantity), int(item_id)))
                            if cursor:
                                self.populate_sales_list()
                                self.populate_inventory_list()
                                self.clear_sale_fields()
                else:
                    messagebox.showerror("Error", "Invalid item ID")
        else:
            messagebox.showerror("Error", "Please fill in all fields")

    def populate_customer_list(self):
        self.customer_tree.delete(*self.customer_tree.get_children())
        cursor = self.execute_query("SELECT * FROM customers")
        if cursor:
            for row in cursor.fetchall():
                self.customer_tree.insert("", "end", values=row)

    def populate_inventory_list(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        try:
            cursor = self.execute_query("""
                SELECT i.id, i.item_name, c.name, s.size_name, i.base_price, is_.quantity
                FROM inventory i
                JOIN categories c ON i.category_id = c.id
                JOIN inventory_sizes is_ ON i.id = is_.inventory_id
                JOIN sizes s ON is_.size_id = s.id
            """)
            if cursor:
                for row in cursor.fetchall():
                    self.inventory_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while populating inventory: {e}")

    def populate_employee_list(self):
        self.employee_tree.delete(*self.employee_tree.get_children())
        cursor = self.execute_query("SELECT * FROM employees")
        if cursor:
            for row in cursor.fetchall():
                self.employee_tree.insert("", "end", values=row)

    def populate_sales_list(self):
        self.sales_tree.delete(*self.sales_tree.get_children())
        cursor = self.execute_query("""
            SELECT o.id, c.name, i.item_name, oi.quantity, o.total_amount, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN inventory i ON oi.inventory_id = i.id
        """)
        if cursor:
            for row in cursor.fetchall():
                self.sales_tree.insert("", "end", values=row)

    def populate_sales_summary(self):
        self.sales_summary_tree.delete(*self.sales_summary_tree.get_children())
        cursor = self.execute_query("SELECT * FROM sales_summary")
        if cursor:
            for row in cursor.fetchall():
                self.sales_summary_tree.insert("", "end", values=row)

    def populate_inventory_status(self):
        self.inventory_status_tree.delete(*self.inventory_status_tree.get_children())
        cursor = self.execute_query("SELECT * FROM inventory_status")
        if cursor:
            for row in cursor.fetchall():
                self.inventory_status_tree.insert("", "end", values=row)

    def clear_customer_fields(self):
        self.customer_name.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)

    def clear_inventory_fields(self):
        self.item_name.delete(0, tk.END)
        self.item_category.delete(0, tk.END)
        self.item_size.delete(0, tk.END)
        self.item_price.delete(0, tk.END)
        self.item_quantity.delete(0, tk.END)

    def clear_employee_fields(self):
        self.employee_name.delete(0, tk.END)
        self.employee_position.delete(0, tk.END)
        self.employee_hire_date.delete(0, tk.END)
        self.employee_salary.delete(0, tk.END)

    def clear_sale_fields(self):
        self.sale_customer_id.delete(0, tk.END)
        self.sale_item_id.delete(0, tk.END)
        self.sale_quantity.delete(0, tk.END)

    def check_and_reorder(self):
        reordered_items = check_and_reorder_inventory(self.db_path)
        if reordered_items:
            message = "The following items have been reordered:\n\n"
            for item in reordered_items:
                message += f"- {item[1]} (ID: {item[0]}, Current Quantity: {item[2]})\n"
            messagebox.showinfo("Inventory Reorder", message)
        else:
            messagebox.showinfo("Inventory Reorder", "No items need to be reordered at this time.")

        # Refresh the inventory list to show updated quantities
        self.populate_inventory_list()

    def create_schema_explanation_widgets(self):
        explanation_text = """
        Expanded Schema Explanation:

        Main Tables:
        1. CUSTOMERS: Stores customer information (id, name, email, phone, address, registration_date)
        2. ORDERS: Represents customer orders (id, customer_id, employee_id, order_date, total_amount, status)
        3. INVENTORY: Contains product information (id, item_name, category_id, supplier_id, base_price, description, added_date)
        4. EMPLOYEES: Stores employee data (id, name, position, hire_date, salary, email, phone)
        5. SUPPLIERS: Contains supplier information (id, name, contact_person, email, phone, address)

        Supporting Tables:
        1. ORDER_ITEMS: Links orders to inventory items (id, order_id, inventory_id, quantity, unit_price, subtotal)
        2. CATEGORIES: Stores product categories (id, name, description)
        3. SIZES: Contains available sizes (id, size_name)
        4. INVENTORY_SIZES: Links inventory items to sizes and quantities (id, inventory_id, size_id, quantity)
        5. SHIFTS: Stores employee work shifts (id, employee_id, shift_date, start_time, end_time)

        Key Relationships:
        - Customers place Orders (one-to-many)
        - Orders contain Order Items (one-to-many)
        - Inventory Items are included in Order Items (one-to-many)
        - Employees process Orders (one-to-many)
        - Suppliers supply Inventory Items (one-to-many)
        - Categories categorize Inventory Items (one-to-many)
        - Inventory Items have multiple Sizes through Inventory_Sizes (many-to-many)
        - Employees work Shifts (one-to-many)

        This schema maintains 3NF by ensuring that all non-key attributes are dependent only on the primary key, and
        there are no transitive dependencies. The use of foreign keys and junction tables (like INVENTORY_SIZES and
        ORDER_ITEMS) helps maintain relationships without violating 3NF principles.
        """

        explanation_scrolled_text = scrolledtext.ScrolledText(self.schema_explanation_tab, wrap=tk.WORD, width=80,
                                                              height=30)
        explanation_scrolled_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        explanation_scrolled_text.insert(tk.END, explanation_text)
        explanation_scrolled_text.config(state=tk.DISABLED)  # Make the text read-only


if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingStoreDB(root)
    root.mainloop()

