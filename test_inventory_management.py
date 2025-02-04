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


def test_inventory_management():
    try:
        # Create failed_sales table
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

        # Drop existing trigger
        run_query('DROP TRIGGER IF EXISTS after_sale_update_inventory')

        # Create new trigger
        run_query('''
        CREATE TRIGGER after_sale_update_inventory
        INSTEAD OF INSERT ON sales
        BEGIN
            SELECT CASE
                WHEN (SELECT quantity FROM inventory_sizes WHERE inventory_id = NEW.item_id ORDER BY quantity DESC LIMIT 1) >= NEW.quantity
                THEN
                    (UPDATE inventory_sizes
                    SET quantity = quantity - NEW.quantity
                    WHERE inventory_id = NEW.item_id AND size = (
                        SELECT size FROM inventory_sizes 
                        WHERE inventory_id = NEW.item_id 
                        ORDER BY quantity DESC 
                        LIMIT 1
                    ))
            END;

            SELECT CASE
                WHEN (SELECT quantity FROM inventory_sizes WHERE inventory_id = NEW.item_id ORDER BY quantity DESC LIMIT 1) >= NEW.quantity
                THEN
                    (INSERT INTO sales (item_id, quantity, total_price, date)
                    VALUES (NEW.item_id, NEW.quantity, NEW.total_price, NEW.date))
            END;

            INSERT INTO low_stock_alerts (inventory_id, current_quantity)
            SELECT inventory_id, SUM(quantity) as total_quantity
            FROM inventory_sizes
            WHERE inventory_id = NEW.item_id
            GROUP BY inventory_id
            HAVING total_quantity <= 10;

            INSERT INTO failed_sales (item_id, attempted_quantity, available_quantity)
            SELECT NEW.item_id, NEW.quantity, quantity
            FROM inventory_sizes
            WHERE inventory_id = NEW.item_id
            ORDER BY quantity DESC
            LIMIT 1
            WHEN quantity < NEW.quantity;
        END
        ''')

        # Test inventory management
        print("\nTesting inventory management:")
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

    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    test_inventory_management()

