# Description: API for connecting to the panel
import os
import re
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from config import *
import psutil
import logging

logging.basicConfig(filename="hiddify-telegram-bot.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Global variables
# Make Session for requests
session = requests.session()
# Base panel URL - example: https://panel.example.com
BASE_URL = urlparse(PANEL_URL).scheme + "://" + urlparse(PANEL_URL).netloc
# Users directory in panel
USERS_DIR = "/admin/user/"


# Get request - return request object
def get_request(url):
    logging.info(f"GET Request to ***REMOVED***privacy_friendly_logging_request(url)***REMOVED***")
    global session
    try:
        req = session.get(url)
        logging.info(f"GET Request to ***REMOVED***privacy_friendly_logging_request(url)***REMOVED*** - Status Code: ***REMOVED***req.status_code***REMOVED***")
        return req
    except requests.exceptions.ConnectionError as e:
        logging.exception(f"Connection Exception: ***REMOVED***e***REMOVED***")
        return False
    except requests.exceptions.Timeout as e:
        logging.exception(f"Timeout Exception: ***REMOVED***e***REMOVED***")
        return False
    except requests.exceptions.RequestException as e:
        logging.exception(f"General Connection Exception: ***REMOVED***e***REMOVED***")
        return False
    except Exception as e:
        logging.exception(f"General Exception: ***REMOVED***e***REMOVED***")
        return False


# Post request - return request object
def post_request(url, data):
    logging.info(f"POST Request to ***REMOVED***privacy_friendly_logging_request(url)***REMOVED*** - Data: ***REMOVED***data***REMOVED***")
    global session
    try:
        req = session.post(url, data=data)
        return req
    except requests.exceptions.ConnectionError as e:
        logging.exception(f"Connection Exception: ***REMOVED***e***REMOVED***")
        return False
    except requests.exceptions.Timeout as e:
        logging.exception(f"Timeout Exception: ***REMOVED***e***REMOVED***")
        return False
    except requests.exceptions.RequestException as e:
        logging.exception(f"General Connection Exception: ***REMOVED***e***REMOVED***")
        return False
    except Exception as e:
        logging.exception(f"General Exception: ***REMOVED***e***REMOVED***")
        return False


# Send request to users page - return bs4 object
def users_page():
    logging.info(f"Request for users page")
    global session
    users_url = PANEL_URL + USERS_DIR
    req = get_request(users_url)
    if not req:
        return False

    try:
        soup = BeautifulSoup(req.text, "html.parser")
        return soup
    except Exception as e:
        logging.exception(f"Parse BeautifulSoup Exception: ***REMOVED***e***REMOVED***")
        return False


# List users - return list of all users
def list_users():
    logging.info(f"Parse users page")
    users_list = []

    users = users_page()
    if not users:
        return False

    table = users.find("table", ***REMOVED***"class": "table table-bordered table-hover"***REMOVED***)
    rows = table.find_all("tr")
    rows.pop(0)

    for row in rows:
        uuid = row.find("td", ***REMOVED***"class": "col-uuid"***REMOVED***)
        name = row.find("td", ***REMOVED***"class": "col-name"***REMOVED***)
        if name.find("i", ***REMOVED***"class": "fa-solid fa-circle-check text-success"***REMOVED***):
            enable = "y"
        else:
            enable = "n"
        usage = row.find("td", ***REMOVED***"class": "col-current_usage_GB"***REMOVED***)
        remaining_day = row.find("td", ***REMOVED***"class": "col-remaining_days"***REMOVED***)
        comment = row.find("td", ***REMOVED***"class": "col-comment"***REMOVED***)
        last_connection = row.find("td", ***REMOVED***"class": "col-last_online"***REMOVED***)
        mode = row.find("td", ***REMOVED***"class": "col-mode"***REMOVED***)

        delete_info = row.find("td", ***REMOVED***"class": "list-buttons-column"***REMOVED***)

        delete_url_action = delete_info.find("form")['action']

        delete_id_param = delete_info.find("input", ***REMOVED***"id": "id"***REMOVED***)['value']
        delete_url_param = delete_info.find("input", ***REMOVED***"id": "url"***REMOVED***)['value']
        delete_csrf_param = row.find("input", ***REMOVED***"name": "csrf_token"***REMOVED***)['value']
        try:
            edit_url = row.find("a", ***REMOVED***"title": "Edit Record"***REMOVED***)['href']
        except:
            edit_url = row.find("a", ***REMOVED***"title": "ویرایش رکورد"***REMOVED***)['href']

        users_list.append(***REMOVED***
            "name": name.text.strip(),
            "usage": usage.text.strip(),
            "remaining_day": remaining_day.text.strip(),
            "comment": comment.text.strip(),
            "last_connection": last_connection.text.strip(),
            "uuid": uuid.text.strip(),
            "link": f"***REMOVED***BASE_URL***REMOVED***/***REMOVED***urlparse(PANEL_URL).path.split('/')[1]***REMOVED***/***REMOVED***uuid.text.strip()***REMOVED***/",
            "edit_url": edit_url,
            "mode": mode.text.strip(),
            "enable": enable,
            "delete": ***REMOVED***
                "action": delete_url_action,
                "id": delete_id_param,
                "url": delete_url_param,
                "csrf": delete_csrf_param
            ***REMOVED***
        ***REMOVED***)
    return users_list


# Get single user info - return dict of user info
def user_info(uuid):
    logging.info(f"Get info of user single user - ***REMOVED***uuid***REMOVED***")
    lu = list_users()
    if not lu:
        return False
    for user in lu:
        if user['uuid'] == uuid:
            return user
    return False


# Add user - return UUID of created user
def add_user(name, usage_limit_GB=100, package_days=30, mode="no_reset", comment="", enable="y"):
    logging.info(f"Add user")
    users = users_page()
    if not users:
        return False
    try:
        add_user_btn = users.find("a", ***REMOVED***"title": "Create New Record"***REMOVED***)['href']
    except:
        add_user_btn = users.find("a", ***REMOVED***"title": "ایجاد رکورد جدید"***REMOVED***)['href']

    add_user_page_url = BASE_URL + add_user_btn
    add_get_req = get_request(add_user_page_url)
    if not add_get_req:
        return False
    if add_get_req.status_code != 200:
        return False

    try:
        soup = BeautifulSoup(add_get_req.text, "html.parser")
    except Exception as e:
        logging.exception(f"Parse BeautifulSoup Exception: ***REMOVED***e***REMOVED***")
        return False

    csrf_token = soup.find("input", ***REMOVED***"name": "csrf_token"***REMOVED***)['value']
    uuid = soup.find("input", ***REMOVED***"name": "uuid"***REMOVED***)['value']

    params = ***REMOVED***
        "csrf_token": csrf_token,
        "uuid": uuid,
        "name": name,
        "usage_limit_GB": usage_limit_GB,
        "package_days": package_days,
        "mode": mode,
        "comment": comment,
        "enable": enable
    ***REMOVED***

    add_post_req = post_request(add_user_page_url, data=params)
    if not add_post_req:
        return False
    if add_post_req.status_code == 200:
        return uuid


# Delete user - return True if user deleted
def delete_user(uuid):
    logging.info(f"Delete user - ***REMOVED***uuid***REMOVED***")
    users = list_users()

    for user in users:
        if user['uuid'] == uuid:
            delete_user_url = BASE_URL + user['delete']['action']
            params = ***REMOVED***
                "id": user['delete']['id'],
                "url": user['delete']['url'],
                "csrf_token": user['delete']['csrf']
            ***REMOVED***
            delete_req = post_request(delete_user_url, data=params)
            if not delete_req:
                return False
            if delete_req.status_code == 200:
                return True
            else:
                return False


# Edit user - return True if user edited
def edit_user(uuid, **kwargs):
    logging.info(f"Edit user - ***REMOVED***uuid***REMOVED***")
    user = user_info(uuid)
    if not user:
        return False

    edit_user_page_url = BASE_URL + user['edit_url']
    edit_get_req = get_request(edit_user_page_url)
    if not edit_get_req:
        return False
    if edit_get_req.status_code != 200:
        return False

    soup = BeautifulSoup(edit_get_req.text, "html.parser")
    csrf_token = soup.find("input", ***REMOVED***"name": "csrf_token"***REMOVED***)['value']
    uuid = soup.find("input", ***REMOVED***"name": "uuid"***REMOVED***)['value']
    name = soup.find("input", ***REMOVED***"name": "name"***REMOVED***)['value']
    usage_limit_GB = soup.find("input", ***REMOVED***"name": "usage_limit_GB"***REMOVED***)['value']
    package_days = soup.find("input", ***REMOVED***"name": "package_days"***REMOVED***)['value']
    mode = soup.find("select", ***REMOVED***"name": "mode"***REMOVED***).find("option", selected=True)['value']
    comment = soup.find("input", ***REMOVED***"name": "comment"***REMOVED***).text.strip()
    enable = soup.find("input", ***REMOVED***"name": "enable"***REMOVED***)['value']

    if not kwargs:
        return False
    if "name" in kwargs:
        name = kwargs['name']
    if "usage_limit_GB" in kwargs:
        usage_limit_GB = kwargs['usage_limit_GB']
    if "remaining_days" in kwargs:
        package_days = kwargs['remaining_days']
    if "mode" in kwargs:
        mode = kwargs['mode']
    if "comment" in kwargs:
        comment = kwargs['comment']
    if "enable" in kwargs:
        enable = kwargs['enable']
    if "reset_usage" in kwargs:
        reset_usage = kwargs['reset_usage']
    else:
        reset_usage = False
    if "reset_days" in kwargs:
        reset_days = kwargs['reset_days']
    else:
        reset_days = False

    params = ***REMOVED***
        "csrf_token": csrf_token,
        "uuid": uuid,
        "name": name,
        "usage_limit_GB": usage_limit_GB,
        "package_days": package_days,
        "mode": mode,
        "comment": comment,
        "enable": enable
    ***REMOVED***
    if reset_usage:
        params['reset_usage'] = reset_usage
    if reset_days:
        params['reset_days'] = reset_days

    add_post_req = post_request(edit_user_page_url, data=params)
    if not add_post_req:
        return False
    if add_post_req.status_code == 200:
        return True


def sub_links(uuid):
    logging.info(f"Get sub links of user - ***REMOVED***uuid***REMOVED***")
    sub = ***REMOVED******REMOVED***
    PANEL_DIR = urlparse(PANEL_URL).path.split('/')
    # Clash open app: clash://install-config?url=
    # Hidden open app: clashmeta://install-config?url=
    sub['clash_configs'] = f"***REMOVED***BASE_URL***REMOVED***/***REMOVED***PANEL_DIR[1]***REMOVED***/***REMOVED***uuid***REMOVED***/clash/all.yml"
    sub['hiddify_configs'] = f"***REMOVED***BASE_URL***REMOVED***/***REMOVED***PANEL_DIR[1]***REMOVED***/***REMOVED***uuid***REMOVED***/clash/meta/all.yml"
    sub['sub_link'] = f"***REMOVED***BASE_URL***REMOVED***/***REMOVED***PANEL_DIR[1]***REMOVED***/***REMOVED***uuid***REMOVED***/all.txt"
    sub['sub_link_b64'] = f"***REMOVED***BASE_URL***REMOVED***/***REMOVED***PANEL_DIR[1]***REMOVED***/***REMOVED***uuid***REMOVED***/all.txt"
    return sub


# Parse sub links
def sub_parse(sub):
    logging.info(f"Parse sub links")
    res = get_request(sub)
    if not res or res.status_code != 200:
        return False

    urls = re.findall(r'(vless:\/\/[^\n]+)|(vmess:\/\/[^\n]+)|(trojan:\/\/[^\n]+)', res.text)

    config_links = ***REMOVED***
        'vless': [],
        'vmess': [],
        'trojan': []
    ***REMOVED***
    for url in urls:
        if url[0]:
            match = re.search(r'#(.+)$', url[0])
            if match:
                config_links['vless'].append([url[0], match.group(1)])
        elif url[1]:
            config = url[1].replace("vmess://", "")
            config_parsed = base64decoder(config)
            if config_parsed:
                config_links['vmess'].append([url[1], config_parsed['ps']])
        elif url[2]:
            match = re.search(r'#(.+)$', url[2])
            if match:
                config_links['trojan'].append([url[2], match.group(1)])

    return config_links


# Backup panel
def backup_panel():
    logging.info(f"Backup panel")
    dir_panel = urlparse(PANEL_URL).path.split('/')
    backup_url = f"***REMOVED***BASE_URL***REMOVED***/***REMOVED***dir_panel[1]***REMOVED***/***REMOVED***dir_panel[2]***REMOVED***/admin/backup/backupfile/"

    backup_req = get_request(backup_url)
    if not backup_req or backup_req.status_code != 200:
        return False

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    folder_name = "backup"
    file_name = f"backup_***REMOVED***dt_string***REMOVED***.json"

    file_name = os.path.join(folder_name, file_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(file_name, 'w+') as f:
        f.write(backup_req.text)
    return file_name


# Extract UUID from config
def extract_uuid_from_config(config):
    logging.info(f"Extract UUID from config")
    uuid_pattern = r"([0-9a-fA-F]***REMOVED***8***REMOVED***-(?:[0-9a-fA-F]***REMOVED***4***REMOVED***-)***REMOVED***3***REMOVED***[0-9a-fA-F]***REMOVED***12***REMOVED***)"
    match = re.search(uuid_pattern, config)

    if match:
        uuid = match.group(1)
        return uuid
    else:
        return None


# System status
def system_status():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    return ***REMOVED***
        'cpu': cpu_usage,
        'ram': ram_usage,
        'disk': disk_usage
    ***REMOVED***


# Search user by name
def search_user_by_name(name):
    users = list_users()
    if not users:
        return False
    res = []
    for user in users:
        if name.lower() in user['name'].lower():
            res.append(user)
    if res:
        return res
    return False


# Search user by uuid
def search_user_by_uuid(uuid):
    users = list_users()
    if not users:
        return False
    for user in users:
        if user['uuid'] == uuid:
            return user
    return False


# Base64 decoder
def base64decoder(s):
    import base64
    try:
        conf = base64.b64decode(s).decode("utf-8")
        conf = json.loads(conf)
    except Exception as e:
        logging.exception(f"Parse BeautifulSoup Exception: ***REMOVED***e***REMOVED***")
        conf = False

    return conf


# Search user by config
def search_user_by_config(config):
    if config.startswith("vmess://"):
        config = config.replace("vmess://", "")
        config = base64decoder(config)
        if config:
            uuid = config['id']
            user = search_user_by_uuid(uuid)
            if user:
                return user
    uuid = extract_uuid_from_config(config)
    if uuid:
        user = search_user_by_uuid(uuid)
        if user:
            return user
    return False


# Privacy-friendly logging - replace your panel url with panel.private.com
def privacy_friendly_logging_request(url):
    url = urlparse(url)
    url = url.scheme + "://" + "panel.private.com" + url.path
    return url
