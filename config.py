# Description: Configuration file for the bot
import json
import logging
import os
from urllib.parse import urlparse
import requests
from termcolor import colored

# import Utils.utils
from version import __version__

# PANEL_URL, API_PATH = None, None

# Bypass proxy
os.environ['no_proxy'] = '*'

VERSION = __version__

USERS_DB_LOC = os.path.join(os.getcwd(), "Database", "hidyBot.db")
LOG_DIR = os.path.join(os.getcwd(), "Logs")
LOG_LOC = os.path.join(LOG_DIR, "hidyBot.log")
BACKUP_LOC = os.path.join(os.getcwd(), "Backup")
RECEIPTIONS_LOC = os.path.join(os.getcwd(), "UserBot", "Receiptions")
BOT_BACKUP_LOC = os.path.join(os.getcwd(), "Backup", "Bot")
API_PATH = "/api/v1"
HIDY_BOT_ID = "@HidyBotGroup"

# if directories not exists, create it
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
if not os.path.exists(BACKUP_LOC):
    os.mkdir(BACKUP_LOC)
if not os.path.exists(RECEIPTIONS_LOC):
    os.mkdir(RECEIPTIONS_LOC)

# set logging  
logging.basicConfig(handlers=[logging.FileHandler(filename=LOG_LOC,
                                                  encoding='utf-8', mode='w')],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def setup_users_db():
    # global USERS_DB
    try:
        if not os.path.exists(USERS_DB_LOC):
            logging.error(f"Database file not found in {USERS_DB_LOC} directory!")
            with open(USERS_DB_LOC, "w") as f:
                pass
        # USERS_DB = Database.dbManager.UserDBManager(USERS_DB_LOC)
    except Exception as e:
        logging.error(f"Error while connecting to database \n Error:{e}")
        raise Exception(f"Error while connecting to database \nBe in touch with {HIDY_BOT_ID}")
    # return USERS_DB


setup_users_db()
from Database.dbManager import UserDBManager


def load_config(db):
    try:
        config = db.select_str_config()
        if not config:
            db.set_default_configs()
            config = db.select_str_config()
        configs = {}
        for conf in config:
            configs[conf['key']] = conf['value']

        return configs
    except Exception as e:
        logging.error(f"Error while loading config \n Error:{e}")
        raise Exception(f"Error while loading config \nBe in touch with {HIDY_BOT_ID}")


def load_server_url(db):
    try:
        panel_url = db.select_servers()
        if not panel_url:
            return None
        return panel_url[0]['url']
    except Exception as e:
        logging.error(f"Error while loading panel_url \n Error:{e}")
        raise Exception(f"Error while loading panel_url \nBe in touch with {HIDY_BOT_ID}")


ADMINS_ID, TELEGRAM_TOKEN, CLIENT_TOKEN, PANEL_URL, LANG, PANEL_ADMIN_ID = None, None, None, None, None, None


def set_config_variables(configs, server_url):
    if not conf['bot_admin_id'] and not conf['bot_token_admin'] and not conf['bot_lang'] or not server_url:
        print(colored("Config is not set! , Please run config.py first", "red"))
        raise Exception(f"Config is not set!\nBe in touch with {HIDY_BOT_ID}")

    global ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG, PANEL_ADMIN_ID, CLIENT_TOKEN
    json_admin_ids = configs["bot_admin_id"]
    ADMINS_ID = json.loads(json_admin_ids)
    TELEGRAM_TOKEN = configs["bot_token_admin"]
    try:
        CLIENT_TOKEN = configs["bot_token_client"]
    except KeyError:
        CLIENT_TOKEN = None

    if CLIENT_TOKEN:
        setup_users_db()
    PANEL_URL = server_url
    LANG = configs["bot_lang"]
    # PANEL_ADMIN_ID = ADMIN_DB.find_admins(uuid=urlparse(PANEL_URL).path.split('/')[2])
    PANEL_ADMIN_ID = urlparse(PANEL_URL).path.split('/')[2]
    if not PANEL_ADMIN_ID:
        print(colored("Admin panel UUID is not valid!", "red"))
        raise Exception(f"Admin panel UUID is not valid!\nBe in touch with {HIDY_BOT_ID}")
    PANEL_ADMIN_ID = PANEL_ADMIN_ID[0][0]


def panel_url_validator(url):
    if not (url.startswith("https://") or url.startswith("http://")):
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
    except requests.exceptions.ConnectionError as e:
        print(colored("URL is not valid! Error in connection", "red"))
        print(colored(f"Error: {e}", "red"))
        return False
    
    if request.status_code != 200:
        print(colored("URL is not valid!", "red"))
        print(colored(f"Error: {request.status_code}", "red"))
        return False
    elif request.status_code == 200:
        print(colored("URL is valid!", "green"))
    return url


def bot_token_validator(token):
    print(colored("Checking Bot Token...", "yellow"))
    try:
        request = requests.get(f"https://api.telegram.org/bot{token}/getMe")
    except requests.exceptions.ConnectionError:
        print(colored("Bot Token is not valid! Error in connection", "red"))
        return False
    if request.status_code != 200:
        print(colored("Bot Token is not valid!", "red"))
        return False
    elif request.status_code == 200:
        print(colored("Bot Token is valid!", "green"))
        print(colored("Bot Username:", "green"), "@"+request.json()['result']['username'])
    return True


def set_by_user():
    print()
    print(
        colored("Example: 123456789\nIf you have more than one admin, split with comma(,)\n[get it from @userinfobot]",
                "yellow"))
    while True:
        admin_id = input("[+] Enter Telegram Admin Number IDs: ")
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
        token = input("[+] Enter your Admin bot token: ")
        if not token:
            print(colored("Token is required", "red"))
            continue
        if not bot_token_validator(token):
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
            client_token = input("[+] Enter your client (For Users) bot token: ")
            if not client_token:
                print(colored("Token is required!", "red"))
                continue
            if client_token == token:
                print(colored("Client token must be different from Admin token!", "red"))
                continue
            if not bot_token_validator(client_token):
                continue
            break
    else:
        client_token = None
    print()
    print(colored(
        "Example: https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4\n[exactly like this!]",
        "yellow"))
    while True:
        url = input("[+] Enter your panel URL:")
        if not url:
            print(colored("URL is required!", "red"))
            continue
        url = panel_url_validator(url)
        if not url:
            continue
        break
    print()
    print(colored("Example: EN (default: FA)\n[It is better that the language of the bot is the same as the panel]",
                  "yellow"))
    while True:
        lang = input("[+] Select your language (EN(English), FA(Persian)): ") or "FA"
        if lang not in ["EN", "FA"]:
            print(colored("Language must be EN or FA!", "red"))
            continue
        break

    return admin_ids, token, url, lang, client_token


def set_config_in_db(db, admin_ids, token, url, lang, client_token):
    try:
        # if str_config is not exists, create it
        if not db.select_str_config():
            db.add_str_config("bot_admin_id", value=json.dumps(admin_ids))
            db.add_str_config("bot_token_admin", value=token)
            db.add_str_config("bot_token_client", value=client_token)
            db.add_str_config("bot_lang", value=lang)
        else:
            print(json.dumps(admin_ids))
            db.edit_str_config("bot_admin_id", value=json.dumps(admin_ids))
            db.edit_str_config("bot_token_admin", value=token)
            db.edit_str_config("bot_token_client", value=client_token)
            db.edit_str_config("bot_lang", value=lang)
        # if servers is not exists, create it
        if not db.select_servers():
            db.add_server(url, 2000, title="Main Server", default_server=True)
        else:
            # find default server
            default_server = db.find_server(default_server=True)
            default_server_id = default_server[0]['id']
            if default_server:
                if default_server['url'] != url:
                    db.edit_server(default_server_id, url=url)
            else:
                db.add_server(url, 2000, title="Main Server", default_server=True)
    except Exception as e:
        logging.error(f"Error while inserting config to database \n Error:{e}")
        raise Exception(f"Error while inserting config to database \nBe in touch with {HIDY_BOT_ID}")


def print_current_conf(conf, server_url):
    print()
    print(colored("Current configration data:", "yellow"))
    print(f"[+] Admin IDs: {conf['bot_admin_id']}")
    print(f"[+] Admin Bot Token: {conf['bot_token_admin']}")
    print(f"[+] Client Bot Token: {conf['bot_token_client']}")
    print(f"[+] Panel URL: {server_url}")
    print(f"[+] Language: {conf['bot_lang']}")
    print()


if __name__ == '__main__':
    db = UserDBManager(USERS_DB_LOC)
    conf = load_config(db)
    server_url = load_server_url(db)
    if conf['bot_admin_id'] and conf['bot_token_admin'] and conf['bot_lang'] and server_url:
        print("Config is already set!")
        print_current_conf(conf, server_url)
        print("Do you want to change config? (y/n): ")
        if input().lower() == "y":
            admin_ids, token, url, lang, client_token = set_by_user()
            set_config_in_db(db, admin_ids, token, url, lang, client_token)
            conf = load_config(db)
            server_url = load_server_url(db)
            set_config_variables(conf, server_url)
    else:
        admin_ids, token, url, lang, client_token = set_by_user()
        set_config_in_db(db, admin_ids, token, url, lang, client_token)
        conf = load_config(db)
        server_url = load_server_url(db)
    set_config_variables(conf, server_url)
    # close database connection
    db.close()

db = UserDBManager(USERS_DB_LOC)
db.set_default_configs()
conf = load_config(db)
server_url = load_server_url(db)
set_config_variables(conf, server_url)
db.close()