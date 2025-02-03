import atexit
import base64
import io
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from Cryptodome.Cipher import AES
from PIL import Image, ImageTk

secret_key = b'Sixteen byte key'


class ClothingStoreDB:
    def __init__(self, master):
        self.master = master
        self.master.title("Clothing Store Database")
        self.master.geometry("1000x700")  # Updated window size

        self.conn = sqlite3.connect("clothing_store.db")
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.check_table_structure()
        self.update_inventory_sizes()

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_inventory_tab()
        self.create_add_item_tab()
        self.create_update_delete_tab()
        self.create_sales_report_tab()
        self.create_customers_tab()
        self.create_employees_tab()

    def create_tables(self):
        self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        item_name TEXT NOT NULL,
        category TEXT,
        base_price TEXT NOT NULL, 
        description TEXT
    )
    ''')

        self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_sizes (
        id INTEGER PRIMARY KEY,
        inventory_id INTEGER,
        size TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (inventory_id) REFERENCES inventory (id)
    )
    ''')

        self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_images (
        id INTEGER PRIMARY KEY,
        inventory_id INTEGER,
        image_data BLOB,
        FOREIGN KEY (inventory_id) REFERENCES inventory (id)
    )
    ''')

        self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        inventory_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        sale_date TEXT,
        FOREIGN KEY (inventory_id) REFERENCES inventory (id)
    )
    ''')

        self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT
    )
    ''')

        self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        position TEXT,
        hire_date TEXT,
        salary REAL
    )
    ''')

        self.conn.commit()

    def check_table_structure(self):
        # Check inventory table
        self.cursor.execute("PRAGMA table_info(inventory)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        print("Inventory table columns:", column_names)

        if 'category' not in column_names:
            print("Category column is missing. Adding it now.")
            self.cursor.execute("ALTER TABLE inventory ADD COLUMN category TEXT")
            self.conn.commit()

        # Check inventory_sizes table
        self.cursor.execute("PRAGMA table_info(inventory_sizes)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        print("Inventory_sizes table columns:", column_names)

        if 'size' not in column_names:
            print("Size column is missing in inventory_sizes. Adding it now.")
            self.cursor.execute("ALTER TABLE inventory_sizes ADD COLUMN size TEXT")
            self.conn.commit()

        # Check item_images table
        self.cursor.execute("PRAGMA table_info(item_images)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        print("Item_images table columns:", column_names)

        # Check sales table
        self.cursor.execute("PRAGMA table_info(sales)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        print("Sales table columns:", column_names)

    @staticmethod
    def encrypt_data(data):
        cipher = AES.new(secret_key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    @staticmethod
    def decrypt_data(enc_data):
        enc_data = base64.b64decode(enc_data)
        nonce = enc_data[:16]
        ciphertext = enc_data[16:]
        cipher = AES.new(secret_key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode('utf-8')

    def create_inventory_tab(self):
        inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(inventory_tab, text="Inventory")

        # Search frame
        search_frame = ttk.Frame(inventory_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.inventory_search_entry = ttk.Entry(search_frame)
        self.inventory_search_entry.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_inventory).pack(side="left", padx=5)

        self.inventory_tree = ttk.Treeview(inventory_tab,
                                           columns=("ID", "Name", "Category", "Price", "Size", "Quantity"),
                                           show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Size", text="Size")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.pack(expand=True, fill="both", padx=10, pady=10)

        refresh_button = ttk.Button(inventory_tab, text="Refresh", command=self.refresh_inventory)
        refresh_button.pack(pady=10)

        self.inventory_tree.bind("<Double-1>", self.on_item_double_click)

        self.refresh_inventory()

    def refresh_inventory(self):
        try:
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            self.cursor.execute('''
                SELECT i.id, i.item_name, COALESCE(i.category, 'N/A') as category, i.base_price, 
                       COALESCE(inv_sizes.size, 'N/A') as size, COALESCE(inv_sizes.quantity, 0) as quantity
                FROM inventory i
                LEFT JOIN inventory_sizes inv_sizes ON i.id = inv_sizes.inventory_id
                ''')
            for row in self.cursor.fetchall():
                try:
                    decrypted_price = self.decrypt_data(str(row[3]))
                except:
                    decrypted_price = "N/A"
                self.inventory_tree.insert("", "end", values=(
                    row[0], row[1], row[2], f"${decrypted_price}" if decrypted_price != "N/A" else "N/A", row[4],
                    row[5]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh inventory: {str(e)}")
            print(f"Error details: {str(e)}")

    def create_add_item_tab(self):
        add_item_tab = ttk.Frame(self.notebook)
        self.notebook.add(add_item_tab, text="Add Item")

        ttk.Label(add_item_tab, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.item_name_entry = ttk.Entry(add_item_tab)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_item_tab, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_combobox = ttk.Combobox(add_item_tab, values=[
            "T-Shirts", "Jeans", "Dresses", "Skirts", "Jackets", "Sweaters",
            "Shorts", "Pants", "Blouses", "Suits", "Activewear", "Underwear",
            "Socks", "Accessories"
        ])
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.category_combobox.set("Select a category")

        ttk.Label(add_item_tab, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.price_entry = ttk.Entry(add_item_tab)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(add_item_tab, text="Size:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.size_entry = ttk.Entry(add_item_tab)
        self.size_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(add_item_tab, text="Quantity:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(add_item_tab)
        self.quantity_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(add_item_tab, text="Description:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.description_entry = ttk.Entry(add_item_tab)
        self.description_entry.grid(row=5, column=1, padx=5, pady=5)

        self.image_path = None
        ttk.Button(add_item_tab, text="Choose Image", command=self.choose_image).grid(row=6, column=0, columnspan=2,
                                                                                      pady=10)

        ttk.Button(add_item_tab, text="Add Item", command=self.add_item).grid(row=7, column=0, columnspan=2, pady=10)

    def create_update_delete_tab(self):
        update_delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(update_delete_tab, text="Update/Delete")

        ttk.Label(update_delete_tab, text="Item ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.update_id_entry = ttk.Entry(update_delete_tab)
        self.update_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(update_delete_tab, text="Item Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.update_name_entry = ttk.Entry(update_delete_tab)
        self.update_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(update_delete_tab, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.update_category_entry = ttk.Entry(update_delete_tab)
        self.update_category_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(update_delete_tab, text="Price:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.update_price_entry = ttk.Entry(update_delete_tab)
        self.update_price_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(update_delete_tab, text="Size:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.update_size_entry = ttk.Entry(update_delete_tab)
        self.update_size_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(update_delete_tab, text="Quantity:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.update_quantity_entry = ttk.Entry(update_delete_tab)
        self.update_quantity_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(update_delete_tab, text="Load Item", command=self.load_item).grid(row=6, column=0, columnspan=2,
                                                                                     pady=10)
        ttk.Button(update_delete_tab, text="Update Item", command=self.update_item).grid(row=7, column=0, columnspan=2,
                                                                                         pady=10)
        ttk.Button(update_delete_tab, text="Delete Item", command=self.delete_item).grid(row=8, column=0, columnspan=2,
                                                                                         pady=10)

    def create_sales_report_tab(self):
        sales_report_tab = ttk.Frame(self.notebook)
        self.notebook.add(sales_report_tab, text="Sales Report")

        self.sales_tree = ttk.Treeview(sales_report_tab, columns=("ID", "Item", "Quantity", "Total Price", "Date"),
                                       show="headings")
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Item", text="Item")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Total Price", text="Total Price")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        refresh_button = ttk.Button(sales_report_tab, text="Refresh", command=self.refresh_sales_report)
        refresh_button.pack(pady=10)

        export_button = ttk.Button(sales_report_tab, text="Export Report", command=self.export_sales_report)
        export_button.pack(pady=10)

        self.refresh_sales_report()

    def refresh_sales_report(self):
        self.sales_tree.delete(*self.sales_tree.get_children())
        self.cursor.execute('''
        SELECT s.id, i.item_name, s.quantity, s.total_price, s.sale_date
        FROM sales s
        JOIN inventory i ON s.inventory_id = i.id
        ORDER BY s.sale_date DESC
        ''')
        for row in self.cursor.fetchall():
            self.sales_tree.insert("", "end", values=row)

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self.image_path = file_path

    def add_item(self):
        if not self.validate_inputs():
            return
        encrypted_price = self.encrypt_data(self.price_entry.get())
        try:
            self.cursor.execute('''
                INSERT INTO inventory (item_name, category, base_price, description)
                VALUES (?, ?, ?, ?)
            ''', (
                self.item_name_entry.get(), self.category_combobox.get(), encrypted_price,
                self.description_entry.get()))
            inventory_id = self.cursor.lastrowid
            self.cursor.execute('''
                INSERT INTO inventory_sizes (inventory_id, size, quantity)
                VALUES (?, ?, ?)
            ''', (inventory_id, self.size_entry.get(), self.quantity_entry.get()))
            if self.image_path:
                with open(self.image_path, "rb") as img_file:
                    image_blob = img_file.read()
                self.cursor.execute('''
                    INSERT INTO item_images (inventory_id, image_data)
                    VALUES (?, ?)
                ''', (inventory_id, image_blob))
            self.conn.commit()
            messagebox.showinfo("Success", "Item added successfully")
            self.refresh_inventory()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def load_item(self):
        item_id = self.update_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an item ID")
            return

        self.cursor.execute('''
        SELECT i.*, is.size, is.quantity
        FROM inventory i
        JOIN inventory_sizes is ON i.id = is.inventory_id
        WHERE i.id = ?
        ''', (item_id,))
        item_data = self.cursor.fetchone()

        if item_data:
            self.update_name_entry.delete(0, tk.END)
            self.update_name_entry.insert(0, item_data[1])
            self.update_category_entry.delete(0, tk.END)
            self.update_category_entry.insert(0, item_data[2])
            self.update_price_entry.delete(0, tk.END)
            self.update_price_entry.insert(0, self.decrypt_data(str(item_data[3])))
            self.update_size_entry.delete(0, tk.END)
            self.update_size_entry.insert(0, item_data[6])
            self.update_quantity_entry.delete(0, tk.END)
            self.update_quantity_entry.insert(0, item_data[7])
        else:
            messagebox.showerror("Error", "Item not found")

    def update_item(self):
        item_id = self.update_id_entry.get()
        name = self.update_name_entry.get()
        category = self.update_category_entry.get()
        price = self.update_price_entry.get()
        size = self.update_size_entry.get()
        quantity = self.update_quantity_entry.get()

        if not self.validate_input(name, category, price, size, quantity):
            return

        encrypted_price = self.encrypt_data(price)

        self.cursor.execute('''
        UPDATE inventory
        SET item_name = ?, category = ?, base_price = ?
        WHERE id = ?
        ''', (name, category, encrypted_price, item_id))

        self.cursor.execute('''
        UPDATE inventory_sizes
        SET size = ?, quantity = ?
        WHERE inventory_id = ?
        ''', (size, int(quantity), item_id))

        self.conn.commit()
        self.refresh_inventory()
        messagebox.showinfo("Success", "Item updated successfully")

    def delete_item(self):
        item_id = self.update_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an item ID")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            self.cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            self.cursor.execute("DELETE FROM inventory_sizes WHERE inventory_id = ?", (item_id,))
            self.cursor.execute("DELETE FROM item_images WHERE inventory_id = ?", (item_id,))
            self.conn.commit()
            self.refresh_inventory()
            messagebox.showinfo("Success", "Item deleted successfully")
            self.clear_update_delete_fields()

    def clear_add_item_fields(self):
        self.item_name_entry.delete(0, tk.END)
        self.category_combobox.set("Select a category")
        self.price_entry.delete(0, tk.END)
        self.size_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.image_path = None

    def clear_update_delete_fields(self):
        self.update_id_entry.delete(0, tk.END)
        self.update_name_entry.delete(0, tk.END)
        self.update_category_entry.delete(0, tk.END)
        self.update_price_entry.delete(0, tk.END)
        self.update_size_entry.delete(0, tk.END)
        self.update_quantity_entry.delete(0, tk.END)

    def on_item_double_click(self, event):
        item = self.inventory_tree.selection()[0]
        item_id = self.inventory_tree.item(item, "values")[0]
        self.show_item_details(item_id)

    def show_item_details(self, item_id):
        self.cursor.execute('''
        SELECT i.*, is.size, is.quantity, im.image_data
        FROM inventory i
        JOIN inventory_sizes is ON i.id = is.inventory_id
        LEFT JOIN item_images im ON i.id = im.inventory_id
        WHERE i.id = ?
        ''', (item_id,))
        item_data = self.cursor.fetchone()

        if item_data:
            details_window = tk.Toplevel(self.master)
            details_window.title(f"Item Details - {item_data[1]}")
            details_window.geometry("400x500")

            ttk.Label(details_window, text=f"Name: {item_data[1]}").pack(pady=5)
            ttk.Label(details_window, text=f"Category: {item_data[2]}").pack(pady=5)
            ttk.Label(details_window, text=f"Price: ${self.decrypt_data(str(item_data[3]))}").pack(pady=5)
            ttk.Label(details_window, text=f"Size: {item_data[6]}").pack(pady=5)
            ttk.Label(details_window, text=f"Quantity: {item_data[7]}").pack(pady=5)
            ttk.Label(details_window, text=f"Description: {item_data[4]}").pack(pady=5)

            if item_data[8]:
                image = Image.open(io.BytesIO(item_data[8]))
                image.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(image)
                image_label = ttk.Label(details_window, image=photo)
                image_label.image = photo
                image_label.pack(pady=10)

            ttk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)

    def validate_input(self, name, category, price, size, quantity):
        if not all([name, category, price, size, quantity]):
            messagebox.showerror("Error", "Please fill in all fields")
            return False

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity")
            return False

        if price <= 0 or quantity <= 0:
            messagebox.showerror("Error", "Price and quantity must be positive")
            return False

        return True

    def validate_inputs(self):
        if not self.item_name_entry.get():
            messagebox.showwarning("Validation Error", "Item Name is required")
            return False
        try:
            float(self.price_entry.get())
        except ValueError:
            messagebox.showwarning("Validation Error", "Price must be a number")
            return False
        try:
            int(self.quantity_entry.get())
        except ValueError:
            messagebox.showwarning("Validation Error", "Quantity must be an integer")
            return False
        return True

    def export_sales_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            self.cursor.execute('''
            SELECT s.id, i.item_name, s.quantity, s.total_price, s.sale_date
            FROM sales s
            JOIN inventory i ON s.inventory_id = i.id
            ORDER BY s.sale_date DESC
            ''')
            sales_data = self.cursor.fetchall()

            with open(file_path, 'w') as f:
                f.write("Sales Report\n\n")
                f.write(f"{'ID':<5}{'Item':<20}{'Quantity':<10}{'Total Price':<15}{'Date':<20}\n")
                f.write("-" * 70 + "\n")
                for sale in sales_data:
                    f.write(f"{sale[0]:<5}{sale[1]:<20}{sale[2]:<10}${sale[3]:<14.2f}{sale[4]:<20}\n")

            messagebox.showinfo("Success", f"Sales report exported to {file_path}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def create_customers_tab(self):
        customers_tab = ttk.Frame(self.notebook)
        self.notebook.add(customers_tab, text="Customers")

        # Search frame
        search_frame = ttk.Frame(customers_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.customer_search_entry = ttk.Entry(search_frame)
        self.customer_search_entry.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_customers).pack(side="left", padx=5)

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
        button_frame = ttk.Frame(customers_tab)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Add Customer", command=self.add_customer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_customers).pack(side="left", padx=5)

        self.refresh_customers()

    def add_customer(self):
        add_customer_window = tk.Toplevel(self.master)
        add_customer_window.title("Add Customer")
        add_customer_window.geometry("400x300")

        ttk.Label(add_customer_window, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = ttk.Entry(add_customer_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_customer_window, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        email_entry = ttk.Entry(add_customer_window)
        email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_customer_window, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        phone_entry = ttk.Entry(add_customer_window)
        phone_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_customer():
            name = name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()

            if name and email:
                try:
                    self.cursor.execute('''
                    INSERT INTO customers (name, email, phone)
                    VALUES (?, ?, ?)
                    ''', (name, email, phone))
                    self.conn.commit()
                    self.refresh_customers()
                    messagebox.showinfo("Success", "Customer added successfully")
                    add_customer_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
            else:
                messagebox.showwarning("Validation Error", "Name and Email are required fields")

        ttk.Button(add_customer_window, text="Save", command=save_customer).grid(row=3, column=0, columnspan=2, pady=20)

    def search_customers(self):
        search_term = self.customer_search_entry.get()
        try:
            self.customers_tree.delete(*self.customers_tree.get_children())
            self.cursor.execute('''
            SELECT id, name, email, phone FROM customers
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            for row in self.cursor.fetchall():
                self.customers_tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search customers: {str(e)}")

    def search_inventory(self):
        search_term = self.inventory_search_entry.get()
        try:
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            self.cursor.execute('''
            SELECT i.id, i.item_name, COALESCE(i.category, 'N/A') as category, i.base_price,
                   COALESCE(inv_sizes.size, 'N/A') as size, COALESCE(inv_sizes.quantity, 0) as quantity
            FROM inventory i
            LEFT JOIN inventory_sizes inv_sizes ON i.id = inv_sizes.inventory_id
            WHERE i.item_name LIKE ? OR i.category LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%'))
            for row in self.cursor.fetchall():
                try:
                    decrypted_price = self.decrypt_data(str(row[3]))
                except:
                    decrypted_price = "N/A"
                self.inventory_tree.insert("", "end", values=(
                    row[0], row[1], row[2], f"${decrypted_price}" if decrypted_price != "N/A" else "N/A", row[4],
                    row[5]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search inventory: {str(e)}")
            print(f"Error details: {str(e)}")

    def refresh_customers(self):
        try:
            self.customers_tree.delete(*self.customers_tree.get_children())
            self.cursor.execute('SELECT id, name, email, phone FROM customers')
            for row in self.cursor.fetchall():
                self.customers_tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh customers: {str(e)}")
            print(f"Error details: {str(e)}")

    def update_inventory_sizes(self):
        try:
            self.cursor.execute('''
                SELECT id, size, quantity FROM inventory_sizes
            ''')
            rows = self.cursor.fetchall()
            for row in rows:
                if not row[1] or not row[2]:
                    self.cursor.execute('''
                        DELETE FROM inventory_sizes WHERE id = ?
                    ''', (row[0],))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update inventory sizes: {str(e)}")
            print(f"Error details: {str(e)}")

    def create_employees_tab(self):
        employees_tab = ttk.Frame(self.notebook)
        self.notebook.add(employees_tab, text="Employees")

        # Search frame
        search_frame = ttk.Frame(employees_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.employee_search_entry = ttk.Entry(search_frame)
        self.employee_search_entry.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_employees).pack(side="left", padx=5)

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
        button_frame = ttk.Frame(employees_tab)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_employees).pack(side="left", padx=5)

        self.refresh_employees()

    def add_employee(self):
        name = simpledialog.askstring("Add Employee", "Enter employee name:")
        if name:
            position = simpledialog.askstring("Add Employee", "Enter employee position:")
            hire_date = simpledialog.askstring("Add Employee", "Enter hire date (YYYY-MM-DD):")
            salary = simpledialog.askfloat("Add Employee", "Enter employee salary:")

            try:
                self.cursor.execute('''
                INSERT INTO employees (name, position, hire_date, salary)
                VALUES (?, ?, ?, ?)
                ''', (name, position, hire_date, salary))
                self.conn.commit()
                self.refresh_employees()
                messagebox.showinfo("Success", "Employee added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add employee: {str(e)}")

    def refresh_employees(self):
        try:
            self.employees_tree.delete(*self.employees_tree.get_children())
            self.cursor.execute('SELECT id, name, position, hire_date, salary FROM employees')
            for row in self.cursor.fetchall():
                self.employees_tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh employees: {str(e)}")

    def search_employees(self):
        search_term = self.employee_search_entry.get()
        try:
            self.employees_tree.delete(*self.employees_tree.get_children())
            self.cursor.execute('''
            SELECT id, name, position, hire_date, salary FROM employees
            WHERE name LIKE ? OR position LIKE ? OR hire_date LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            for row in self.cursor.fetchall():
                self.employees_tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search employees: {str(e)}")


def cleanup():
    # This function will be called when the program exits
    if hasattr(ClothingStoreDB, 'conn') and ClothingStoreDB.conn:
        ClothingStoreDB.conn.close()


atexit.register(cleanup)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingStoreDB(root)
    root.mainloop()

