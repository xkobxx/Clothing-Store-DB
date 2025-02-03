import sqlite3


def create_triggers(conn):
    """Create all database triggers"""
    cursor = conn.cursor()

    triggers = [
        # Prevent negative inventory
        '''
        CREATE TRIGGER IF NOT EXISTS check_inventory_quantity
        BEFORE UPDATE ON inventory_sizes
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ROLLBACK, 'Quantity cannot be negative')
            WHERE (NEW.quantity < 0);
        END;
        ''',

        # Update order total amount when items are added
        '''
        CREATE TRIGGER IF NOT EXISTS update_order_total
        AFTER INSERT ON order_items
        BEGIN
            UPDATE orders 
            SET total_amount = (
                SELECT SUM(subtotal) 
                FROM order_items 
                WHERE order_id = NEW.order_id
            )
            WHERE id = NEW.order_id;
        END;
        ''',

        # Log inventory changes
        '''
        CREATE TRIGGER IF NOT EXISTS log_inventory_changes
        AFTER UPDATE ON inventory_sizes
        BEGIN
            INSERT INTO inventory_log (
                inventory_id,
                size_id,
                old_quantity,
                new_quantity,
                change_date
            ) VALUES (
                NEW.inventory_id,
                NEW.size_id,
                OLD.quantity,
                NEW.quantity,
                DATETIME('now')
            );
        END;
        ''',

        # Ensure order items quantity is available in inventory
        '''
        CREATE TRIGGER IF NOT EXISTS check_order_quantity
        BEFORE INSERT ON order_items
        BEGIN
            SELECT RAISE(ROLLBACK, 'Insufficient inventory')
            WHERE (
                SELECT quantity 
                FROM inventory_sizes 
                WHERE inventory_id = NEW.inventory_id
            ) < NEW.quantity;
        END;
        ''',

        # Calculate subtotal for order items
        '''
        CREATE TRIGGER IF NOT EXISTS calculate_order_item_subtotal
        BEFORE INSERT ON order_items
        BEGIN
            UPDATE order_items 
            SET subtotal = NEW.quantity * NEW.unit_price 
            WHERE rowid = NEW.rowid;
        END;
        ''',

        # Create inventory log table if it doesn't exist
        '''
        CREATE TABLE IF NOT EXISTS inventory_log (
            id INTEGER PRIMARY KEY,
            inventory_id INTEGER,
            size_id INTEGER,
            old_quantity INTEGER,
            new_quantity INTEGER,
            change_date DATETIME,
            FOREIGN KEY (inventory_id) REFERENCES inventory (id),
            FOREIGN KEY (size_id) REFERENCES sizes (id)
        );
        '''
    ]

    try:
        for trigger in triggers:
            cursor.execute(trigger)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating triggers: {e}")
        conn.rollback()
        raise


def create_audit_triggers(conn):
    """Create audit triggers for tracking changes"""
    cursor = conn.cursor()

    # Create audit tables
    audit_tables = [
        '''
        CREATE TABLE IF NOT EXISTS customer_audit (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            action TEXT,
            change_date DATETIME,
            old_values TEXT,
            new_values TEXT
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS inventory_audit (
            id INTEGER PRIMARY KEY,
            inventory_id INTEGER,
            action TEXT,
            change_date DATETIME,
            old_values TEXT,
            new_values TEXT
        )
        '''
    ]

    # Create audit triggers
    audit_triggers = [
        # Customer audit trigger
        '''
        CREATE TRIGGER IF NOT EXISTS audit_customer_changes
        AFTER UPDATE ON customers
        BEGIN
            INSERT INTO customer_audit (
                customer_id,
                action,
                change_date,
                old_values,
                new_values
            ) VALUES (
                OLD.id,
                'UPDATE',
                DATETIME('now'),
                json_object(
                    'name', OLD.name,
                    'email', OLD.email,
                    'phone', OLD.phone,
                    'address', OLD.address
                ),
                json_object(
                    'name', NEW.name,
                    'email', NEW.email,
                    'phone', NEW.phone,
                    'address', NEW.address
                )
            );
        END;
        ''',

        # Inventory audit trigger
        '''
        CREATE TRIGGER IF NOT EXISTS audit_inventory_changes
        AFTER UPDATE ON inventory
        BEGIN
            INSERT INTO inventory_audit (
                inventory_id,
                action,
                change_date,
                old_values,
                new_values
            ) VALUES (
                OLD.id,
                'UPDATE',
                DATETIME('now'),
                json_object(
                    'item_name', OLD.item_name,
                    'base_price', OLD.base_price,
                    'description', OLD.description
                ),
                json_object(
                    'item_name', NEW.item_name,
                    'base_price', NEW.base_price,
                    'description', NEW.description
                )
            );
        END;
        '''
    ]

    try:
        # Create audit tables
        for table in audit_tables:
            cursor.execute(table)

        # Create audit triggers
        for trigger in audit_triggers:
            cursor.execute(trigger)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating audit triggers: {e}")
        conn.rollback()
        raise