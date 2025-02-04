import sqlite3
import os

# Database file path
db_path = 'clothing_store.db'


def execute_query(conn, query):
    """Execute a query and fetch all results."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


def get_table_info(conn, table_name):
    """Get column information for a given table."""
    return execute_query(conn, f"PRAGMA table_info({table_name})")


def main():
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return

    conn = sqlite3.connect(db_path)

    try:
        # Check existing tables
        tables = execute_query(conn, "SELECT name FROM sqlite_master WHERE type='table';")
        print("Existing tables:")
        for table in tables:
            print(f"- {table[0]}")
            columns = get_table_info(conn, table[0])
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")

        # Check if categories table exists and has the right column
        categories_info = get_table_info(conn, 'categories')
        if not categories_info:
            print("\nCategories table not found. Creating it...")
            conn.execute('''
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')
            print("Categories table created.")
        else:
            category_name_column = next((col for col in categories_info if col[1] == 'name'), None)
            if not category_name_column:
                print("\nAdding 'name' column to categories table...")
                conn.execute('ALTER TABLE categories ADD COLUMN name TEXT')
                print("Column 'name' added to categories table.")

        # Update views
        update_views_sql = """
        -- View 1: Sales Performance Analysis
        DROP VIEW IF EXISTS sales_performance_analysis;
        CREATE VIEW sales_performance_analysis AS
        WITH sales_data AS (
            SELECT 
                s.id AS sale_id,
                i.id AS item_id,
                i.item_name,
                c.name AS category_name,
                s.quantity,
                s.total_price,
                strftime('%Y-%m', s.date) AS sale_month
            FROM 
                sales s
            JOIN 
                inventory i ON s.item_id = i.id
            LEFT JOIN 
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
            total_sales >= 1
        ORDER BY 
            sale_month DESC, total_revenue DESC;

        -- View 2: Inventory Reorder Recommendations
        DROP VIEW IF EXISTS inventory_reorder_recommendations;
        CREATE VIEW inventory_reorder_recommendations AS
        WITH inventory_status AS (
            SELECT 
                i.id AS item_id,
                i.item_name,
                c.name AS category_name,
                SUM(inv_sizes.quantity) AS current_stock,
                AVG(s.quantity) AS avg_daily_sales
            FROM 
                inventory i
            LEFT JOIN 
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

        conn.executescript(update_views_sql)
        print("\nViews updated successfully.")

        # Test the updated views
        print("\nSample data from sales_performance_analysis:")
        sales_data = execute_query(conn, "SELECT * FROM sales_performance_analysis LIMIT 5;")
        if sales_data:
            for row in sales_data:
                print(row)
        else:
            print("No data found in sales_performance_analysis view.")

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