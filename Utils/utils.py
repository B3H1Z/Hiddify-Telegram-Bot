# Description: API for connecting to the panel
import json
import logging
import os
import random
import string
from io import BytesIO
import re
from datetime import datetime
from urllib.parse import urlparse
from Database.dbManager import USERS_DB
import psutil
import qrcode
import requests
from config import PANEL_URL, BACKUP_LOC, CLIENT_TOKEN
import AdminBot.templates
from Utils.api import api
# Global variables
# Make Session for requests
session = requests.session()
# Base panel URL - example: https://panel.example.com
BASE_URL = urlparse(PANEL_URL).scheme + "://" + urlparse(PANEL_URL).netloc


# Users directory in panel
# USERS_DIR = "/admin/user/"


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


# Change user data format
# def users_to_dict(users_dict):
#     if not users_dict:
#         return False
#     users_array = []
#     for user in users_dict:
#         users_array.append({'id': user[0], 'uuid': user[1], 'name': user[2], 'last_online': user[3],
#                             'expiry_time': user[4],
#                             'usage_limit_GB': user[5], 'package_days': user[6], 'mode': user[7],
#                             'monthly': user[8], 'start_date': user[9], 'current_usage_GB': user[10],
#                             'last_reset_time': user[11], 'comment': user[12], 'telegram_id': user[13],
#                             'added_by': user[14], 'max_ips': user[15], 'enable': user[16]})
#     return users_array

def users_to_dict(users_dict):
    print(f"users_dict: {users_dict}")
    if not users_dict:
        return False
    users_array = []
    for user in users_dict:
        users_array.append({'uuid': user['uuid'], 'name': user['name'], 'last_online': user['last_online'],
                            'expiry_time': None,
                            'usage_limit_GB': user['usage_limit_GB'], 'package_days': user['package_days'],
                            'mode': user['mode'],
                            'monthly': None, 'start_date': user['start_date'],
                            'current_usage_GB': user['current_usage_GB'],
                            'last_reset_time': user['last_reset_time'], 'comment': user['comment'],
                            'telegram_id': user['telegram_id'],
                            'added_by': user['added_by_uuid'], 'max_ips': None, 'enable': None})
    return users_array


# Change telegram user data format
def Telegram_users_to_dict(Tel_users_dict):
    if not Tel_users_dict:
        return False
    users_array = []
    for user in Tel_users_dict:
        users_array.append({'id': user[0], 'telegram_id': user[1], 'created_at': user[3], })
    return users_array


# Calculate remaining days
def calculate_remaining_days(start_date, package_days):
    import datetime
    if start_date is None:
        return package_days
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    remaining_days = package_days - (datetime.datetime.now() - start_date).days
    if remaining_days < 0:
        return 0
    return remaining_days


# Calculate remaining usage
def calculate_remaining_usage(usage_limit_GB, current_usage_GB):
    remaining_usage = usage_limit_GB - current_usage_GB
    return round(remaining_usage, 2)


# Calculate last online time
def calculate_remaining_last_online(last_online_date_time):
    import datetime
    if last_online_date_time == "0001-01-01 00:00:00.000000" or last_online_date_time == "1-01-01 00:00:00":
        return AdminBot.content.MESSAGES['NEVER']
    # last_online_date_time = datetime.datetime.strptime(last_online_date_time, "%Y-%m-%d %H:%M:%S.%f")
    last_online_date_time = datetime.datetime.strptime(last_online_date_time, "%Y-%m-%d %H:%M:%S")
    last_online_time = (datetime.datetime.now() - last_online_date_time)
    last_online = AdminBot.templates.last_online_time_template(last_online_time)
    return last_online


# Process users data - return list of users
def dict_process(users_dict, sub_id=None):
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
            "sub_id": sub_id
        })

    return users_list


# Get single user info - return dict of user info
def user_info(uuid):
    logging.info(f"Get info of user single user - {uuid}")
    lu = api.select()
    if not lu:
        return False
    for user in lu:
        if user['uuid'] == uuid:
            return user
    return False


# Get sub links - return dict of sub links
def sub_links(uuid):
    logging.info(f"Get sub links of user - {uuid}")
    sub = {}
    PANEL_DIR = urlparse(PANEL_URL).path.split('/')
    # Clash open app: clash://install-config?url=
    # Hidden open app: clashmeta://install-config?url=
    sub['clash_configs'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/clash/all.yml"
    sub['hiddify_configs'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/clash/meta/all.yml"
    sub['sub_link'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/all.txt"
    sub['sub_link_b64'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/all.txt?base64=True"
    # Add in v8.0 Hiddify
    sub['sub_link_auto'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/sub/?asn=unknown"
    sub['sing_box_full'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/full-singbox.json?asn=unknown"
    sub['sing_box'] = f"{BASE_URL}/{PANEL_DIR[1]}/{uuid}/singbox.json?asn=unknown"
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

    file_name = f"Backup_{dt_string}.json"

    file_name = os.path.join(BACKUP_LOC, file_name)
    if not os.path.exists(BACKUP_LOC):
        os.makedirs(BACKUP_LOC)
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
    # users = dict_process(users_to_dict(ADMIN_DB.select_users()))
    users = api.select()
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
    # users = dict_process(users_to_dict(ADMIN_DB.select_users()))
    users = api.select()
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


# Check text is it config or sub
def is_it_config_or_sub(config):
    if config.startswith("vmess://"):
        config = config.replace("vmess://", "")
        config = base64decoder(config)
        if config:
            return config['id']
    uuid = extract_uuid_from_config(config)
    if uuid:
        return uuid


# Users bot add plan
def users_bot_add_plan(size, days, price):
    if not CLIENT_TOKEN:
        return False
    # randon 4 digit number
    plan_id = random.randint(10000, 99999)
    plan_status = USERS_DB.add_plan(plan_id, size, days, price)
    if not plan_status:
        return False
    return True


# Check user is expired
def is_user_expired(user):
    if user['remaining_day'] == 0:
        return True
    return False


# Expired users list
def expired_users_list(users):
    expired_users = []
    for user in users:
        if is_user_expired(user):
            expired_users.append(user)
    return expired_users


# Text to QR code
def txt_to_qr(txt):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(txt)
    qr.make(fit=True, )
    img_qr = qr.make_image(fill_color="black", back_color="white")
    stream = BytesIO()
    img_qr.save(stream)
    img = stream.getvalue()

    return img


# List of users who not ordered from bot (Link Subscription)
def non_order_user_info(telegram_id):
    users_list = []
    non_ordered_subscriptions = USERS_DB.find_non_order_subscription(telegram_id=telegram_id)
    if non_ordered_subscriptions:
        for subscription in non_ordered_subscriptions:
            # non_order_user = ADMIN_DB.find_user(uuid=subscription['uuid'])
            non_order_user = api.find(subscription['uuid'])
            # print(f"non_order_user:{non_order_user}")
            # non_order_user = search_by_property(non_order_user, uuid=subscription['uuid'])

            if non_order_user:
                non_order_user = users_to_dict([non_order_user])
                non_order_user = dict_process(non_order_user, subscription['id'])
                if non_order_user:
                    non_order_user = non_order_user[0]
                    users_list.append(non_order_user)
    return users_list


# List of users who ordered from bot and made payment
def order_user_info(telegram_id):
    users_list = []
    orders = USERS_DB.find_order(telegram_id=telegram_id)
    if orders:
        for order in orders:
            ordered_subscriptions = USERS_DB.find_order_subscription(order_id=order['id'])
            if ordered_subscriptions:
                for subscription in ordered_subscriptions:
                    order_user = api.find(subscription['uuid'])
                    # print(f"order_user:{order_user}")
                    # order_user = search_by_property(order_user, uuid=subscription['uuid'])
                    if order_user:
                        order_user = users_to_dict([order_user])
                        order_user = dict_process(order_user, subscription['id'])
                        if order_user:
                            order_user = order_user[0]
                            users_list.append(order_user)
    return users_list


# Replace last three characters of a string with random numbers (For Payment)
def replace_last_three_with_random(input_string):
    if len(input_string) <= 3:
        return input_string  # Not enough characters to replace

    random_numbers = ''.join(random.choice(string.digits) for _ in range(3))
    modified_string = input_string[:-3] + random_numbers
    return modified_string


# Privacy-friendly logging - replace your panel url with panel.private.com
def privacy_friendly_logging_request(url):
    url = urlparse(url)
    url = url.scheme + "://" + "panel.private.com" + url.path
    return url


# def settings_config_to_dict(configs):
#     dict_configs = {}
#     for entry in configs:
#         key = entry['key']
#         value = entry['value']
#         dict_configs[key] = value
#     return dict_configs


def all_configs_settings():
    bool_configs = USERS_DB.select_bool_config()
    int_configs = USERS_DB.select_int_config()
    str_configs = USERS_DB.select_str_config()

    # all configs to one dict
    all_configs = {}
    for config in bool_configs:
        all_configs[config['key']] = config['value']
    for config in int_configs:
        all_configs[config['key']] = config['value']
    for config in str_configs:
        all_configs[config['key']] = config['value']
    return all_configs


def find_order_subscription_by_uuid(uuid):
    order_subscription = USERS_DB.find_order_subscription(uuid=uuid)
    non_order_subscription = USERS_DB.find_non_order_subscription(uuid=uuid)
    if order_subscription:
        return order_subscription[0]
    elif non_order_subscription:
        return non_order_subscription[0]
    else:
        return False


def toman_to_rial(toman):
    return int(toman) * 10


def rial_to_toman(rial):
    return int(int(rial) / 10)


def search_by_property(list, **kwargs):
    print(f"kwargs:{kwargs}")
    for item in list:
        if all(item[key] == value for key, value in kwargs.items()):
            print(f"item:{item}")
            return item
    return None
