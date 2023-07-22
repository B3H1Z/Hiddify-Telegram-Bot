# Description: Configuration file for the bot
import json
import logging

logging.basicConfig(filename="log.txt", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


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
    if not is_config_exists():
        print("Config file not found! Please run config.py script first!")
        raise FileNotFoundError("config.json file not found!")
    with open("config.json", "r") as f:
        return json.load(f)


ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG = None, None, None, None


def set_variables(json):
    global ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG
    ADMINS_ID = json["admin_id"]
    TELEGRAM_TOKEN = json["token"]
    PANEL_URL = json["url"]
    LANG = json["lang"]


def set_by_user():
    print("Example: 123456789 (get it from @userinfobot)")
    admin_id = input("Enter Telegram Admin Number ID: ")
    if not admin_id.isdigit():
        raise ValueError("Admin ID must be a number!")

    print("Example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ (get it from @BotFather)")
    token = input("Enter your bot token: ")
    if not token:
        raise ValueError("Token is required!")

    print(
        "Example: https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4 (exactly like this!))")
    url = input("Enter your panel URL:")
    if not url:
        raise ValueError("URL is required!")

    print("Example: EN (default: FA)")
    lang = input("Enter your language (EN, FA): ") or "FA"
    if lang not in ["EN", "FA"]:
        raise ValueError("Language must be EN or FA!")
    return int(admin_id), token, url, lang


if __name__ == '__main__':
    if not is_config_exists():
        logging.info("Config file not found, creating...")

        # Create config file
        create_config_file(*set_by_user())
        print("Config file created successfully!")
        logging.info("Config file created successfully!")
    else:
        logging.info("Config file found!")
        print("Config file is exist!")
        if input("Do you want to change config? (y/n): ").lower() == "y":
            # Create config file
            create_config_file(*set_by_user())
            print("Config file updated successfully!")
            logging.info("Config file updated successfully!")

set_variables(read_config_file())
