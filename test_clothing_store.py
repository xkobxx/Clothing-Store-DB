import os
import sqlite3
import tkinter as tk
import unittest
from tkinter import ttk

from clothing_store_db import ClothingStoreDB
from inventory_utils import check_and_reorder_inventory, get_reorder_history, analyze_reorder_patterns
from triggers import create_triggers, create_audit_triggers


class TestDatabaseOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "test_clothing_store.db"
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        cls.conn = sqlite3.connect(cls.test_db_path)
        create_triggers(cls.conn)
        create_audit_triggers(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        self.cursor = self.conn.cursor()
        self.setup_test_data()

    def tearDown(self):
        self.cursor.execute("DELETE FROM customers")
        self.cursor.execute("DELETE FROM inventory")
        self.cursor.execute("DELETE FROM categories")
        self.cursor.execute("DELETE FROM suppliers")
        self.cursor.execute("DELETE FROM sizes")
        self.cursor.execute("DELETE FROM inventory_sizes")
        self.cursor.execute("DELETE FROM orders")
        self.cursor.execute("DELETE FROM order_items")
        self.cursor.execute("DELETE FROM reorder_log")
        self.conn.commit()

    def setup_test_data(self):
        """Set up test data in the database"""
        # Insert test category
        self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                            ("Test Category", "Test Description"))
        self.category_id = self.cursor.lastrowid

        # Insert test supplier
        self.cursor.execute("""
            INSERT INTO suppliers (name, contact_person, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, ("Test Supplier", "John Doe", "supplier@test.com", "1234567890", "123 Test St"))
        self.supplier_id = self.cursor.lastrowid

        # Insert test size
        self.cursor.execute("INSERT INTO sizes (size_name) VALUES (?)", ("M",))
        self.size_id = self.cursor.lastrowid

        # Insert test inventory item
        self.cursor.execute("""
            INSERT INTO inventory (item_name, category_id, supplier_id, base_price, description)
            VALUES (?, ?, ?, ?, ?)
        """, ("Test Item", self.category_id, self.supplier_id, 29.99, "Test Description"))
        self.inventory_id = self.cursor.lastrowid

        # Insert test inventory size
        self.cursor.execute("""
            INSERT INTO inventory_sizes (inventory_id, size_id, quantity)
            VALUES (?, ?, ?)
        """, (self.inventory_id, self.size_id, 100))

        self.conn.commit()

    def test_inventory_utils(self):
        """Test inventory utility functions"""
        # Test check_and_reorder_inventory
        self.cursor.execute("""
            UPDATE inventory_sizes 
            SET quantity = 10 
            WHERE inventory_id = ? AND size_id = ?
        """, (self.inventory_id, self.size_id))
        self.conn.commit()

        reordered_items = check_and_reorder_inventory(self.test_db_path, threshold=15)
        self.assertTrue(len(reordered_items) > 0)

        # Test get_reorder_history
        history = get_reorder_history(self.test_db_path, days=30)
        self.assertTrue(len(history) > 0)

        # Test analyze_reorder_patterns
        patterns = analyze_reorder_patterns(self.test_db_path)
        self.assertIsInstance(patterns, list)

    def test_triggers(self):
        """Test database triggers"""
        # Test inventory update trigger
        initial_quantity = 100
        update_quantity = 90

        self.cursor.execute("""
            UPDATE inventory_sizes 
            SET quantity = ? 
            WHERE inventory_id = ? AND size_id = ?
        """, (update_quantity, self.inventory_id, self.size_id))
        self.conn.commit()

        # Check inventory log
        self.cursor.execute("SELECT COUNT(*) FROM inventory_log")
        log_count = self.cursor.fetchone()[0]
        self.assertTrue(log_count > 0)

        # Test negative quantity prevention
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                UPDATE inventory_sizes 
                SET quantity = -10 
                WHERE inventory_id = ? AND size_id = ?
            """, (self.inventory_id, self.size_id))

    def test_order_processing(self):
        """Test order processing functionality"""
        # Create test customer
        self.cursor.execute("""
            INSERT INTO customers (name, email, phone, address)
            VALUES (?, ?, ?, ?)
        """, ("Test Customer", "test@example.com", "1234567890", "123 Test St"))
        customer_id = self.cursor.lastrowid

        # Create test employee
        self.cursor.execute("""
            INSERT INTO employees (name, position, hire_date, salary)
            VALUES (?, ?, ?, ?)
        """, ("Test Employee", "Sales", "2024-01-01", 50000))
        employee_id = self.cursor.lastrowid

        # Create order
        self.cursor.execute("""
            INSERT INTO orders (customer_id, employee_id, total_amount, status)
            VALUES (?, ?, ?, ?)
        """, (customer_id, employee_id, 0, "Pending"))
        order_id = self.cursor.lastrowid

        # Add order items
        self.cursor.execute("""
            INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, self.inventory_id, 2, 29.99, 59.98))

        self.conn.commit()

        # Verify order total update trigger
        self.cursor.execute("SELECT total_amount FROM orders WHERE id = ?", (order_id,))
        total_amount = self.cursor.fetchone()[0]
        self.assertEqual(float(total_amount), 59.98)

        # Verify inventory quantity update
        self.cursor.execute("""
            SELECT quantity 
            FROM inventory_sizes 
            WHERE inventory_id = ? AND size_id = ?
        """, (self.inventory_id, self.size_id))
        updated_quantity = self.cursor.fetchone()[0]
        self.assertEqual(updated_quantity, 98)  # 100 - 2


class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the main window

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.app = ClothingStoreDB(self.root)

    def tearDown(self):
        if hasattr(self, 'app'):
            del self.app

    def test_widget_creation(self):
        """Test UI widget creation"""
        # Test main window properties
        self.assertEqual(self.app.master.title(), "Clothing Store Database")

        # Test notebook tabs
        self.assertTrue(isinstance(self.app.notebook, ttk.Notebook))
        self.assertEqual(self.app.notebook.index("end"), 7)  # Check number of tabs

        # Test customer widgets
        self.assertTrue(hasattr(self.app, 'customer_name'))
        self.assertTrue(hasattr(self.app, 'customer_email'))
        self.assertTrue(hasattr(self.app, 'customer_phone'))
        self.assertTrue(hasattr(self.app, 'customer_tree'))

        # Test inventory widgets
        self.assertTrue(hasattr(self.app, 'item_name'))
        self.assertTrue(hasattr(self.app, 'item_price'))
        self.assertTrue(hasattr(self.app, 'item_quantity'))
        self.assertTrue(hasattr(self.app, 'inventory_tree'))

    def test_customer_operations(self):
        """Test customer-related UI operations"""
        # Test customer addition
        self.app.customer_name.insert(0, "UI Test Customer")
        self.app.customer_email.insert(0, "uitest@example.com")
        self.app.customer_phone.insert(0, "1234567890")
        self.app.add_customer()

        # Verify customer was added to treeview
        items = self.app.customer_tree.get_children()
        self.assertTrue(len(items) > 0)

        # Test clear fields
        self.app.clear_fields()
        self.assertEqual(self.app.customer_name.get(), "")
        self.assertEqual(self.app.customer_email.get(), "")
        self.assertEqual(self.app.customer_phone.get(), "")

    def test_inventory_operations(self):
        """Test inventory-related UI operations"""
        # Test inventory addition
        self.app.item_name.insert(0, "UI Test Item")
        self.app.category_combo.set("Test Category")
        self.app.size_combo.set("M")
        self.app.item_price.insert(0, "29.99")
        self.app.item_quantity.insert(0, "100")
        self.app.add_inventory_item()

        # Verify inventory was added to treeview
        items = self.app.inventory_tree.get_children()
        self.assertTrue(len(items) > 0)


def run_tests():
    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseOperations))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUIComponents))

    # Run tests
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run_tests()