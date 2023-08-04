# Description: Configuration file for the bot
import json
import logging
import os
from urllib.parse import urlparse
import requests
from termcolor import colored
from db import DBManager

logging.basicConfig(handlers=[logging.FileHandler(filename="hiddify-telegram-bot.log",
                                                  encoding='utf-8', mode='w')],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
DB_LOC = "/opt/hiddify-config/hiddify-panel/hiddifypanel.db"
# DB_LOC = "hiddifypanel.db"
try:
    # Check is database file exists
    if not os.path.exists(DB_LOC):
        logging.error(f"Database file not found in {DB_LOC} directory!")
        raise FileNotFoundError("Database file not found!")
    DB = DBManager(DB_LOC)
except Exception as e:
    logging.error(f"Error while connecting to database \n Error:{e}")
    raise Exception("Error while connecting to database")


def is_config_exists():
    try:
        with open("config.json", "r") as f:
            return True
    except FileNotFoundError:
        return False


def create_config_file(admin_id, token, url, lang):
    with open("config.json", "w") as f:
        json.dump({
            "admin_id": admin_id,
            "token": token,
            "url": url,
            "lang": lang
        }, f, indent=4)


def read_config_file():
    if not is_config_exists():
        print(colored("Config file not found! Please run config.py script first!", "red"))
        raise FileNotFoundError("config.json file not found!")
    with open("config.json", "r") as f:
        return json.load(f)


ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG, PANEL_ADMIN_ID = None, None, None, None, None


def set_variables(json):
    global ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG, PANEL_ADMIN_ID
    ADMINS_ID = json["admin_id"]
    TELEGRAM_TOKEN = json["token"]
    PANEL_URL = json["url"]
    LANG = json["lang"]
    PANEL_ADMIN_ID = DB.find_admins(uuid=urlparse(PANEL_URL).path.split('/')[2])[0][0]
    if not PANEL_ADMIN_ID:
        print(colored("Admin panel UUID is not valid!", "red"))
        raise Exception("Admin panel UUID is not valid!")


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
    request = requests.get(f"{url}/admin/")
    if request.status_code != 200:
        print(colored("URL is not valid!", "red"))
        return False
    elif request.status_code == 200:
        print(colored("URL is valid!", "green"))
    admin_url_uuid = urlparse(url).path.split('/')[2]
    status = DB.find_admins(uuid=admin_url_uuid)
    if not status:
        print(colored("Admin URL UUID is not valid!", "red"))
        return False
    return url


def set_by_user():
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

    print(colored("Example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ\n[get it from @BotFather]", "yellow"))
    while True:
        token = input("Enter your bot token: ")
        if not token:
            print(colored("Token is required!", "red"))
            continue
        break

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

    return admin_ids, token, url, lang


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
        if input("Do you want to change config? (y/n): ").lower() == "y":
            # Create config file
            create_config_file(*set_by_user())
            print(colored("Config file updated successfully!"))
            logging.info("Config file updated successfully!")

set_variables(read_config_file())
