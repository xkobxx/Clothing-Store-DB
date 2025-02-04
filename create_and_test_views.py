import sqlite3
import os

# Database file path
db_path = 'clothing_store.db'

# SQL to create views
create_views_sql = """
-- View 1: Sales Performance Analysis
CREATE VIEW IF NOT EXISTS sales_performance_analysis AS
WITH sales_data AS (
    SELECT 
        s.id AS sale_id,
        i.id AS item_id,
        i.item_name,
        c.category_name,
        s.quantity,
        s.total_price,
        strftime('%Y-%m', s.date) AS sale_month
    FROM 
        sales s
    JOIN 
        inventory i ON s.item_id = i.id
    JOIN 
        categories c ON i.category_id = c.id
)
SELECT 
    sale_month,
    category_name,
    COUNT(DISTINCT sale_id) AS total_sales,
    SUM(quantity) AS total_quantity_sold,
    ROUND(SUM(total_price), 2) AS total_revenue,
    ROUND(AVG(total_price), 2) AS avg_sale_value
FROM 
    sales_data
GROUP BY 
    sale_month, category_name
HAVING 
    total_sales >= 5
ORDER BY 
    sale_month DESC, total_revenue DESC;

-- View 2: Inventory Reorder Recommendations
CREATE VIEW IF NOT EXISTS inventory_reorder_recommendations AS
WITH inventory_status AS (
    SELECT 
        i.id AS item_id,
        i.item_name,
        c.category_name,
        SUM(inv_sizes.quantity) AS current_stock,
        AVG(s.quantity) AS avg_daily_sales
    FROM 
        inventory i
    JOIN 
        categories c ON i.category_id = c.id
    LEFT JOIN 
        inventory_sizes inv_sizes ON i.id = inv_sizes.inventory_id
    LEFT JOIN 
        sales s ON i.id = s.item_id
    GROUP BY 
        i.id
)
SELECT 
    item_id,
    item_name,
    category_name,
    current_stock,
    ROUND(avg_daily_sales, 2) AS avg_daily_sales,
    ROUND(current_stock / CASE WHEN avg_daily_sales > 0 THEN avg_daily_sales ELSE 1 END) AS days_until_stockout,
    CASE 
        WHEN current_stock / CASE WHEN avg_daily_sales > 0 THEN avg_daily_sales ELSE 1 END <= 7 THEN 'Urgent Reorder'
        WHEN current_stock / CASE WHEN avg_daily_sales > 0 THEN avg_daily_sales ELSE 1 END <= 14 THEN 'Reorder Soon'
        ELSE 'Stock Sufficient'
    END AS reorder_status
FROM 
    inventory_status
WHERE 
    avg_daily_sales > 0 OR current_stock < 10
ORDER BY 
    days_until_stockout ASC;
"""


def execute_query(conn, query):
    """Execute a query and fetch all results."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


def main():
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return

    # Connect to the database
    conn = sqlite3.connect(db_path)

    try:
        # Create views
        conn.executescript(create_views_sql)
        print("Views created successfully.")

        # Verify that views have been created
        views = execute_query(conn, "SELECT name FROM sqlite_master WHERE type='view';")
        if views:
            print("Existing views:")
            for view in views:
                print(f"- {view[0]}")
        else:
            print("No views found in the database.")

        # Query the sales_performance_analysis view
        print("\nSample data from sales_performance_analysis:")
        sales_data = execute_query(conn, "SELECT * FROM sales_performance_analysis LIMIT 5;")
        if sales_data:
            for row in sales_data:
                print(row)
        else:
            print("No data found in sales_performance_analysis view.")

        # Query the inventory_reorder_recommendations view
        print("\nSample data from inventory_reorder_recommendations:")
        inventory_data = execute_query(conn, "SELECT * FROM inventory_reorder_recommendations LIMIT 5;")
        if inventory_data:
            for row in inventory_data:
                print(row)
        else:
            print("No data found in inventory_reorder_recommendations view.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

