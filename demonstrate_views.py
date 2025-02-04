import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from PIL import ImageGrab

def capture_screenshot(filename):
    screenshot = ImageGrab.grab()
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")

def execute_query(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

def plot_data(data, title, filename):
    df = pd.DataFrame(data)
    df.plot(kind='bar')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Plot saved as {filename}")

def demonstrate_views():
    conn = sqlite3.connect('clothing_store.db')
    cursor = conn.cursor()

    # Demonstrate sales_summary view
    print("Sales Summary:")
    sales_data = execute_query(cursor, "SELECT * FROM sales_summary")
    print(pd.DataFrame(sales_data, columns=['Category', 'Quantity Sold', 'Total Revenue', 'Average Price']))
    plot_data(sales_data, 'Sales Summary by Category', 'sales_summary.png')
    capture_screenshot('sales_summary_screenshot.png')

    # Demonstrate inventory_status view
    print("\nInventory Status:")
    inventory_data = execute_query(cursor, "SELECT * FROM inventory_status")
    print(pd.DataFrame(inventory_data, columns=['ID', 'Item Name', 'Category', 'Total Quantity', 'Size Count', 'Base Price']))
    plot_data(inventory_data, 'Inventory Status', 'inventory_status.png')
    capture_screenshot('inventory_status_screenshot.png')

    # Demonstrate top_customers view
    print("\nTop Customers:")
    customer_data = execute_query(cursor, "SELECT * FROM top_customers")
    print(pd.DataFrame(customer_data, columns=['ID', 'Name', 'Total Purchases', 'Total Spent']))
    plot_data(customer_data, 'Top Customers', 'top_customers.png')
    capture_screenshot('top_customers_screenshot.png')

    conn.close()

if __name__ == "__main__":
    demonstrate_views()

