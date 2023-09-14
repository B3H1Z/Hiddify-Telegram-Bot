import sqlite3
from version import __version__
from config import *

import argparse


def version():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-v4-v5", action="store_true", help="Update database from version 4 to 5")
    args = parser.parse_args()
    return args


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

    # finally:
    #     # Close the cursor and database connection to release resources
    #     if cur:
    #         cur.close()
    #     if conn:
    #         conn.close()


main_version = __version__.split(".")[0]


def update_v4_v5():
    if main_version != "4":
        print("No update is needed")
        return
    with sqlite3.connect(USERS_DB_LOC) as conn:
        print("Updating database from version 4 to 5")

        # Changes in orders table
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM orders WHERE approved = 0")
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM orders WHERE approved IS NULL")
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)
        drop_columns_from_table('orders', ['payment_image', 'payment_method', 'approved'])

        # Changes in owner_info table
        # try:
        #     cur = conn.cursor()
        #     cur.execute("SELECT * FROM owner_info")
        #     owner_info = cur.fetchone()
        #     if owner_info:
        #         cur.execute("UPDATE str_config SET value = ? WHERE key = 'card_number'", (owner_info[0],))
        #         cur.execute("UPDATE str_config SET value = ? WHERE key = 'card_holder'", (owner_info[1],))
        #         cur.execute("UPDATE str_config SET value = ? WHERE key = 'support_username'", (owner_info[2],))
        #         conn.commit()
        # except sqlite3.Error as e:
        #     print("SQLite error:", e)

        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE owner_info")
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)

        # Drop settings table
        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE settings")
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)

        # Add test_subscription bool default 0 to users table
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE users ADD COLUMN test_subscription BOOLEAN DEFAULT 0")
            conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)


if __name__ == "__main__":
    args = version()
    if args.update_v4_v5:
        update_v4_v5()
    else:
        print("No update is needed")
