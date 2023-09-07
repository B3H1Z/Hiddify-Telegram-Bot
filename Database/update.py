import sqlite3
from version import __version__
from config import *

conn = sqlite3.connect(USERS_DB_LOC)


def drop_columns_from_table(table_name, columns_to_drop):
    try:
        # Connect to the SQLite database

        # Create a cursor object to execute SQL commands
        cur = conn.cursor()

        # Create a list of column names to keep
        columns_to_keep = [col for col in cur.execute(f"PRAGMA table_info({table_name});")]
        columns_to_keep = [col[1] for col in columns_to_keep if col[1] not in columns_to_drop]

        # Create a new table without the columns to be dropped
        columns_to_keep_str = ', '.join(columns_to_keep)
        cur.execute(f"CREATE TABLE new_{table_name} AS SELECT {columns_to_keep_str} FROM {table_name};")

        # Drop the original table
        cur.execute(f"DROP TABLE {table_name};")

        # Rename the new table to the original table name
        cur.execute(f"ALTER TABLE new_{table_name} RENAME TO {table_name};")

        # Commit the changes to the database
        conn.commit()

        return True

    except sqlite3.Error as e:
        # Handle any database errors that may occur
        print("SQLite error:", e)
        return False

    finally:
        # Close the cursor and database connection to release resources
        if cur:
            cur.close()
        if conn:
            conn.close()


if __version__ == "4.2.0":
    print("Updating to version 4.2.1")
    print("Updating database...")
    # First, remove not approved orders
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE approved = 0")
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite error:", e)
        raise Exception("Database update failed")

    # Then, drop the columns
    status = drop_columns_from_table('orders', ['payment_image', 'payment_method', 'approved'])
    if status:
        print("Database updated successfully")
    else:
        raise Exception("Database update failed")
