import datetime
import logging
import sqlite3
from sqlite3 import Error


class AdminDBManager:
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

    def add_user(self, uuid, name, last_online, expiry_time, usage_limit_GB, package_days, mode, monthly, start_date,
                 current_usage_GB, last_reset_time, comment, telegram_id, added_by, max_ips, enable):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO user(uuid, name, last_online, expiry_time, usage_limit_GB, package_days, mode, "
                        "monthly, start_date, current_usage_GB, last_reset_time, comment, telegram_id, added_by, "
                        "max_ips, enable) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (uuid, name, last_online, expiry_time, usage_limit_GB, package_days, mode, monthly, start_date,
                         current_usage_GB, last_reset_time, comment, telegram_id, added_by, max_ips, enable))
            self.conn.commit()
            logging.info(f"User [{uuid}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding user [{uuid}] \n Error: {e}")
            return False

    def add_user_detail(self, user_id, last_online, current_usage_GB, connected_ips='', child_id=0):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO user_detail(user_id, last_online, current_usage_GB, connected_ips, child_id) "
                        "VALUES(?,?,?,?,?)", (user_id, last_online, current_usage_GB, connected_ips, child_id))
            self.conn.commit()
            logging.info(f"User details [{user_id}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding user details [{user_id}] \n Error: {e}")
            return False

    def add_default_user(self, name, package_days, usage_limit_GB, added_by, comment=None, mode='no_reset', monthly=0,
                         max_ips=100, enable=1, telegram_id=None):
        import uuid
        uuid = str(uuid.uuid4())
        logging.info(f"Adding default user [{uuid}]")
        last_online = '0001-01-01 00:00:00.000000'
        expiry_time = (datetime.datetime.now() + datetime.timedelta(days=180)).strftime("%Y-%m-%d")
        start_date = None
        current_usage_GB = 0
        last_reset_time = datetime.datetime.now().strftime("%Y-%m-%d")
        user_added = self.add_user(uuid, name, last_online, expiry_time, usage_limit_GB, package_days, mode, monthly,
                                   start_date,
                                   current_usage_GB, last_reset_time, comment, telegram_id, added_by, max_ips, enable)
        if user_added:
            logging.info(f"User [{uuid}] added successfully!")
            self.add_user_detail(self.find_user(uuid=uuid)[0][0], last_online, current_usage_GB)
            return uuid
        else:
            logging.error(f"Error while adding user [{uuid}]")
            self.delete_user(uuid=uuid)
            return None

    def reset_package_days(self, uuid):
        logging.info(f"Resetting package days for user [{uuid}]")
        user = self.find_user(uuid=uuid)
        if user is None:
            return False
        status = self.edit_user(uuid, start_date=datetime.datetime.now().strftime("%Y-%m-%d"))
        if status:
            logging.info(f"Package days for user [{uuid}] reset successfully!")
            return True
        else:
            logging.error(f"Error while resetting package days for user [{uuid}]")
            return False

    def reset_package_usage(self, uuid):
        logging.info(f"Resetting package usage for user [{uuid}]")
        user = self.find_user(uuid=uuid)
        if user is None:
            return False
        status = self.edit_user(uuid, current_usage_GB=0)
        if status:
            logging.info(f"Package usage for user [{uuid}] reset successfully!")
            return True
        else:
            logging.error(f"Error while resetting package usage for user [{uuid}]")
            return False

    def select_admins(self):
        logging.info(f"Selecting all admins")
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM admin_user")
            rows = cur.fetchall()
            return rows
        except Error as e:
            logging.error(f"Error while selecting all admins \n Error:{e}")
            return None

    def find_admins(self, **kwargs):
        logging.info(f"Finding admin {kwargs}")
        if len(kwargs) != 1:
            logging.error(f"Error while finding admin {kwargs} \n Error: You can only use one key to find admin!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM admin_user WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"Admin {kwargs} not found!")
                return None
            return rows
        except Error as e:
            logging.error(f"Error while finding admin {kwargs} \n Error:{e}")
            return None

class UserDBManager:
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
                        "uuid TEXT NULL,"
                        "telegram_id INTEGER NOT NULL)")
            self.conn.commit()
            logging.info("User table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS plans ("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "size_gb INTEGER NOT NULL,"
                        "days INTEGER NOT NULL,"
                        "price INTEGER NOT NULL,"
                        "description TEXT NULL,"
                        "status BOOLEAN NOT NULL)")
            self.conn.commit()
            logging.info("Plans table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS orders ("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "telegram_id INTEGER NOT NULL,"
                        "plan_id INTEGER NOT NULL,"
                        "approved BOOLEAN NOT NULL,"
                        "FOREIGN KEY (telegram_id) REFERENCES user (telegram_id),"
                        "FOREIGN KEY (plan_id) REFERENCES plans (id))")
            self.conn.commit()
            logging.info("Orders table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS owner_info ("
                        "card_number TEXT NULL,"
                        "card_owner TEXT NULL,"
                        "telegram_username TEXT NULL)")
            self.conn.commit()
            # add one empty row
            cur.execute("INSERT INTO owner_info VALUES (NULL, NULL, NULL)")
            logging.info("Owner info table created successfully!")


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

    def edit_user(self, telegram_id, **kwargs):
        cur = self.conn.cursor()

        for key, value in kwargs.items():
            try:
                cur.execute(f"UPDATE user SET {key}=? WHERE telegram_id=?", (value, telegram_id))
                self.conn.commit()
                logging.info(f"User [{telegram_id}] successfully update [{key}] to [{value}]")
            except Error as e:
                logging.error(f"Error while updating user [{telegram_id}] [{key}] to [{value}] \n Error: {e}")
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

    def add_plan(self, size_gb, days, price, description=None, status=True):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO plans(size_gb, days, price, description, status) VALUES(?,?,?,?,?)",
                        (size_gb, days, price, description, status))
            self.conn.commit()
            logging.info(f"Plan [{size_gb}GB] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding plan [{size_gb}GB] \n Error: {e}")
            return False

    def select_plans(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM plans")
            rows = cur.fetchall()
            return rows
        except Error as e:
            logging.error(f"Error while selecting all plans \n Error:{e}")
            return None

    def find_plan(self, only_one=False, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to find plan!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM plans WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"Plan {kwargs} not found!")
                return None
            if only_one:
                return rows[0]
            return rows
        except Error as e:
            logging.error(f"Error while finding plan {kwargs} \n Error:{e}")
            return None

    def edit_owner_info(self, **kwargs):
        # There is only one row in owner_info table
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"UPDATE owner_info SET {key}=?", (value,))
                self.conn.commit()
                logging.info(f"Owner info successfully update [{key}] to [{value}]")
            return True
        except Error as e:
            logging.error(f"Error while updating owner info [{key}] to [{value}] \n Error: {e}")
            return False

    def select_owner_info(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM owner_info")
            rows = cur.fetchall()
            # rows to dict
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all owner info \n Error:{e}")
            return None

