# Description: Configuration file for the bot
import json
import logging
import requests
from termcolor import colored

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
        json.dump({
            "admin_id": [admin_id],
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


ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG = None, None, None, None


def set_variables(json):
    global ADMINS_ID, TELEGRAM_TOKEN, PANEL_URL, LANG
    ADMINS_ID = json["admin_id"]
    TELEGRAM_TOKEN = json["token"]
    PANEL_URL = json["url"]
    LANG = json["lang"]


def panel_url_validator(url):
    if not url.startswith("https://" or "http://"):
        raise ValueError("URL must start with http:// or https://")
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
        raise ValueError("URL is not valid!")
    elif request.status_code == 200:
        print(colored("URL is valid!", "green"))
    return url

def set_by_user():
    print(colored("Example: 123456789\n[get it from @userinfobot]", "yellow"))
    admin_id = input("Enter Telegram Admin Number ID: ")
    if not admin_id.isdigit():
        print(colored("Admin ID must be a number!", "red"))
        raise ValueError("Admin ID must be a number!")

    print(colored("Example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ\n[get it from @BotFather]", "yellow"))
    token = input("Enter your bot token: ")
    if not token:
        print(colored("Token is required!", "red"))
        raise ValueError("Token is required!")

    print(
        colored(
            "Example: https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4\n[exactly like this!]",
            "yellow"))
    url = input("Enter your panel URL:")
    if not url:
        print(colored("URL is required!", "red"))
        raise ValueError("URL is required!")
    url = panel_url_validator(url)

    print(colored("Example: EN (default: FA)\n[It is better that the language of the bot is the same as the panel]", "yellow"))
    lang = input("Select your language (EN(English), FA(Persian)): ") or "FA"
    if lang not in ["EN", "FA"]:
        print(colored("Language must be EN or FA!", "red"))
        raise ValueError("Language must be EN or FA!")
    return int(admin_id), token, url, lang


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
