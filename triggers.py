import sqlite3
import datetime

# Connect to the database
conn = sqlite3.connect('clothing_store.db')

# Use the recommended approach for datetime adaptation
conn.execute('PRAGMA foreign_keys = ON')
conn.execute('PRAGMA journal_mode = WAL')
conn.execute('PRAGMA synchronous = NORMAL')
conn.execute('PRAGMA temp_store = MEMORY')


def adapt_datetime(val):
    return val.isoformat()


sqlite3.register_adapter(datetime.datetime, adapt_datetime)

cursor = conn.cursor()


def run_query(query, params=None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        print(f"Executed query: {query}")
        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            print("Results:", results)
            return results
    except sqlite3.Error as e:
        print(f"An error occurred executing query: {query}")
        print(f"Error details: {e}")
        conn.rollback()


def test_triggers():
    try:
        # Create failed_sales table if it doesn't exist
        run_query('''
        CREATE TABLE IF NOT EXISTS failed_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            attempted_quantity INTEGER NOT NULL,
            available_quantity INTEGER NOT NULL,
            sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES inventory(id)
        )
        ''')

        # Create low_stock_alerts table if it doesn't exist
        run_query('''
        CREATE TABLE IF NOT EXISTS low_stock_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER NOT NULL,
            current_quantity INTEGER NOT NULL,
            alert_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inventory_id) REFERENCES inventory(id)
        )
        ''')

        # Update the after_sale_update_inventory trigger
        run_query('''
        DROP TRIGGER IF EXISTS after_sale_update_inventory;

        CREATE TRIGGER after_sale_update_inventory
        AFTER INSERT ON sales
        BEGIN
            UPDATE inventory_sizes
            SET quantity = CASE
                WHEN quantity >= NEW.quantity THEN quantity - NEW.quantity
                ELSE quantity
            END
            WHERE inventory_id = NEW.item_id AND size = (
                SELECT size FROM inventory_sizes 
                WHERE inventory_id = NEW.item_id 
                ORDER BY quantity DESC 
                LIMIT 1
            );

            INSERT INTO failed_sales (item_id, attempted_quantity, available_quantity, sale_date)
            SELECT NEW.item_id, NEW.quantity, quantity, NEW.date
            FROM inventory_sizes
            WHERE inventory_id = NEW.item_id
            AND quantity < NEW.quantity
            ORDER BY quantity DESC
            LIMIT 1;

            INSERT INTO low_stock_alerts (inventory_id, current_quantity)
            SELECT inventory_id, SUM(quantity) as total_quantity
            FROM inventory_sizes
            WHERE inventory_id = NEW.item_id
            GROUP BY inventory_id
            HAVING total_quantity <= 10;
        END;
        ''')

        # Test after_sale_update_inventory trigger
        print("\nTesting after_sale_update_inventory trigger:")
        run_query("SELECT * FROM inventory_sizes WHERE inventory_id = 1")
        current_quantity = \
        run_query("SELECT quantity FROM inventory_sizes WHERE inventory_id = 1 ORDER BY quantity DESC LIMIT 1")[0][0]

        # Try to sell more than available
        print("\nAttempting to sell more than available:")
        run_query("INSERT INTO sales (item_id, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                  (1, current_quantity + 1, 39.98, datetime.datetime.now()))

        # Check failed_sales table
        print("\nChecking failed_sales table:")
        run_query("SELECT * FROM failed_sales")

        # Try to sell available quantity
        print("\nAttempting to sell available quantity:")
        run_query("INSERT INTO sales (item_id, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                  (1, current_quantity, 39.98, datetime.datetime.now()))

        # Check updated inventory and sales
        print("\nChecking updated inventory:")
        run_query("SELECT * FROM inventory_sizes WHERE inventory_id = 1")
        print("\nChecking sales table:")
        run_query("SELECT * FROM sales WHERE item_id = 1 ORDER BY id DESC LIMIT 1")
        print("\nChecking low_stock_alerts:")
        run_query("SELECT * FROM low_stock_alerts WHERE inventory_id = 1")

        # Test log_price_change trigger
        print("\nTesting log_price_change trigger:")
        run_query("UPDATE inventory SET base_price = ? WHERE id = ?", (24.99, 1))
        run_query("SELECT * FROM price_change_log WHERE inventory_id = 1")

        # Test update_order_status trigger
        print("\nTesting update_order_status trigger:")
        run_query(
            "INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
            (1, 1, datetime.datetime.now(), 1000, 'Processing'))
        order_id = run_query("SELECT last_insert_rowid() as id")[0][0]
        run_query(
            "INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
            (order_id, 1, 10, 100, 1000))
        run_query(
            "INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
            (order_id, 2, 5, 100, 500))
        run_query(f"SELECT * FROM orders WHERE id = {order_id}")

        # Simulate the delivery by updating the order status directly
        run_query("UPDATE orders SET status = 'Delivered' WHERE id = ?", (order_id,))
        run_query(f"SELECT * FROM orders WHERE id = {order_id}")

    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    test_triggers()

