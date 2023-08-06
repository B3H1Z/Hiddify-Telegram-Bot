# Description: API for connecting to the panel

from config import *
import AdminBot.template
import re
from datetime import datetime
import psutil
import logging

# Global variables
# Make Session for requests
session = requests.session()
# Base panel URL - example: https://panel.example.com
BASE_URL = urlparse(PANEL_URL).scheme + "://" + urlparse(PANEL_URL).netloc
# Users directory in panel
USERS_DIR = "/admin/user/"


# Get request - return request object
def get_request(url):
    logging.info(f"GET Request to {privacy_friendly_logging_request(url)}")
    global session
    try:
        req = session.get(url)
        logging.info(f"GET Request to {privacy_friendly_logging_request(url)} - Status Code: {req.status_code}")
        return req
    except requests.exceptions.ConnectionError as e:
        logging.exception(f"Connection Exception: {e}")
        return False
    except requests.exceptions.Timeout as e:
        logging.exception(f"Timeout Exception: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logging.exception(f"General Connection Exception: {e}")
        return False
    except Exception as e:
        logging.exception(f"General Exception: {e}")
        return False


# Post request - return request object
def post_request(url, data):
    logging.info(f"POST Request to {privacy_friendly_logging_request(url)} - Data: {data}")
    global session
    try:
        req = session.post(url, data=data)
        return req
    except requests.exceptions.ConnectionError as e:
        logging.exception(f"Connection Exception: {e}")
        return False
    except requests.exceptions.Timeout as e:
        logging.exception(f"Timeout Exception: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logging.exception(f"General Connection Exception: {e}")
        return False
    except Exception as e:
        logging.exception(f"General Exception: {e}")
        return False


def users_to_dict(users_dict):
    if not users_dict:
        return False
    users_array = []
    for user in users_dict:
        users_array.append({'id': user[0], 'uuid': user[1], 'name': user[2], 'last_online': user[3],
                            'expiry_time': user[4],
                            'usage_limit_GB': user[5], 'package_days': user[6], 'mode': user[7],
                            'monthly': user[8], 'start_date': user[9], 'current_usage_GB': user[10],
                            'last_reset_time': user[11], 'comment': user[12], 'telegram_id': user[13],
                            'added_by': user[14], 'max_ips': user[15], 'enable': user[16]})
    return users_array


def calculate_remaining_days(start_date, package_days):
    import datetime
    if start_date is None:
        return package_days
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    remaining_days = package_days - (datetime.datetime.now() - start_date).days
    return remaining_days


def calculate_remaining_usage(usage_limit_GB, current_usage_GB):
    remaining_usage = usage_limit_GB - current_usage_GB
    return round(remaining_usage, 2)


def calculate_remaining_last_online(last_online_date_time):
    import datetime
    if last_online_date_time == "0001-01-01 00:00:00.000000":
        return AdminBot.template.MESSAGES['NEVER']
    last_online_date_time = datetime.datetime.strptime(last_online_date_time, "%Y-%m-%d %H:%M:%S.%f")
    last_online_time = (datetime.datetime.now() - last_online_date_time)
    last_online = AdminBot.template.last_online_time_template(last_online_time)
    return last_online


# List users - return list of all users
def dict_process(users_dict):
    logging.info(f"Parse users page")
    if not users_dict:
        return False
    users_list = []
    for user in users_dict:
        users_list.append({
            "name": user['name'],
            "usage": {
                'usage_limit_GB': round(user['usage_limit_GB'], 2),
                'current_usage_GB': round(user['current_usage_GB'], 2),
                'remaining_usage_GB': calculate_remaining_usage(user['usage_limit_GB'], user['current_usage_GB'])
            },
            "remaining_day": calculate_remaining_days(user['start_date'], user['package_days']),
            "comment": user['comment'],
            "last_connection": calculate_remaining_last_online(user['last_online']) if user['last_online'] else None,
            "uuid": user['uuid'],
            "link": f"{BASE_URL}/{urlparse(PANEL_URL).path.split('/')[1]}/{user['uuid']}/",
            "mode": user['mode'],
            "enable": user['enable'],
        })

    return users_list


# Get single user info - return dict of user info
def user_info(uuid):
    logging.info(f"Get info of user single user - {uuid}")
    lu = dict_process(users_to_dict(DB.select_users()))
    if not lu:
        return False
    for user in lu:
        if user['uuid'] == uuid:
            return user
    return False


def sub_links(uuid):
    logging.info(f"Get sub links of user - {uuid}")
    sub = {}
    PANEL_DIR = urlparse(PANEL_URL).path.split('/')
    # Clash open app: clash://install-config?url=
    # Hidden open app: clashmeta://install-config?url=
    sub['clash_configs'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/clash/all.yml"
    sub['hiddify_configs'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/clash/meta/all.yml"
    sub['sub_link'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/all.txt"
    sub['sub_link_b64'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/all.txt"
    return sub


# Parse sub links
def sub_parse(sub):
    logging.info(f"Parse sub links")
    res = get_request(sub)
    if not res or res.status_code != 200:
        return False

    urls = re.findall(r'(vless:\/\/[^\n]+)|(vmess:\/\/[^\n]+)|(trojan:\/\/[^\n]+)', res.text)

    config_links = {
        'vless': [],
        'vmess': [],
        'trojan': []
    }
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
    backup_url = f"{BASE_URL}/{dir_panel[1]}/{dir_panel[2]}/admin/backup/backupfile/"

    backup_req = get_request(backup_url)
    if not backup_req or backup_req.status_code != 200:
        return False

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    folder_name = "Backup"
    file_name = f"Backup_{dt_string}.json"

    file_name = os.path.join(folder_name, file_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(file_name, 'w+') as f:
        f.write(backup_req.text)
    return file_name


# Extract UUID from config
def extract_uuid_from_config(config):
    logging.info(f"Extract UUID from config")
    uuid_pattern = r"([0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12})"
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
    return {
        'cpu': cpu_usage,
        'ram': ram_usage,
        'disk': disk_usage
    }


# Search user by name
def search_user_by_name(name):
    users = dict_process(users_to_dict(DB.select_users()))
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
    users = dict_process(users_to_dict(DB.select_users()))
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
