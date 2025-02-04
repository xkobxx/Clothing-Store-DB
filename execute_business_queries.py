import sqlite3

def execute_query(cursor, query):
    try:
        cursor.execute(query)
        if cursor.description:
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            return columns, results
        return None, None
    except sqlite3.Error as e:
        print(f"An error occurred executing query: {query}")
        print(f"Error details: {e}")
        return None, None

def print_results(message, columns, results):
    if columns and results:
        print(f"\n{message}")
        print("-" * 80)
        print(" | ".join(columns))
        print("-" * 80)
        for row in results:
            print(" | ".join(str(item) for item in row))
        print("-" * 80)
    else:
        print(f"\n{message}")
        print("No results found or an error occurred.")

def is_message_query(result):
    if result and len(result) > 0 and isinstance(result[0], tuple) and len(result[0]) > 0:
        first_item = result[0][0]
        return isinstance(first_item, str) and (first_item.endswith('Analysis') or first_item.startswith('Top Selling'))
    return False

def main():
    try:
        conn = sqlite3.connect('clothing_store.db')
        cursor = conn.cursor()

        with open('business_requirement_queries.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            queries = sql_script.split(';')

            for query in queries:
                query = query.strip()
                if query:
                    if query.upper().startswith('SELECT'):
                        columns, results = execute_query(cursor, query)
                        if columns and results:
                            if is_message_query(results):
                                message = results[0][0]
                                # Execute the next query for actual data
                                next_query = next((q for q in queries if q.strip().startswith('SELECT') and q != query), None)
                                if next_query:
                                    columns, results = execute_query(cursor, next_query)
                            else:
                                message = "Query Results"
                            print_results(message, columns, results)
                    else:
                        cursor.execute(query)
                        conn.commit()
                        print(f"Executed non-SELECT query: {query[:50]}...")  # Print first 50 chars of query

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while reading the SQL file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()