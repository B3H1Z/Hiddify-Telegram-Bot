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
        self.create_user_table()
        self.set_default_settings()
        self.set_default_owner_info()

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
            cur.execute("CREATE TABLE IF NOT EXISTS users ("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "telegram_id INTEGER NOT NULL UNIQUE,"
                        "wallet_balance INTEGER NOT NULL UNIQUE,"
                        "created_at TEXT NOT NULL)")
            self.conn.commit()
            logging.info("User table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS plans ("
                        "id INTEGER PRIMARY KEY,"
                        "size_gb INTEGER NOT NULL,"
                        "days INTEGER NOT NULL,"
                        "price INTEGER NOT NULL,"
                        "description TEXT NULL,"
                        "status BOOLEAN NOT NULL)")
            self.conn.commit()
            logging.info("Plans table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS orders ("
                        "id INTEGER PRIMARY KEY,"
                        "telegram_id INTEGER NOT NULL,"
                        "user_name TEXT NOT NULL,"
                        "plan_id INTEGER NOT NULL,"
                        "paid_amount TEXT NOT NULL,"
                        "payment_method TEXT NOT NULL,"
                        "approved BOOLEAN NULL,"
                        "payment_image TEXT NOT NULL,"
                        "created_at TEXT NOT NULL,"
                        "FOREIGN KEY (telegram_id) REFERENCES user (telegram_id),"
                        "FOREIGN KEY (plan_id) REFERENCES plans (id))")
            self.conn.commit()
            logging.info("Orders table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS order_subscriptions ("
                        "id INTEGER PRIMARY KEY,"
                        "order_id INTEGER NOT NULL,"
                        "uuid TEXT NOT NULL,"
                        "FOREIGN KEY (order_id) REFERENCES orders (id))")
            self.conn.commit()
            logging.info("Order subscriptions table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS non_order_subscriptions ("
                        "id INTEGER PRIMARY KEY,"
                        "telegram_id INTEGER NOT NULL,"
                        "uuid TEXT NOT NULL UNIQUE,"
                        "FOREIGN KEY (telegram_id) REFERENCES user (telegram_id))")
            self.conn.commit()
            logging.info("Non order subscriptions table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS owner_info ("
                        "card_number TEXT NULL,"
                        "card_owner TEXT NULL,"
                        "telegram_username TEXT NULL)")
            self.conn.commit()
            logging.info("Owner info table created successfully!")

            cur.execute("CREATE TABLE IF NOT EXISTS settings ("
                        "visible_hiddify_hyperlink BOOLEAN NOT NULL DEFAULT 1)")
            self.conn.commit()
            logging.info("Settings table created successfully!")



        except Error as e:
            logging.error(f"Error while creating user table \n Error:{e}")
            return False
        return True

    def select_users(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all users \n Error:{e}")
            return None

    def find_user(self, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to find user!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM users WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"User {kwargs} not found!")
                return None
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
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
                cur.execute(f"DELETE FROM users WHERE {key}=?", (value,))
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
                cur.execute(f"UPDATE users SET {key}=? WHERE telegram_id=?", (value, telegram_id))
                self.conn.commit()
                logging.info(f"User [{telegram_id}] successfully update [{key}] to [{value}]")
            except Error as e:
                logging.error(f"Error while updating user [{telegram_id}] [{key}] to [{value}] \n Error: {e}")
                return False

        return True

    def add_user(self, telegram_id, wallet_balance, created_at):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO users(telegram_id,created_at) VALUES(?,?,?)",
                        (telegram_id, wallet_balance, created_at))
            self.conn.commit()
            logging.info(f"User [{telegram_id}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding user [{telegram_id}] \n Error: {e}")
            return False

    def add_plan(self, plan_id, size_gb, days, price, description=None, status=True):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO plans(id,size_gb, days, price, description, status) VALUES(?,?,?,?,?,?)",
                        (plan_id, size_gb, days, price, description, status))
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
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all plans \n Error:{e}")
            return None

    def find_plan(self, **kwargs):
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
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while finding plan {kwargs} \n Error:{e}")
            return None

    def delete_plan(self, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to delete plan!")
            return False
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"DELETE FROM plans WHERE {key}=?", (value,))
                self.conn.commit()
            logging.info(f"Plan {kwargs} deleted successfully!")
            return True
        except Error as e:
            logging.error(f"Error while deleting plan {kwargs} \n Error:{e}")
            return False

    def edit_plan(self, plan_id, **kwargs):
        cur = self.conn.cursor()

        for key, value in kwargs.items():
            try:
                cur.execute(f"UPDATE plans SET {key}=? WHERE id=?", (value, plan_id))
                self.conn.commit()
                logging.info(f"Plan [{plan_id}] successfully update [{key}] to [{value}]")
            except Error as e:
                logging.error(f"Error while updating plan [{plan_id}] [{key}] to [{value}] \n Error: {e}")
                return False

        return True

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

    def set_default_owner_info(self):
        rows = self.select_owner_info()
        if not rows:
            cur = self.conn.cursor()
            try:
                cur.execute("INSERT INTO owner_info VALUES(?,?,?)",
                            (None, None, None))
                self.conn.commit()
                logging.info(f"Owner info added successfully!")
                return True

            except Error as e:
                logging.error(f"Error while adding owner info \n Error: {e}")
                return False
        else:
            logging.info("Owner info already exists!")
            return False

    def add_order(self, order_id, telegram_id, user_name, plan_id, paid_amount, payment_method, payment_image,
                  created_at, approved=None):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO orders(id,telegram_id,user_name, plan_id,paid_amount,payment_method, approved,payment_image,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (order_id, telegram_id, user_name, plan_id, paid_amount, payment_method, approved, payment_image,
                 created_at))
            self.conn.commit()
            logging.info(f"Order [{order_id}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding order [{order_id}] \n Error: {e}")
            return False

    def select_orders(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM orders")
            rows = cur.fetchall()
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all orders \n Error:{e}")
            return None

    def find_order(self, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to find order!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM orders WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"Order {kwargs} not found!")
                return None
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while finding order {kwargs} \n Error:{e}")
            return None

    def edit_order(self, order_id, **kwargs):
        cur = self.conn.cursor()

        for key, value in kwargs.items():
            try:
                cur.execute(f"UPDATE orders SET {key}=? WHERE id=?", (value, order_id))
                self.conn.commit()
                logging.info(f"Order [{order_id}] successfully update [{key}] to [{value}]")
            except Error as e:
                logging.error(f"Error while updating order [{order_id}] [{key}] to [{value}] \n Error: {e}")
                return False

        return True

    def add_order_subscription(self, sub_id, order_id, uuid):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO order_subscriptions(id,order_id,uuid) VALUES(?,?,?)",
                (sub_id, order_id, uuid))
            self.conn.commit()
            logging.info(f"Order [{order_id}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding order [{order_id}] \n Error: {e}")
            return False

    def select_order_subscription(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM order_subscriptions")
            rows = cur.fetchall()
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all orders \n Error:{e}")
            return None

    def find_order_subscription(self, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to find order!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM order_subscriptions WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"Order {kwargs} not found!")
                return None
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while finding order {kwargs} \n Error:{e}")
            return None

    def edit_order_subscriptions(self, order_id, **kwargs):
        cur = self.conn.cursor()

        for key, value in kwargs.items():
            try:
                cur.execute(f"UPDATE order_subscriptions SET {key}=? WHERE order_id=?", (value, order_id))
                self.conn.commit()
                logging.info(f"Order [{order_id}] successfully update [{key}] to [{value}]")
            except Error as e:
                logging.error(f"Error while updating order [{order_id}] [{key}] to [{value}] \n Error: {e}")
                return False

        return True

    def delete_order_subscriptions(self, order_id):
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM order_subscriptions WHERE order_id=?", (order_id,))
            self.conn.commit()
            logging.info(f"Order [{order_id}] deleted successfully!")
            return True
        except Error as e:
            logging.error(f"Error while deleting order [{order_id}] \n Error: {e}")
            return False

    def add_non_order_subscriptions(self, non_sub_id, telegram_id, uuid):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO non_order_subscriptions(id,telegram_id,uuid) VALUES(?,?,?)",
                (non_sub_id, telegram_id, uuid))
            self.conn.commit()
            logging.info(f"Order [{telegram_id}] added successfully!")
            return True

        except Error as e:
            logging.error(f"Error while adding order [{telegram_id}] \n Error: {e}")
            return False

    def select_non_order_subscriptions(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM non_order_subscriptions")
            rows = cur.fetchall()
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all orders \n Error:{e}")
            return None

    def find_non_order_subscription(self, **kwargs):
        if len(kwargs) != 1:
            logging.warning("You can only use one key to find order!")
            return None
        rows = []
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"SELECT * FROM non_order_subscriptions WHERE {key}=?", (value,))
                rows = cur.fetchall()
            if len(rows) == 0:
                logging.info(f"Order {kwargs} not found!")
                return None
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while finding order {kwargs} \n Error:{e}")
            return None

    def delete_non_order_subscriptions(self, **kwargs):
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"DELETE FROM non_order_subscriptions WHERE {key}=?", (value,))
                self.conn.commit()
                logging.info(f"Order [{value}] deleted successfully!")
            return True
        except Error as e:
            logging.error(f"Error while deleting order [{kwargs}] \n Error: {e}")
            return False

    def select_settings(self):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM settings")
            rows = cur.fetchall()
            rows = [dict(zip([key[0] for key in cur.description], row)) for row in rows]
            return rows
        except Error as e:
            logging.error(f"Error while selecting all settings \n Error:{e}")
            return None

    def edit_settings(self, **kwargs):
        # There is only one row in settings table
        cur = self.conn.cursor()
        try:
            for key, value in kwargs.items():
                cur.execute(f"UPDATE settings SET {key}=?", (value,))
                self.conn.commit()
                logging.info(f"settings successfully update [{key}] to [{value}]")
            return True
        except Error as e:
            logging.error(f"Error while updating settings [{key}] to [{value}] \n Error: {e}")
            return False

    def set_default_settings(self):
        rows = self.select_settings()
        if not rows:
            # insert an empty row
            cur = self.conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO Settings(visible_hiddify_hyperlink) VALUES(?)",
                    (True,))
                self.conn.commit()
                logging.info(f"Default settings added successfully!")
                return True
            except Error as e:
                logging.error(f"Error while adding default settings \n Error: {e}")
                return False
        else:
            logging.info("Settings already exists!")
            return False
