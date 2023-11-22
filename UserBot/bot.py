import datetime
import random

import telebot
from telebot.types import Message, CallbackQuery
from config import *
from AdminBot.templates import configs_template
from UserBot.markups import *
from UserBot.templates import *
from UserBot.content import *

import Utils.utils as utils
from Shared.common import admin_bot
from Database.dbManager import USERS_DB
from Utils import api

# *********************************** Configuration Bot ***********************************
bot = telebot.TeleBot(CLIENT_TOKEN, parse_mode="HTML")
bot.remove_webhook()
admin_bot = admin_bot()
BASE_URL = f"{urlparse(PANEL_URL).scheme}://{urlparse(PANEL_URL).netloc}"
selected_server_id = 0

# *********************************** Helper Functions ***********************************
# Check if message is digit
def is_it_digit(message: Message,allow_float=False, response=MESSAGES['ERROR_INVALID_NUMBER'], markup=main_menu_keyboard_markup()):
    if not message.text:
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return False
    try:
        value = float(message.text) if allow_float else int(message.text)
        return True
    except ValueError:
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return False


# Check if message is cancel
def is_it_cancel(message: Message, response=MESSAGES['CANCELED']):
    if message.text == KEY_MARKUP['CANCEL']:
        bot.send_message(message.chat.id, response, reply_markup=main_menu_keyboard_markup())
        return True
    return False


# Check if message is command
def is_it_command(message: Message):
    if message.text.startswith("/"):
        return True
    return False


# Check is it UUID, Config or Subscription Link
def type_of_subscription(text):
    if text.startswith("vmess://"):
        config = text.replace("vmess://", "")
        config = utils.base64decoder(config)
        if not config:
            return False
        uuid = config['id']
    else:
        uuid = utils.extract_uuid_from_config(text)
    return uuid

# check is user banned
def is_user_banned(user_id):
    user = USERS_DB.find_user(telegram_id=user_id)
    if user:
        user = user[0]
        if user['banned']:
            bot.send_message(user_id, MESSAGES['BANNED_USER'], reply_markup=main_menu_keyboard_markup())
            return True
    return False
# *********************************** Next-Step Handlers ***********************************
# ----------------------------------- Buy Plan Area -----------------------------------
charge_wallet = {}
renew_subscription_dict = {}


def user_channel_status(user_id):
    try:
        settings = utils.all_configs_settings()
        if settings['channel_id']:
            user = bot.get_chat_member(settings['channel_id'], user_id)
            return user.status in ['member', 'administrator', 'creator']
        else:
            return True
    except telebot.apihelper.ApiException as e:
        logging.error("ApiException: %s" % e)
        return False


def is_user_in_channel(user_id):
    settings = all_configs_settings()
    if settings['force_join_channel'] == 1:
        if not settings['channel_id']:
            return True
        if not user_channel_status(user_id):
            bot.send_message(user_id, MESSAGES['REQUEST_JOIN_CHANNEL'],
                             reply_markup=force_join_channel_markup(settings['channel_id']))
            return False
    return True

# Next Step Buy From Wallet - Confirm
def buy_from_wallet_confirm(message: Message, plan):
    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    if not wallet:
        # Wallet not created
        bot.send_message(message.chat.id, MESSAGES['LACK_OF_WALLET_BALANCE'],
                         reply_markup=wallet_info_markup())
    if wallet:
        wallet = wallet[0]
        if plan['price'] > wallet['balance']:
            bot.send_message(message.chat.id, MESSAGES['LACK_OF_WALLET_BALANCE'],
                             reply_markup=wallet_info_specific_markup(plan['price'] - wallet['balance']))
            return
        else:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'], reply_markup=cancel_markup())
            bot.register_next_step_handler(message, next_step_send_name_for_buy_from_wallet, plan)


def renewal_from_wallet_confirm(message: Message):
    if not renew_subscription_dict:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    if not renew_subscription_dict[message.chat.id]:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    if not renew_subscription_dict[message.chat.id]['plan_id'] or not renew_subscription_dict[message.chat.id][
        'uuid']:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    uuid = renew_subscription_dict[message.chat.id]['uuid']
    plan_id = renew_subscription_dict[message.chat.id]['plan_id']

    wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    if not wallet:
        status = USERS_DB.add_wallet(telegram_id=message.chat.id)
        if not status:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return

    wallet = wallet[0]
    plan_info = USERS_DB.find_plan(id=plan_id)
    if not plan_info:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    plan_info = plan_info[0]
    if plan_info['price'] > wallet['balance']:
        bot.send_message(message.chat.id, MESSAGES['LACK_OF_WALLET_BALANCE'],reply_markup=wallet_info_specific_markup(plan_info['price'] - wallet['balance']))
        del renew_subscription_dict[message.chat.id]
        return

    server_id = plan_info['server_id']
    server = USERS_DB.find_server(id=server_id)
    if not server:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    server = server[0]
    URL = server['url'] + API_PATH
    user = api.find(URL, uuid=uuid)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    user_info = utils.users_to_dict([user])
    if not user_info:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    user_info_process = utils.dict_process(URL, user_info)
    user_info = user_info[0]

    if not user_info_process:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    user_info_process = user_info_process[0]
    new_balance = int(wallet['balance']) - int(plan_info['price'])
    edit_wallet = USERS_DB.edit_wallet(message.chat.id, balance=new_balance)
    if not edit_wallet:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    last_reset_time = datetime.datetime.now().strftime("%Y-%m-%d")    
    sub = utils.find_order_subscription_by_uuid(uuid) 
    if not sub:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return   
    settings = utils.all_configs_settings()
    #Default renewal mode
    if settings['renewal_method'] == 1:
        if user_info_process['remaining_day'] <= 0 or user_info_process['usage']['remaining_usage_GB'] <= 0:
            new_usage_limit = plan_info['size_gb']
            new_package_days = plan_info['days']
            current_usage_GB = 0
            edit_status = api.update(URL, uuid=uuid, usage_limit_GB=new_usage_limit, package_days=new_package_days,start_date=last_reset_time, current_usage_GB=current_usage_GB,comment=f"HidyBot:{sub['id']}")

        else:
            new_usage_limit = user_info['usage_limit_GB'] + plan_info['size_gb']
            new_package_days = plan_info['days'] + (user_info['package_days'] - user_info_process['remaining_day'])
            edit_status = api.update(URL, uuid=uuid, usage_limit_GB=new_usage_limit, package_days=new_package_days,last_reset_time=last_reset_time,comment=f"HidyBot:{sub['id']}")


    #advance renewal mode        
    elif settings['renewal_method'] == 2:
            new_usage_limit = plan_info['size_gb']
            new_package_days = plan_info['days']
            current_usage_GB = 0
            edit_status = api.update(URL, uuid=uuid, usage_limit_GB=new_usage_limit, start_date=last_reset_time, package_days=new_package_days, current_usage_GB=current_usage_GB,comment=f"HidyBot:{sub['id']}")

    
    #Fair renewal mode
    elif settings['renewal_method'] == 3:
        if user_info_process['remaining_day'] <= 0 or user_info_process['usage']['remaining_usage_GB'] <= 0:
            new_usage_limit = plan_info['size_gb']
            new_package_days = plan_info['days']
            current_usage_GB = 0
            edit_status = api.update(URL, uuid=uuid, usage_limit_GB=new_usage_limit, package_days=new_package_days,start_date=last_reset_time, current_usage_GB=current_usage_GB,comment=f"HidyBot:{sub['id']}")
        else:
            print(user_info)
            new_usage_limit = user_info['usage_limit_GB'] + plan_info['size_gb']
            new_package_days = plan_info['days'] + user_info['package_days']
            edit_status = api.update(URL, uuid=uuid, usage_limit_GB=new_usage_limit,package_days=new_package_days,last_reset_time=last_reset_time,comment=f"HidyBot:{sub['id']}")

            

    if not edit_status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    # Add New Order
    order_id = random.randint(1000000, 9999999)
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = USERS_DB.add_order(order_id, message.chat.id,user_info_process['name'], plan_id, created_at)
    if not status:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    # edit_status = ADMIN_DB.edit_user(uuid=uuid, usage_limit_GB=new_usage_limit, package_days=new_package_days)
    # edit_status = api.update(URL, uuid=uuid, usage_limit_GB=new_usage_limit, package_days=new_package_days)
    # if not edit_status:
    #     bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
    #                      reply_markup=main_menu_keyboard_markup())
    #     return

    bot.send_message(message.chat.id, MESSAGES['SUCCESSFUL_RENEWAL'], reply_markup=main_menu_keyboard_markup())
    update_info_subscription(message, uuid)
    BASE_URL = urlparse(server['url']).scheme + "://" + urlparse(server['url']).netloc
    link = f"{BASE_URL}/{urlparse(server['url']).path.split('/')[1]}/{uuid}/"
    user_name = f"<a href='{link}'> {user_info_process['name']} </a>"
    bot_users = USERS_DB.find_user(telegram_id=message.chat.id)
    if bot_users:
        bot_user = bot_users[0]
    for ADMIN in ADMINS_ID:
        admin_bot.send_message(ADMIN,
                               f"""{MESSAGES['ADMIN_NOTIFY_NEW_RENEWAL']} {user_name} {MESSAGES['ADMIN_NOTIFY_NEW_RENEWAL_2']}
{MESSAGES['SERVER']}<a href='{server['url']}/admin'> {server['title']} </a>
{MESSAGES['INFO_ID']} <code>{sub['id']}</code>""", reply_markup=notify_to_admin_markup(bot_user))


# Next Step Buy Plan - Send Screenshot

def next_step_send_screenshot(message, charge_wallet):
    if is_it_cancel(message):
        return
    if not charge_wallet:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    if message.content_type != 'photo':
        bot.send_message(message.chat.id, MESSAGES['ERROR_TYPE_SEND_SCREENSHOT'], reply_markup=cancel_markup())
        bot.register_next_step_handler(message, next_step_send_screenshot, charge_wallet)
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"{message.chat.id}-{charge_wallet['id']}.jpg"
    path_recp = os.path.join(os.getcwd(), 'UserBot', 'Receiptions', file_name)
    if not os.path.exists(os.path.join(os.getcwd(), 'UserBot', 'Receiptions')):
        os.makedirs(os.path.join(os.getcwd(), 'UserBot', 'Receiptions'))
    with open(path_recp, 'wb') as new_file:
        new_file.write(downloaded_file)

    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payment_method = "Card"

    status = USERS_DB.add_payment(charge_wallet['id'], message.chat.id,
                                  charge_wallet['amount'], payment_method, file_name, created_at)
    if status:
        payment = USERS_DB.find_payment(id=charge_wallet['id'])
        if not payment:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        payment = payment[0]
        user_data = USERS_DB.find_user(telegram_id=message.chat.id)
        if not user_data:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        user_data = user_data[0]
        for ADMIN in ADMINS_ID:
            admin_bot.send_photo(ADMIN, open(path_recp, 'rb'),
                                 caption=payment_received_template(payment,user_data),
                                 reply_markup=confirm_payment_by_admin(charge_wallet['id']))
        bot.send_message(message.chat.id, MESSAGES['WAIT_FOR_ADMIN_CONFIRMATION'],
                         reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        
# Next Step Payment - Send Answer
def next_step_answer_to_admin(message, admin_id):
    if is_it_cancel(message):
        return
    bot_users = USERS_DB.find_user(telegram_id=message.chat.id)
    if bot_users:
        bot_user = bot_users[0]
    admin_bot.send_message(int(admin_id), f"{MESSAGES['NEW_TICKET_RECEIVED']}\n{MESSAGES['TICKET_TEXT']} {message.text}",
                           reply_markup=answer_to_user_markup(bot_user,message.chat.id))
    bot.send_message(message.chat.id, MESSAGES['SEND_TICKET_TO_ADMIN_RESPONSE'],
                         reply_markup=main_menu_keyboard_markup())

# Next Step Payment - Send Ticket To Admin
def next_step_send_ticket_to_admin(message):
    if is_it_cancel(message):
        return
    bot_users = USERS_DB.find_user(telegram_id=message.chat.id)
    if bot_users:
        bot_user = bot_users[0]
    for ADMIN in ADMINS_ID:
        admin_bot.send_message(ADMIN, f"{MESSAGES['NEW_TICKET_RECEIVED']}\n{MESSAGES['TICKET_TEXT']} {message.text}",
                               reply_markup=answer_to_user_markup(bot_user,message.chat.id))
        bot.send_message(message.chat.id, MESSAGES['SEND_TICKET_TO_ADMIN_RESPONSE'],
                            reply_markup=main_menu_keyboard_markup())

# ----------------------------------- Buy From Wallet Area -----------------------------------
# Next Step Buy From Wallet - Send Name
def next_step_send_name_for_buy_from_wallet(message: Message, plan):
    if is_it_cancel(message):
        return

    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    name = message.text
    while is_it_command(message):
        message = bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'])
        bot.register_next_step_handler(message, next_step_send_name_for_buy_from_wallet, plan)
        return
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    paid_amount = plan['price']

    order_id = random.randint(1000000, 9999999)
    server_id = plan['server_id']
    server = USERS_DB.find_server(id=server_id)
    if not server:
        bot.send_message(message.chat.id, f"{MESSAGES['UNKNOWN_ERROR']}:Server Not Found",
                         reply_markup=main_menu_keyboard_markup())
        return
    server = server[0]
    URL = server['url'] + API_PATH

    # value = ADMIN_DB.add_default_user(name, plan['days'], plan['size_gb'],)
    sub_id = random.randint(1000000, 9999999)
    value = api.insert(URL, name=name, usage_limit_GB=plan['size_gb'], package_days=plan['days'],comment=f"HidyBot:{sub_id}")
    if not value:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}:Create User Error\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    add_sub_status = USERS_DB.add_order_subscription(sub_id, order_id, value, server_id)
    if not add_sub_status:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}:Add Subscription Error\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    status = USERS_DB.add_order(order_id, message.chat.id,name, plan['id'], created_at)
    if not status:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}:Add Order Error\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    if wallet:
        wallet = wallet[0]
        wallet_balance = int(wallet['balance']) - int(paid_amount)
        user_info = USERS_DB.edit_wallet(message.chat.id, balance=wallet_balance)
        if not user_info:
            bot.send_message(message.chat.id,
                             f"{MESSAGES['UNKNOWN_ERROR']}:Edit Wallet Balance Error\n{MESSAGES['ORDER_ID']} {order_id}",
                             reply_markup=main_menu_keyboard_markup())
            return
    bot.send_message(message.chat.id,
                     f"{MESSAGES['PAYMENT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {order_id}",
                     reply_markup=main_menu_keyboard_markup())
    
    user_info = api.find(URL, value)
    user_info = utils.users_to_dict([user_info])
    user_info = utils.dict_process(URL, user_info)
    user_info = user_info[0]
    api_user_data = user_info_template(sub_id, server, user_info, MESSAGES['INFO_USER'])
    bot.send_message(message.chat.id, api_user_data,
                                 reply_markup=user_info_markup(user_info['uuid']))
    
    BASE_URL = urlparse(server['url']).scheme + "://" + urlparse(server['url']).netloc
    link = f"{BASE_URL}/{urlparse(server['url']).path.split('/')[1]}/{value}/"
    user_name = f"<a href='{link}'> {name} </a>"
    bot_users = USERS_DB.find_user(telegram_id=message.chat.id)
    if bot_users:
        bot_user = bot_users[0]
    for ADMIN in ADMINS_ID:
        admin_bot.send_message(ADMIN,
                               f"""{MESSAGES['ADMIN_NOTIFY_NEW_SUB']} {user_name} {MESSAGES['ADMIN_NOTIFY_CONFIRM']}
{MESSAGES['SERVER']}<a href='{server['url']}/admin'> {server['title']} </a>
{MESSAGES['INFO_ID']} <code>{sub_id}</code>""", reply_markup=notify_to_admin_markup(bot_user))


# ----------------------------------- Get Free Test Area -----------------------------------
# Next Step Get Free Test - Send Name
def next_step_send_name_for_get_free_test(message: Message, server_id):
    if is_it_cancel(message):
        return
    name = message.text
    while is_it_command(message):
        message = bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'])
        bot.register_next_step_handler(message, next_step_send_name_for_get_free_test)
        return

    settings = utils.all_configs_settings()
    test_user_comment = "HidyBot:FreeTest"
    server = USERS_DB.find_server(id=server_id)
    if not server:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    server = server[0]
    URL = server['url'] + API_PATH
    # uuid = ADMIN_DB.add_default_user(name, test_user_days, test_user_size_gb, int(PANEL_ADMIN_ID), test_user_comment)
    uuid = api.insert(URL, name=name, usage_limit_GB=settings['test_sub_size_gb'], package_days=settings['test_sub_days'],
                      comment=test_user_comment)
    if not uuid:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    non_order_id = random.randint(10000000, 99999999)
    non_order_status = USERS_DB.add_non_order_subscription(non_order_id, message.chat.id, uuid, server_id)
    if not non_order_status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    edit_user_status = USERS_DB.edit_user(message.chat.id, test_subscription=True)
    if not edit_user_status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['GET_FREE_CONFIRMED'],
                     reply_markup=main_menu_keyboard_markup())
    user_info = api.find(URL, uuid)
    user_info = utils.users_to_dict([user_info])
    user_info = utils.dict_process(URL, user_info)
    user_info = user_info[0]
    api_user_data = user_info_template(non_order_id, server, user_info, MESSAGES['INFO_USER'])
    bot.send_message(message.chat.id, api_user_data,
                                 reply_markup=user_info_markup(user_info['uuid']))
    BASE_URL = urlparse(server['url']).scheme + "://" + urlparse(server['url']).netloc
    link = f"{BASE_URL}/{urlparse(server['url']).path.split('/')[1]}/{uuid}/"
    user_name = f"<a href='{link}'> {name} </a>"
    bot_users = USERS_DB.find_user(telegram_id=message.chat.id)
    if bot_users:
        bot_user = bot_users[0]
    for ADMIN in ADMINS_ID:
        admin_bot.send_message(ADMIN,
                               f"""{MESSAGES['ADMIN_NOTIFY_NEW_FREE_TEST']} {user_name} {MESSAGES['ADMIN_NOTIFY_CONFIRM']}
{MESSAGES['SERVER']}<a href='{server['url']}/admin'> {server['title']} </a>
{MESSAGES['INFO_ID']} <code>{non_order_id}</code>""", reply_markup=notify_to_admin_markup(bot_user))


# ----------------------------------- To QR Area -----------------------------------
# Next Step QR - QR Code
def next_step_to_qr(message: Message):
    if is_it_cancel(message):
        return
    if not message.text:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    is_it_valid = utils.is_it_config_or_sub(message.text)
    if is_it_valid:
        qr_code = utils.txt_to_qr(message.text)
        if qr_code:
            bot.send_photo(message.chat.id, qr_code, reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_TO_QR_ERROR'],
                         reply_markup=main_menu_keyboard_markup())


# ----------------------------------- Link Subscription Area -----------------------------------
# Next Step Link Subscription to bot
def next_step_link_subscription(message: Message):
    if not message.text:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    if is_it_cancel(message):
        return
    uuid = utils.is_it_config_or_sub(message.text)
    if uuid:
        # check is it already subscribed
        is_it_subscribed = utils.is_it_subscription_by_uuid_and_telegram_id(uuid, message.chat.id)
        if is_it_subscribed:
            bot.send_message(message.chat.id, MESSAGES['ALREADY_SUBSCRIBED'],
                             reply_markup=main_menu_keyboard_markup())
            return
        non_sub_id = random.randint(10000000, 99999999)
        servers = USERS_DB.select_servers()
        if not servers:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'], reply_markup=main_menu_keyboard_markup())
            return
        server_id = None
        for server in servers:
            users_list = api.find(server['url'] + API_PATH, uuid)
            if users_list:
                server_id = server['id']
                break
        if not server_id:
             bot.send_message(message.chat.id, f"{MESSAGES['UNKNOWN_ERROR']}-server not found",
                             reply_markup=main_menu_keyboard_markup())
        status = USERS_DB.add_non_order_subscription(non_sub_id, message.chat.id, uuid, server_id)
        if status:
            bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_CONFIRMED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_INFO_NOT_FOUND'],
                         reply_markup=main_menu_keyboard_markup())


# ----------------------------------- wallet balance Area -----------------------------------
# Next Step increase wallet balance - Send amount
def next_step_increase_wallet_balance(message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=cancel_markup()):
        bot.register_next_step_handler(message, next_step_increase_wallet_balance)
        return
    minimum_deposit_amount = utils.all_configs_settings()
    minimum_deposit_amount = minimum_deposit_amount['min_deposit_amount']
    amount = utils.toman_to_rial(message.text)
    if amount < minimum_deposit_amount:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['INCREASE_WALLET_BALANCE_AMOUNT']}\n{MESSAGES['MINIMUM_DEPOSIT_AMOUNT']}: "
                         f"{rial_to_toman(minimum_deposit_amount)} {MESSAGES['TOMAN']}", reply_markup=cancel_markup())
        bot.register_next_step_handler(message, next_step_increase_wallet_balance)
        return
    settings = utils.all_configs_settings()
    if not settings:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    charge_wallet['amount'] = str(amount)
    if settings['three_random_num_price'] == 1:
        charge_wallet['amount'] = utils.replace_last_three_with_random(str(amount))

    charge_wallet['id'] = random.randint(1000000, 9999999)
    # Send 0 to identify wallet balance charge
    bot.send_message(message.chat.id,
                     owner_info_template(settings['card_number'], settings['card_holder'], charge_wallet['amount']),
                     reply_markup=send_screenshot_markup(plan_id=charge_wallet['id']))

def increase_wallet_balance_specific(message,amount):
    settings = utils.all_configs_settings()
    user = USERS_DB.find_user(telegram_id=message.chat.id)
    if user:
        wallet_status = USERS_DB.find_wallet(telegram_id=message.chat.id)
        if not wallet_status:
            status = USERS_DB.add_wallet(telegram_id=message.chat.id)
            if not status:
                bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'])
                return
    charge_wallet['amount'] = str(amount)
    if settings['three_random_num_price'] == 1:
        charge_wallet['amount'] = utils.replace_last_three_with_random(str(amount))

    charge_wallet['id'] = random.randint(1000000, 9999999)

    # Send 0 to identify wallet balance charge
    bot.send_message(message.chat.id,
                     owner_info_template(settings['card_number'], settings['card_holder'], charge_wallet['amount']),
                     reply_markup=send_screenshot_markup(plan_id=charge_wallet['id']))
    


def update_info_subscription(message: Message, uuid,markup=None):
    value = uuid
    sub = utils.find_order_subscription_by_uuid(value)
    if not sub:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    if not markup:
        if sub.get('telegram_id', None):
            # Non-Order Subscription markup
            mrkup = user_info_non_sub_markup(sub['uuid'])
        else:
            # Ordered Subscription markup
            mrkup = user_info_markup(sub['uuid'])
    else:
        mrkup = markup
    server_id = sub['server_id']
    server = USERS_DB.find_server(id=server_id)
    if not server:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    server = server[0]
    URL = server['url'] + API_PATH
    user = api.find(URL, uuid=sub['uuid'])
    if not user:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    user = utils.dict_process(URL, utils.users_to_dict([user]))[0]
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=user_info_template(sub['id'], server, user, MESSAGES['INFO_USER']),
                              reply_markup=mrkup)
    except:
        pass


# *********************************** Callback Query Area ***********************************
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    bot.clear_step_handler(call.message)
    if is_user_banned(call.message.chat.id):
        return
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    value = data[1]

    global selected_server_id
    # ----------------------------------- Link Subscription Area -----------------------------------
    # Confirm Link Subscription
    if key == 'force_join_status':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        join_status = is_user_in_channel(call.message.chat.id)

        if not join_status:
            return
        else:
            bot.send_message(call.message.chat.id, MESSAGES['JOIN_CHANNEL_SUCCESSFUL'])
            
    elif key == 'confirm_subscription':
        edit_status = USERS_DB.add_non_order_subscription(call.message.chat.id, value, )
        if edit_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_CONFIRMED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
    # Reject Link Subscription
    elif key == 'cancel_subscription':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['CANCEL_SUBSCRIPTION'],
                         reply_markup=main_menu_keyboard_markup())

    # ----------------------------------- Buy Plan Area -----------------------------------
    elif key == 'server_selected':
        if value == 'False':
            bot.send_message(call.message.chat.id, MESSAGES['SERVER_IS_FULL'], reply_markup=main_menu_keyboard_markup())
            return
        selected_server_id = int(value)
        plans = USERS_DB.find_plan(server_id=int(value))
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['PLANS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
            return
        plan_markup = plans_list_markup(plans)
        if not plan_markup:
            bot.send_message(call.message.chat.id, MESSAGES['PLANS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
            return
        bot.edit_message_text(MESSAGES['PLANS_LIST'], call.message.chat.id, call.message.message_id,
                                    reply_markup=plan_markup)
        
    elif key == 'free_test_server_selected':
        if value == 'False':
            bot.send_message(call.message.chat.id, MESSAGES['SERVER_IS_FULL'], reply_markup=main_menu_keyboard_markup())
            return
        users = USERS_DB.find_user(telegram_id=call.message.chat.id)
        if users:
            user = users[0]
            if user['test_subscription']:
                bot.send_message(call.message.chat.id, MESSAGES['ALREADY_RECEIVED_FREE'],
                                reply_markup=main_menu_keyboard_markup())
                return
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['REQUEST_SEND_NAME'], reply_markup=cancel_markup())
            bot.register_next_step_handler(call.message, next_step_send_name_for_get_free_test, value)
    # Send Asked Plan Info
    elif key == 'plan_selected':
        plan = USERS_DB.find_plan(id=value)[0]
        if not plan:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=plan_info_template(plan),
                              reply_markup=confirm_buy_plan_markup(plan['id']))

    # Confirm To Buy From Wallet
    elif key == 'confirm_buy_from_wallet':
        plan = USERS_DB.find_plan(id=value)[0]
        buy_from_wallet_confirm(call.message, plan)
    elif key == 'confirm_renewal_from_wallet':
        plan = USERS_DB.find_plan(id=value)[0]
        renewal_from_wallet_confirm(call.message)

    # Ask To Send Screenshot
    elif key == 'send_screenshot':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['REQUEST_SEND_SCREENSHOT'])
        bot.register_next_step_handler(call.message, next_step_send_screenshot, charge_wallet)

    #Answer to Admin After send Screenshot
    elif key == 'answer_to_admin':
        #bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['ANSWER_TO_ADMIN'],
                        reply_markup=cancel_markup())
        bot.register_next_step_handler(call.message, next_step_answer_to_admin, value)

    #Send Ticket to Admin 
    elif key == 'send_ticket_to_support':
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['SEND_TICKET_TO_ADMIN'],
                        reply_markup=cancel_markup())
        bot.register_next_step_handler(call.message, next_step_send_ticket_to_admin)

    # ----------------------------------- User Subscriptions Info Area -----------------------------------
    # Unlink non-order subscription
    elif key == 'unlink_subscription':
        delete_status = USERS_DB.delete_non_order_subscription(uuid=value)
        if delete_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_UNLINKED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())

    elif key == 'update_info_subscription':
        update_info_subscription(call.message, value)

    # ----------------------------------- wallet Area -----------------------------------
    # INCREASE WALLET BALANCE
    elif key == 'increase_wallet_balance':
        bot.send_message(call.message.chat.id, MESSAGES['INCREASE_WALLET_BALANCE_AMOUNT'], reply_markup=cancel_markup())

        bot.register_next_step_handler(call.message, next_step_increase_wallet_balance)
    elif key == 'increase_wallet_balance_specific':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        increase_wallet_balance_specific(call.message,value)
    elif key == 'renewal_subscription':
        settings = utils.all_configs_settings()
        if not settings['renewal_subscription_status']:
            bot.send_message(call.message.chat.id, MESSAGES['RENEWAL_SUBSCRIPTION_CLOSED'],
                             reply_markup=main_menu_keyboard_markup())
            return
        servers = USERS_DB.select_servers()
        server_id = 0
        user= []
        URL = "url"
        if servers:
            for server in servers:
                user = api.find(server['url'] + API_PATH, value)
                if user:
                    selected_server_id = server['id']
                    URL = server['url'] + API_PATH
                    break
        if not user:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        user_info = utils.users_to_dict([user])
        if not user_info:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return

        user_info_process = utils.dict_process(URL, user_info)
        if not user_info_process:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        user_info_process = user_info_process[0]
        if settings['renewal_method'] == 2:
            if user_info_process['remaining_day'] > settings['advanced_renewal_days'] and user_info_process['usage']['remaining_usage_GB'] > settings['advanced_renewal_usage']:
                bot.send_message(call.message.chat.id, renewal_unvalable_template(settings),
                                 reply_markup=main_menu_keyboard_markup())
                return
        

        renew_subscription_dict[call.message.chat.id] = {
            'uuid': None,
            'plan_id': None,
        }
        plans = USERS_DB.find_plan(server_id=selected_server_id)
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['PLANS_NOT_FOUND'],
                             reply_markup=main_menu_keyboard_markup())
            return
        renew_subscription_dict[call.message.chat.id]['uuid'] = value
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=plans_list_markup(plans, renewal=True,uuid=user_info_process['uuid']))

    elif key == 'renewal_plan_selected':
        plan = USERS_DB.find_plan(id=value)[0]
        if not plan:
            bot.send_message(call.message.chat.id, MESSAGES['PLANS_NOT_FOUND'],
                             reply_markup=main_menu_keyboard_markup())
            return
        renew_subscription_dict[call.message.chat.id]['plan_id'] = plan['id']
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=plan_info_template(plan),
                              reply_markup=confirm_buy_plan_markup(plan['id'], renewal=True,uuid=renew_subscription_dict[call.message.chat.id]['uuid']))

    elif key == 'cancel_increase_wallet_balance':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['CANCEL_INCREASE_WALLET_BALANCE'],
                         reply_markup=main_menu_keyboard_markup())
    # ----------------------------------- User Configs Area -----------------------------------
    # User Configs - Main Menu
    elif key == 'configs_list':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_url_user_list_markup(value))
    # User Configs - Direct Link
    elif key == 'conf_dir':
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_user_list_markup(value,configs))
        
    # User Configs - Vless Configs Callback
    elif key == "conf_dir_vless":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        if not configs['vless']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        msgs = configs_template(configs['vless'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=main_menu_keyboard_markup())
    # User Configs - VMess Configs Callback
    elif key == "conf_dir_vmess":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        if not configs['vmess']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        msgs = configs_template(configs['vmess'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=main_menu_keyboard_markup())
    # User Configs - Trojan Configs Callback
    elif key == "conf_dir_trojan":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        if not configs['trojan']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        msgs = configs_template(configs['trojan'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=main_menu_keyboard_markup())

    # User Configs - Subscription Configs Callback
    elif key == "conf_sub_url":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['sub_link'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_SUB']}\n<code>{sub['sub_link']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )
    # User Configs - Base64 Subscription Configs Callback
    elif key == "conf_sub_url_b64":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['sub_link_b64'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_SUB_B64']}\n<code>{sub['sub_link_b64']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )
    # User Configs - Subscription Configs For Clash Callback
    elif key == "conf_clash":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['clash_configs'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_CLASH']}\n<code>{sub['clash_configs']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )
    # User Configs - Subscription Configs For Hiddify Callback
    elif key == "conf_hiddify":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['hiddify_configs'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_HIDDIFY']}\n<code>{sub['hiddify_configs']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )

    elif key == "conf_sub_auto":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['sub_link_auto'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_SUB_AUTO']}\n<code>{sub['sub_link_auto']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )

    elif key == "conf_sub_sing_box":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['sing_box'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_SING_BOX']}\n<code>{sub['sing_box']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )

    elif key == "conf_sub_full_sing_box":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        qr_code = utils.txt_to_qr(sub['sing_box_full'])
        if not qr_code:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        bot.send_photo(
            call.message.chat.id,
            photo=qr_code,
            caption=f"{KEY_MARKUP['CONFIGS_FULL_SING_BOX']}\n<code>{sub['sing_box_full']}</code>",
            reply_markup=main_menu_keyboard_markup()
        )

    # manual
    elif key == "msg_manual":
        settings = utils.all_configs_settings()
        android_msg = settings['msg_manual_android'] if settings['msg_manual_android'] else MESSAGES['MANUAL_ANDROID']
        ios_msg = settings['msg_manual_ios'] if settings['msg_manual_ios'] else MESSAGES['MANUAL_IOS']
        win_msg = settings['msg_manual_windows'] if settings['msg_manual_windows'] else MESSAGES['MANUAL_WIN']
        mac_msg = settings['msg_manual_mac'] if settings['msg_manual_mac'] else MESSAGES['MANUAL_MAC']
        linux_msg = settings['msg_manual_linux'] if settings['msg_manual_linux'] else MESSAGES['MANUAL_LIN']
        if value == 'android':
            bot.send_message(call.message.chat.id, android_msg, reply_markup=main_menu_keyboard_markup())
        elif value == 'ios':
            bot.send_message(call.message.chat.id, ios_msg, reply_markup=main_menu_keyboard_markup())
        elif value == 'win':
            bot.send_message(call.message.chat.id, win_msg, reply_markup=main_menu_keyboard_markup())
        elif value == 'mac':
            bot.send_message(call.message.chat.id, mac_msg, reply_markup=main_menu_keyboard_markup())
        elif value == 'lin':
            bot.send_message(call.message.chat.id, linux_msg, reply_markup=main_menu_keyboard_markup())





    # ----------------------------------- Back Area -----------------------------------
    # Back To User Menu
    elif key == "back_to_user_panel":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=user_info_markup(value))
        

    # Back To Plans
    elif key == "back_to_plans":
        plans = USERS_DB.find_plan(server_id=selected_server_id)
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=MESSAGES['PLANS_LIST'], reply_markup=plans_list_markup(plans))

    # Back To Renewal Plans
    elif key == "back_to_renewal_plans":
        plans = USERS_DB.find_plan(server_id=selected_server_id)
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
        #                               reply_markup=plans_list_markup(plans, renewal=True,uuid=value))
        update_info_subscription(call.message, value,plans_list_markup(plans, renewal=True,uuid=value))
    
    elif key == "back_to_servers":
        servers = USERS_DB.select_servers()
        server_list = []
        if not servers:
            bot.send_message(message.chat.id, MESSAGES['SERVERS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
            return
        for server in servers:
            user_index = 0
            #if server['status']:
            users_list = api.select(server['url'] + API_PATH)
            if users_list:
                user_index = len(users_list)
            if server['user_limit'] > user_index:
                server_list.append([server,True])
            else:
                server_list.append([server,False])
                
        # bad request telbot api
        # bot.edit_message_text(chat_id=message.chat.id, message_id=msg_wait.message_id,
        #                                   text= MESSAGES['SERVERS_LIST'], reply_markup=servers_list_markup(server_list))
        #bot.delete_message(message.chat.id, msg_wait.message_id)
        bot.edit_message_text(reply_markup=servers_list_markup(server_list), chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=MESSAGES['SERVERS_LIST'])
        

    # Delete Message
    elif key == "del_msg":
        bot.delete_message(call.message.chat.id, call.message.message_id)

    # Invalid Command
    else:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_INVALID_COMMAND'])


# *********************************** Message Handler Area ***********************************
# Bot Start Message Handler
@bot.message_handler(commands=['start'])
def start_bot(message: Message):
    if is_user_banned(message.chat.id):
        return
    settings = utils.all_configs_settings()

    MESSAGES['WELCOME'] = MESSAGES['WELCOME'] if not settings['msg_user_start'] else settings['msg_user_start']
    
    if USERS_DB.find_user(telegram_id=message.chat.id):
        edit_name= USERS_DB.edit_user(telegram_id=message.chat.id,full_name=message.from_user.full_name)
        edit_username = USERS_DB.edit_user(telegram_id=message.chat.id,username=message.from_user.username)
        bot.send_message(message.chat.id, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())
    else:
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = USERS_DB.add_user(telegram_id=message.chat.id,username=message.from_user.username, full_name=message.from_user.full_name, created_at=created_at)
        if not status:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        wallet_status = USERS_DB.find_wallet(telegram_id=message.chat.id)
        if not wallet_status:
            status = USERS_DB.add_wallet(telegram_id=message.chat.id)
            if not status:
                bot.send_message(message.chat.id, f"{MESSAGES['UNKNOWN_ERROR']}:Wallet",
                                 reply_markup=main_menu_keyboard_markup())
                return
            bot.send_message(message.chat.id, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())

    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return


# If user is not in users table, request /start
@bot.message_handler(func=lambda message: not USERS_DB.find_user(telegram_id=message.chat.id))
def not_in_users_table(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    bot.send_message(message.chat.id, MESSAGES['REQUEST_START'], reply_markup=main_menu_keyboard_markup())


# User Subscription Status Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SUBSCRIPTION_STATUS'])
def subscription_status(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    non_order_subs = utils.non_order_user_info(message.chat.id)
    order_subs = utils.order_user_info(message.chat.id)

    if not non_order_subs and not order_subs:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return

    if non_order_subs:
        for non_order_sub in non_order_subs:
            if non_order_sub:
                server_id = non_order_sub['server_id']
                server = USERS_DB.find_server(id=server_id)
                if not server:
                    bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                                    reply_markup=main_menu_keyboard_markup())
                    return
                server = server[0]
                api_user_data = user_info_template(non_order_sub['sub_id'], server, non_order_sub, MESSAGES['INFO_USER'])
                bot.send_message(message.chat.id, api_user_data,
                                 reply_markup=user_info_non_sub_markup(non_order_sub['uuid']))
    if order_subs:
        for order_sub in order_subs:
            if order_sub:
                server_id = order_sub['server_id']
                server = USERS_DB.find_server(id=server_id)
                if not server:
                    bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                                    reply_markup=main_menu_keyboard_markup())
                    return
                server = server[0]
                api_user_data = user_info_template(order_sub['sub_id'], server, order_sub, MESSAGES['INFO_USER'])
                bot.send_message(message.chat.id, api_user_data,
                                 reply_markup=user_info_markup(order_sub['uuid']))


# User Buy Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['BUY_SUBSCRIPTION'])
def buy_subscription(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    settings = utils.all_configs_settings()
    if not settings['buy_subscription_status']:
        bot.send_message(message.chat.id, MESSAGES['BUY_SUBSCRIPTION_CLOSED'], reply_markup=main_menu_keyboard_markup())
        return
    wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    if not wallet:
        create_wallet_status = USERS_DB.add_wallet(message.chat.id)
        if not create_wallet_status: 
            bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    #msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=main_menu_keyboard_markup())
    servers = USERS_DB.select_servers()
    server_list = []
    if not servers:
        bot.send_message(message.chat.id, MESSAGES['SERVERS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    for server in servers:
        user_index = 0
        #if server['status']:
        users_list = api.select(server['url'] + API_PATH)
        if users_list:
            user_index = len(users_list)
        if server['user_limit'] > user_index:
            server_list.append([server,True])
        else:
            server_list.append([server,False])
    # bad request telbot api
    # bot.edit_message_text(chat_id=message.chat.id, message_id=msg_wait.message_id,
    #                                   text= MESSAGES['SERVERS_LIST'], reply_markup=servers_list_markup(server_list))
    #bot.delete_message(message.chat.id, msg_wait.message_id)
    bot.send_message(message.chat.id, MESSAGES['SERVERS_LIST'], reply_markup=servers_list_markup(server_list))


# Config To QR Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['TO_QR'])
def to_qr(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_TO_QR'], reply_markup=cancel_markup())
    bot.register_next_step_handler(message, next_step_to_qr)


# Help Guide Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['MANUAL'])
def help_guide(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    bot.send_message(message.chat.id, MESSAGES['MANUAL_HDR'],
                     reply_markup=users_bot_management_settings_panel_manual_markup())
    
# Help Guide Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['FAQ'])
def faq(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    settings = utils.all_configs_settings()
    faq_msg = settings['msg_faq'] if settings['msg_faq'] else MESSAGES['UNKNOWN_ERROR']
    bot.send_message(message.chat.id, faq_msg, reply_markup=main_menu_keyboard_markup())


# Ticket To Support Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SEND_TICKET'])
def send_ticket(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    bot.send_message(message.chat.id, MESSAGES['SEND_TICKET_TO_ADMIN_TEMPLATE'], reply_markup=send_ticket_to_admin())


# Link Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['LINK_SUBSCRIPTION'])
def link_subscription(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    bot.send_message(message.chat.id, MESSAGES['ENTER_SUBSCRIPTION_INFO'], reply_markup=cancel_markup())
    bot.register_next_step_handler(message, next_step_link_subscription)


# User Buy Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['WALLET'])
def wallet_balance(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    user = USERS_DB.find_user(telegram_id=message.chat.id)
    if user:
        wallet_status = USERS_DB.find_wallet(telegram_id=message.chat.id)
        if not wallet_status:
            status = USERS_DB.add_wallet(telegram_id=message.chat.id)
            if not status:
                bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'])
                return

        wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
        wallet = wallet[0]
        telegram_user_data = wallet_info_template(wallet['balance'])

        bot.send_message(message.chat.id, telegram_user_data,
                         reply_markup=wallet_info_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'])


# User Buy Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['FREE_TEST'])
def free_test(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    settings = utils.all_configs_settings()
    if not settings['test_subscription']:
        bot.send_message(message.chat.id, MESSAGES['FREE_TEST_NOT_AVAILABLE'], reply_markup=main_menu_keyboard_markup())
        return
    users = USERS_DB.find_user(telegram_id=message.chat.id)
    if users:
        user = users[0]
        if user['test_subscription']:
            bot.send_message(message.chat.id, MESSAGES['ALREADY_RECEIVED_FREE'],
                             reply_markup=main_menu_keyboard_markup())
            return
        else:
            # bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'], reply_markup=cancel_markup())
            # bot.register_next_step_handler(message, next_step_send_name_for_get_free_test)
            msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
            servers = USERS_DB.select_servers()
            server_list = []
            if not servers:
                bot.send_message(message.chat.id, MESSAGES['SERVERS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
                return
            for server in servers:
                user_index = 0
                #if server['status']:
                users_list = api.select(server['url'] + API_PATH)
                if users_list:
                    user_index = len(users_list)
                if server['user_limit'] > user_index:
                    server_list.append([server,True])
                else:
                    server_list.append([server,False])
            # bad request telbot api
            # bot.edit_message_text(chat_id=message.chat.id, message_id=msg_wait.message_id,
            #                                   text= MESSAGES['SERVERS_LIST'], reply_markup=servers_list_markup(server_list))
            bot.delete_message(message.chat.id, msg_wait.message_id)
            bot.send_message(message.chat.id, MESSAGES['SERVERS_LIST'], reply_markup=servers_list_markup(server_list, True))



# Cancel Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['CANCEL'])
def cancel(message: Message):
    if is_user_banned(message.chat.id):
        return
    join_status = is_user_in_channel(message.chat.id)
    if not join_status:
        return
    bot.send_message(message.chat.id, MESSAGES['CANCELED'], reply_markup=main_menu_keyboard_markup())


# *********************************** Main Area ***********************************
def start():
    # Bot Start Commands
    try:
        bot.set_my_commands([
            telebot.types.BotCommand("/start", BOT_COMMANDS['START']),
        ])
    except telebot.apihelper.ApiTelegramException as e:
        if e.result.status_code == 401:
            logging.error("Invalid Telegram Bot Token!")
            exit(1)
    # Welcome to Admin
    for admin in ADMINS_ID:
        try:
            bot.send_message(admin, MESSAGES['WELCOME_TO_ADMIN'])
        except Exception as e:
            logging.warning(f"Error in send message to admin {admin}: {e}")
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.infinity_polling()
