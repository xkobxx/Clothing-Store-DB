import atexit
import base64
import io
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
#from Cryptodome.Cipher import AES
#from Cryptodome.Random import get_random_bytes
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET
import logging
from config import ENCRYPTION_KEY, DB_NAME, INVENTORY_TABLE, INVENTORY_SIZES_TABLE, SALES_TABLE, CUSTOMERS_TABLE, EMPLOYEES_TABLE, ITEM_IMAGES_TABLE, LOG_FILE, LOG_LEVEL
from datetime import datetime
import csv
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Set up logging
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ClothingStoreDB:
    def __init__(self, master):
        self.customer_name = None
        self.master = master
        self.master.title("Clothing Store Database")
        self.master.geometry("1000x600")

        # Initialize database connection
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.update_inventory_sizes()
        self.check_table_structure()
        self.check_sales_table_structure()

        # Create main frame
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both")

        # Create tabs
        self.create_inventory_tab()
        self.create_add_item_tab()
        self.create_update_delete_tab()
        self.create_sales_report_tab()
        self.create_customers_tab()
        self.create_employees_tab()

        self.print_table_info(INVENTORY_TABLE)
        self.print_table_info(INVENTORY_SIZES_TABLE)
        self.print_table_info(SALES_TABLE)

    def print_table_info(self, table_name):
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            print(f"Table structure for {table_name}:")
            for column in columns:
                print(f"  {column[1]} ({column[2]})")
        except sqlite3.Error as e:
            print(f"Error getting table info for {table_name}: {e}")

    def create_inventory_tab(self):
        inventory_tab = tk.Frame(self.notebook)
        self.notebook.add(inventory_tab, text="Inventory")

        # Search frame
        search_frame = tk.Frame(inventory_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.inventory_search_entry = tk.Entry(search_frame)
        self.inventory_search_entry.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_inventory).pack(side="left", padx=5)

        # Inventory tree view
        self.inventory_tree = ttk.Treeview(inventory_tab,
                                           columns=("ID", "Name", "Category", "Price", "Size", "Quantity", "Colors"),
                                           show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Size", text="Size")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Colors", text="Colors")
        self.inventory_tree.pack(expand=True, fill="both", padx=10, pady=10)

        refresh_button = tk.Button(inventory_tab, text="Refresh", command=self.refresh_inventory)
        refresh_button.pack(pady=10)

        self.inventory_tree.bind("<Double-1>", self.on_item_double_click)

        self.refresh_inventory()

    def create_add_item_tab(self):
        add_item_tab = tk.Frame(self.notebook)
        self.notebook.add(add_item_tab, text="Add Item")

        # Item details entry fields
        tk.Label(add_item_tab, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.item_name_entry = tk.Entry(add_item_tab)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_item_tab, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_combobox = ttk.Combobox(add_item_tab, values=[
            "T-Shirts", "Jeans", "Dresses", "Skirts", "Jackets", "Sweaters",
            "Shorts", "Pants", "Blouses", "Suits", "Activewear", "Underwear",
            "Socks", "Accessories"
        ])
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.category_combobox.set("Select a category")

        tk.Label(add_item_tab, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.price_entry = tk.Entry(add_item_tab)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_item_tab, text="Size:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.size_entry = tk.Entry(add_item_tab)
        self.size_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(add_item_tab, text="Quantity:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.quantity_entry = tk.Entry(add_item_tab)
        self.quantity_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(add_item_tab, text="Description:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.description_entry = tk.Entry(add_item_tab)
        self.description_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(add_item_tab, text="Colors (comma-separated):").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.colors_entry = tk.Entry(add_item_tab)
        self.colors_entry.grid(row=6, column=1, padx=5, pady=5)

        self.image_path = None
        tk.Button(add_item_tab, text="Choose Image", command=self.choose_image).grid(row=7, column=0, columnspan=2, pady=10)

        tk.Button(add_item_tab, text="Add Item", command=self.add_item).grid(row=8, column=0, columnspan=2, pady=10)

    def create_update_delete_tab(self):
        update_delete_tab = tk.Frame(self.notebook)
        self.notebook.add(update_delete_tab, text="Update/Delete")

        tk.Label(update_delete_tab, text="Item ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.update_id_entry = tk.Entry(update_delete_tab)
        self.update_id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.update_id_entry.bind('<FocusOut>', self.on_id_entry_change)

        tk.Label(update_delete_tab, text="Item Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.update_name_entry = tk.Entry(update_delete_tab)
        self.update_name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(update_delete_tab, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.update_category_entry = tk.Entry(update_delete_tab)
        self.update_category_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(update_delete_tab, text="Price:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.update_price_entry = tk.Entry(update_delete_tab)
        self.update_price_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(update_delete_tab, text="Size:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.update_size_entry = tk.Entry(update_delete_tab)
        self.update_size_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(update_delete_tab, text="Quantity:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.update_quantity_entry = tk.Entry(update_delete_tab)
        self.update_quantity_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(update_delete_tab, text="Colors (comma-separated):").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.update_colors_entry = tk.Entry(update_delete_tab)
        self.update_colors_entry.grid(row=6, column=1, padx=5, pady=5)

        tk.Button(update_delete_tab, text="Load Item", command=self.load_item).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(update_delete_tab, text="Update Item", command=self.update_item).grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(update_delete_tab, text="Delete Item", command=self.delete_item).grid(row=9, column=0, columnspan=2, pady=10)

    def create_sales_report_tab(self):
        sales_report_tab = tk.Frame(self.notebook)
        self.notebook.add(sales_report_tab, text="Sales Report")

        self.sales_tree = ttk.Treeview(sales_report_tab, columns=("ID", "Item", "Quantity", "Total Price", "Date"),
                                       show="headings")
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Item", text="Item")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Total Price", text="Total Price")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        refresh_button = tk.Button(sales_report_tab, text="Refresh", command=self.refresh_sales_report)
        refresh_button.pack(pady=10)

        export_button = tk.Button(sales_report_tab, text="Export Report", command=self.export_sales_report)
        export_button.pack(pady=10)

        self.refresh_sales_report()

    def create_customers_tab(self):
        customers_tab = tk.Frame(self.notebook)
        self.notebook.add(customers_tab, text="Customers")

        # Search frame
        search_frame = tk.Frame(customers_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.customer_search_entry = tk.Entry(search_frame)
        self.customer_search_entry.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_customers).pack(side="left", padx=5)

        # Treeview
        self.customers_tree = ttk.Treeview(customers_tab,
                                           columns=("ID", "Name", "Email", "Phone"),
                                           show="headings")
        self.customers_tree.heading("ID", text="ID")
        self.customers_tree.heading("Name", text="Name")
        self.customers_tree.heading("Email", text="Email")
        self.customers_tree.heading("Phone", text="Phone")
        self.customers_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons
        button_frame = tk.Frame(customers_tab)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(button_frame, text="Add Customer", command=self.add_customer).pack(side="left", padx=5)
        tk.Button(button_frame, text="Refresh", command=self.refresh_customers).pack(side="left", padx=5)

        self.refresh_customers()

    def create_employees_tab(self):
        employees_tab = tk.Frame(self.notebook)
        self.notebook.add(employees_tab, text="Employees")

        # Search frame
        search_frame = tk.Frame(employees_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.employee_search_entry = tk.Entry(search_frame)
        self.employee_search_entry.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_employees).pack(side="left", padx=5)

        # Treeview
        self.employees_tree = ttk.Treeview(employees_tab,
                                           columns=("ID", "Name", "Position", "Hire Date", "Salary"),
                                           show="headings")
        self.employees_tree.heading("ID", text="ID")
        self.employees_tree.heading("Name", text="Name")
        self.employees_tree.heading("Position", text="Position")
        self.employees_tree.heading("Hire Date", text="Hire Date")
        self.employees_tree.heading("Salary", text="Salary")
        self.employees_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons
        button_frame = tk.Frame(employees_tab)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side="left", padx=5)
        tk.Button(button_frame, text="Refresh", command=self.refresh_employees).pack(side="left", padx=5)

        self.refresh_employees()

    def create_tables(self):
        try:
            self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {INVENTORY_TABLE} (
            id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            base_price REAL NOT NULL,
            description TEXT,
            item_details TEXT
        )
        ''')

            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {INVENTORY_SIZES_TABLE} (
                id INTEGER PRIMARY KEY,
                inventory_id INTEGER,
                size TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (inventory_id) REFERENCES {INVENTORY_TABLE}(id)
            )
            ''')

            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {SALES_TABLE} (
                id INTEGER PRIMARY KEY,
                item_id INTEGER,
                quantity INTEGER,
                total_price REAL,
                date TEXT,
                FOREIGN KEY (item_id) REFERENCES {INVENTORY_TABLE}(id)
            )
            ''')

            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {CUSTOMERS_TABLE} (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
            ''')

            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {EMPLOYEES_TABLE} (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                hire_date TEXT,
                salary REAL
            )
            ''')

            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {ITEM_IMAGES_TABLE} (
                id INTEGER PRIMARY KEY,
                inventory_id INTEGER,
                image_data BLOB,
                FOREIGN KEY (inventory_id) REFERENCES {INVENTORY_TABLE}(id)
            )
            ''')

            self.conn.commit()
            logging.info("Database tables created successfully")
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            messagebox.showerror("Database Error", f"Failed to create tables: {e}")

    def check_table_structure(self):
        try:
            self.cursor.execute(f"PRAGMA table_info({INVENTORY_TABLE})")
            columns = [column[1] for column in self.cursor.fetchall()]
            if 'description' not in columns:
                self.cursor.execute(f"ALTER TABLE {INVENTORY_TABLE} ADD COLUMN description TEXT")
                self.conn.commit()
                logging.info("Added 'description' column to inventory table")
            if 'item_details' not in columns:
                self.cursor.execute(f"ALTER TABLE {INVENTORY_TABLE} ADD COLUMN item_details TEXT")
                self.conn.commit()
                logging.info("Added 'item_details' column to inventory table")
        except sqlite3.Error as e:
            logging.error(f"Error checking table structure: {e}")
            messagebox.showerror("Database Error", f"Failed to check table structure: {e}")

    def check_sales_table_structure(self):
        try:
            self.cursor.execute(f"PRAGMA table_info({SALES_TABLE})")
            columns = [column[1] for column in self.cursor.fetchall()]
            if 'date' not in columns:
                self.cursor.execute(f"ALTER TABLE {SALES_TABLE} ADD COLUMN date TEXT")
                self.conn.commit()
                logging.info("Added 'date' column to sales table")
            if 'item_id' not in columns:
                self.cursor.execute(f"ALTER TABLE {SALES_TABLE} ADD COLUMN item_id INTEGER REFERENCES {INVENTORY_TABLE}(id)")
                self.conn.commit()
                logging.info("Added 'item_id' column to sales table")
        except sqlite3.Error as e:
            logging.error(f"Error checking sales table structure: {e}")
            messagebox.showerror("Database Error", f"Failed to check sales table structure: {e}")

    def update_inventory_sizes(self):
        try:
            self.cursor.execute(f"SELECT id FROM {INVENTORY_TABLE}")
            items = self.cursor.fetchall()
            for item in items:
                self.cursor.execute(f"SELECT COUNT(*) FROM {INVENTORY_SIZES_TABLE} WHERE inventory_id = ?", (item[0],))
                count = self.cursor.fetchone()[0]
                if count == 0:
                    self.cursor.execute(f"INSERT INTO {INVENTORY_SIZES_TABLE} (inventory_id, size, quantity) VALUES (?, ?, ?)",
                                        (item[0], 'One Size', 0))
            self.conn.commit()
            logging.info("Inventory sizes updated successfully")
        except sqlite3.Error as e:
            logging.error(f"Error updating inventory sizes: {e}")
            messagebox.showerror("Database Error", f"Failed to update inventory sizes: {e}")

    def refresh_inventory(self):
        try:
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            query = f'''
    SELECT {INVENTORY_TABLE}.id, {INVENTORY_TABLE}.item_name, {INVENTORY_TABLE}.category, {INVENTORY_TABLE}.base_price, 
           {INVENTORY_SIZES_TABLE}.size, {INVENTORY_SIZES_TABLE}.quantity, {INVENTORY_TABLE}.item_details
    FROM {INVENTORY_TABLE}
    JOIN {INVENTORY_SIZES_TABLE} ON {INVENTORY_TABLE}.id = {INVENTORY_SIZES_TABLE}.inventory_id
    '''
            print("Executing query:", query)  # Debug print
            self.cursor.execute(query)
            for row in self.cursor.fetchall():
                try:
                    decrypted_price = self.decrypt_data(str(row[3]))
                    if decrypted_price is None:
                        decrypted_price = "N/A"
                except Exception as e:
                    logging.error(f"Error decrypting price: {e}")
                    decrypted_price = "N/A"
                colors = self.parse_colors_xml(row[6])
                self.inventory_tree.insert('', 'end', values=(row[0], row[1], row[2], f"${decrypted_price}" if decrypted_price != "N/A" else "N/A", row[4], row[5], colors))
            logging.info("Inventory refreshed successfully")
        except sqlite3.Error as e:
            logging.error(f"Error refreshing inventory: {e}")
            messagebox.showerror("Database Error", f"Failed to refresh inventory: {e}")

    def search_inventory(self):
        search_term = self.inventory_search_entry.get().lower()
        try:
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            self.cursor.execute(f'''
SELECT {INVENTORY_TABLE}.id, {INVENTORY_TABLE}.item_name, {INVENTORY_TABLE}.category, {INVENTORY_TABLE}.base_price, 
       {INVENTORY_SIZES_TABLE}.size, {INVENTORY_SIZES_TABLE}.quantity, {INVENTORY_TABLE}.item_details
FROM {INVENTORY_TABLE}
JOIN {INVENTORY_SIZES_TABLE} ON {INVENTORY_TABLE}.id = {INVENTORY_SIZES_TABLE}.inventory_id
WHERE LOWER({INVENTORY_TABLE}.item_name) LIKE ? OR LOWER({INVENTORY_TABLE}.category) LIKE ?
''', (f'%{search_term}%', f'%{search_term}%'))
            for row in self.cursor.fetchall():
                try:
                    decrypted_price = self.decrypt_data(str(row[3]))
                    if decrypted_price is None:
                        decrypted_price = "N/A"
                except Exception as e:
                    logging.error(f"Error decrypting price: {e}")
                    decrypted_price = "N/A"
                colors = self.parse_colors_xml(row[6])
                self.inventory_tree.insert('', 'end', values=(row[0], row[1], row[2], f"${decrypted_price}" if decrypted_price != "N/A" else "N/A", row[4], row[5], colors))
            logging.info(f"Inventory search performed for term: {search_term}")
        except sqlite3.Error as e:
            logging.error(f"Error searching inventory: {e}")
            messagebox.showerror("Database Error", f"Failed to search inventory: {e}")

    def on_item_double_click(self, event):
        item = self.inventory_tree.selection()[0]
        item_id = self.inventory_tree.item(item, "values")[0]
        self.show_item_details(item_id)

    def show_item_details(self, item_id):
        try:
            self.cursor.execute(f'''
        SELECT i.*, "is".size, "is".quantity, im.image_data
        FROM {INVENTORY_TABLE} i
        JOIN {INVENTORY_SIZES_TABLE} "is" ON i.id = "is".inventory_id
        LEFT JOIN {ITEM_IMAGES_TABLE} im ON i.id = im.inventory_id
        WHERE i.id = ?
        ''', (item_id,))
            item_data = self.cursor.fetchone()

            if item_data:
                details_window = tk.Toplevel(self.master)
                details_window.title(f"Item Details - {item_data[1]}")
                details_window.geometry("400x600")

                tk.Label(details_window, text=f"Name: {item_data[1]}").pack(pady=5)
                tk.Label(details_window, text=f"Category: {item_data[2]}").pack(pady=5)
                tk.Label(details_window, text=f"Price: ${self.decrypt_data(str(item_data[3]))}").pack(pady=5)
                tk.Label(details_window, text=f"Size: {item_data[7]}").pack(pady=5)
                tk.Label(details_window, text=f"Quantity: {item_data[8]}").pack(pady=5)
                tk.Label(details_window, text=f"Description: {item_data[4]}").pack(pady=5)

                colors = "N/A"
                if item_data[5]:
                    try:
                        xml_data = ET.fromstring(item_data[5])
                        color_elements = xml_data.findall('.//color')
                        if color_elements:
                            colors = ', '.join([color.get('name', '') for color in color_elements])
                    except ET.ParseError:
                        logging.error(f"Error parsing XML data for item ID {item_id}")
                tk.Label(details_window, text=f"Colors: {colors}").pack(pady=5)

                if item_data[9]:
                    image = Image.open(io.BytesIO(item_data[9]))
                    image.thumbnail((200, 200))
                    photo = ImageTk.PhotoImage(image)
                    image_label = tk.Label(details_window, image=photo)
                    image_label.image = photo
                    image_label.pack(pady=10)

                tk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)
                logging.info(f"Item details displayed: ID {item_id}")
        except sqlite3.Error as e:
            logging.error(f"Error displaying item details: {e}")
            messagebox.showerror("Database Error", f"Failed to display item details: {e}")

    def choose_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if self.image_path:
            messagebox.showinfo("Image Selected", "Image file selected successfully")

    def add_item(self):
        name = self.item_name_entry.get().strip()
        category = self.category_combobox.get().strip()
        price = self.price_entry.get().strip()
        size = self.size_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        description = self.description_entry.get().strip()
        colors = self.colors_entry.get().strip()

        if not all([name, category, price, size, quantity]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity. Please enter numeric values.")
            return

        try:
            encrypted_price = self.encrypt_data(str(price))
            colors_xml = self.create_colors_xml(colors)

            self.cursor.execute(f'''
            INSERT INTO {INVENTORY_TABLE} (item_name, category, base_price, description, item_details)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, category, encrypted_price, description, colors_xml))

            item_id = self.cursor.lastrowid

            self.cursor.execute(f'''
            INSERT INTO {INVENTORY_SIZES_TABLE} (inventory_id, size, quantity)
            VALUES (?, ?, ?)
            ''', (item_id, size, quantity))

            if self.image_path:
                with open(self.image_path, 'rb') as file:
                    image_data = file.read()
                self.cursor.execute(f'''
                INSERT INTO {ITEM_IMAGES_TABLE} (inventory_id, image_data)
                VALUES (?, ?)
                ''', (item_id, image_data))

            self.conn.commit()
            messagebox.showinfo("Success", "Item added successfully")
            self.refresh_inventory()
            logging.info(f"New item added: {name}")

            # Clear entry fields
            for entry in [self.item_name_entry, self.price_entry, self.size_entry, self.quantity_entry, self.description_entry, self.colors_entry]:
                entry.delete(0, 'end')
            self.category_combobox.set("Select a category")
            self.image_path = None

        except sqlite3.Error as e:
            self.conn.rollback()
            logging.error(f"SQLite error in add_item: {e}")
            messagebox.showerror("Database Error", f"Failed to add item: {e}")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Unexpected error in add_item: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def on_id_entry_change(self, event):
        item_id = self.update_id_entry.get()
        if item_id:
            self.load_item()

    def load_item(self):
        item_id = self.update_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an item ID")
            return

        try:
            self.cursor.execute(f'''
        SELECT i.*, "is".size, "is".quantity
        FROM {INVENTORY_TABLE} i
        JOIN {INVENTORY_SIZES_TABLE} "is" ON i.id = "is".inventory_id
        WHERE i.id = ?
        ''', (item_id,))
            item = self.cursor.fetchone()

            if item:
                self.update_name_entry.delete(0, 'end')
                self.update_name_entry.insert(0, item[1])
                self.update_category_entry.delete(0, 'end')
                self.update_category_entry.insert(0, item[2])
                self.update_price_entry.delete(0, 'end')
                self.update_price_entry.insert(0, self.decrypt_data(str(item[3])))
                self.update_size_entry.delete(0, 'end')
                self.update_size_entry.insert(0, item[7])
                self.update_quantity_entry.delete(0, 'end')
                self.update_quantity_entry.insert(0, item[8])
                colors = self.parse_colors_xml(item[5])
                self.update_colors_entry.delete(0, 'end')
                self.update_colors_entry.insert(0, colors)
            else:
                messagebox.showerror("Error", "Item not found")
        except sqlite3.Error as e:
            logging.error(f"Error loading item: {e}")
            messagebox.showerror("Database Error", f"Failed to load item: {e}")

    def update_item(self):
        item_id = self.update_id_entry.get()
        name = self.update_name_entry.get()
        category = self.update_category_entry.get()
        price = self.update_price_entry.get()
        size = self.update_size_entry.get()
        quantity = self.update_quantity_entry.get()
        colors = self.update_colors_entry.get()

        if not all([item_id, name, category, price, size, quantity]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity")
            return

        try:
            encrypted_price = self.encrypt_data(str(price))
            colors_xml = self.create_colors_xml(colors)

            self.cursor.execute(f'''
        UPDATE {INVENTORY_TABLE}
        SET item_name = ?, category = ?, base_price = ?,item_details = ?
        WHERE id = ?
        ''', (name, category, encrypted_price, colors_xml, item_id))

            self.cursor.execute(f'''
            UPDATE {INVENTORY_SIZES_TABLE}
            SET size = ?, quantity = ?
            WHERE inventory_id = ?
                        ''', (size, quantity, item_id))

            self.conn.commit()
            messagebox.showinfo("Success", "Item updated successfully")
            self.refresh_inventory()
            logging.info(f"Item updated: ID {item_id}")

            # Clear entry fields
            for entry in[self.update_id_entry, self.update_name_entry, self.update_category_entry, self.update_price_entry, self.update_size_entry, self.update_quantity_entry, self.update_colors_entry]:
                entry.delete(0, 'end')

        except sqlite3.Error as e:
            logging.error(f"Error updating item: {e}")
            messagebox.showerror("Database Error", f"Failed to update item: {e}")

    def delete_item(self):
        item_id = self.update_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an item ID")
            return

        try:
            self.cursor.execute(f"DELETE FROM {INVENTORY_TABLE} WHERE id = ?", (item_id,))
            self.cursor.execute(f"DELETE FROM {INVENTORY_SIZES_TABLE} WHERE inventory_id = ?", (item_id,))
            self.cursor.execute(f"DELETE FROM {ITEM_IMAGES_TABLE} WHERE inventory_id = ?", (item_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Item deleted successfully")
            self.refresh_inventory()
            logging.info(f"Item deleted: ID {item_id}")

            # Clear entry fields
            for entry in [self.update_id_entry, self.update_name_entry, self.update_category_entry, self.update_price_entry, self.update_size_entry, self.update_quantity_entry, self.update_colors_entry]:
                entry.delete(0, 'end')

        except sqlite3.Error as e:
            logging.error(f"Error deleting item: {e}")
            messagebox.showerror("Database Error", f"Failed to delete item: {e}")

    def refresh_sales_report(self):
        try:
            self.sales_tree.delete(*self.sales_tree.get_children())
            query = f'''
        SELECT {SALES_TABLE}.id, 
               COALESCE({INVENTORY_TABLE}.item_name, 'Unknown Item') as item_name, 
               {SALES_TABLE}.quantity, 
               {SALES_TABLE}.total_price, 
               COALESCE({SALES_TABLE}.date, 'N/A') as date
        FROM {SALES_TABLE}
        LEFT JOIN {INVENTORY_TABLE} ON {SALES_TABLE}.item_id = {INVENTORY_TABLE}.id
        ORDER BY {SALES_TABLE}.id DESC
        '''
            print("Executing query:", query)  # Debug print
            self.cursor.execute(query)
            for row in self.cursor.fetchall():
                try:
                    decrypted_price = self.decrypt_data(str(row[3]))
                    if decrypted_price is None:
                        decrypted_price = "N/A"
                except Exception as e:
                    logging.error(f"Error decrypting price: {e}")
                    decrypted_price = "N/A"
                self.sales_tree.insert('', 'end', values=(row[0], row[1], row[2], f"${decrypted_price}" if decrypted_price != "N/A" else "N/A", row[4]))
            logging.info("Sales report refreshed successfully")
        except sqlite3.Error as e:
            logging.error(f"Error refreshing sales report: {e}")
            messagebox.showerror("Database Error", f"Failed to refresh sales report: {e}")

    def add_sale(self, item_id, quantity, total_price):
        try:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encrypted_price = self.encrypt_data(str(total_price))
            self.cursor.execute(f'''
            INSERT INTO {SALES_TABLE} (item_id, quantity, total_price, date)
            VALUES (?, ?, ?, ?)
            ''', (item_id, quantity, encrypted_price, date))
            self.conn.commit()
            logging.info(f"Sale added: Item ID {item_id}, Quantity {quantity}, Date {date}")
        except sqlite3.Error as e:
            logging.error(f"Error adding sale: {e}")
            messagebox.showerror("Database Error", f"Failed to add sale: {e}")

    def export_sales_report(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if filename:
                self.cursor.execute(f'''
                SELECT {SALES_TABLE}.id, {INVENTORY_TABLE}.item_name, {SALES_TABLE}.quantity, {SALES_TABLE}.total_price, {SALES_TABLE}.date
                FROM {SALES_TABLE}
                JOIN {INVENTORY_TABLE} ON {SALES_TABLE}.item_id = {INVENTORY_TABLE}.id
                ORDER BY {SALES_TABLE}.date DESC
                ''')
                with open(filename, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(['ID', 'Item', 'Quantity', 'Total Price', 'Date'])
                    for row in self.cursor.fetchall():
                        decrypted_price = self.decrypt_data(str(row[3]))
                        csvwriter.writerow([row[0], row[1], row[2], f"${decrypted_price:.2f}" if decrypted_price != "N/A" else "N/A", row[4]])
                messagebox.showinfo("Success", "Sales report exported successfully")
                logging.info(f"Sales report exported to {filename}")
        except (sqlite3.Error, IOError) as e:
            logging.error(f"Error exporting sales report: {e}")
            messagebox.showerror("Export Error", f"Failed to export sales report: {e}")

    def refresh_customers(self):
        try:
            self.customers_tree.delete(*self.customers_tree.get_children())
            self.cursor.execute(f"SELECT * FROM {CUSTOMERS_TABLE}")
            for row in self.cursor.fetchall():
                self.customers_tree.insert('', 'end', values=row)
            logging.info("Customers list refreshed successfully")
        except sqlite3.Error as e:
            logging.error(f"Error refreshing customers list: {e}")
            messagebox.showerror("Database Error", f"Failed to refresh customers list: {e}")

    def search_customers(self):
        search_term = self.customer_search_entry.get().lower()
        try:
            self.customers_tree.delete(*self.customers_tree.get_children())
            self.cursor.execute(f'''
            SELECT * FROM {CUSTOMERS_TABLE}
            WHERE LOWER(name) LIKE ? OR LOWER(email) LIKE ? OR LOWER(phone) LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            for row in self.cursor.fetchall():
                self.customers_tree.insert('', 'end', values=row)
            logging.info(f"Customer search performed for term: {search_term}")
        except sqlite3.Error as e:
            logging.error(f"Error searching customers: {e}")
            messagebox.showerror("Database Error", f"Failed to search customers: {e}")

    def add_customer(self):
        name = simpledialog.askstring("Add Customer", "Enter customer name:")
        if name:
            email = simpledialog.askstring("Add Customer", "Enter customer email:")
            phone = simpledialog.askstring("Add Customer", "Enter customer phone:")
            try:
                self.cursor.execute(f"INSERT INTO {CUSTOMERS_TABLE} (name, email, phone) VALUES (?, ?, ?)",
                                    (name, email, phone))
                self.conn.commit()
                messagebox.showinfo("Success", "Customer added successfully")
                self.refresh_customers()
                logging.info(f"New customer added: {name}")
            except sqlite3.Error as e:
                logging.error(f"Error adding customer: {e}")
                messagebox.showerror("Database Error", f"Failed to add customer: {e}")

    def refresh_employees(self):
        try:
            self.employees_tree.delete(*self.employees_tree.get_children())
            self.cursor.execute(f"SELECT * FROM {EMPLOYEES_TABLE}")
            for row in self.cursor.fetchall():
                self.employees_tree.insert('', 'end', values=row)
            logging.info("Employees list refreshed successfully")
        except sqlite3.Error as e:
            logging.error(f"Error refreshing employees list: {e}")
            messagebox.showerror("Database Error", f"Failed to refresh employees list: {e}")

    def search_employees(self):
        search_term = self.employee_search_entry.get().lower()
        try:
            self.employees_tree.delete(*self.employees_tree.get_children())
            self.cursor.execute(f'''
            SELECT * FROM {EMPLOYEES_TABLE}
            WHERE LOWER(name) LIKE ? OR LOWER(position) LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%'))
            for row in self.cursor.fetchall():
                self.employees_tree.insert('', 'end', values=row)
            logging.info(f"Employee search performed for term: {search_term}")
        except sqlite3.Error as e:
            logging.error(f"Error searching employees: {e}")
            messagebox.showerror("Database Error", f"Failed to search employees: {e}")

    def add_employee(self):
        name = simpledialog.askstring("Add Employee", "Enter employee name:")
        if name:
            position = simpledialog.askstring("Add Employee", "Enter employee position:")
            hire_date = simpledialog.askstring("Add Employee", "Enter hire date (YYYY-MM-DD):")
            salary = simpledialog.askfloat("Add Employee", "Enter employee salary:")
            try:
                self.cursor.execute(f"INSERT INTO {EMPLOYEES_TABLE} (name, position, hire_date, salary) VALUES (?, ?, ?, ?)",
                                    (name, position, hire_date, salary))
                self.conn.commit()
                messagebox.showinfo("Success", "Employee added successfully")
                self.refresh_employees()
                logging.info(f"New employee added: {name}")
            except sqlite3.Error as e:
                logging.error(f"Error adding employee: {e}")
                messagebox.showerror("Database Error", f"Failed to add employee: {e}")

    @staticmethod
    def derive_key(password, salt):
        """
        Derive a 32-byte key from a password and salt using PBKDF2.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt_data(data):
        """
        Encrypt the data using AES-256-GCM.

        :param data: The data to encrypt (string)
        :return: Encrypted data as a base64 encoded string
        """
        try:
            # Generate a random salt
            salt = os.urandom(16)

            # Derive the key
            key = ClothingStoreDB.derive_key(ENCRYPTION_KEY, salt)

            # Generate a random 96-bit IV
            iv = os.urandom(12)

            # Convert data to bytes
            data_bytes = data.encode('utf-8')

            # Create AES-GCM cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Encrypt the data
            ciphertext = encryptor.update(data_bytes) + encryptor.finalize()

            # Get the tag
            tag = encryptor.tag

            # Combine salt, IV, ciphertext, and tag
            encrypted_data = salt + iv + ciphertext + tag

            # Encode as base64 for storage
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logging.error(f"Encryption error: {e}")
            raise

    @staticmethod
    def decrypt_data(encrypted_data):
        """
        Decrypt the data using AES-256-GCM.

        :param encrypted_data: The encrypted data as a base64 encoded string
        :return: Decrypted data as a string
        """
        try:
            # Decode the base64 encoded data
            encrypted_bytes = base64.b64decode(encrypted_data)

            # Extract salt, IV, ciphertext, and tag
            salt = encrypted_bytes[:16]
            iv = encrypted_bytes[16:28]
            ciphertext = encrypted_bytes[28:-16]
            tag = encrypted_bytes[-16:]

            # Derive the key
            key = ClothingStoreDB.derive_key(ENCRYPTION_KEY, salt)

            # Create AES-GCM cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt the data
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

            return decrypted_data.decode('utf-8')
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return None

    def create_colors_xml(self, colors):
        root = ET.Element("colors")
        for color in colors.split(','):
            color_elem = ET.SubElement(root, "color")
            color_elem.set("name", color.strip())
        return ET.tostring(root, encoding='unicode')

    def parse_colors_xml(self, xml_string):
        if xml_string:
            try:
                root = ET.fromstring(xml_string)
                return ', '.join([color.get('name', '') for color in root.findall('.//color')])
            except ET.ParseError:
                logging.error(f"Error parsing XML: {xml_string}")
                return "Error parsing colors"
        return ""

def cleanup():
    """Clean up function to be called when the program exits."""
    if hasattr(ClothingStoreDB, 'conn') and ClothingStoreDB.conn:
        ClothingStoreDB.conn.close()
        logging.info("Database connection closed")

atexit.register(cleanup)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingStoreDB(root)
    root.mainloop()

