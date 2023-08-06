import datetime
import logging
import sqlite3
from sqlite3 import Error


class TelegramDBManager:
    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        """ Create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
            return conn
        except Error as e:
            logging.error(f"Error while connecting to database \n Error:{e}")
            return None

    def create_user_table(self):
        cur = self.conn.cursor()
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS user ("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "uuid TEXT NOT NULL,"
                        "telegram_id INTEGER NOT NULL)")
            self.conn.commit()
        except Error as e:
            logging.error(f"Error while creating user table \n Error:{e}")
            return False
        return True

    def select_users(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM user")
            rows = cur.fetchall()
            return rows
        except Error as e:
            logging.error(f"Error while selecting all users \n Error:{e}")
            return None

    def find_user(self, only_one=False, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to find user!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM user WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"User {kwargs} not found!")
                return None
            if only_one:
                return rows[0]
            return rows
        except Error as e:
            logging.error(f"Error while finding user {kwargs} \n Error:{e}")
            return None

    def delete_user(self, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to delete user!")
            return False
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"DELETE FROM user WHERE {key}=?", (value,))
                self.conn.commit()
            logging.info(f"User {kwargs} deleted successfully!")
            return True
        except Error as e:
            logging.error(f"Error while deleting user {kwargs} \n Error:{e}")
            return False

    def edit_user(self, uuid, **kwargs):
        cur = self.conn.cursor()

        for key, value in kwargs.items():
            try:
                cur.execute(f"UPDATE user SET {key}=? WHERE uuid=?", (value, uuid))
                self.conn.commit()
                logging.info(f"User [{uuid}] successfully update [{key}] to [{value}]")
            except Error as e:
                logging.error(f"Error while updating user [{uuid}] [{key}] to [{value}] \n Error: {e}")
                return False

        return True

    def add_user(self, uuid, telegram_id):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO user(uuid, telegram_id) VALUES(?,?)",
                        (uuid, telegram_id))
            self.conn.commit()
            logging.info(f"User [{uuid}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding user [{uuid}] \n Error: {e}")
            return False
