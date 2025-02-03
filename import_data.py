import sqlite3
import csv


def import_data(db_name, table_name, csv_file):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Try UTF-8 first, then fall back to ISO-8859-1 if that fails
    encodings = ['utf-8', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)

                placeholders = ','.join(['?' for _ in headers])
                insert_query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({placeholders})"

                for row in csv_reader:
                    cursor.execute(insert_query, row)

            conn.commit()
            print(f"Successfully imported data from {csv_file} using {encoding} encoding.")
            break  # If successful, exit the loop
        except UnicodeDecodeError:
            print(f"Failed to decode {csv_file} with {encoding} encoding. Trying next encoding...")
            continue  # Try the next encoding
        except Exception as e:
            print(f"An error occurred while importing {csv_file}: {str(e)}")
            conn.rollback()  # Rollback changes if an error occurs
            break  # Exit the loop on other errors

    conn.close()


# Import data for each table
import_data('clothing_store.db', 'customers', 'customers.csv')
import_data('clothing_store.db', 'inventory', 'inventory.csv')
import_data('clothing_store.db', 'employees', 'employees.csv')
import_data('clothing_store.db', 'sales', 'sales.csv')

print("Data import completed.")