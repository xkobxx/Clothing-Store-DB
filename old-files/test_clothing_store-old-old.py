import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
import unittest
from datetime import datetime


class TestClothingStoreDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test database
        cls.test_db_path = "../test_clothing_store.db"
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        self.root = tk.Tk()
        from clothing_store_db import ClothingStoreDB
        self.app = ClothingStoreDB(self.root)
        self.app.db_path = self.test_db_path

    def tearDown(self):
        self.root.destroy()
        if hasattr(self, 'app'):
            del self.app

    def test_database_connection(self):
        """Test database connection and cleanup"""
        try:
            # Verify connection is active
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1, "Database connection should be active")

            # Test connection cleanup
            del self.app
            with self.assertRaises(sqlite3.ProgrammingError):
                cursor.execute("SELECT 1")
        except Exception as e:
            self.fail(f"Database connection test failed: {str(e)}")

    def test_restock_query(self):
        """Test the fixed restock query"""
        try:
            # Add test inventory items
            cursor = self.app.conn.cursor()

            # Add test category
            cursor.execute("INSERT INTO categories (name) VALUES (?)", ("Test Category",))
            category_id = cursor.lastrowid

            # Add test supplier
            cursor.execute("INSERT INTO suppliers (name) VALUES (?)", ("Test Supplier",))
            supplier_id = cursor.lastrowid

            # Add test inventory item with low quantity
            cursor.execute("""
                INSERT INTO inventory (item_name, category_id, supplier_id, base_price) 
                VALUES (?, ?, ?, ?)""",
                           ("Test Item", category_id, supplier_id, 10.0))
            inventory_id = cursor.lastrowid

            # Add size
            cursor.execute("INSERT INTO sizes (size_name) VALUES (?)", ("M",))
            size_id = cursor.lastrowid

            # Add inventory size with low quantity
            cursor.execute("""
                INSERT INTO inventory_sizes (inventory_id, size_id, quantity) 
                VALUES (?, ?, ?)""",
                           (inventory_id, size_id, 10))

            self.app.conn.commit()

            # Test restock query
            self.app.populate_restock_needed()

            # Verify item appears in restock tree
            items = self.app.restock_tree.get_children()
            self.assertTrue(len(items) > 0, "Restock tree should contain items")

        except Exception as e:
            self.fail(f"Restock query test failed: {str(e)}")

    def test_add_customer(self):
        """Test customer addition with error handling"""
        try:
            # Test valid customer
            self.app.customer_name.insert(0, "Test Customer")
            self.app.customer_email.insert(0, "test@example.com")
            self.app.customer_phone.insert(0, "1234567890")

            self.app.add_customer()

            # Verify customer was added
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE email = ?", ("test@example.com",))
            customer = cursor.fetchone()
            self.assertIsNotNone(customer, "Customer should be added to database")

            # Test duplicate email
            self.app.customer_name.insert(0, "Test Customer 2")
            self.app.customer_email.insert(0, "test@example.com")
            self.app.customer_phone.insert(0, "0987654321")

            self.app.add_customer()

            # Verify duplicate was not added
            cursor.execute("SELECT COUNT(*) FROM customers WHERE email = ?", ("test@example.com",))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1, "Duplicate email should not be added")

        except Exception as e:
            self.fail(f"Add customer test failed: {str(e)}")

    def test_add_inventory(self):
        """Test inventory addition with validation"""
        try:
            # Test valid inventory item
            self.app.item_name.insert(0, "Test Item")
            self.app.item_category.insert(0, "1")  # Assuming category ID 1 exists
            self.app.item_size.insert(0, "1")  # Assuming size ID 1 exists
            self.app.item_price.insert(0, "29.99")
            self.app.item_quantity.insert(0, "100")

            self.app.add_inventory_item()

            # Verify item was added
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE item_name = ?", ("Test Item",))
            item = cursor.fetchone()
            self.assertIsNotNone(item, "Inventory item should be added to database")

            # Test invalid price
            self.app.item_name.insert(0, "Test Item 2")
            self.app.item_price.insert(0, "invalid")

            self.app.add_inventory_item()

            # Verify invalid item was not added
            cursor.execute("SELECT COUNT(*) FROM inventory WHERE item_name = ?", ("Test Item 2",))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 0, "Invalid item should not be added")

        except Exception as e:
            self.fail(f"Add inventory test failed: {str(e)}")


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClothingStoreDB)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run_tests()