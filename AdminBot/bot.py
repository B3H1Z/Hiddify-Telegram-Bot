# Description: Main Bot File
import datetime
import html
import logging
import operator
import time
import telebot
import os
from telebot.types import Message, CallbackQuery

from config import TELEGRAM_TOKEN, ADMINS_ID, PANEL_ADMIN_ID, CLIENT_TOKEN, BOT_BACKUP_LOC
from AdminBot.content import BOT_COMMANDS, MESSAGES, KEY_MARKUP
from AdminBot import markups
from AdminBot import templates
from Utils import utils
from Shared.common import user_bot
from Database.dbManager import USERS_DB
from Utils import api
from config import panel_url_validator, API_PATH

# Initialize Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")
bot.remove_webhook()

URL = 'url'
selected_server = None
search_mode = "Single"
server_mode = "Single"
searched_name = ""
list_mode = ""
item_mode= ""
selected_telegram_id = "0"

if CLIENT_TOKEN:
    user_bot = user_bot()
# ----------------------------------- Helper Functions -----------------------------------
# Check if message is digit
def is_it_digit(message: Message, allow_float=False, response=MESSAGES['ERROR_INVALID_NUMBER'],
                markup=markups.main_menu_keyboard_markup()):
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
        bot.send_message(message.chat.id, response, reply_markup=markups.main_menu_keyboard_markup())
        return True
    return False


def message_to_html(message: Message):
    text = message.text
    entities = message.entities

    html_content = ""

    offset = 0
    for entity in entities:
        html_content += html.escape(text[offset:entity.offset])
        if entity.type == 'bold':
            html_content += f'<b>{html.escape(text[entity.offset:entity.offset + entity.length])}</b>'
        elif entity.type == 'italic':
            html_content += f'<i>{html.escape(text[entity.offset:entity.offset + entity.length])}</i>'
        elif entity.type == 'code':
            html_content += f'<code>{html.escape(text[entity.offset:entity.offset + entity.length])}</code>'
        elif entity.type == 'pre':
            html_content += f'<pre>{html.escape(text[entity.offset:entity.offset + entity.length])}</pre>'
        elif entity.type == 'text_link':
            html_content += f'<a href="{html.escape(entity.url)}">{html.escape(text[entity.offset:entity.offset + entity.length])}</a>'
        offset = entity.offset + entity.length
    html_content += html.escape(text[offset:])
    return html_content


# ----------------------------------- Add User Area -----------------------------------
# Add user Data dict
add_user_data = {}


# Add User - Name
def add_user_name(message: Message, server_id):
    if is_it_cancel(message):
        return
    add_user_data['name'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_USAGE_LIMIT'], reply_markup=markups.while_edit_user_markup())
    bot.register_next_step_handler(message, add_user_limit, server_id)


# Add User - Usage Limit
def add_user_limit(message: Message, server_id):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, f"{MESSAGES['ERROR_INVALID_NUMBER']}\n{MESSAGES['ADD_USER_USAGE_LIMIT']}",
                       markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, add_user_limit, server_id)
        return
    add_user_data['limit'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_DAYS'], reply_markup=markups.while_edit_user_markup())
    bot.register_next_step_handler(message, add_user_usage_days, server_id)


# Add User - Usage Days
def add_user_usage_days(message: Message, server_id):
    if is_it_cancel(message, MESSAGES['CANCEL_ADD_USER']):
        return
    if not is_it_digit(message, f"{MESSAGES['ERROR_INVALID_NUMBER']}\n{MESSAGES['ADD_USER_DAYS']}",
                       markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, add_user_usage_days, server_id)
        return
    add_user_data['usage_days'] = message.text
    bot.send_message(message.chat.id,
                     f"{MESSAGES['ADD_USER_CONFIRM']}\n\n{MESSAGES['INFO_USER_NAME']} {add_user_data['name']}\n"
                     f"{MESSAGES['INFO_USAGE']} {add_user_data['limit']} {MESSAGES['GB']}\n{MESSAGES['INFO_REMAINING_DAYS']} {add_user_data['usage_days']} {MESSAGES['DAY']}",
                     reply_markup=markups.confirm_add_user_markup())
    bot.register_next_step_handler(message, confirm_add_user, server_id)


# Add User - Confirm to add user
def confirm_add_user(message: Message, server_id):
    
    if message.text == KEY_MARKUP['CANCEL']:
        bot.send_message(message.chat.id, MESSAGES['CANCEL_ADD_USER'], reply_markup=markups.main_menu_keyboard_markup())
        return
    if message.text == KEY_MARKUP['CONFIRM']:
        msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
        # res = ADMIN_DB.add_default_user(name=add_user_data['name'], package_days=int(add_user_data['usage_days']),
        #                                 usage_limit_GB=int(add_user_data['limit']))
        server = USERS_DB.find_server(id=int(server_id))
        if not server:
            bot.send_message(message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
            return
        server = server[0]
        URL = server['url'] + API_PATH
        res = api.insert(URL, name=add_user_data['name'], package_days=int(add_user_data['usage_days']),
                         usage_limit_GB=int(add_user_data['limit']))
        if res:
            bot.send_message(message.chat.id, MESSAGES['SUCCESS_ADD_USER'],
                             reply_markup=markups.main_menu_keyboard_markup())
            usr = utils.user_info(URL, res)
            if not usr:
                bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
                return
            msg = templates.user_info_template(usr, server, MESSAGES['NEW_USER_INFO'])
            bot.delete_message(message.chat.id, msg_wait.message_id)
            bot.send_message(message.chat.id, msg, reply_markup=markups.user_info_markup(usr['uuid']))

        else:
            bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                             reply_markup=markups.main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['CANCEL_ADD_USER'], reply_markup=markups.main_menu_keyboard_markup())


# ----------------------------------- Edit User Area -----------------------------------
# Edit User - Name
def edit_user_name(message: Message, uuid):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    # status = ADMIN_DB.edit_user(uuid, name=message.text)
    status = api.update(URL, uuid, name=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_USER_NAME_EDITED']} {message.text} ",
                     reply_markup=markups.main_menu_keyboard_markup())


# Edit User - Usage
def edit_user_usage(message: Message, uuid):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, edit_user_usage, uuid)
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    # status = ADMIN_DB.edit_user(uuid, usage_limit_GB=int(message.text))
    status = api.update(URL, uuid, usage_limit_GB=int(message.text))
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_USER_USAGE_EDITED']} {message.text} {MESSAGES['GB']}",
                     reply_markup=markups.main_menu_keyboard_markup())


# Edit User - Days
def edit_user_days(message: Message, uuid):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, edit_user_days, uuid)
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    # status = ADMIN_DB.edit_user(uuid, package_days=int(message.text))
    status = api.update(URL, uuid, package_days=int(message.text))
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id,
                     f"{MESSAGES['SUCCESS_USER_DAYS_EDITED']} {message.text} {MESSAGES['DAY_EXPIRE']} ",
                     reply_markup=markups.main_menu_keyboard_markup())


# Edit User - Comment
def edit_user_comment(message: Message, uuid):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    # status = ADMIN_DB.edit_user(uuid, comment=message.text)
    status = api.update(URL, uuid, comment=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_USER_COMMENT_EDITED']} {message.text} ",
                     reply_markup=markups.main_menu_keyboard_markup())


# ----------------------------------- Search User Area -----------------------------------
# Search User - Name
def search_user_name(message: Message, server_id):
    global searched_name
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    searched_name = message.text
    users = utils.search_user_by_name(URL, searched_name)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())

    bot.send_message(message.chat.id, templates.users_list_template(users, MESSAGES['SEARCH_RESULT']),
                     reply_markup=markups.users_list_markup(server_id, users))


# Search User - UUID
def search_user_uuid(message: Message, server_id):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    user = utils.search_user_by_uuid(URL, message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    server = USERS_DB.find_server(id=int(server_id))
    if not server:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
        return
    server = server[0]
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, templates.user_info_template(user, server, MESSAGES['SEARCH_RESULT']),
                     reply_markup=markups.user_info_markup(user['uuid']))


# Search User - Config
def search_user_config(message: Message, server_id):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    user = utils.search_user_by_config(URL, message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    server = USERS_DB.find_server(id=int(server_id))
    if not server:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
        return
    server = server[0]
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, templates.user_info_template(user, server, MESSAGES['SEARCH_RESULT']),
                     reply_markup=markups.user_info_markup(user['uuid']))

# All Servers Search User - Name
def all_server_search_user_name(message: Message):
    global searched_name
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    users = []
    searched_name = message.text
    servers = USERS_DB.select_servers()
    if servers:
        for server in servers:
            URL = server['url'] + API_PATH
            searched_users = utils.search_user_by_name(URL, searched_name)
            if searched_users:
                users.extend(searched_users)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())

    bot.send_message(message.chat.id, templates.users_list_template(users, MESSAGES['SEARCH_RESULT']),
                     reply_markup=markups.users_list_markup("None", users))


# All Servers Search User - UUID
def all_server_search_user_uuid(message: Message):
    selected_server = None
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    servers = USERS_DB.select_servers()
    if servers:
        for server in servers:
            URL = server['url'] + API_PATH
            user = utils.search_user_by_uuid(URL, message.text)
            if user:
                selected_server = server
                break
    
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, templates.user_info_template(user, selected_server, MESSAGES['SEARCH_RESULT']),
                     reply_markup=markups.user_info_markup(user['uuid']))


# All Servers Search User - Config
def all_server_search_user_config(message: Message):
    selected_server = None
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    servers = USERS_DB.select_servers()
    if servers:
        for server in servers:
            URL = server['url'] + API_PATH
            user = utils.search_user_by_config(URL, message.text)
            if user:
                selected_server = server
                break
    
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, templates.user_info_template(user, selected_server, MESSAGES['SEARCH_RESULT']),
                     reply_markup=markups.user_info_markup(user['uuid']))

# ----------------------------------- Users Bot Search Area -----------------------------------
# User Bot Search  - Name
def search_bot_user_name(message: Message):
    global searched_name
    if is_it_cancel(message):
        return
    searched_name = message.text
    users = USERS_DB.find_user(full_name=searched_name)
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    users.sort(key = operator.itemgetter('created_at'), reverse=True)
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())

    wallets_list = USERS_DB.select_wallet()
    orders_list = USERS_DB.select_orders()
    msg = templates.bot_users_list_template(users, wallets_list, orders_list)
    bot.send_message(message.chat.id, msg, reply_markup=markups.bot_users_list_markup(users))

# User Bot Search  - Name
def search_bot_user_telegram_id(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, search_bot_user_telegram_id)
        return
    searched_id = message.text
    users = USERS_DB.find_user(telegram_id=int(searched_id))
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                        reply_markup=markups.main_menu_keyboard_markup())
        return
    user = users[0]
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=markups.main_menu_keyboard_markup())

    orders = USERS_DB.find_order(telegram_id=user['telegram_id'])
    paymets = USERS_DB.find_payment(telegram_id=user['telegram_id'])
    wallet = None
    wallets = USERS_DB.find_wallet(telegram_id=user['telegram_id'])
    if wallets:
        wallet = wallets[0]
    non_order_subs = utils.non_order_user_info(user['telegram_id'])
    order_subs = utils.order_user_info(user['telegram_id'])
    plans_list = USERS_DB.select_plans()
    msg = templates.bot_users_info_template(user, orders, paymets, wallet, non_order_subs, order_subs, plans_list)
    bot.send_message(message.chat.id, msg, reply_markup=markups.bot_user_info_markup(user['telegram_id']))


# User Bot Search  - Order
def search_bot_user_order(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, search_bot_user_order)
        return
    orders = USERS_DB.find_order(id=int(message.text))
    if not orders:
        bot.send_message(message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'],
                        reply_markup=markups.main_menu_keyboard_markup())
        return
    order = orders[0]
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_ORDER'], reply_markup=markups.main_menu_keyboard_markup())
    plans = USERS_DB.find_plan(id=order['plan_id'])
    if not plans:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                            reply_markup=markups.main_menu_keyboard_markup())
        return
    plan = plans[0]
    #subs = 
    users = USERS_DB.find_user(telegram_id=order['telegram_id'])
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                            reply_markup=markups.main_menu_keyboard_markup())
        return
    user = users[0]
    servers = USERS_DB.find_server(id=plan['server_id'])
    if not servers:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                            reply_markup=markups.main_menu_keyboard_markup())
        return
    server = servers[0]
    msg = templates.bot_orders_info_template(order, plan, user, server)
    bot.send_message(message.chat.id, msg)

# User Bot Search  - Payment
def search_bot_user_payment(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, search_bot_user_payment)
        return
    payments = USERS_DB.find_payment(id=int(message.text))
    if not payments:
        bot.send_message(message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'],
                        reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_PAYMENT'], reply_markup=markups.main_menu_keyboard_markup())
    payment = payments[0]
    user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
    if not user_data:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                            reply_markup=markups.main_menu_keyboard_markup())
        return
    user_data = user_data[0]
    
    msg = templates.bot_payment_info_template(payment,user_data)
    photo_path = os.path.join(os.getcwd(), 'UserBot', 'Receiptions', payment['payment_image'])
    bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'),
                caption=msg, reply_markup=markups.change_status_payment_by_admin(payment['id']))


# ----------------------------------- Users Bot Management Area -----------------------------------
#add_plan_data = {}


# Add Plan - Size
# def users_bot_add_plan_usage(message: Message):
#     if is_it_cancel(message):
#         return
#     if not is_it_digit(message):
#         return
#     add_plan_data['usage'] = int(message.text)
#     bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_DAYS'],
#                      reply_markup=markups.while_edit_user_markup())
#     bot.register_next_step_handler(message, users_bot_add_plan_days)


# # Add Plan - Days
# def users_bot_add_plan_days(message: Message):
#     if is_it_cancel(message):
#         return
#     if not is_it_digit(message):
#         return
#     add_plan_data['days'] = int(message.text)
#     bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_PRICE'],
#                      reply_markup=markups.while_edit_user_markup())
#     bot.register_next_step_handler(message, users_bot_add_plan_price)


# # Add Plan - Price
# def users_bot_add_plan_price(message: Message):
#     if is_it_cancel(message):
#         return
#     if not is_it_digit(message):
#         return
#     add_plan_data['price'] = utils.toman_to_rial(message.text)
#     msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
#     status = utils.users_bot_add_plan(add_plan_data['usage'], add_plan_data['days'], add_plan_data['price'])
#     bot.delete_message(message.chat.id, msg_wait.message_id)
#     if not status:
#         bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
#         return
#     bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_SUCCESS'],
#                      reply_markup=markups.main_menu_keyboard_markup())


# ----------------------------------- Server Management Area -----------------------------------
add_server_data = {}


# Add Server - Title
def add_server_title(message: Message):
    if is_it_cancel(message):
        return
    add_server_data['title'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_SERVER_URL'],
                     reply_markup=markups.while_edit_user_markup())
    bot.register_next_step_handler(message, add_server_url)


# Add Server - url
def add_server_url(message: Message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    url = panel_url_validator(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not url:
        bot.reply_to(message, MESSAGES['ERROR_ADD_SERVER_URL'],
                     reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(message, add_server_url)
        return
    servers = USERS_DB.select_servers()
    if servers:
        for server in servers:
            if server['url'] == url:
                bot.reply_to(message, MESSAGES['ERROR_SAME_SERVER_URL'],
                            reply_markup=markups.while_edit_user_markup())
                bot.register_next_step_handler(message, add_server_url)
                return
                
    add_server_data['url'] = url
    bot.send_message(message.chat.id, MESSAGES['ADD_SERVER_USER_LIMIT'],
                     reply_markup=markups.while_edit_user_markup())
    bot.register_next_step_handler(message, add_server_user_limit)


# Add Server - User Limit
def add_server_user_limit(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, add_server_user_limit)
        return
    add_server_data['user_limit'] = int(message.text)
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    status = utils.add_server(url=add_server_data['url'], user_limit=add_server_data['user_limit'], title=add_server_data['title'])
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['ADD_SERVER_SUCCESS'],
                     reply_markup=markups.main_menu_keyboard_markup())
    servers = USERS_DB.select_servers()
    bot.send_message(message.chat.id, KEY_MARKUP['SERVERS_MANAGEMENT'],
                     reply_markup=markups.servers_management_markup(servers))
    
# Edit Server - Server Title
def edit_server_title(message: Message, server_id):
    if is_it_cancel(message):
        return
    status = USERS_DB.edit_server(int(server_id), title=message.text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    server = USERS_DB.find_server(id=int(server_id))
    if not server:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
        return
    server = server[0]
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_SERVER_TITLE_EDITED']}{server['title']}",
                     reply_markup=markups.main_menu_keyboard_markup())
    plans = USERS_DB.select_plans()
    msg = templates.server_info_template(server,plans)
    bot.send_message(message.chat.id, msg,
                     reply_markup=markups.server_edit_markup(server_id))
    
# Edit Server - Server User Limit
def edit_server_user_limit(message: Message, server_id):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, edit_server_user_limit, server_id)
        return
    status = USERS_DB.edit_server(int(server_id), user_limit=int(message.text))
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    server = USERS_DB.find_server(id=int(server_id))
    if not server:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
        return
    server = server[0]
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_SERVER_USER_LIMIT_EDITED']}{server['user_limit']}",
                     reply_markup=markups.main_menu_keyboard_markup())
    plans = USERS_DB.select_plans()
    msg = templates.server_info_template(server,plans)
    bot.send_message(message.chat.id, msg,
                     reply_markup=markups.server_edit_markup(server_id))

# Edit Server - Server Url
def edit_server_url(message: Message, server_id):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    url = panel_url_validator(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not url:
        bot.send_message(message.chat.id, MESSAGES['ERROR_ADD_SERVER_URL'],
                     reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(message, edit_server_url, server_id)
        return
    servers = USERS_DB.select_servers()
    if servers:
        for server in servers:
            if server['url'] == url:
                bot.reply_to(message, MESSAGES['ERROR_SAME_SERVER_URL'],
                            reply_markup=markups.while_edit_user_markup())
                bot.register_next_step_handler(message, edit_server_url, server_id)
                return
    status = USERS_DB.edit_server(int(server_id), url=url)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
        return
    server = USERS_DB.find_server(id=int(server_id))
    if not server:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
        return
    server = server[0]
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_SERVER_URL_EDITED']}\n{server['url']}",
                     reply_markup=markups.main_menu_keyboard_markup())
    plans = USERS_DB.select_plans()
    msg = templates.server_info_template(server,plans)
    bot.send_message(message.chat.id, msg,
                     reply_markup=markups.server_edit_markup(server_id))


# ----------------------------------- Users Bot Management Area -----------------------------------
add_plan_data = {}


# Add Plan - Size
def users_bot_add_plan_usage(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_add_plan_usage)
        return
    add_plan_data['usage'] = int(message.text)
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_DAYS'],
                     reply_markup=markups.while_edit_user_markup())
    bot.register_next_step_handler(message, users_bot_add_plan_days)


# Add Plan - Days
def users_bot_add_plan_days(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_add_plan_days)
        return
    add_plan_data['days'] = int(message.text)
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_PRICE'],
                     reply_markup=markups.while_edit_user_markup())
    bot.register_next_step_handler(message, users_bot_add_plan_price)


# Add Plan - Price
def users_bot_add_plan_price(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_add_plan_price)
        return
    add_plan_data['price'] = utils.toman_to_rial(message.text)
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_DESC'],
                     reply_markup=markups.while_edit_skip_user_markup())
    bot.register_next_step_handler(message, users_bot_add_plan_description)
def users_bot_add_plan_description(message: Message):
    if is_it_cancel(message):
        return
    if message.text == KEY_MARKUP['SKIP']:
        add_plan_data['description'] = None
    else:
        add_plan_data['description'] = message.text
    
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    status = utils.users_bot_add_plan(add_plan_data['usage'], add_plan_data['days'],
                                      add_plan_data['price'], add_plan_data['server_id'], add_plan_data['description'])
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_SUCCESS'],
                     reply_markup=markups.main_menu_keyboard_markup())
    plans_list = []
    plans = USERS_DB.select_plans()
    if plans:
        for plan in plans:
            if plan['status']:
                if plan['server_id'] == int(add_plan_data['server_id']):
                        plans_list.append(plan)
        plans_markup = markups.plans_list_markup(plans_list,add_plan_data['server_id'])
        bot.send_message(message.chat.id, {MESSAGES['USERS_BOT_PLANS_LIST']},
                         reply_markup=plans_markup)


    

# Users Bot - Edit Owner Info - Username
def users_bot_edit_owner_info_username(message: Message):
    if is_it_cancel(message):
        return
    if not message.text.startswith('@'):
        bot.send_message(message.chat.id, MESSAGES['ERROR_INVALID_USERNAME'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    status = USERS_DB.edit_str_config("support_username", value=message.text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


# Users Bot - Edit Owner Info - Card Number
def users_bot_edit_owner_info_card_number(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_edit_owner_info_card_number)
        return
    if len(message.text) != 16:
        bot.send_message(message.chat.id, MESSAGES['ERROR_INVALID_CARD_NUMBER'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    status = USERS_DB.edit_str_config("card_number", value=message.text)

    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


# Users Bot - Edit Owner Info - Cardholder Name
def users_bot_edit_owner_info_card_name(message: Message):
    if is_it_cancel(message):
        return
    status = USERS_DB.edit_str_config("card_holder", value=message.text)

    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


# Users Bot - Send Message - All Users
def users_bot_send_msg_users(message: Message):
    if is_it_cancel(message):
        return
    if not CLIENT_TOKEN:
        bot.send_message(message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=markups.while_edit_user_markup())
    users_number_id = USERS_DB.select_users()
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not users_number_id:
        bot.send_message(message.chat.id, MESSAGES['ERROR_NO_USERS'], reply_markup=markups.main_menu_keyboard_markup())
        return
    for user in users_number_id:
        time.sleep(0.05)
        try:
            user_bot.send_message(user['telegram_id'], message.text)
        except Exception as e:
            logging.warning(f"Error in send message to user {user['telegram_id']}: {e}")
            continue
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEND_MSG_USERS'],
                     reply_markup=markups.main_menu_keyboard_markup())


# Users Bot - Settings - Update Message
def users_bot_settings_update_message(message: Message, markup,title=MESSAGES['USERS_BOT_SETTINGS']):
    settings = utils.all_configs_settings()

    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=title,
                          reply_markup=markup)


# # Users Bot - Order Status
# def users_bot_order_status(message: Message):
#     from UserBot.templates import payment_received_template
#     if is_it_cancel(message):
#         return
#     if not is_it_digit(message):
#         return

#     payment = USERS_DB.find_payment(id=int(message.text))
#     if not payment:
#         bot.send_message(message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'],
#                          reply_markup=markups.main_menu_keyboard_markup())
#         return

#     # plan = USERS_DB.find_plan(id=payment[0]['plan_id'])
#     # if not payment:
#     #     bot.send_message(message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'], reply_markup=markups.main_menu_keyboard_markup())
#     #     return
#     payment = payment[0]
#     user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
#     if not user_data:
#             bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
#                              reply_markup=markups.main_menu_keyboard_markup())
#             return
#     user_data = user_data[0]
#     is_it_accepted = None
#     if payment['approved'] == 0:
#         is_it_accepted = MESSAGES['PAYMENT_ACCEPT_STATUS_NOT_CONFIRMED']
#     elif payment['approved'] == 1:
#         is_it_accepted = MESSAGES['PAYMENT_ACCEPT_STATUS_CONFIRMED']
#     else:
#         is_it_accepted = MESSAGES['PAYMENT_ACCEPT_STATUS_WAITING']

#     photo_path = path_recp = os.path.join(os.getcwd(), 'UserBot', 'Receiptions', payment['payment_image'])
#     bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'),
#                    caption=payment_received_template(payment,user_data,
#                                                      footer=f"{MESSAGES['PAYMENT_ACCEPT_STATUS']} {is_it_accepted}\n{MESSAGES['CREATED_AT']} {payment['created_at']}"),
#                    reply_markup=markups.main_menu_keyboard_markup())


def users_bot_sub_status(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_sub_status)
        return
    bot_user = None
    if len(message.text) == 7:
        user = USERS_DB.find_order_subscription(id=int(message.text))
        if user:
            orders = USERS_DB.find_order(id=user[0]['order_id'])
            if orders:
                bot_users = USERS_DB.find_user(telegram_id=orders[0]['telegram_id'])
                if bot_users:
                    bot_user = bot_users[0]
    elif len(message.text) == 8:
        user = USERS_DB.find_non_order_subscription(id=int(message.text))
        if user:
            bot_users = USERS_DB.find_user(telegram_id=user[0]['telegram_id'])
            if bot_users:
                bot_user = bot_users[0]
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SUB_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return

    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SUB_NOT_FOUND'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    
    if not bot_user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    user_uuid = user[0]['uuid']
    selected_server = None
    servers = USERS_DB.select_servers()
    usr = None
    if servers:
        for server in servers:
            URL = server['url'] + API_PATH
            usr = utils.user_info(URL, user_uuid)
            if usr:
                selected_server = server
                break
            else:
                continue
        if not usr:
            bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'],
                             reply_markup=markups.main_menu_keyboard_markup())
            return
        bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_SUB'],
                             reply_markup=markups.main_menu_keyboard_markup())
        msg = templates.user_info_template(usr, selected_server)
        bot.send_message(message.chat.id, msg,
                        reply_markup=markups.sub_search_info_markup(usr['uuid'], bot_user))




def users_bot_settings_min_depo(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_min_depo)
        return
    new_min_depo = utils.toman_to_rial(message.text)
    new_min_depo = int(new_min_depo)
    status = USERS_DB.edit_int_config("min_deposit_amount", value=new_min_depo)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


def users_bot_settings_channel_id(message: Message):
    if is_it_cancel(message):
        return
    if not message.text.startswith('@'):
        bot.send_message(message.chat.id, MESSAGES['ERROR_INVALID_USERNAME'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
    status = USERS_DB.edit_str_config("channel_id", value=message.text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


def users_bot_settings_welcome_msg(message: Message):
    if is_it_cancel(message):
        return
    
    status = USERS_DB.edit_str_config("msg_user_start", value=message.html_text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())

def users_bot_settings_set_faq_msg(message: Message, msg):
    if is_it_cancel(message):
        return
    
    status = USERS_DB.edit_str_config("msg_faq", value=message.html_text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    settings = utils.all_configs_settings()
    try:
        bot.edit_message_reply_markup(message.chat.id, msg.message_id,
                                  reply_markup=markups.users_bot_management_settings_faq_markup())
    except:
        pass

    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())

def users_bot_settings_test_sub_size(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, allow_float=True, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_test_sub_size)
        return
    # if float convert float else convert int
    if '.' in message.text:
        new_test_sub_size = float(message.text)
    else:
        new_test_sub_size = int(message.text)  
    status = USERS_DB.edit_int_config("test_sub_size_gb", value=new_test_sub_size)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


def users_bot_settings_test_sub_days(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_test_sub_days)
        return
    new_test_sub_days = int(message.text)
    status = USERS_DB.edit_int_config("test_sub_days", value=new_test_sub_days)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


def users_bot_settings_notif_reminder_usage(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, allow_float=True, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_notif_reminder_usage)
        return
    if '.' in message.text:
        new_reminder_usage = float(message.text)
    else:
        new_reminder_usage = int(message.text)
    status = USERS_DB.edit_int_config("reminder_notification_usage", value=new_reminder_usage)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


def users_bot_settings_notif_reminder_days(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_notif_reminder_days)
        return
    new_test_sub_days = int(message.text)
    status = USERS_DB.edit_int_config("reminder_notification_days", value=new_test_sub_days)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())


def users_bot_settings_panel_manual(message: Message, db_key):
    if is_it_cancel(message):
        return
    status = USERS_DB.edit_str_config(db_key, value=message.html_text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())

def users_bot_settings_restore_bot(message: Message):
    if is_it_cancel(message):
        return
    # save file
    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_save_path = os.path.join(BOT_BACKUP_LOC,"Restore")
    if not os.path.exists(file_save_path):
        os.makedirs(file_save_path)
        
    # save in Backup/bot/restore
    
    with open(os.path.join(file_save_path,file_name), 'wb') as new_file:
        new_file.write(downloaded_file)
        
    restore_status = utils.restore_json_bot(os.path.join(file_save_path,file_name))
    if not restore_status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_RESTORE_BOT'], reply_markup=markups.main_menu_keyboard_markup())

def users_bot_settings_renewal_method_advanced_days(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_renewal_method_advanced_days)
        return
    new_test_sub_days = int(message.text)
    status = USERS_DB.edit_int_config("advanced_renewal_days", value=new_test_sub_days)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())

def users_bot_settings_renewal_method_advanced_usage(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, allow_float=True, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, users_bot_settings_renewal_method_advanced_usage)
        return
    if '.' in message.text:
        new_renewal_usage = float(message.text)
    else:
        new_renewal_usage = int(message.text)
    status = USERS_DB.edit_int_config("advanced_renewal_usage", value=new_renewal_usage)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())

def edit_wallet_balance(message: Message,telegram_id):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, markup=markups.while_edit_user_markup()):
        bot.register_next_step_handler(message, edit_wallet_balance)
        return
    new_balance = utils.toman_to_rial(message.text)
    wallet_status = USERS_DB.find_wallet(telegram_id=telegram_id)
    if not wallet_status:
        status = USERS_DB.add_wallet(telegram_id=telegram_id)
        if not status:
                bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'])
                return
    status = USERS_DB.edit_wallet(telegram_id=telegram_id, balance=new_balance)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'])
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=markups.main_menu_keyboard_markup())
    user_bot.send_message(telegram_id, f"{MESSAGES['WALLET_BALANCE_CHANGED_BY_ADMIN_P1']} {message.text} {MESSAGES['WALLET_BALANCE_CHANGED_BY_ADMIN_P2']}")
    


def send_message_to_user(message: Message, payment_id):
    if is_it_cancel(message):
        return
    payment_info = USERS_DB.find_payment(id=int(payment_id))
    if not payment_info:
        bot.send_message(message.chat.id,
                            f"{MESSAGES['ERROR_PAYMENT_NOT_FOUND']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        return
    payment_info = payment_info[0]
    user_bot.send_message(int(payment_info['telegram_id']),
                        f"{MESSAGES['ADMIN']}\n{message.text}\n{MESSAGES['ORDER_ID']} {payment_id}",
                        reply_markup=markups.send_message_to_user_markup(message.chat.id))
    bot.send_message(message.chat.id, MESSAGES['MESSAGE_SENDED'],
                        reply_markup=markups.main_menu_keyboard_markup())
    
def users_bot_send_message_to_user(message: Message, telegram_id):
    if is_it_cancel(message):
        return
    user_bot.send_message(int(telegram_id),
                        f"{MESSAGES['MESSAGE_FROM_ADMIN']}\n{MESSAGES['MESSAGE_TEXT']} {message.text}", reply_markup=markups.send_message_to_user_markup(message.chat.id))
    bot.send_message(message.chat.id, MESSAGES['MESSAGE_SENDED'],
                        reply_markup=markups.main_menu_keyboard_markup())
    
# ----------------------------------- Callbacks -----------------------------------
# Callback Handler for Inline Buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    logging.info(f"Callback Query: {call.data}")
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    # Check if user is not admin
    if call.from_user.id not in ADMINS_ID:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_NOT_ADMIN'])
        return
    bot.clear_step_handler(call.message)
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    value = data[1]
    global URL
    #Single , Single_name , Single_expired , All_server_name , All_server_expired
    global search_mode
    # All , Single
    global server_mode
    global searched_name
    global selected_server 
    #User_Orders, User_Payments, User_Gifts, Orders, Approved_Payments
    #Non_Approved_Payments, Pending_Payments, Card_Payments, Digital_Payments
    #Bot_User, Bot_Users_Search_Name, User_Refferals
    global list_mode 
    #Order, Payment, Gift
    global item_mode
    global selected_telegram_id
    # ----------------------------------- Users List Area Callbacks -----------------------------------
    # Single User Info Callback
    if key == "info":
        if server_mode == "Single":
            usr = utils.user_info(URL, value)
        else:
            servers = USERS_DB.select_servers()
            if servers:
                for server in servers:
                    URL = server['url'] + API_PATH
                    usr = utils.user_info(URL, value)
                    if usr:
                        selected_server = server
                        break
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = templates.user_info_template(usr, selected_server)
        bot.send_message(call.message.chat.id, msg,
                        reply_markup=markups.user_info_markup(usr['uuid']))


    # Next Page Callback
    elif key == "next":
        # users_list = utils.dict_process(utils.users_to_dict(ADMIN_DB.select_users()))
        users_list = []
        server_id = selected_server['id']
        if search_mode == "Single":
            users_list = api.select(URL)
            server_id = selected_server['id']
        elif search_mode == "Single_name":
            users_list = utils.search_user_by_name(URL, searched_name)
            server_id = selected_server['id']
        elif search_mode == "Single_expired":
            users_list = api.select(URL)
            users_list = utils.expired_users_list(users_list)
            server_id = selected_server['id']
        elif search_mode == "All_server_name":
            servers = USERS_DB.select_servers()
            if servers:
                for server in servers:
                    server_url = server['url'] + API_PATH
                    searched_users = utils.search_user_by_name(server_url, searched_name)
                    users_list.extend(searched_users)
            server_id = "None"
        elif search_mode == "All_server_expired":
            servers = USERS_DB.select_servers()
            if servers:
                for server in servers:
                    server_url = server['url'] + API_PATH
                    users = api.select(server_url)
                    users = utils.expired_users_list(users)
                    users_list.extend(users)
            server_id = "None"
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.users_list_markup(server_id, users_list, int(value)))

    # ----------------------------------- Single User Info Area Callbacks -----------------------------------
    # Delete User Callback
    elif key == "user_delete":
        # status = ADMIN_DB.delete_user(uuid=value)
        bot.send_message(call.message.chat.id, MESSAGES['FEATUR_UNAVAILABLE'],
                         reply_markup=markups.main_menu_keyboard_markup())
        return
        # if not status:
        #     bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
        #                      reply_markup=markups.main_menu_keyboard_markup())
        #     return
        # bot.delete_message(call.message.chat.id, call.message.message_id)
        # bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_USER_DELETED'],
        #                  reply_markup=markups.main_menu_keyboard_markup())
    # Edit User Main Button Callback
    elif key == "user_edit":
        if server_mode == "All":
            servers = USERS_DB.select_servers()
            if servers:
                for server in servers:
                    users_list = api.find(server['url'] + API_PATH, value)
                    if users_list:
                        URL = server['url'] + API_PATH
                        selected_server = server
                        break
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.edit_user_markup(value))

    # Configs User Callback
    elif key == "user_config":
        if server_mode == "All":
            servers = USERS_DB.select_servers()
            if servers:
                for server in servers:
                    users_list = api.find(server['url'] + API_PATH, value)
                    if users_list:
                        URL = server['url'] + API_PATH
                        selected_server = server
                        break
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.sub_url_user_list_markup(value))

    # ----------------------------------- Edit User Area Callbacks -----------------------------------
    # Edit User - Update Message Callback
    elif key == "user_edit_update":
        usr = utils.user_info(URL, value)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        msg = templates.user_info_template(usr, selected_server, MESSAGES['EDITED_USER_INFO'])
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.edit_user_markup(value))
    # Edit User - Edit Usage Callback
    elif key == "user_edit_usage":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_USAGE_LIMIT'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_usage, value)
    # Edit User - Reset Usage Callback
    elif key == "user_edit_reset_usage":
        status = api.update(URL, uuid=value, current_usage_GB=0)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                             reply_markup=markups.main_menu_keyboard_markup())
            return
        bot.send_message(call.message.chat.id, MESSAGES['RESET_USAGE'],
                         reply_markup=markups.main_menu_keyboard_markup())
    # Edit User - Edit Days Callback
    elif key == "user_edit_days":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_DAYS'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_days, value)
    # Edit User - Reset Days Callback
    elif key == "user_edit_reset_days":
        # status = ADMIN_DB.reset_package_days(uuid=value)
        last_reset_time = datetime.datetime.now().strftime("%Y-%m-%d")
        status = api.update(URL, uuid=value, start_date=last_reset_time)
        # api.insert()
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                             reply_markup=markups.main_menu_keyboard_markup())
            return
        bot.send_message(call.message.chat.id, MESSAGES['RESET_DAYS'], reply_markup=markups.main_menu_keyboard_markup())
    # Edit User - Edit Comment Callback
    elif key == "user_edit_comment":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_COMMENT'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_comment, value)
    # Edit User - Edit Name Callback
    elif key == "user_edit_name":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_NAME'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_name, value)

    # ----------------------------------- Configs User Info Area Callbacks -----------------------------------
    # User Configs - DIR Configs Callback

    elif key == "conf_dir":
        sub = utils.sub_links(value, URL)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.sub_user_list_markup(value,configs))
    # User Configs - VLESS Configs Callback
    elif key == "conf_dir_vless":
        sub = utils.sub_links(value, URL)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        if not configs['vless']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        msgs = templates.configs_template(configs['vless'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=markups.main_menu_keyboard_markup())
    # User Configs - VMess Configs Callback
    elif key == "conf_dir_vmess":
        sub = utils.sub_links(value, URL)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        if not configs['vmess']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        msgs = templates.configs_template(configs['vmess'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=markups.main_menu_keyboard_markup())
    # User Configs - Trojan Configs Callback
    elif key == "conf_dir_trojan":
        sub = utils.sub_links(value, URL)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        configs = utils.sub_parse(sub['sub_link'])
        if not configs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        if not configs['trojan']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CONFIG_NOT_FOUND'])
            return
        msgs = templates.configs_template(configs['trojan'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=markups.main_menu_keyboard_markup())

    # User Configs - Main Menu
    elif key == 'configs_list':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.sub_url_user_list_markup(value))
        
    # User Configs - Subscription Configs Callback
    elif key == "conf_sub_url":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )
    # User Configs - Base64 Subscription Configs Callback
    elif key == "conf_sub_url_b64":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )
    # User Configs - Subscription Configs For Clash Callback
    elif key == "conf_clash":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )
    # User Configs - Subscription Configs For Hiddify Callback
    elif key == "conf_hiddify":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )

    elif key == "conf_sub_auto":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )

    elif key == "conf_sub_sing_box":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )

    elif key == "conf_sub_full_sing_box":
        sub = utils.sub_links(value, URL)
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
            reply_markup=markups.main_menu_keyboard_markup()
        )

    else:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_INVALID_COMMAND'])

    # ----------------------------------- Search User Area Callbacks -----------------------------------
    # Search User - Name Callback
    if key == "search_name":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_NAME'],
                         reply_markup=markups.while_edit_user_markup())
        if value == "None":
            search_mode = "All_server_name"
            bot.register_next_step_handler(call.message, all_server_search_user_name)
        else:
            search_mode = "Single_name"
            bot.register_next_step_handler(call.message, search_user_name, value)
    # Search User - UUID Callback
    elif key == "search_uuid":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_UUID'],
                         reply_markup=markups.while_edit_user_markup())
        if value == "None":
            bot.register_next_step_handler(call.message, all_server_search_user_uuid)
        else:
            bot.register_next_step_handler(call.message, search_user_uuid, value)
    # Search User - Config Callback
    elif key == "search_config":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_CONFIG'],
                         reply_markup=markups.while_edit_user_markup())
        if value == "None":
            bot.register_next_step_handler(call.message, all_server_search_user_config)
        else:
            bot.register_next_step_handler(call.message, search_user_config, value)
    # Search User - Expired Callback
    elif key == "search_expired":
        users_list = []
        if value == "None":
            search_mode = "All_server_expired"
            servers = USERS_DB.select_servers()
            if servers:
                for server in servers:
                    server_url = server['url'] + API_PATH
                    users = api.select(server_url)
                    users = utils.expired_users_list(users)
                    users_list.extend(users)
        else:
            search_mode = "Single_expired"
            users_list = api.select(URL)
            users_list = utils.expired_users_list(users_list)
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = templates.users_list_template(users_list, MESSAGES['EXPIRED_USERS_LIST'])
        bot.send_message(call.message.chat.id, msg, reply_markup=markups.users_list_markup(value, users_list))

    # ----------------------------------- Server Management Callbacks -----------------------------------
    elif key == "server_selected":
        server_mode = "Single"
        server = USERS_DB.find_server(id=int(value))
        if not server:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
            return
        server = server[0]
        URL = server['url'] + API_PATH
        selected_server = server
        plans = USERS_DB.select_plans()
        msg = templates.server_info_template(server,plans)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.server_selected_markup(value))

    # Server Management - Add Server Callback
    elif key == "add_server":
        bot.send_message(call.message.chat.id, MESSAGES['ADD_SERVER'],
                         reply_markup=markups.while_edit_user_markup())
        bot.send_message(call.message.chat.id, MESSAGES['ADD_SERVER_TITLE'])
        bot.register_next_step_handler(call.message, add_server_title)

    # Server Management - Delete Server Callback
    elif key == "delete_server":
        bot.edit_message_text(MESSAGES['DELETE_SERVER_QUESTION'], call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.server_delete_markup(value))
    
    # Server Management - Edit Server Callback
    elif key == "edit_server":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.server_edit_markup(value))
        
    # Server Management - Edit Title Server Callback
    elif key == "server_edit_title":
        bot.send_message(call.message.chat.id, MESSAGES['ADD_SERVER_TITLE'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_server_title, value)
        
    # Server Management - Edit User Limit Server Callback
    elif key == "server_edit_user_limit":
        bot.send_message(call.message.chat.id, MESSAGES['ADD_SERVER_USER_LIMIT'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_server_user_limit, value)

    # Server Management - Edit Url Server Callback
    elif key == "server_edit_url":
        bot.send_message(call.message.chat.id, MESSAGES['ADD_SERVER_URL'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_server_url, value)
    # Server Management - Confirm Delete Server Callback
    elif key == "confirm_delete_server":
        server_id = int(value)
        #status = USERS_DB.edit_server(value, status=0)
        status = USERS_DB.delete_server(id=server_id)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        
        USERS_DB.delete_plan(server_id=server_id)
        USERS_DB.delete_order_subscription(server_id=server_id)
        USERS_DB.delete_non_order_subscription(server_id=server_id)
    
        servers = USERS_DB.select_servers()
        bot.edit_message_text(KEY_MARKUP['SERVERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.servers_management_markup(servers)) 
        bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_REMOVED_SERVER'], reply_markup=markups.main_menu_keyboard_markup())

        
    # Server Management - List of Plans for Server Callback
    elif key == "server_list_of_plans":
        plans_list = []
        plans = USERS_DB.select_plans()
        if plans:
            for plan in plans:
                if plan['status']:
                    if plan['server_id'] == int(value):
                        plans_list.append(plan)
        plans_markup = markups.plans_list_markup(plans_list,value)
        bot.edit_message_text({MESSAGES['USERS_BOT_PLANS_LIST']}, call.message.chat.id, call.message.message_id,
                         reply_markup=plans_markup)
        
    elif key == "server_list_of_users":
        users_list = api.select(URL)
        search_mode = "Single"
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = templates.users_list_template(users_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_list_markup(value, users_list))
    
    elif key == "server_add_user":
        global add_user_data
        bot.send_message(call.message.chat.id, MESSAGES['ADD_USER_NAME'], reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, add_user_name, value)

    elif key == "server_search_user":
        bot.edit_message_text(MESSAGES['SEARCH_USER'],call.message.chat.id, call.message.message_id, 
                              reply_markup=markups.search_user_markup(server_id=value))

    # ----------------------------------- Users Bot Management Callbacks -----------------------------------
    elif key == "users_bot_management_menu":
        bot.edit_message_text(KEY_MARKUP['USERS_BOT_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_markup())
        
    elif key == "bot_users_list_management":
         bot.edit_message_text(KEY_MARKUP['BOT_USERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_users_management_markup())
        
    elif key == "bot_users_list":
        list_mode = "Bot_Users"
        users_list = USERS_DB.select_users()
        wallets_list = USERS_DB.select_wallet()
        orders_list = USERS_DB.select_orders()
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        users_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_users_list_template(users_list, wallets_list, orders_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_users_list_markup(users_list))
        users_list.sort(key = operator.itemgetter('created_at'), reverse=True)
    elif key == "search_users_bot":
         
         bot.edit_message_text(MESSAGES['SEARCH_USER'], call.message.chat.id, call.message.message_id,
                          reply_markup=markups.users_bot_users_search_method_markup())
    
    elif key == "bot_users_search_name":
        list_mode = "Bot_Users"
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_NAME'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_bot_user_name)

    elif key == "bot_users_search_telegram_id":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_TELEGRAM_ID'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_bot_user_telegram_id)

    elif key == "bot_user_info":
        selected_telegram_id = value
        users = USERS_DB.find_user(telegram_id=int(value))
        if not users:
             bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                              reply_markup=markups.main_menu_keyboard_markup())
             return
        user = users[0]
        orders = USERS_DB.find_order(telegram_id=user['telegram_id'])
        paymets = USERS_DB.find_payment(telegram_id=user['telegram_id'])
        wallet = None
        wallets = USERS_DB.find_wallet(telegram_id=user['telegram_id'])
        if wallets:
            wallet = wallets[0]
        non_order_subs = utils.non_order_user_info(user['telegram_id'])
        order_subs = utils.order_user_info(user['telegram_id'])
        plans_list = USERS_DB.select_plans()
        msg = templates.bot_users_info_template(user, orders, paymets, wallet, non_order_subs, order_subs, plans_list)
        bot.send_message(call.message.chat.id, msg, reply_markup=markups.bot_user_info_markup(value))

    elif key == "bot_user_next":
        if list_mode == "Bot_Users":
           users_list = USERS_DB.select_users()
        elif list_mode == "Bot_Users_Search_Name":
            users_list = USERS_DB.find_user(full_name=searched_name)
        elif list_mode == "User_Refferals":
            users_list = USERS_DB.find_user(telegram_id=int(selected_telegram_id))
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return 
        users_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.bot_users_list_markup(users_list, int(value)))


    elif key == "bot_user_item_info":
        if item_mode == "Order":
            orders = USERS_DB.find_order(id=int(value))
            if not orders:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
            order = orders[0]
            plans = USERS_DB.find_plan(id=order['plan_id'])
            if not plans:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
            plan = plans[0]
            #subs = 
            users = USERS_DB.find_user(telegram_id=order['telegram_id'])
            if not users:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
            user = users[0]
            servers = USERS_DB.find_server(id=plan['server_id'])
            if not servers:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
            server = servers[0]
            msg = templates.bot_orders_info_template(order, plan, user, server)
            bot.send_message(call.message.chat.id, msg)
        elif item_mode == "Payment":
            payments = USERS_DB.find_payment(id=int(value))
            if not payments:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
                return
            payment = payments[0]
            user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
            if not user_data:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
                return
            user_data = user_data[0]
            msg = templates.bot_payment_info_template(payment,user_data)
            photo_path = os.path.join(os.getcwd(), 'UserBot', 'Receiptions', payment['payment_image'])
            if payment['approved'] == None:
                bot.send_photo(call.message.chat.id, photo=open(photo_path, 'rb'),
                            caption=msg, reply_markup=markups.confirm_payment_by_admin(payment['id']))
            else:
                bot.send_photo(call.message.chat.id, photo=open(photo_path, 'rb'),
                            caption=msg, reply_markup=markups.change_status_payment_by_admin(payment['id']))
        elif item_mode == "Gift":
            gift = USERS_DB.find_user_plans(id=int(value))

    elif key == "bot_user_item_next":
        if list_mode == "User_Orders":
            item_list = USERS_DB.find_order(telegram_id=int(selected_telegram_id))
        elif list_mode == "User_Payments":
            item_list = USERS_DB.find_payment(telegram_id=int(selected_telegram_id))
        elif list_mode == "User_Gifts":
            item_list = USERS_DB.find_user_plans(telegram_id=int(selected_telegram_id))
        elif list_mode == "Orders":
            item_list = USERS_DB.select_orders()
        if list_mode == "Approved_Payments":
            payments_list = USERS_DB.select_payments()
            item_list = [payment for payment in payments_list if payment['approved'] == 1]
        elif list_mode == "Non_Approved_Payments":
            payments_list = USERS_DB.select_payments()
            item_list = [payment for payment in payments_list if payment['approved'] == 0]
        elif list_mode == "Pending_Payments":
            payments_list = USERS_DB.select_payments()
            item_list = [payment for payment in payments_list if payment['approved'] == None]
        elif list_mode == "Card_Payments":
            payments_list = USERS_DB.select_payments()
            item_list = [payment for payment in payments_list if payment['payment_method'] == "Card"]
        elif list_mode == "Digital_Payments":
            payments_list = USERS_DB.select_payments()
            item_list = [payment for payment in payments_list if payment['payment_method'] == "Digital"]
        if not item_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return 
        if not list_mode == "User_Gifts":
            item_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.bot_user_item_list_markup(item_list, int(value)))

    elif key == "bot_users_sub_user_list":
        server_mode = "All"
        subs = utils.non_order_user_info(int(value))
        order_subs = utils.order_user_info(int(value))
        if order_subs:
            subs.extend(order_subs)
        if not subs:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_SUB_NOT_FOUND'])
            return
        msg = templates.users_list_template(subs)
        bot.send_message(call.message.chat.id, msg, reply_markup=markups.users_list_markup("None", subs))

    elif key == "users_bot_orders_user_list":
        list_mode = "User_Orders"
        item_mode = "Order"
        orders_list = USERS_DB.find_order(telegram_id=int(value))
        
        plans_list = USERS_DB.select_plans()
        if not orders_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'])
            return
        orders_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_orders_list_template(orders_list, plans_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(orders_list))

    elif key == "users_bot_payments_user_list":
        list_mode = "User_Payments"
        item_mode = "Payment"
        paymets = USERS_DB.find_payment(telegram_id=int(value))
        if not paymets:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        paymets.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_payments_list_template(paymets)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(paymets))
    
    elif key == "users_bot_wallet_edit_balance":
        bot.send_message(call.message.chat.id, MESSAGES['EDIT_WALLET_BALANCE'],
                            reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_wallet_balance, value)
    
    elif key == "users_bot_reset_test":
        users = USERS_DB.find_user(telegram_id=int(value))
        if not users:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
        user = users[0]
        if user['test_subscription'] == 0:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_HAVE_TEST_SUB'])
            return
        status = USERS_DB.edit_user(telegram_id=int(value), test_subscription=0)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_RESET_TEST_SUB'])
    
    elif key == "users_bot_ban_user":
        users = USERS_DB.find_user(telegram_id=int(value))
        if not users:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
        user = users[0]
        if user['banned'] == 0:
            status = USERS_DB.edit_user(telegram_id=int(value), banned=1)
            if not status:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
            bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_BAN_USER'])
            return
        if user['banned'] == 1:
            status = USERS_DB.edit_user(telegram_id=int(value), banned=0)
            if not status:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
            bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_UNBAN_USER'])
            return
    elif key == "users_bot_gifts_user_list":
        list_mode = "User_Gifts"
        item_mode = "Gift"
        gift = USERS_DB.find_user_plans(telegram_id=int(value))
        if not gift:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_GIFT_NOT_FOUND'])
            return
        # msg = templates.bot_gift_list_template(paymets)
        # bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
        #                       reply_markup=markups.bot_user_item_list_markup(gift))

    elif key == "users_bot_referred_user_list":
        list_mode = "User_Refferals"
        users = USERS_DB.find_user(telegram_id=int(value))
        if not users:
             bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                              reply_markup=markups.main_menu_keyboard_markup())
             return
        user = users[0] 
        #referred_user = 



    elif key == "users_bot_orders_list_management":
        bot.edit_message_text(KEY_MARKUP['ORDERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_orders_management_markup())

    elif key == "users_bot_orders_list":
        list_mode = "Orders"
        item_mode = "Order"
        orders_list = USERS_DB.select_orders()
        plans_list = USERS_DB.select_plans()
        if not orders_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'])
            return
        orders_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_orders_list_template(orders_list, plans_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(orders_list))
        

    elif key == "search_orders":
        bot.send_message(call.message.chat.id, MESSAGES['ORDER_NUMBER_REQUEST'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_bot_user_order)
        

    elif key == "users_bot_payments_list_management":
         bot.edit_message_text(KEY_MARKUP['PAYMENT_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_payments_management_markup())
        
    elif key == "search_payments":
        bot.send_message(call.message.chat.id, MESSAGES['PAYMENT_NUMBER_REQUEST'],
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_bot_user_payment)

    elif key == "bot_users_approved_payments_list":
        list_mode = "Approved_Payments"
        item_mode = "Payment"
        payments_list = USERS_DB.select_payments()
        if not payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        approved_payments_list = [payment for payment in payments_list if payment['approved'] == 1]
        if not approved_payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        approved_payments_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_payments_list_template(approved_payments_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(approved_payments_list))

    elif key == "users_bot_non_approved_payments_list":
        list_mode = "Non_Approved_Payments"
        item_mode = "Payment"
        payments_list = USERS_DB.select_payments()
        if not payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        non_approved_payments_list = [payment for payment in payments_list if payment['approved'] == 0]
        if not non_approved_payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        non_approved_payments_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_payments_list_template(non_approved_payments_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(non_approved_payments_list))

    elif key == "users_bot_pending_payments_list":
        list_mode = "Pending_Payments"
        item_mode = "Payment"
        payments_list = USERS_DB.select_payments()
        if not payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        pending_payments_list = [payment for payment in payments_list if payment['approved'] == None]
        if not pending_payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        pending_payments_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_payments_list_template(pending_payments_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(pending_payments_list))

    elif key == "users_bot_card_payments_list":
        list_mode = "Card_Payments"
        item_mode = "Payment"
        payments_list = USERS_DB.select_payments()
        if not payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        card_payments_list = [payment for payment in payments_list if payment['payment_method'] == "Card"]
        if not card_payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        card_payments_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_payments_list_template(card_payments_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(card_payments_list))

    elif key == "users_bot_digital_payments_list":
        list_mode = "Digital_Payments"
        item_mode = "Payment"
        payments_list = USERS_DB.select_payments()
        if not payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        digital_payments_list = [payment for payment in payments_list if payment['payment_method'] == "Digital"]
        if not digital_payments_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        digital_payments_list.sort(key = operator.itemgetter('created_at'), reverse=True)
        msg = templates.bot_payments_list_template(digital_payments_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.bot_user_item_list_markup(digital_payments_list))


    # Plan Management - Add Plan Callback
    elif key == "users_bot_add_plan":
        bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN'],
                         reply_markup=markups.while_edit_user_markup())
        bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_USAGE'])
        add_plan_data['server_id'] = int(value)
        bot.register_next_step_handler(call.message, users_bot_add_plan_usage)

    # Plan Management - Info Plan Callback
    elif key == "info_plan_selected":
        plans= USERS_DB.find_plan(id=value)
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        orders = USERS_DB.find_order(plan_id=value)
        plan = plans[0]
        msg = templates.plan_info_template(plan, orders)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.plan_info_selected_markup(plan['server_id']))



    # Plan Management - Edit Plan Callback
    elif key == "users_bot_del_plan":
        status = USERS_DB.edit_plan(value, status=0)
        if status:
            plans= USERS_DB.find_plan(id=value)
            if not plans:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
            del_plan = plans[0]
            server_id = del_plan['server_id']
            plans_list = []
            plans = USERS_DB.select_plans()
            if plans:
                for plan in plans:
                    if plan['status']:
                        if plan['server_id'] == server_id:
                            plans_list.append(plan)
            plans_markup = markups.plans_list_markup(plans_list, server_id,delete_mode = True)
            bot.edit_message_text({MESSAGES['USERS_BOT_SELECT_PLAN_TO_DELETE']}, call.message.chat.id, call.message.message_id,
                         reply_markup=plans_markup)
        else:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])

    # Plan Management - List Plans Callback
    elif key == "users_bot_list_plans":
        plans_list = []
        plans = USERS_DB.select_plans()
        if plans:
            for plan in plans:
                if plan['status']:
                    if plan['server_id'] == int(value):
                        plans_list.append(plan)
        plans_markup = markups.plans_list_markup(plans_list,value,delete_mode = True)
        bot.edit_message_text({MESSAGES['USERS_BOT_SELECT_PLAN_TO_DELETE']}, call.message.chat.id, call.message.message_id,
                         reply_markup=plans_markup)

    # Owner Info - Edit Owner Info Callback
    elif key == "users_bot_owner_info":
        owner_info = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         templates.owner_info_template(owner_info['support_username'], owner_info['card_number'],
                                                       owner_info['card_holder']),
                         reply_markup=markups.users_bot_edit_owner_info_markup())
    # Owner Info - Edit Owner Username Callback
    elif key == "users_bot_owner_info_edit_username":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_OWNER_INFO_ADD_USERNAME']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_edit_owner_info_username)

    # Owner Info - Edit Owner Card Number Callback
    elif key == "users_bot_owner_info_edit_card_number":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_OWNER_INFO_ADD_CARD_NUMBER']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_edit_owner_info_card_number)

    # Owner Info - Edit Owner Cardholder Callback
    elif key == "users_bot_owner_info_edit_card_name":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_OWNER_INFO_ADD_CARD_NAME']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_edit_owner_info_card_name)

    # Send Message - Send Message To All Users Callback
    elif key == "users_bot_send_msg_users":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_SEND_MSG_USERS']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_send_msg_users)

    # User Bot Settings  - Main Settings Callback
    elif key == "users_bot_settings":
        settings = USERS_DB.select_bool_config()
        if not settings:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        settings = utils.all_configs_settings()
        bot.edit_message_text(MESSAGES['USERS_BOT_SETTINGS'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_management_settings_markup(settings))

    # User Bot Settings  - Set Hyperlink Status Callback
    elif key == "users_bot_settings_hyperlink":
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("visible_hiddify_hyperlink", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("visible_hiddify_hyperlink", value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))

    # User Bot Settings  - Set three random letters for define price
    elif key == "users_bot_settings_three_rand_price":
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("three_random_num_price", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("three_random_num_price", value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))

    elif key == "users_bot_settings_panel_auto_backup":
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("panel_auto_backup", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("panel_auto_backup", value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))
    
    elif key == "users_bot_settings_bot_auto_backup": 
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("bot_auto_backup", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("bot_auto_backup", value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))

    elif key == "users_bot_settings_min_depo":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {utils.rial_to_toman(settings['min_deposit_amount'])}\n{MESSAGES['USERS_BOT_SETTING_MIN_DEPO']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_min_depo)

    # elif key == "users_bot_settings_panel_v8":
    #     if value == "1":
    #         edit_config = USERS_DB.edit_bool_config("hiddify_v8_feature", value=False)
    #         if not edit_config:
    #             bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    #             return
    #     elif value == "0":
    #         edit_config = USERS_DB.edit_bool_config("hiddify_v8_feature", value=True)
    #         if not edit_config:
    #             bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    #             return
    #     users_bot_settings_update_message(call.message)

    elif key == "users_bot_settings_channel_id":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['channel_id']}\n{MESSAGES['USERS_BOT_SETTING_CHANNEL_ID']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_channel_id)

    elif key == "users_bot_settings_force_join":
        settings = utils.all_configs_settings()
        if not settings['channel_id']:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CHANNEL_ID_NOT_SET'])
            return
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("force_join_channel", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("force_join_channel", value=True)
            bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_SETTING_FORCE_JOIN_HELP'])
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))

    elif key == "users_bot_settings_visible_sub_menu":
        settings = utils.all_configs_settings()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_visible_sub_markup(settings))
    elif key == "users_bot_settings_visible_sub":
        settings = utils.all_configs_settings()
        row_key = value
        current_status = settings[row_key]
        if current_status == 1:
            edit_config = USERS_DB.edit_bool_config(row_key, value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif current_status == 0:
            edit_config = USERS_DB.edit_bool_config(row_key, value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message,
                                          markups.users_bot_management_settings_visible_sub_markup(settings))

    elif key == "users_bot_settings_set_welcome_msg":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['msg_user_start']}\n{MESSAGES['USERS_BOT_SETTING_WELCOME_MSG']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_welcome_msg)

    elif key == "users_bot_settings_faq_management":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_faq_markup())

    elif key == "users_bot_settings_set_faq_msg":
        settings = utils.all_configs_settings()
        faq_text = settings['msg_faq']
        msg = call.message
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {faq_text}\n{MESSAGES['USERS_BOT_SETTING_FAQ_MSG']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_set_faq_msg, msg)

    elif key == "users_bot_settings_hide_faq":
        settings = utils.all_configs_settings()
        status = USERS_DB.edit_str_config("msg_faq", value=None)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
            return
        settings = utils.all_configs_settings()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.users_bot_management_settings_faq_markup())
        
    elif key == "users_bot_settings_test_sub_menu":
        settings = utils.all_configs_settings()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_test_sub_markup(settings))

    elif key == "users_bot_settings_test_sub":
        settings = utils.all_configs_settings()
        row_key = value
        current_status = settings['test_subscription']
        if current_status == 1:
            edit_config = USERS_DB.edit_bool_config(row_key, value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif current_status == 0:
            edit_config = USERS_DB.edit_bool_config(row_key, value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_test_sub_markup(settings))
    elif key == "users_bot_settings_test_sub_size":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['test_sub_size_gb']} {MESSAGES['GB']}\n{MESSAGES['USERS_BOT_SETTINGS_TEST_SUB_USAGE']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_test_sub_size)
    elif key == "users_bot_settings_test_sub_days":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['test_sub_days']} {MESSAGES['DAY']}\n{MESSAGES['USERS_BOT_SETTINGS_TEST_SUB_DAYS']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_test_sub_days)

    # User Bot Settings  - Reminder Notification Callback
    elif key == "users_bot_settings_notif_reminder_menu":
        settings = utils.all_configs_settings()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_notif_reminder_markup(
                                          settings))

    elif key == "users_bot_settings_notif_reminder":
        settings = utils.all_configs_settings()
        row_key = value
        current_status = settings['reminder_notification']
        if current_status == 1:
            edit_config = USERS_DB.edit_bool_config(row_key, value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif current_status == 0:
            edit_config = USERS_DB.edit_bool_config(row_key, value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message,
                                          markups.users_bot_management_settings_notif_reminder_markup(settings))

    elif key == "users_bot_settings_notif_reminder_usage":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['reminder_notification_usage']} {MESSAGES['GB']}\n{MESSAGES['USERS_BOT_SETTINGS_NOTIF_REMINDER_USAGE']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_notif_reminder_usage)
    elif key == "users_bot_settings_notif_reminder_days":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['reminder_notification_days']} {MESSAGES['DAY']}\n{MESSAGES['USERS_BOT_SETTINGS_NOTIF_REMINDER_DAYS']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_notif_reminder_days)
    elif key == "users_bot_settings_panel_manual_menu":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_panel_manual_markup())
    elif key == "users_bot_settings_panel_manual":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings[value]}\n{MESSAGES['USERS_BOT_SETTINGS_PANEL_MANUAL']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_panel_manual, value)
    elif key == "users_bot_settings_backup_bot":
        backup_file = utils.backup_json_bot()
        if not backup_file:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_document(call.message.chat.id, open(backup_file, 'rb'),caption=MESSAGES['USERS_BOT_SETTINGS_BACKUP_BOT'])
    
    elif key == "users_bot_settings_restore_bot":
        bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_SETTINGS_RESTORE_BOT'], reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_restore_bot)
    
    elif key == "users_bot_settings_buy_sub_status":
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("buy_subscription_status", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("buy_subscription_status", value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))

    elif key == "users_bot_settings_renewal_sub_status":
        if value == "1":
            edit_config = USERS_DB.edit_bool_config("renewal_subscription_status", value=False)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "0":
            edit_config = USERS_DB.edit_bool_config("renewal_subscription_status", value=True)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_markup(settings))
    
    elif key == "users_bot_settings_renewal_method_menu":
        settings = utils.all_configs_settings()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_renewal_method_markup(settings))
    
    elif key == "users_bot_settings_renewal_method":
        if value == "1":
            edit_config = USERS_DB.edit_int_config("renewal_method", value=1)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "2":
            edit_config = USERS_DB.edit_int_config("renewal_method", value=2)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        elif value == "3":
            edit_config = USERS_DB.edit_int_config("renewal_method", value=3)
            if not edit_config:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
        settings = utils.all_configs_settings()
        users_bot_settings_update_message(call.message, markups.users_bot_management_settings_renewal_method_markup(settings))
    
    elif key == "users_bot_settings_renewal_method_advanced_days":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['advanced_renewal_days']} {MESSAGES['DAY']}\n{MESSAGES['USERS_BOT_SETTINGS_RENEWAL_METHOD_ADVANCED_DAYS']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_renewal_method_advanced_days)
    elif key == "users_bot_settings_renewal_method_advanced_usage":
        settings = utils.all_configs_settings()
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['CURRENT_VALUE']}: {settings['advanced_renewal_usage']} {MESSAGES['GB']}\n{MESSAGES['USERS_BOT_SETTINGS_RENEWAL_METHOD_ADVANCED_USAGE']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_settings_renewal_method_advanced_usage)
    # User Bot Settings  - Order Status Callback
    # elif key == "users_bot_orders_status":
    #     bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_ORDER_NUMBER_REQUEST']}")
    #     bot.register_next_step_handler(call.message, users_bot_order_status)

    elif key == "users_bot_sub_status":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_SUB_ID_REQUEST']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_sub_status)

    elif key == "users_bot_settings_reset_free_test_limit_question":
        bot.edit_message_text(MESSAGES['USERS_BOT_SETTINGS_RESET_FREE_TEST_LIMIT_QUESTION'], call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.users_bot_management_settings_reset_free_test_markup())
        
    elif key == "users_bot_management_settings_reset_free_test_confirm":
        users_list = USERS_DB.select_users()
        free_test_bot_users =  [user for user in users_list if user['test_subscription']]
        if free_test_bot_users:
            for user in free_test_bot_users:
                status = USERS_DB.edit_user(telegram_id=user['telegram_id'],test_subscription=False)
                if not status:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=markups.main_menu_keyboard_markup())
                    return
            bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_RESET_FREE_TEST'], reply_markup=markups.main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=markups.main_menu_keyboard_markup())
            
            


    # ----------------------------------- Payment Callbacks -----------------------------------
    # Payment - Confirm Payment Callback
    elif key == "confirm_payment_by_admin":
        if not CLIENT_TOKEN:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
            return
        payment_id = value
        payment_info = USERS_DB.find_payment(id=payment_id)
        if not payment_info:
            bot.send_message(call.message.chat.id,
                             f"{MESSAGES['ERROR_PAYMENT_NOT_FOUND']}\n{MESSAGES['ORDER_ID']} {payment_id}")
            return
        payment_info = payment_info[0]
        if payment_info['approved'] == 1:
            bot.send_message(call.message.chat.id,
                             f"{MESSAGES['ERROR_PAYMENT_ALREADY_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
            return
        
        wallet = USERS_DB.find_wallet(telegram_id=payment_info['telegram_id'])
        if not wallet:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        wallet = wallet[0]
        payment_status = USERS_DB.edit_payment(payment_id, approved=True)
        if payment_status:
            new_balance = int(wallet['balance']) + int(payment_info['payment_amount'])
            wallet_status = USERS_DB.edit_wallet(wallet['telegram_id'], balance=new_balance)
            if not wallet_status:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
            bot.delete_message(call.message.chat.id, call.message.message_id)
            user_bot.send_message(int(payment_info['telegram_id']),
                                  f"{MESSAGES['WALLET_PAYMENT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
            bot.send_message(call.message.chat.id,
                             f"{MESSAGES['PAYMENT_CONFIRMED_ADMIN']}\n{MESSAGES['ORDER_ID']} {payment_id}")

    # Payment - Reject Payment Callback
    elif key == 'cancel_payment_by_admin':
        if not CLIENT_TOKEN:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
            return
        payment_id = value
        payment_info = USERS_DB.find_payment(id=payment_id)
        if not payment_info:
            bot.send_message(call.message.chat.id,
                             f"{MESSAGES['ERROR_PAYMENT_NOT_FOUND']}\n{MESSAGES['ORDER_ID']} {payment_id}")
            return
        payment_info = payment_info[0]
        if payment_info['approved'] == 0:
            bot.send_message(call.message.chat.id,
                             f"{MESSAGES['ERROR_PAYMENT_ALREADY_REJECTED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
            return
        payment_status = USERS_DB.edit_payment(payment_id, approved=False)
        if payment_status:
            user_bot.send_message(int(payment_info['telegram_id']),
                                  f"{MESSAGES['PAYMENT_NOT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
            bot.send_message(call.message.chat.id,
                             f"{MESSAGES['PAYMENT_NOT_CONFIRMED_ADMIN']}\n{MESSAGES['ORDER_ID']}: {payment_id}")
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.send_message(call.message.chat.id, f"{MESSAGES['ERROR_UNKNOWN']}\n{MESSAGES['ORDER_ID']}: {payment_id}")

    # Payment - Change status Payment Callback
    elif key == "change_status_payment_by_admin":
        payments = USERS_DB.find_payment(id=int(value))
        if not payments:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        payment = payments[0]
        user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
        if not user_data:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        user_data = user_data[0]
        msg = templates.bot_payment_info_template(payment,user_data, footer=MESSAGES['CHANGE_STATUS_PAYMENT_CONFIRM_REQUEST'])
        bot.edit_message_caption(msg, call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.confirm_change_status_payment_by_admin(value))
    # Payment - Confirm change status Payment Callback
    elif key == "confirm_change_status_payment_by_admin":
        if not CLIENT_TOKEN:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
            return
        payment_id = int(value)
        payments = USERS_DB.find_payment(id=payment_id)
        if not payments:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        payment = payments[0]
        if payment['approved']:
            payment_status = USERS_DB.edit_payment(payment_id, approved=False)
            if payment_status:
                wallet = USERS_DB.find_wallet(telegram_id=payment['telegram_id'])
                if not wallet:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                    return
                wallet = wallet[0]
                new_balance = int(wallet['balance']) - int(payment['payment_amount'])
                wallet_status = USERS_DB.edit_wallet(wallet['telegram_id'], balance=new_balance)
                if not wallet_status:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                    return
                payments = USERS_DB.find_payment(id=payment_id)
                if not payments:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
                    return
                payment = payments[0]
                user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
                if not user_data:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                    return
                user_data = user_data[0]
                msg = templates.bot_payment_info_template(payment,user_data)
                bot.edit_message_caption(msg, call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.change_status_payment_by_admin(value))
                user_bot.send_message(int(payment['telegram_id']),
                                    f"{MESSAGES['PAYMENT_CHANGED_TO_NOT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
                bot.send_message(call.message.chat.id,
                                f"{MESSAGES['PAYMENT_CHANGED_TO_NOT_CONFIRMED_ADMIN']}\n{MESSAGES['ORDER_ID']} {payment_id}")

        elif payment['approved'] == False:
            payment_status = USERS_DB.edit_payment(payment_id, approved=True)
            if payment_status:
                wallet = USERS_DB.find_wallet(telegram_id=payment['telegram_id'])
                if not wallet:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                    return
                wallet = wallet[0]
                new_balance = int(wallet['balance']) + int(payment['payment_amount'])
                wallet_status = USERS_DB.edit_wallet(wallet['telegram_id'], balance=new_balance)
                if not wallet_status:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                    return
                payments = USERS_DB.find_payment(id=payment_id)
                if not payments:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
                    return
                payment = payments[0]
                user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
                if not user_data:
                    bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                    return
                user_data = user_data[0]
                msg = templates.bot_payment_info_template(payment,user_data)
                bot.edit_message_caption(msg, call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.change_status_payment_by_admin(value))
                user_bot.send_message(int(payment['telegram_id']),
                                    f"{MESSAGES['WALLET_CHANGED_TO_PAYMENT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
                bot.send_message(call.message.chat.id,
                                f"{MESSAGES['PAYMENT_CHANGED_TO_CONFIRMED_ADMIN']}\n{MESSAGES['ORDER_ID']} {payment_id}")
                
    elif key == "cancel_change_status_payment_by_admin":
        payments = USERS_DB.find_payment(id=int(value))
        if not payments:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PAYMENT_NOT_FOUND'])
            return
        payment = payments[0]
        user_data = USERS_DB.find_user(telegram_id=payment['telegram_id'])
        if not user_data:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        user_data = user_data[0]
        msg = templates.bot_payment_info_template(payment,user_data)
        bot.edit_message_caption(msg, call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.change_status_payment_by_admin(value))
        
    # Payment - Send Message Callback
    elif key == "send_message_by_admin":
        if not CLIENT_TOKEN:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
            return
        bot.send_message(call.message.chat.id, f"{MESSAGES['SEND_MESSAGE_TO_USER']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, send_message_to_user, value)

    elif key == "users_bot_send_message_by_admin":
        if not CLIENT_TOKEN:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
            return
        bot.send_message(call.message.chat.id, f"{MESSAGES['SEND_MESSAGE_TO_USER']}",
                         reply_markup=markups.while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_send_message_to_user, value)

            
    # Back to User Panel Callback
    elif key == "back_to_user_panel":
        usr = utils.user_info(URL, value)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = templates.user_info_template(usr, selected_server)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.user_info_markup(usr['uuid']))
    elif key == "back_to_sub_url_user_list":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=markups.sub_url_user_list_markup(value))
    elif key == "back_to_server_management":
        servers = USERS_DB.select_servers()
        bot.edit_message_text(KEY_MARKUP['SERVERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                                    reply_markup=markups.servers_management_markup(servers))
    
    elif key == "back_to_server_list_of_plans":
        plans_list = []
        plans = USERS_DB.select_plans()
        if plans:
            for plan in plans:
                if plan['status']:
                    if plan['server_id'] == int(value):
                        plans_list.append(plan)
        plans_markup = markups.plans_list_markup(plans_list,value)
        bot.edit_message_text({MESSAGES['USERS_BOT_PLANS_LIST']}, call.message.chat.id, call.message.message_id,
                         reply_markup=plans_markup)
        
    elif key == "back_to_server_selected":
        if search_mode == "Single":
            server = USERS_DB.find_server(id=int(value))
            if not server:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_SERVER_NOT_FOUND'])
                return
            server = server[0]
            plans = USERS_DB.select_plans()
            msg = templates.server_info_template(server,plans)
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                                        reply_markup=markups.server_selected_markup(value))
        else:
            bot.edit_message_text(MESSAGES['SEARCH_USER'],call.message.chat.id, call.message.message_id, 
                              reply_markup=markups.search_user_markup(server_id=value))
            search_mode = "Single"

    elif key == "back_to_server_user_list":
        users_list = api.select(URL)
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = templates.users_list_template(users_list)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_list_markup(value, users_list))
        
    elif key == "back_to_users_bot_users_management":
        bot.edit_message_text(KEY_MARKUP['BOT_USERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_users_management_markup())
    elif key == "back_to_bot_users_or_reffral_management":
        if list_mode == "Bot_Users_Search_Name" or "Bot_User":
            bot.edit_message_text(KEY_MARKUP['BOT_USERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_users_management_markup())
        elif list_mode == "User_Refferals":
            users = USERS_DB.find_user(telegram_id=int(selected_telegram_id))
            if not users:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
            user = users[0]
            orders = USERS_DB.find_order(telegram_id=user['telegram_id'])
            paymets = USERS_DB.find_payment(telegram_id=user['telegram_id'])
            wallet = None
            wallets = USERS_DB.find_wallet(telegram_id=user['telegram_id'])
            if wallets:
                wallet = wallets[0]
            non_order_subs = utils.non_order_user_info(user['telegram_id'])
            order_subs = utils.order_user_info(user['telegram_id'])
            plans_list = USERS_DB.select_plans()
            msg = templates.bot_users_info_template(user, orders, paymets, wallet, non_order_subs, order_subs, plans_list)
            bot.send_message(call.message.chat.id, msg, reply_markup=markups.bot_user_info_markup(value))
    
    elif key == "back_management_item_list":
        approved_payments = list_mode == "Approved_Payments"
        non_approved_payments = list_mode == "Non_Approved_Payments"
        pending_payments = list_mode == "Pending_Payments"
        card_payments = list_mode == "Card_Payments"
        digital_payments = list_mode == "Digital_Payments"
        if list_mode == "Orders":
            bot.edit_message_text(KEY_MARKUP['ORDERS_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_orders_management_markup())
        elif approved_payments  or non_approved_payments or pending_payments or card_payments or digital_payments:
            bot.edit_message_text(KEY_MARKUP['PAYMENT_MANAGEMENT'], call.message.chat.id, call.message.message_id,
                              reply_markup=markups.users_bot_payments_management_markup())
        elif list_mode == "User_Payments" or list_mode == "User_Gifts" or list_mode == "User_Orders":
            users = USERS_DB.find_user(telegram_id=int(selected_telegram_id))
            if not users:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'],
                                reply_markup=markups.main_menu_keyboard_markup())
                return
            user = users[0]
            orders = USERS_DB.find_order(telegram_id=user['telegram_id'])
            paymets = USERS_DB.find_payment(telegram_id=user['telegram_id'])
            wallet = None
            wallets = USERS_DB.find_wallet(telegram_id=user['telegram_id'])
            if wallets:
                wallet = wallets[0]
            non_order_subs = utils.non_order_user_info(user['telegram_id'])
            order_subs = utils.order_user_info(user['telegram_id'])
            plans_list = USERS_DB.select_plans()
            msg = templates.bot_users_info_template(user, orders, paymets, wallet, non_order_subs, order_subs, plans_list)
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.bot_user_info_markup(selected_telegram_id))




# Check Admin Permission
@bot.message_handler(func=lambda message: message.chat.id not in ADMINS_ID)
def not_admin(message: Message):
    bot.reply_to(message, MESSAGES['ERROR_NOT_ADMIN'])


# Send Welcome Message Handler
@bot.message_handler(commands=['help', 'start', 'restart'])
def send_welcome(message: Message):
    bot.reply_to(message, MESSAGES['WELCOME'], reply_markup=markups.main_menu_keyboard_markup())
    bot.send_message(message.chat.id, MESSAGES['REQUEST_JOIN_HIDY'], reply_markup=markups.start_bot_markup())


# Send users list Message Handler
# @bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_LIST'])
# def all_users_list(message: Message):
#     # users_list = utils.dict_process(utils.users_to_dict(ADMIN_DB.select_users()))
#     users_list = api.select(URL)
#     if not users_list:
#         bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
#         return
#     msg = templates.users_list_template(users_list)
#     bot.send_message(message.chat.id, msg, reply_markup=markups.users_list_markup(users_list))


# Add User Message Handler
# @bot.message_handler(func=lambda message: message.text == KEY_MARKUP['ADD_USER'])
# def add_user(message: Message):
#     global add_user_data
#     bot.send_message(message.chat.id, MESSAGES['ADD_USER_NAME'], reply_markup=markups.while_add_user_markup())
#     bot.register_next_step_handler(message, add_user_name)


# Panel Backup Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVER_BACKUP'])
def server_backup(message: Message):
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
    zip_file_name = utils.full_backup()
    if not zip_file_name:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
        logging.error("Backup failed")
        return
    
    if message.chat.id in ADMINS_ID:
        bot.send_document(message.chat.id, open(zip_file_name, 'rb'), caption="🤖Backup",disable_notification=True)
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
        
    bot.delete_message(message.chat.id, msg_wait.message_id)


# Server Status Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVER_STATUS'])
def server_status(message: Message):
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
    status = templates.system_status_template(utils.system_status())

    if status:
        bot.send_message(message.chat.id, status)
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    bot.delete_message(message.chat.id, msg_wait.message_id)


# Search User Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_SEARCH'])
def search_user(message: Message):
    global server_mode
    server_mode = "All"
    bot.send_message(message.chat.id, MESSAGES['SEARCH_USER'],
    reply_markup=markups.search_user_markup())


# Users Bot Management Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_BOT_MANAGEMENT'])
def users_bot_management(message: Message):
    if not CLIENT_TOKEN:
        bot.send_message(message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
        return
    bot.send_message(message.chat.id, KEY_MARKUP['USERS_BOT_MANAGEMENT'],
                     reply_markup=markups.users_bot_management_markup())
    
# Server Management Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVERS_MANAGEMENT'])
def servers_management(message: Message):
    servers = USERS_DB.select_servers()
    bot.send_message(message.chat.id, KEY_MARKUP['SERVERS_MANAGEMENT'],
                     reply_markup=markups.servers_management_markup(servers))

# About Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['ABOUT_BOT'])
def about_bot(message: Message):
    bot.send_message(message.chat.id, templates.about_template())

# Debug Handler
@bot.message_handler(commands=['debug'])
def debug(message: Message):
    debug_zip = utils.debug_data()
    if not debug_zip:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
        return
    bot.send_document(message.chat.id, open(debug_zip, 'rb'), caption="👹Debug")


# ----------------------------------- Main -----------------------------------
# Start Bot
def start():
    # Bot Start Commands
    try:
        bot.set_my_commands([
            telebot.types.BotCommand("/start", BOT_COMMANDS['START']),
            telebot.types.BotCommand("/debug", BOT_COMMANDS['DEBUG']),
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
