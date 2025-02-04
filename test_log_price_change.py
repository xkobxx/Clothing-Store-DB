import sqlite3
import datetime

# Connect to the database
conn = sqlite3.connect('clothing_store.db')
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


def test_log_price_change_trigger():
    try:
        # 1. Get an item from the inventory
        item = run_query("SELECT id, item_name, base_price FROM inventory LIMIT 1")
        if not item:
            print("No items in inventory. Please add items before testing.")
            return

        item_id, item_name, old_price = item[0]
        print(f"Testing with item: {item_name} (ID: {item_id}), Current price: {old_price}")

        # 2. Update the price
        new_price = float(old_price) + 10.00  # Increase price by $10
        run_query("UPDATE inventory SET base_price = ? WHERE id = ?", (new_price, item_id))

        # 3. Check if the price was updated
        updated_item = run_query("SELECT base_price FROM inventory WHERE id = ?", (item_id,))
        if updated_item[0][0] != new_price:
            print("Price was not updated correctly.")
            return

        # 4. Check the price_change_log
        log_entry = run_query("""
            SELECT inventory_id, old_price, new_price 
            FROM price_change_log 
            WHERE inventory_id = ? 
            ORDER BY change_date DESC 
            LIMIT 1
        """, (item_id,))

        if log_entry:
            logged_item_id, logged_old_price, logged_new_price = log_entry[0]
            print(f"Log entry found:")
            print(f"Item ID: {logged_item_id}")
            print(f"Old price: {logged_old_price}")
            print(f"New price: {logged_new_price}")

            if logged_item_id == item_id and logged_old_price == old_price and logged_new_price == new_price:
                print("Test passed: Price change was logged correctly.")
            else:
                print("Test failed: Log entry does not match the price change.")
        else:
            print("Test failed: No log entry was created.")

    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    test_log_price_change_trigger()