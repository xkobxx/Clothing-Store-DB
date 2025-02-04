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


def test_order_items():
    try:
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

        # Update the before_order_item_insert trigger
        run_query('''
        DROP TRIGGER IF EXISTS before_order_item_insert;

        CREATE TRIGGER before_order_item_insert
        BEFORE INSERT ON order_items
        BEGIN
            SELECT CASE
                WHEN (SELECT SUM(quantity) FROM inventory_sizes WHERE inventory_id = NEW.inventory_id) < NEW.quantity
                THEN RAISE(ABORT, 'Insufficient inventory')
            END;

            UPDATE inventory_sizes
            SET quantity = quantity - NEW.quantity
            WHERE inventory_id = NEW.inventory_id
            AND size = (
                SELECT size FROM inventory_sizes 
                WHERE inventory_id = NEW.inventory_id 
                ORDER BY quantity DESC 
                LIMIT 1
            );

            INSERT INTO low_stock_alerts (inventory_id, current_quantity)
            SELECT inventory_id, SUM(quantity) as total_quantity
            FROM inventory_sizes
            WHERE inventory_id = NEW.inventory_id
            GROUP BY inventory_id
            HAVING total_quantity <= 10;
        END;
        ''')

        # Test order_items insertion
        print("\nTesting order_items insertion:")

        # Check current inventory
        print("\nCurrent inventory:")
        run_query("SELECT * FROM inventory_sizes WHERE inventory_id = 1")
        current_quantity = run_query("SELECT SUM(quantity) FROM inventory_sizes WHERE inventory_id = 1")[0][0]

        # Create a test order
        run_query(
            "INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
            (1, 1, datetime.datetime.now(), 1000, 'Processing'))
        order_id = run_query("SELECT last_insert_rowid() as id")[0][0]

        # Try to add an order item with more quantity than available
        print("\nAttempting to add order item with more quantity than available:")
        try:
            run_query(
                "INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                (order_id, 1, current_quantity + 1, 100, (current_quantity + 1) * 100))
        except sqlite3.Error as e:
            print(f"Expected error occurred: {e}")

        # Check inventory after failed insertion (should be unchanged)
        print("\nInventory after failed insertion:")
        run_query("SELECT * FROM inventory_sizes WHERE inventory_id = 1")

        # Try to add an order item with available quantity
        print("\nAttempting to add order item with available quantity:")
        run_query(
            "INSERT INTO order_items (order_id, inventory_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
            (order_id, 1, current_quantity, 100, current_quantity * 100))

        # Check updated inventory
        print("\nUpdated inventory:")
        run_query("SELECT * FROM inventory_sizes WHERE inventory_id = 1")

        # Check low_stock_alerts
        print("\nChecking low_stock_alerts:")
        run_query("SELECT * FROM low_stock_alerts WHERE inventory_id = 1")

    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    test_order_items()

