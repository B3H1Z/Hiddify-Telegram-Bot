# Description: Configuration file for the bot
import json
import logging
import os
from urllib.parse import urlparse
import requests
from termcolor import colored
from Database.dbManager import AdminDBManager
from Database.dbManager import UserDBManager
from version import __version__

# Bypass proxy
os.environ['no_proxy'] = '*'
DEBUG = False

VERSION = __version__

if DEBUG:
    MAIN_DB_LOC = os.path.join(os.getcwd(), "hiddifypanel.db")
else:
    MAIN_DB_LOC = "/opt/hiddify-config/hiddify-panel/hiddifypanel.db"

USERS_DB_LOC = os.path.join(os.getcwd(), "Database", "hidyBot.db")
CONF_LOC = os.path.join(os.getcwd(), "config.json")
LOG_LOC = os.path.join(os.getcwd(), "Logs", "hidyBot.log")
BACKUP_LOC = os.path.join(os.getcwd(), "Backup")
API_PATH = "/api/v1"

logging.basicConfig(handlers=[logging.FileHandler(filename=LOG_LOC,
                                                  encoding='utf-8', mode='w')],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

try:
    # Check is database file exists
    if not os.path.exists(MAIN_DB_LOC):
        logging.error(f"Database file not found in {MAIN_DB_LOC} directory!")
        raise FileNotFoundError("Database file not found!")
    ADMIN_DB = AdminDBManager(MAIN_DB_LOC)
except Exception as e:
    logging.error(f"Error while connecting to database \n Error:{e}")
    raise Exception("Error while connecting to database")

USERS_DB = None


def setup_users_db():
    global USERS_DB
    try:
        if not os.path.exists(USERS_DB_LOC):
            logging.error(f"Database file not found in {USERS_DB_LOC} directory!")
            # Create database file
            with open(USERS_DB_LOC, "w") as f:
                pass
        USERS_DB = UserDBManager(USERS_DB_LOC)
    except Exception as e:
        logging.error(f"Error while connecting to database \n Error:{e}")
        raise Exception("Error while connecting to database")
    return USERS_DB


def is_config_exists():
    try:
        with open(CONF_LOC, "r") as f:
            return True
    except FileNotFoundError:
        return False


def create_config_file(admin_id, token, url, lang, client_token):
    with open(CONF_LOC, "w") as f:
        json.dump({
            "admin_id": admin_id,
            "token": token,
            "url": url,
            "lang": lang,
            "client_token": client_token
        }, f, indent=4)


def read_config_file():
    if not is_config_exists():
        print(colored("Config file not found! Please run config.py script first!", "red"))
        raise FileNotFoundError(f"{CONF_LOC} file not found!")
    with open(CONF_LOC, "r") as f:
        return json.load(f)


ADMINS_ID, TELEGRAM_TOKEN, CLIENT_TOKEN, PANEL_URL, LANG, PANEL_ADMIN_ID = None, None, None, None, None, None


def set_variables(json):
    global ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG, PANEL_ADMIN_ID, CLIENT_TOKEN
    ADMINS_ID = json["admin_id"]
    TELEGRAM_TOKEN = json["token"]
    try:
        CLIENT_TOKEN = json["client_token"]
    except KeyError:
        CLIENT_TOKEN = None

    if CLIENT_TOKEN:
        setup_users_db()
    PANEL_URL = json["url"]
    LANG = json["lang"]
    PANEL_ADMIN_ID = ADMIN_DB.find_admins(uuid=urlparse(PANEL_URL).path.split('/')[2])
    if not PANEL_ADMIN_ID:
        print(colored("Admin panel UUID is not valid!", "red"))
        raise Exception("Admin panel UUID is not valid!")
    PANEL_ADMIN_ID = PANEL_ADMIN_ID[0][0]


def panel_url_validator(url):
    if not url.startswith("https://" or "http://"):
        print(colored("URL must start with http:// or https://", "red"))
        return False
    if url.endswith("/"):
        url = url[:-1]
    if url.endswith("admin"):
        url = url.replace("/admin", "")
    if url.endswith("admin/user"):
        url = url.replace("/admin/user", "")
    print(colored("Checking URL...", "yellow"))
    try:
        request = requests.get(f"{url}/admin/")
    except requests.exceptions.ConnectionError:
        print(colored("URL is not valid! Error in connection", "red"))

        return False
    if request.status_code != 200:
        print(colored("URL is not valid!", "red"))
        return False
    elif request.status_code == 200:
        print(colored("URL is valid!", "green"))
    admin_url_uuid = urlparse(url).path.split('/')[2]
    status = ADMIN_DB.find_admins(uuid=admin_url_uuid)
    if not status:
        print(colored("Admin URL UUID is not valid!", "red"))
        return False
    return url


def set_by_user():
    print()
    print(
        colored("Example: 123456789\nIf you have more than one admin, split with comma(,)\n[get it from @userinfobot]",
                "yellow"))
    while True:
        admin_id = input("Enter Telegram Admin Number IDs: ")
        admin_ids = admin_id.split(',')
        admin_ids = [admin_id.strip() for admin_id in admin_ids]
        if not all(admin_id.isdigit() for admin_id in admin_ids):
            print(colored("Admin IDs must be numbers separated by commas!", "red"))
            continue
        admin_ids = [int(admin_id) for admin_id in admin_ids]
        break
    print()
    print(colored("Example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ\n[get it from @BotFather]", "yellow"))
    while True:
        token = input("Enter your Admin bot token: ")
        if not token:
            print(colored("Token is required!", "red"))
            continue
        break
    print()
    print(colored("You can use the bot as a userbot for your clients!", "yellow"))
    while True:
        userbot = input("Do you want a  Bot for your users? (y/n): ").lower()
        if userbot not in ["y", "n"]:
            print(colored("Please enter y or n!", "red"))
            continue
        break
    if userbot == "y":
        print()
        print(colored("Example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ\n[get it from @BotFather]", "yellow"))
        while True:
            client_token = input("Enter your client (For Users) bot token: ")
            if not client_token:
                print(colored("Token is required!", "red"))
                continue
            if client_token == token:
                print(colored("Client token must be different from Admin token!", "red"))
                continue
            break
    else:
        client_token = None
    print()
    print(colored(
        "Example: https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4\n[exactly like this!]",
        "yellow"))
    while True:
        url = input("Enter your panel URL:")
        if not url:
            print(colored("URL is required!", "red"))
            continue
        url = panel_url_validator(url)
        if not url:
            continue
        break

    print(colored("Example: EN (default: FA)\n[It is better that the language of the bot is the same as the panel]",
                  "yellow"))
    while True:
        lang = input("Select your language (EN(English), FA(Persian)): ") or "FA"
        if lang not in ["EN", "FA"]:
            print(colored("Language must be EN or FA!", "red"))
            continue
        break

    return admin_ids, token, url, lang, client_token


if __name__ == '__main__':
    if not is_config_exists():
        logging.info("Config file not found, creating...")

        # Create config file
        create_config_file(*set_by_user())
        print(colored("Config file created successfully!", "green"))
        logging.info("Config file created successfully!")
    else:
        logging.info("Config file found!")
        print(colored("Config file is exist!", "green"))
        set_variables(read_config_file())
        # Show current configration data
        print()
        print(colored("Current configration data:", "yellow"))
        print(f"Admin IDs: {ADMINS_ID}")
        print(f"Admin Bot Token: {TELEGRAM_TOKEN}")
        print(f"Client Bot Token: {CLIENT_TOKEN}")
        print(f"Panel URL: {PANEL_URL}")
        print(f"Language: {LANG}")
        print()
        if input("Do you want to change config? (y/n): ").lower() == "y":
            # Create config file
            create_config_file(*set_by_user())
            print(colored("Config file updated successfully!"))
            logging.info("Config file updated successfully!")

set_variables(read_config_file())
