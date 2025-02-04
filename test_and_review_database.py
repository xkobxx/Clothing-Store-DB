import sqlite3
from prettytable import PrettyTable


def connect_to_db(db_name):
    try:
        conn = sqlite3.connect(db_name)
        print(f"Successfully connected to {db_name}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def get_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]


def get_table_schema(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()


def run_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall(), cursor.description
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None, None


def display_table_data(conn, table_name, limit=5):
    schema = get_table_schema(conn, table_name)
    columns = [col[1] for col in schema]

    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    data, _ = run_query(conn, query)

    if data:
        table = PrettyTable(columns)
        for row in data:
            table.add_row(row)
        print(f"\nSample data from {table_name}:")
        print(table)
    else:
        print(f"No data found in {table_name}")


def check_data_integrity(conn):
    integrity_checks = [
        ("Check for NULL values in important columns",
         "SELECT COUNT(*) FROM inventory WHERE item_name IS NULL OR base_price IS NULL"),
        ("Check for duplicate product names",
         "SELECT item_name, COUNT(*) FROM inventory GROUP BY item_name HAVING COUNT(*) > 1"),
        ("Check for negative prices",
         "SELECT * FROM inventory WHERE CAST(base_price AS FLOAT) < 0"),
        ("Check for orders without items",
         "SELECT o.id FROM orders o LEFT JOIN order_items oi ON o.id = oi.order_id WHERE oi.id IS NULL"),
    ]

    print("\nRunning data integrity checks:")
    for check_name, query in integrity_checks:
        result, _ = run_query(conn, query)
        if result is not None:
            if len(result) > 0 and result[0][0] > 0:
                print(f"{check_name}: Found {result[0][0]} issues")
            else:
                print(f"{check_name}: No issues found")
        else:
            print(f"{check_name}: Unable to perform check")


def perform_sample_analyses(conn):
    analyses = [
        ("Top 5 selling products",
         """SELECT i.item_name, SUM(oi.quantity) as total_sold 
            FROM order_items oi 
            JOIN inventory i ON oi.inventory_id = i.id 
            GROUP BY i.id 
            ORDER BY total_sold DESC 
            LIMIT 5"""),
        ("Total revenue by category",
         """SELECT COALESCE(c.name, 'Uncategorized') as category, ROUND(SUM(oi.subtotal), 2) as total_revenue 
            FROM order_items oi 
            JOIN inventory i ON oi.inventory_id = i.id 
            LEFT JOIN categories c ON i.category_id = c.id 
            GROUP BY c.id 
            ORDER BY total_revenue DESC"""),
        ("Customer with highest total purchases",
         """SELECT c.name, COUNT(o.id) as order_count, ROUND(SUM(o.total_amount), 2) as total_spent 
            FROM customers c 
            JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id 
            ORDER BY total_spent DESC 
            LIMIT 1"""),
    ]

    print("\nPerforming sample analyses:")
    for analysis_name, query in analyses:
        result, description = run_query(conn, query)
        if result and description:
            print(f"\n{analysis_name}:")
            table = PrettyTable()
            table.field_names = [col[0] for col in description]
            table.add_rows(result)
            print(table)
        else:
            print(f"{analysis_name}: No results found or error occurred")


def main():
    db_name = "clothing_store.db"
    conn = connect_to_db(db_name)
    if not conn:
        return

    try:
        tables = get_table_names(conn)
        if not tables:
            print("No tables found in the database.")
            return

        print(f"\nTables in the database: {', '.join(tables)}")

        for table in tables:
            schema = get_table_schema(conn, table)
            print(f"\nSchema for {table}:")
            for column in schema:
                print(f"  {column[1]} ({column[2]})")

            display_table_data(conn, table)

        check_data_integrity(conn)
        perform_sample_analyses(conn)

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()

