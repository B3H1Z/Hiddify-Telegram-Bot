import json
import sqlite3
import os
import shutil
from config import USERS_DB_LOC
from Database.dbManager import UserDBManager

class SQLiteDBManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def create_user_table(self):
        # Implement table creation logic here
        db = UserDBManager(db_file=self.db_file)
        db.create_user_table()

    # Define methods for creating other tables

    def backup_to_json(self, backup_dir):
        try:
            # Close the database connection before making a copy
            self.conn.close()

            # Define the backup file path and create the backup directory if it doesn't exist
            backup_file = os.path.join(backup_dir, 'backup.json')
            os.makedirs(backup_dir, exist_ok=True)

            backup_data = {}  # Store backup data in a dictionary

            # List of tables to backup
            tables = ['users', 'plans', 'orders', 'order_subscriptions', 'non_order_subscriptions',
                      'str_config', 'int_config', 'bool_config', 'wallet', 'payments', 'servers']

            for table in tables:
                self.cursor.execute(f"SELECT * FROM {table}")
                rows = self.cursor.fetchall()

                # Convert rows to list of dictionaries
                table_data = []
                for row in rows:
                    columns = [column[0] for column in self.cursor.description]
                    table_data.append(dict(zip(columns, row)))

                backup_data[table] = table_data

            # Save the backup data to a JSON file
            with open(backup_file, 'w') as json_file:
                json.dump(backup_data, json_file, indent=4)

            print('Database backed up successfully to:', backup_file)

        except sqlite3.Error as e:
            print('SQLite error:', str(e))

        finally:
            # Reopen the database connection
            self.conn = sqlite3.connect(self.db_file)

    def restore_from_json(self, backup_file):
        try:
            # Close the database connection before restoring
            self.conn.close()

            with open(backup_file, 'r') as json_file:
                backup_data = json.load(json_file)

            for table, data in backup_data.items():
                for entry in data:
                    keys = ', '.join(entry.keys())
                    values = ', '.join([f"'{v}'" for v in entry.values()])
                    self.cursor.execute(f"INSERT INTO {table} ({keys}) VALUES ({values})")

            self.conn.commit()
            print('Database restored successfully from:', backup_file)

        except sqlite3.Error as e:
            print('SQLite error:', str(e))

        finally:
            # Reopen the database connection
            self.conn = sqlite3.connect(self.db_file)


# Example usage
if __name__ == '__main__':
    db_manager = SQLiteDBManager(USERS_DB_LOC)

    # Create tables (implement your table creation logic)
    # db_manager.create_user_table()
    # Add logic to create other tables

    # Backup the database
    backup_dir = os.path.join(os.getcwd(), '..', 'Backup', 'Database')
    # if path not exists, create it
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    db_manager.backup_to_json(backup_dir)

    # # Restore from backup
    # restore_file = os.path.join(backup_dir, 'backup.json')
    # db_manager.restore_from_json(restore_file)
