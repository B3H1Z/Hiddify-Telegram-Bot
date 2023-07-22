# Description: Configuration file for the bot
import json


def is_config_exists():
    try:
        with open("config.json", "r") as f:
            return True
    except FileNotFoundError:
        return False


def create_config_file(admin_id, token, url, lang):
    with open("config.json", "w") as f:
        json.dump(***REMOVED***
        ***REMOVED***admin_id],
            "token": token,
            "url": url,
            "lang": lang
        ***REMOVED***, f, indent=4)


def read_config_file():
    with open("config.json", "r") as f:
        return json.load(f)


def set_variables(json):
    global ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG
    ADMINS_ID = json["admin_id"]
    TELEGRAM_TOKEN = json["token"]
    PANEL_URL = json["url"]
    LANG = json["lang"]


ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG = None, None, None, None
