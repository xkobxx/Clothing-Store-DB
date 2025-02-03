import sqlite3
from datetime import datetime


def create_reorder_log_table(db_path):
    """Create the reorder log table if it doesn't exist"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reorder_log (
                id INTEGER PRIMARY KEY,
                inventory_id INTEGER,
                quantity_before INTEGER,
                quantity_ordered INTEGER,
                reorder_date DATETIME,
                status TEXT,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id)
            )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating reorder log table: {e}")
        raise
    finally:
        if conn:
            conn.close()


def check_and_reorder_inventory(db_path, threshold=20, reorder_quantity=50):
    """
    Check inventory levels and automatically reorder items below threshold
    Returns list of reordered items
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Find items below threshold
        cursor.execute('''
            SELECT 
                i.id,
                i.item_name,
                SUM(is_.quantity) as total_quantity
            FROM 
                inventory i
                JOIN inventory_sizes is_ ON i.id = is_.inventory_id
            GROUP BY 
                i.id
            HAVING 
                total_quantity < ?
        ''', (threshold,))

        low_items = cursor.fetchall()
        reordered_items = []

        for item_id, item_name, current_quantity in low_items:
            try:
                # Start transaction for each reorder
                cursor.execute("BEGIN TRANSACTION")

                # Update inventory quantity
                cursor.execute('''
                    UPDATE inventory_sizes 
                    SET quantity = quantity + ? 
                    WHERE inventory_id = ?
                ''', (reorder_quantity, item_id))

                # Log the reorder
                cursor.execute('''
                    INSERT INTO reorder_log 
                    (inventory_id, quantity_before, quantity_ordered, reorder_date, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (item_id, current_quantity, reorder_quantity,
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Completed'))

                cursor.execute("COMMIT")
                reordered_items.append((item_id, item_name, current_quantity))

            except sqlite3.Error as e:
                cursor.execute("ROLLBACK")
                print(f"Error reordering item {item_name}: {e}")
                continue

        return reordered_items

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_reorder_history(db_path, days=30):
    """Get reorder history for the last N days"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                r.id,
                i.item_name,
                r.quantity_before,
                r.quantity_ordered,
                r.reorder_date,
                r.status
            FROM 
                reorder_log r
                JOIN inventory i ON r.inventory_id = i.id
            WHERE 
                r.reorder_date >= date('now', ?)
            ORDER BY 
                r.reorder_date DESC
        ''', (f'-{days} days',))

        return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Error getting reorder history: {e}")
        raise
    finally:
        if conn:
            conn.close()


def analyze_reorder_patterns(db_path):
    """Analyze reorder patterns to suggest optimal threshold and quantities"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                i.id,
                i.item_name,
                AVG(r.quantity_before) as avg_reorder_point,
                AVG(r.quantity_ordered) as avg_reorder_quantity,
                COUNT(*) as reorder_frequency
            FROM 
                reorder_log r
                JOIN inventory i ON r.inventory_id = i.id
            GROUP BY 
                i.id
            HAVING 
                reorder_frequency > 1
        ''')

        return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Error analyzing reorder patterns: {e}")
        raise
    finally:
        if conn:
            conn.close()