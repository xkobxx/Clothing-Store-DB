import sqlite3
import os
from PIL import ImageGrab
import time

# Connect to the database
conn = sqlite3.connect('clothing_store.db')
cursor = conn.cursor()

def execute_query(query):
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def print_results(results):
    for row in results:
        print(row)
    print("\n")

def capture_screenshot(filename):
    time.sleep(1)  # Wait for terminal to update
    screenshot = ImageGrab.grab()
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")

def demonstrate_virtual_tables():
    # Create virtual tables
    with open('create_virtual_tables.sql', 'r') as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)
    conn.commit()

    # Demonstrate inventory_status view
    print("Inventory Status:")
    results = execute_query("SELECT * FROM inventory_status LIMIT 5")
    print_results(results)
    capture_screenshot("inventory_status.png")

    # Demonstrate sales_summary view
    print("Sales Summary:")
    results = execute_query("SELECT * FROM sales_summary LIMIT 5")
    print_results(results)
    capture_screenshot("sales_summary.png")

    # Demonstrate top_selling_items view
    print("Top Selling Items:")
    results = execute_query("SELECT * FROM top_selling_items LIMIT 5")
    print_results(results)
    capture_screenshot("top_selling_items.png")

if __name__ == "__main__":
    demonstrate_virtual_tables()
    conn.close()

