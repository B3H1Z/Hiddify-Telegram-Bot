# Description: Main Bot File
import random
import time
import telebot
from telebot.types import Message, CallbackQuery

from config import *
from AdminBot.commands import BOT_COMMANDS
from AdminBot.markups import *
from AdminBot.templates import *
import Utils.utils as utils
from Shared.common import user_bot

# Initialize Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")
bot.delete_webhook()

if CLIENT_TOKEN:
    user_bot = user_bot()
# Bot Start Commands
try:
    bot.set_my_commands([
        telebot.types.BotCommand("/start", BOT_COMMANDS['START']),
    ])
except telebot.apihelper.ApiTelegramException as e:
    if e.result.status_code == 401:
        logging.error("Invalid Telegram Bot Token!")
        exit(1)


# ----------------------------------- Helper Functions -----------------------------------
# Check if message is digit
def is_it_digit(message: Message, response=MESSAGES['ERROR_INVALID_NUMBER'], markup=main_menu_keyboard_markup()):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return False
    return True


# Check if message is cancel
def is_it_cancel(message: Message, response=MESSAGES['CANCELED']):
    if message.text == KEY_MARKUP['CANCEL']:
        bot.send_message(message.chat.id, response, reply_markup=main_menu_keyboard_markup())
        return True
    return False


# ----------------------------------- Add User Area -----------------------------------
# Add user Data dict
add_user_data = {}


# Add User - Name
def add_user_name(message: Message):
    if is_it_cancel(message):
        return
    add_user_data['name'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_USAGE_LIMIT'], reply_markup=while_add_user_markup())
    bot.register_next_step_handler(message, add_user_limit)


# Add User - Usage Limit
def add_user_limit(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, f"{MESSAGES['ERROR_INVALID_NUMBER']}\n{MESSAGES['ADD_USER_USAGE_LIMIT']}",
                       while_add_user_markup()):
        bot.register_next_step_handler(message, add_user_limit)
        return
    add_user_data['limit'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_DAYS'], reply_markup=while_add_user_markup())
    bot.register_next_step_handler(message, add_user_usage_days)


# Add User - Usage Days
def add_user_usage_days(message: Message):
    if is_it_cancel(message, MESSAGES['CANCEL_ADD_USER']):
        return
    if not is_it_digit(message, f"{MESSAGES['ERROR_INVALID_NUMBER']}\n{MESSAGES['ADD_USER_DAYS']}",
                       while_add_user_markup()):
        bot.register_next_step_handler(message, add_user_usage_days)
        return
    add_user_data['usage_days'] = message.text
    bot.send_message(message.chat.id,
                     f"{MESSAGES['ADD_USER_CONFIRM']}\n\n{MESSAGES['INFO_USER']} {add_user_data['name']}\n"
                     f"{MESSAGES['INFO_USAGE']} {add_user_data['limit']} {MESSAGES['GB']}\n{MESSAGES['INFO_REMAINING_DAYS']} {add_user_data['usage_days']} {MESSAGES['DAY']}",
                     reply_markup=confirm_add_user_markup())
    bot.register_next_step_handler(message, confirm_add_user)


# Add User - Confirm to add user
def confirm_add_user(message: Message):
    if message.text == KEY_MARKUP['CANCEL']:
        bot.send_message(message.chat.id, MESSAGES['CANCEL_ADD_USER'], reply_markup=main_menu_keyboard_markup())
        return
    if message.text == KEY_MARKUP['CONFIRM']:
        msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
        res = ADMIN_DB.add_default_user(name=add_user_data['name'], package_days=int(add_user_data['usage_days']),
                                        usage_limit_GB=int(add_user_data['limit']), added_by=int(PANEL_ADMIN_ID))
        if res:
            bot.send_message(message.chat.id, MESSAGES['SUCCESS_ADD_USER'], reply_markup=main_menu_keyboard_markup())
            usr = utils.user_info(res)
            if not usr:
                bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
                return
            msg = user_info_template(usr, MESSAGES['NEW_USER_INFO'])
            bot.delete_message(message.chat.id, msg_wait.message_id)
            bot.send_message(message.chat.id, msg, reply_markup=user_info_markup(usr['uuid']))

        else:
            bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['CANCEL_ADD_USER'], reply_markup=main_menu_keyboard_markup())


# ----------------------------------- Edit User Area -----------------------------------
# Edit User - Name
def edit_user_name(message: Message, uuid):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = ADMIN_DB.edit_user(uuid, name=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_USER_NAME_EDITED']} {message.text} ",
                     reply_markup=main_menu_keyboard_markup())


# Edit User - Usage
def edit_user_usage(message: Message, uuid):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = ADMIN_DB.edit_user(uuid, usage_limit_GB=int(message.text))
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_USER_USAGE_EDITED']} {message.text} {MESSAGES['GB']}",
                     reply_markup=main_menu_keyboard_markup())


# Edit User - Days
def edit_user_days(message: Message, uuid):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = ADMIN_DB.edit_user(uuid, package_days=int(message.text))
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id,
                     f"{MESSAGES['SUCCESS_USER_DAYS_EDITED']} {message.text} {MESSAGES['DAY_EXPIRE']} ",
                     reply_markup=main_menu_keyboard_markup())


# Edit User - Comment
def edit_user_comment(message: Message, uuid):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = ADMIN_DB.edit_user(uuid, comment=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"{MESSAGES['SUCCESS_USER_COMMENT_EDITED']} {message.text} ",
                     reply_markup=main_menu_keyboard_markup())


# ----------------------------------- Search User Area -----------------------------------
# Search User - Name
def search_user_name(message: Message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    users = utils.search_user_by_name(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=main_menu_keyboard_markup())

    bot.send_message(message.chat.id, users_list_template(users, MESSAGES['SEARCH_RESULT']),
                     reply_markup=users_list_markup(users))


# Search User - UUID
def search_user_uuid(message: Message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    user = utils.search_user_by_uuid(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=main_menu_keyboard_markup())
    bot.send_message(message.chat.id, user_info_template(user, MESSAGES['SEARCH_RESULT']),
                     reply_markup=user_info_markup(user['uuid']))


# Search User - Config
def search_user_config(message: Message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    user = utils.search_user_by_config(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=main_menu_keyboard_markup())
    bot.send_message(message.chat.id, user_info_template(user, MESSAGES['SEARCH_RESULT']),
                     reply_markup=user_info_markup(user['uuid']))


# ----------------------------------- Users Bot Management Area -----------------------------------
add_plan_data = {}


# Add Plan - Size
def users_bot_add_plan_usage(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    add_plan_data['usage'] = int(message.text)
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_DAYS'], reply_markup=while_edit_user_markup())
    bot.register_next_step_handler(message, users_bot_add_plan_days)


# Add Plan - Days
def users_bot_add_plan_days(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    add_plan_data['days'] = int(message.text)
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_PRICE'], reply_markup=while_edit_user_markup())
    bot.register_next_step_handler(message, users_bot_add_plan_price)


# Add Plan - Price
def users_bot_add_plan_price(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    add_plan_data['price'] = int(message.text)

    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = utils.users_bot_add_plan(add_plan_data['usage'], add_plan_data['days'], add_plan_data['price'])
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_SUCCESS'], reply_markup=main_menu_keyboard_markup())


# Users Bot - Edit Owner Info - Username
def users_bot_edit_owner_info_username(message: Message):
    if is_it_cancel(message):
        return
    if not message.text.startswith('@'):
        bot.send_message(message.chat.id, MESSAGES['ERROR_INVALID_USERNAME'], reply_markup=main_menu_keyboard_markup())
        return
    status = USERS_DB.edit_owner_info(telegram_username=message.text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=main_menu_keyboard_markup())


# Users Bot - Edit Owner Info - Card Number
def users_bot_edit_owner_info_card_number(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    if len(message.text) != 16:
        bot.send_message(message.chat.id, MESSAGES['ERROR_INVALID_CARD_NUMBER'],
                         reply_markup=main_menu_keyboard_markup())
        return
    status = USERS_DB.edit_owner_info(card_number=message.text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=main_menu_keyboard_markup())


# Users Bot - Edit Owner Info - Cardholder Name
def users_bot_edit_owner_info_card_name(message: Message):
    if is_it_cancel(message):
        return
    status = USERS_DB.edit_owner_info(card_owner=message.text)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_UPDATE_DATA'], reply_markup=main_menu_keyboard_markup())


# Users Bot - Send Message - All Users
def users_bot_send_msg_users(message: Message):
    if is_it_cancel(message):
        return
    if not CLIENT_TOKEN:
        bot.send_message(message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'], reply_markup=main_menu_keyboard_markup())
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    users_number_id = USERS_DB.select_users()
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not users_number_id:
        bot.send_message(message.chat.id, MESSAGES['ERROR_NO_USERS'], reply_markup=main_menu_keyboard_markup())
        return
    for user in users_number_id:
        time.sleep(0.05)
        try:
            user_bot.send_message(user['telegram_id'], message.text)
        except Exception as e:
            logging.warning(f"Error in send message to user {user['telegram_id']}: {e}")
            continue
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEND_MSG_USERS'], reply_markup=main_menu_keyboard_markup())


# Users Bot - Settings - Update Message
def users_bot_settings_update_message(message: Message):
    settings = USERS_DB.select_settings()
    if not settings:
        return
    settings = settings[0]
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=f"{MESSAGES['USERS_BOT_SETTINGS']}",
                          reply_markup=users_bot_management_settings_markup(settings))


# Users Bot - Order Status
def users_bot_order_status(message: Message):
    from UserBot.templates import payment_received_template
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return

    payment = USERS_DB.find_payment(id=int(message.text))
    if not payment:
        bot.send_message(message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return

    # plan = USERS_DB.find_plan(id=payment[0]['plan_id'])
    # if not payment:
    #     bot.send_message(message.chat.id, MESSAGES['ERROR_ORDER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
    #     return
    payment = payment[0]
    is_it_accepted = None
    if payment['approved'] == 0:
        is_it_accepted = MESSAGES['PAYMENT_ACCEPT_STATUS_NOT_CONFIRMED']
    elif payment['approved'] == 1:
        is_it_accepted = MESSAGES['PAYMENT_ACCEPT_STATUS_CONFIRMED']
    else:
        is_it_accepted = MESSAGES['PAYMENT_ACCEPT_STATUS_WAITING']

    bot.send_photo(message.chat.id, photo=open(payment['payment_image'], 'rb'),
                   caption=payment_received_template(payment,
                                                     footer=f"{MESSAGES['PAYMENT_ACCEPT_STATUS']} {is_it_accepted}\n{MESSAGES['CREATED_AT']} {payment['created_at']}"),
                   reply_markup=main_menu_keyboard_markup())


def users_bot_sub_status(message: Message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return

    if len(message.text) == 7:
        user = USERS_DB.find_order_subscription(id=int(message.text))
    elif len(message.text) == 8:
        user = USERS_DB.find_non_order_subscription(id=int(message.text))
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SUB_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return

    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_SUB_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    user_uuid = user[0]['uuid']

    usr = utils.user_info(user_uuid)
    if not usr:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
        return
    msg = user_info_template(usr)
    bot.send_message(message.chat.id, msg,
                     reply_markup=user_info_markup(usr['uuid']))


# ----------------------------------- Callbacks -----------------------------------
# Callback Handler for Inline Buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    # Check if user is not admin
    if call.from_user.id not in ADMINS_ID:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_NOT_ADMIN'])
        return
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    value = data[1]

    # ----------------------------------- Users List Area Callbacks -----------------------------------
    # Single User Info Callback
    if key == "info":
        usr = utils.user_info(value)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = user_info_template(usr)
        bot.send_message(call.message.chat.id, msg,
                         reply_markup=user_info_markup(usr['uuid']))

    # Next Page Callback
    elif key == "next":
        users_list = utils.dict_process(utils.users_to_dict(ADMIN_DB.select_users()))
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=users_list_markup(users_list, int(value)))

    # ----------------------------------- Single User Info Area Callbacks -----------------------------------
    # Delete User Callback
    elif key == "user_delete":
        status = ADMIN_DB.delete_user(uuid=value)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_USER_DELETED'],
                         reply_markup=main_menu_keyboard_markup())
    # Edit User Main Button Callback
    elif key == "user_edit":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=edit_user_markup(value))

    # Configs User Callback
    elif key == "user_config":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_url_user_list_markup(value))
        return

    # ----------------------------------- Edit User Area Callbacks -----------------------------------
    # Edit User - Update Message Callback
    elif key == "user_edit_update":
        usr = utils.user_info(value)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        msg = user_info_template(usr, MESSAGES['EDITED_USER_INFO'])
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=edit_user_markup(value))
    # Edit User - Edit Usage Callback
    elif key == "user_edit_usage":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_USAGE_LIMIT'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_usage, value)
    # Edit User - Reset Usage Callback
    elif key == "user_edit_reset_usage":
        status = ADMIN_DB.reset_package_usage(uuid=value)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
            return
        bot.send_message(call.message.chat.id, MESSAGES['RESET_USAGE'], reply_markup=main_menu_keyboard_markup())
    # Edit User - Edit Days Callback
    elif key == "user_edit_days":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_DAYS'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_days, value)
    # Edit User - Reset Days Callback
    elif key == "user_edit_reset_days":
        status = ADMIN_DB.reset_package_days(uuid=value)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
            return
        bot.send_message(call.message.chat.id, MESSAGES['RESET_DAYS'], reply_markup=main_menu_keyboard_markup())
    # Edit User - Edit Comment Callback
    elif key == "user_edit_comment":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_COMMENT'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_comment, value)
    # Edit User - Edit Name Callback
    elif key == "user_edit_name":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_NAME'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_name, value)

    # ----------------------------------- Configs User Info Area Callbacks -----------------------------------
    # User Configs - DIR Configs Callback

    elif key == "conf_dir":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_user_list_markup(value))
    # User Configs - VLESS Configs Callback
    elif key == "conf_dir_vless":
        sub = utils.sub_links(value)
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
        msgs = configs_template(configs['vless'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=main_menu_keyboard_markup())
    # User Configs - VMess Configs Callback
    elif key == "conf_dir_vmess":
        sub = utils.sub_links(value)
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
        msgs = configs_template(configs['vmess'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=main_menu_keyboard_markup())
    # User Configs - Trojan Configs Callback
    elif key == "conf_dir_trojan":
        sub = utils.sub_links(value)
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
        msgs = configs_template(configs['trojan'])
        for message in msgs:
            if message:
                bot.send_message(call.message.chat.id, f"{message}",
                                 reply_markup=main_menu_keyboard_markup())

    # User Configs - Subscription Configs Callback
    elif key == "conf_sub_url":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_SUB']}\n<code>{sub['sub_link']}</code>",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Base64 Subscription Configs Callback
    elif key == "conf_sub_url_b64":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_SUB_B64']}\n<code>{sub['sub_link_b64']}</code>",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Subscription Configs For Clash Callback
    elif key == "conf_clash":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_CLASH']}\n<code>{sub['clash_configs']}</code>",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Subscription Configs For Hiddify Callback
    elif key == "conf_hiddify":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_HIDDIFY']}\n<code>{sub['hiddify_configs']}</code>",
                         reply_markup=main_menu_keyboard_markup())

    else:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_INVALID_COMMAND'])

    # ----------------------------------- Search User Area Callbacks -----------------------------------
    # Search User - Name Callback
    if key == "search_name":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_NAME'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_user_name)
    # Search User - UUID Callback
    elif key == "search_uuid":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_UUID'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_user_uuid)
    # Search User - Config Callback
    elif key == "search_config":
        bot.send_message(call.message.chat.id, MESSAGES['SEARCH_USER_CONFIG'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, search_user_config)
    # Search User - Expired Callback
    elif key == "search_expired":
        users_list = utils.dict_process(utils.users_to_dict(ADMIN_DB.select_users()))
        users_list = utils.expired_users_list(users_list)
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = users_list_template(users_list, MESSAGES['EXPIRED_USERS_LIST'])
        bot.send_message(call.message.chat.id, msg, reply_markup=users_list_markup(users_list))

    # ----------------------------------- Users Bot Management Callbacks -----------------------------------
    # Plan Management - Add Plan Callback
    elif key == "users_bot_add_plan":
        bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN'], reply_markup=while_edit_user_markup())
        bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_ADD_PLAN_USAGE'])
        bot.register_next_step_handler(call.message, users_bot_add_plan_usage)

    # Plan Management - Edit Plan Callback
    elif key == "users_bot_del_plan":
        status = USERS_DB.edit_plan(value, status=0)
        if status:
            bot.send_message(call.message.chat.id, MESSAGES['USERS_BOT_PLAN_DELETED'])
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])

    # Plan Management - List Plans Callback
    elif key == "users_bot_list_plans":
        plans = USERS_DB.select_plans()
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PLAN_NOT_FOUND'])
            return
        plans_markup = plans_list_markup(plans)
        if not plans_markup:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_PLAN_NOT_FOUND'])
            return
        bot.send_message(call.message.chat.id,
                         f"{MESSAGES['USERS_BOT_PLANS_LIST']}\n{MESSAGES['USERS_BOT_SELECT_PLAN_TO_DELETE']}",
                         reply_markup=plans_markup)

    # Owner Info - Edit Owner Info Callback
    elif key == "users_bot_owner_info":
        owner_info = USERS_DB.select_owner_info()[0]
        bot.send_message(call.message.chat.id,
                         owner_info_template(owner_info['telegram_username'], owner_info['card_number'],
                                             owner_info['card_owner']),
                         reply_markup=users_bot_edit_owner_info_markup())
    # Owner Info - Edit Owner Username Callback
    elif key == "users_bot_owner_info_edit_username":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_OWNER_INFO_ADD_USERNAME']}",
                         reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_edit_owner_info_username)

    # Owner Info - Edit Owner Card Number Callback
    elif key == "users_bot_owner_info_edit_card_number":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_OWNER_INFO_ADD_CARD_NUMBER']}",
                         reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_edit_owner_info_card_number)

    # Owner Info - Edit Owner Cardholder Callback
    elif key == "users_bot_owner_info_edit_card_name":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_OWNER_INFO_ADD_CARD_NAME']}",
                         reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_edit_owner_info_card_name)

    # Send Message - Send Message To All Users Callback
    elif key == "users_bot_send_msg_users":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_SEND_MSG_USERS']}",
                         reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, users_bot_send_msg_users)

    # User Bot Settings  - Main Settings Callback
    elif key == "users_bot_settings":
        settings = USERS_DB.select_settings()
        if not settings:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        settings = settings[0]
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_SETTINGS']}",
                         reply_markup=users_bot_management_settings_markup(settings))

    # User Bot Settings  - Set Hyperlink Status Callback
    elif key == "users_bot_settings_hyperlink":
        if value == "1":
            USERS_DB.edit_settings(visible_hiddify_hyperlink=False)
        elif value == "0":
            USERS_DB.edit_settings(visible_hiddify_hyperlink=True)
        users_bot_settings_update_message(call.message)

    # User Bot Settings  - Order Status Callback
    elif key == "users_bot_orders_status":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_ORDER_NUMBER_REQUEST']}")
        bot.register_next_step_handler(call.message, users_bot_order_status)

    elif key == "users_bot_sub_status":
        bot.send_message(call.message.chat.id, f"{MESSAGES['USERS_BOT_SUB_ID_REQUEST']}")
        bot.register_next_step_handler(call.message, users_bot_sub_status)

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

        payment_status = USERS_DB.edit_payment(payment_id, approved=True)
        if payment_status:
            wallet = USERS_DB.find_wallet(telegram_id=payment_info['telegram_id'])
            if not wallet:
                bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
                return
            wallet = wallet[0]
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

        # return
        # if payment_status:
        #     plan_info = USERS_DB.find_payment(id=order_info['plan_id'], )
        #     if plan_info:
        #         plan_info = plan_info[0]
        #         value = ADMIN_DB.add_default_user(order_info['user_name'], plan_info['days'], plan_info['size_gb'],
        #                                           int(PANEL_ADMIN_ID))
        #         if not value:
        #             bot.send_message(call.message.chat.id,
        #                              f"{MESSAGES['ERROR_UNKNOWN']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        #             return
        #         sub_id = random.randint(1000000, 9999999)
        #         add_sub_status = USERS_DB.add_order_subscription(sub_id, order_info['id'], value)
        #         if not add_sub_status:
        #             bot.send_message(call.message.chat.id,
        #                              f"{MESSAGES['ERROR_UNKNOWN']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        #             return
        #         user_bot.send_message(int(order_info['telegram_id']),
        #                               f"{MESSAGES['PAYMENT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        #         bot.send_message(call.message.chat.id,
        #                          f"{MESSAGES['PAYMENT_CONFIRMED_ADMIN']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        #         bot.delete_message(call.message.chat.id, call.message.message_id)
        #     else:
        #         # for wallet balance charge
        #         if order_info['plan_id'] == 0:
        #             users = USERS_DB.find_user(telegram_id=order_info['telegram_id'])
        #             if users:
        #                 user = users[0]
        #                 wallet_balance = int(user['wallet_balance']) + int(order_info['paid_amount'])
        #                 user_info = USERS_DB.edit_user(order_info['telegram_id'], wallet_balance=wallet_balance)
        #                 if user_info:
        #                     user_bot.send_message(int(order_info['telegram_id']),
        #                                           f"{MESSAGES['WALLET_PAYMENT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        #                     bot.send_message(call.message.chat.id,
        #                                      f"{MESSAGES['PAYMENT_CONFIRMED_ADMIN']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        #                     bot.delete_message(call.message.chat.id, call.message.message_id)
        #         else:
        #             bot.send_message(call.message.chat.id,
        #                              f"{MESSAGES['ERROR_UNKNOWN']}\n{MESSAGES['ORDER_ID']} {payment_id}")
        # else:
        #     bot.send_message(call.message.chat.id, f"{MESSAGES['ERROR_UNKNOWN']}\n{MESSAGES['ORDER_ID']} {payment_id}")

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

    # Back to User Panel Callback
    elif key == "back_to_user_panel":
        usr = utils.user_info(value)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = user_info_template(usr)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=user_info_markup(usr['uuid']))


# Check Admin Permission
@bot.message_handler(func=lambda message: message.chat.id not in ADMINS_ID)
def not_admin(message: Message):
    bot.reply_to(message, MESSAGES['ERROR_NOT_ADMIN'])


# Send Welcome Message Handler
@bot.message_handler(commands=['help', 'start', 'restart'])
def send_welcome(message: Message):
    bot.reply_to(message, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())


# Send users list Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_LIST'])
def all_users_list(message: Message):
    users_list = utils.dict_process(utils.users_to_dict(ADMIN_DB.select_users()))
    if not users_list:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
        return
    msg = users_list_template(users_list)
    bot.send_message(message.chat.id, msg, reply_markup=users_list_markup(users_list))


# Add User Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['ADD_USER'])
def add_user(message: Message):
    global add_user_data
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_NAME'], reply_markup=while_add_user_markup())
    bot.register_next_step_handler(message, add_user_name)


# Panel Backup Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVER_BACKUP'])
def server_backup(message: Message):
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
    file_name = utils.backup_panel()
    if file_name:
        bot.send_document(message.chat.id, open(file_name, 'rb'))
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    bot.delete_message(message.chat.id, msg_wait.message_id)


# Server Status Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVER_STATUS'])
def server_status(message: Message):
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
    status = system_status_template(utils.system_status())

    if status:
        bot.send_message(message.chat.id, status)
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    bot.delete_message(message.chat.id, msg_wait.message_id)


# Search User Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_SEARCH'])
def search_user(message: Message):
    bot.send_message(message.chat.id, MESSAGES['SEARCH_USER'], reply_markup=search_user_markup())


# Users Bot Management Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_BOT_MANAGEMENT'])
def users_bot_management(message: Message):
    if not CLIENT_TOKEN:
        bot.send_message(message.chat.id, MESSAGES['ERROR_CLIENT_TOKEN'])
        return
    bot.send_message(message.chat.id, KEY_MARKUP['USERS_BOT_MANAGEMENT'], reply_markup=users_bot_management_markup())


# About Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['ABOUT_BOT'])
def about_bot(message: Message):
    bot.send_message(message.chat.id, about_template())


# ----------------------------------- Main -----------------------------------
# Start Bot
def start():
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.infinity_polling()
