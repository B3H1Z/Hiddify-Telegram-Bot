import json
import sqlite3
import argparse
import logging
import os
USERS_DB_LOC = os.path.join(os.getcwd(), "Database", "hidyBot.db")

LOG_LOC = os.path.join(os.getcwd(), "Logs", "update.log")
logging.basicConfig(handlers=[logging.FileHandler(filename=LOG_LOC,
                                                  encoding='utf-8', mode='w')],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

def version():
    parser = argparse.ArgumentParser(description='Update script')
    # parser.add_argument("--update-v4-v5", action="store_true", help="Update database from version 4 to 5")
    parser.add_argument('--current-version', type=str, help='Current version')
    parser.add_argument('--target-version', type=str, help='Target version')
    args = parser.parse_args()
    return args

def is_version_less(version1, version2):
    v1_parts = list(map(int, version1.split('.')))
    v2_parts = list(map(int, version2.split('.')))

    for part1, part2 in zip(v1_parts, v2_parts):
        if part1 < part2:
            return True
        elif part1 > part2:
            return False

    # If both versions are identical up to the available parts
    return False

conn = sqlite3.connect(USERS_DB_LOC)


def drop_columns_from_table(table_name, columns_to_drop):
    try:
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
        logging.error("Database error: %s" % e)
        return False

# main_version = __version__.split(".")[0]
# print("main_version", main_version)
# logging.info("main_version %s" % main_version)

def update_v4_v5():
    print("Updating database from version v4 to v5")
    logging.info("Updating database from version 4 to 5")
    with sqlite3.connect(USERS_DB_LOC) as conn:
        logging.info("Updating database from version 4 to 5")
        print("Updating database from version 4 to 5")

        # Changes in orders table
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM orders WHERE approved = 0")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
            
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM orders WHERE approved IS NULL")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        drop_columns_from_table('orders', ['payment_image', 'payment_method', 'approved'])

        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE owner_info")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)

        # Drop settings table
        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE settings")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)

        # Add test_subscription bool default 0 to users table
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE users ADD COLUMN test_subscription BOOLEAN DEFAULT 0")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        
        # image path to basename

            
        # move config.json to db
        CONF_LOC = os.path.join(os.getcwd(), "config.json")
        if os.path.exists(CONF_LOC):
            with open(CONF_LOC, "r") as f:
                config = json.load(f)
                try:
                    # if str_config is not exists, create it
                    cur = conn.cursor()
                    cur.execute("CREATE TABLE IF NOT EXISTS str_config (key TEXT PRIMARY KEY, value TEXT)")
                    admin_ids = config["admin_id"]
                    admin_ids = json.dumps(admin_ids)
                    cur.execute("INSERT OR REPLACE INTO str_config VALUES (?, ?)", ("bot_admin_id", admin_ids))
                    cur.execute("INSERT OR REPLACE INTO str_config VALUES (?, ?)", ("bot_token_admin", config["token"]))
                    cur.execute("INSERT OR REPLACE INTO str_config VALUES (?, ?)",
                                ("bot_token_client", config["client_token"]))
                    cur.execute("INSERT OR REPLACE INTO str_config VALUES (?, ?)", ("bot_lang", config["lang"]))
                    conn.commit()

                    # if servers is not exists, create it
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL, title TEXT, description TEXT,default_server BOOLEAN NOT NULL DEFAULT 0)")
                    server_url = config["url"]
                    cur.execute("INSERT INTO servers VALUES (?,?,?,?,?)", (None, server_url, None, None,True))

                    conn.commit()
                except sqlite3.Error as e:
                    logging.error("Database error: %s" % e)
                    print("SQLite error:", e)
            os.remove(CONF_LOC)
def update_v5_1_0_to_v5_5_0():
    print("Updating database from version v5.1.0 to v5.5.0")
    logging.info("Updating database from version v5.1.0 to v5.5.0")
    with sqlite3.connect(USERS_DB_LOC) as conn:
        # add server_id to plans table
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE plans ADD COLUMN server_id INTEGER")
            cur.execute("UPDATE plans SET server_id = 1")
            # set foreign key FOREIGN KEY (server_id) REFERENCES server (id)
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        # add server_id to order_subscriptions table
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE order_subscriptions ADD COLUMN server_id INTEGER")
            cur.execute("UPDATE order_subscriptions SET server_id = 1")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        # add server_id to non_order_subscriptions table
        try:
            # check if server_id is exists
            cur = conn.cursor()
            cur.execute("ALTER TABLE non_order_subscriptions ADD COLUMN server_id INTEGER")
            cur.execute("UPDATE non_order_subscriptions SET server_id = 1")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        # add user_limit, status to servers table
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE servers ADD COLUMN user_limit INTEGER")
            cur.execute("ALTER TABLE servers ADD COLUMN status BOOLEAN DEFAULT 1")
            cur.execute("UPDATE servers SET user_limit = 2000")
            cur.execute("UPDATE servers SET title = Main Server")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        # add full_name,username to users table
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE users ADD COLUMN full_name TEXT NULL")
            cur.execute("ALTER TABLE users ADD COLUMN username TEXT NULL")
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
        
        # remove user_name from payments table
        drop_columns_from_table('payments', ['user_name']) 

def update_v5_9_5_to_v6_1_0():
    print("Updating database from version v5.9.5 to v6.1.0")
    logging.info("Updating database from version v5.9.5 to v6.1.0")
    with sqlite3.connect(USERS_DB_LOC) as conn:
        # add server_id to plans table
        try:
            cur = conn.cursor()
            # add banned column to users table
            cur.execute("ALTER TABLE users ADD COLUMN banned BOOLEAN DEFAULT 0")
            cur.execute("UPDATE users SET banned = 0")
        except sqlite3.Error as e:
            logging.error("Database error: %s" % e)
            print("SQLite error:", e)
            
        
        
    
def update_by_version(current_version, target_version):
    if is_version_less(current_version, target_version):
        print("Updating started...")
        logging.info("Updating started...")
        # if current_version is less than 5, update to 5.0.0
        if is_version_less(current_version, "5.0.0"):
            update_v4_v5()
        if is_version_less(current_version, "5.5.0"):
            update_v5_1_0_to_v5_5_0()
        if is_version_less(current_version, "6.1.0"):
            update_v5_9_5_to_v6_1_0()
    else:
        print("No update is needed")
        logging.info("No update is needed")


if __name__ == "__main__":
    args = version()
    if args.current_version and args.target_version:
        current_version = args.current_version
        target_version = args.target_version
        if current_version.find("-pre"):
            current_version = current_version.split("-pre")[0]
        if target_version.find("-pre"):
            target_version = target_version.split("-pre")[0]
        print(f"current-version: {current_version} -> target-version: {target_version}")
        logging.info(f"current-version: {current_version} -> target-version: {target_version}")
        update_by_version(current_version, target_version)
    else:
        logging.info("No update is needed")
        print("No update is needed")
