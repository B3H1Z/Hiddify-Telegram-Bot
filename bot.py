# Description: Main Bot File
import logging
from config import *
from template import *
from markup import *
import api
import telebot
from telegram.constants import ParseMode

# Initialize Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

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
def is_it_digit(message, response=MESSAGES['ERROR_INVALID_NUMBER'], markup=main_menu_keyboard_markup()):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return False
    return True


# Check if message is cancel
def is_it_cancel(message, response=MESSAGES['CANCELED']):
    if message.text == KEY_MARKUP['CANCEL']:
        bot.send_message(message.chat.id, response, reply_markup=main_menu_keyboard_markup())
        return True
    return False


# ----------------------------------- Edit User Area -----------------------------------
# Edit User - Name
def edit_user_name(message, uuid):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = api.edit_user(uuid, name=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"***REMOVED***MESSAGES['SUCCESS_USER_NAME_EDITED']***REMOVED*** ***REMOVED***message.text***REMOVED*** ",
                     reply_markup=main_menu_keyboard_markup())


# Edit User - Usage
def edit_user_usage(message, uuid):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = api.edit_user(uuid, usage_limit_GB=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"***REMOVED***MESSAGES['SUCCESS_USER_USAGE_EDITED']***REMOVED*** ***REMOVED***message.text***REMOVED*** ",
                     reply_markup=main_menu_keyboard_markup())


# Edit User - Days
def edit_user_days(message, uuid):
    if is_it_cancel(message):
        return
    if not is_it_digit(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = api.edit_user(uuid, remaining_days=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"***REMOVED***MESSAGES['SUCCESS_USER_DAYS_EDITED']***REMOVED*** ***REMOVED***message.text***REMOVED*** ",
                     reply_markup=main_menu_keyboard_markup())


# Edit User - Comment
def edit_user_comment(message, uuid):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    status = api.edit_user(uuid, comment=message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, f"***REMOVED***MESSAGES['SUCCESS_USER_COMMENT_EDITED']***REMOVED*** ***REMOVED***message.text***REMOVED*** ",
                     reply_markup=main_menu_keyboard_markup())


# ----------------------------------- Search User Area -----------------------------------
# Search User - Name
def search_user_name(message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    users = api.search_user_by_name(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not users:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=main_menu_keyboard_markup())

    bot.send_message(message.chat.id, users_list_template(users, MESSAGES['SEARCH_RESULT']),
                     reply_markup=users_list_markup(users))


# Search User - UUID
def search_user_uuid(message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    user = api.search_user_by_uuid(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=main_menu_keyboard_markup())
    bot.send_message(message.chat.id, user_info_template(user, MESSAGES['SEARCH_RESULT']), parse_mode=ParseMode.HTML,
                     reply_markup=user_info_markup(user['uuid']))


# Search User - Config
def search_user_config(message):
    if is_it_cancel(message):
        return
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'], reply_markup=while_edit_user_markup())
    user = api.search_user_by_config(message.text)
    bot.delete_message(message.chat.id, msg_wait.message_id)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['SUCCESS_SEARCH_USER'], reply_markup=main_menu_keyboard_markup())
    bot.send_message(message.chat.id, user_info_template(user, MESSAGES['SEARCH_RESULT']),
                     reply_markup=user_info_markup(user['uuid']), parse_mode=ParseMode.HTML)


# ----------------------------------- Callbacks -----------------------------------
# Callback Handler for Inline Buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    # Check if user is not admin
    if call.from_user.id not in ADMINS_ID:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_NOT_ADMIN'])
        return
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    uuid = data[1]

    # ----------------------------------- Users List Area Callbacks -----------------------------------
    # Single User Info Callback
    if key == "info":
        usr = api.user_info(uuid)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = user_info_template(usr)
        bot.send_message(call.message.chat.id, msg, parse_mode=ParseMode.HTML,
                         reply_markup=user_info_markup(usr['uuid']))

    # Next Page Callback
    elif key == "next":
        users_list = api.list_users()
        if not users_list:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=users_list_markup(users_list, int(uuid)))

    # ----------------------------------- Single User Info Area Callbacks -----------------------------------
    # Delete User Callback
    elif key == "user_delete":
        status = api.delete_user(uuid)
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['SUCCESS_USER_DELETED'],
                         reply_markup=main_menu_keyboard_markup())
    # Edit User Main Button Callback
    elif key == "user_edit":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=edit_user_markup(uuid))

    # Configs User Callback
    elif key == "user_config":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_url_user_list_markup(uuid))
        return

    # ----------------------------------- Edit User Area Callbacks -----------------------------------
    # Edit User - Update Message Callback
    elif key == "user_edit_update":
        usr = api.user_info(uuid)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        msg = user_info_template(usr, MESSAGES['EDITED_USER_INFO'])
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode=ParseMode.HTML,
                              reply_markup=edit_user_markup(uuid))
    # Edit User - Edit Usage Callback
    elif key == "user_edit_usage":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_USAGE_LIMIT'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_usage, uuid)
    # Edit User - Reset Usage Callback
    elif key == "user_edit_reset_usage":
        status = api.edit_user(uuid, reset_usage="y")
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
            return
        bot.send_message(call.message.chat.id, MESSAGES['RESET_USAGE'], reply_markup=main_menu_keyboard_markup())
    # Edit User - Edit Days Callback
    elif key == "user_edit_days":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_DAYS'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_days, uuid)
    # Edit User - Reset Days Callback
    elif key == "user_edit_reset_days":
        status = api.edit_user(uuid, reset_days="y")
        if not status:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
            return
        bot.send_message(call.message.chat.id, MESSAGES['RESET_DAYS'], reply_markup=main_menu_keyboard_markup())
    # Edit User - Edit Comment Callback
    elif key == "user_edit_comment":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_COMMENT'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_comment, uuid)
    # Edit User - Edit Name Callback
    elif key == "user_edit_name":
        bot.send_message(call.message.chat.id, MESSAGES['ENTER_NEW_NAME'], reply_markup=while_edit_user_markup())
        bot.register_next_step_handler(call.message, edit_user_name, uuid)
    # ----------------------------------- Configs User Info Area Callbacks -----------------------------------
    # User Configs - DIR Configs Callback
    elif key == "conf_dir":
        sub = api.sub_links(uuid)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        links = api.sub_parse(sub['sub_link'])
        if not links:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        msgs = configs_template(links)
        for msg in msgs:
            if msg:
                bot.send_message(call.message.chat.id, f"***REMOVED***KEY_MARKUP['CONFIGS_DIR']***REMOVED***\n***REMOVED***msg***REMOVED***",
                                 reply_markup=main_menu_keyboard_markup(),
                                 parse_mode=ParseMode.HTML)
    # User Configs - Subscription Configs Callback
    elif key == "conf_sub_url":
        sub = api.sub_links(uuid)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"***REMOVED***KEY_MARKUP['CONFIGS_SUB']***REMOVED***\n***REMOVED***sub['sub_link']***REMOVED***",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Base64 Subscription Configs Callback
    elif key == "conf_sub_url_b64":
        sub = api.sub_links(uuid)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"***REMOVED***KEY_MARKUP['CONFIGS_SUB_B64']***REMOVED***\n***REMOVED***sub['sub_link_b64']***REMOVED***",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Subscription Configs For Clash Callback
    elif key == "conf_clash":
        sub = api.sub_links(uuid)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"***REMOVED***KEY_MARKUP['CONFIGS_CLASH']***REMOVED***\n***REMOVED***sub['clash_configs']***REMOVED***",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Subscription Configs For Hiddify Callback
    elif key == "conf_hiddify":
        sub = api.sub_links(uuid)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"***REMOVED***KEY_MARKUP['CONFIGS_HIDDIFY']***REMOVED***\n***REMOVED***sub['hiddify_configs']***REMOVED***",
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

    # Back to User Panel Callback
    elif key == "back_to_user_panel":
        usr = api.user_info(uuid)
        if not usr:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
            return
        msg = user_info_template(usr)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode=ParseMode.HTML,
                              reply_markup=user_info_markup(usr['uuid']))


# check if user is admin
@bot.message_handler(func=lambda message: message.chat.id not in ADMINS_ID)
def not_admin(message):
    bot.reply_to(message, MESSAGES['ERROR_NOT_ADMIN'])


# Send Welcome message
@bot.message_handler(commands=['help', 'start', 'restart'])
def send_welcome(message):
    bot.reply_to(message, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())


# Send users list
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_LIST'])
def all_users_list(message):
    users_list = api.list_users()
    if not users_list:
        bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
        return
    msg = users_list_template(users_list)
    bot.send_message(message.chat.id, msg, reply_markup=users_list_markup(users_list))


# Add user Data dict
add_user_data = ***REMOVED******REMOVED***


# ----------------------------------- Add User Area -----------------------------------
# Add User Start
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['ADD_USER'])
def add_user(message):
    global add_user_data
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_NAME'], reply_markup=while_add_user_markup())
    bot.register_next_step_handler(message, add_user_name)


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVER_BACKUP'])
def server_backup(message):
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
    file_name = api.backup_panel()
    if file_name:
        bot.send_document(message.chat.id, open(file_name, 'rb'))
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    bot.delete_message(message.chat.id, msg_wait.message_id)


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SERVER_STATUS'])
def server_status(message):
    msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
    status = system_status_template(api.system_status())

    if status:
        bot.send_message(message.chat.id, status, parse_mode=ParseMode.HTML)
    else:
        bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'])
    bot.delete_message(message.chat.id, msg_wait.message_id)


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['USERS_SEARCH'])
def search_user(message):
    bot.send_message(message.chat.id, MESSAGES['SEARCH_USER'], reply_markup=search_user_markup())


# Add User - Name
def add_user_name(message):
    if is_it_cancel(message):
        return
    add_user_data['name'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_USAGE_LIMIT'], reply_markup=while_add_user_markup())
    bot.register_next_step_handler(message, add_user_limit)


# Add User - Usage Limit
def add_user_limit(message):
    if is_it_cancel(message):
        return
    if not is_it_digit(message, f"***REMOVED***MESSAGES['ERROR_INVALID_NUMBER']***REMOVED***\n***REMOVED***MESSAGES['ADD_USER_USAGE_LIMIT']***REMOVED***",
                       while_add_user_markup()):
        bot.register_next_step_handler(message, add_user_limit)
        return
    add_user_data['limit'] = message.text
    bot.send_message(message.chat.id, MESSAGES['ADD_USER_DAYS'], reply_markup=while_add_user_markup())
    bot.register_next_step_handler(message, add_user_usage_days)


# Add User - Usage Days
def add_user_usage_days(message):
    if is_it_cancel(message, MESSAGES['CANCEL_ADD_USER']):
        return
    if not is_it_digit(message, f"***REMOVED***MESSAGES['ERROR_INVALID_NUMBER']***REMOVED***\n***REMOVED***MESSAGES['ADD_USER_DAYS']***REMOVED***",
                       while_add_user_markup()):
        bot.register_next_step_handler(message, add_user_usage_days)
        return
    add_user_data['usage_days'] = message.text
    bot.send_message(message.chat.id,
                     f"***REMOVED***MESSAGES['ADD_USER_CONFIRM']***REMOVED***\n\n***REMOVED***MESSAGES['INFO_USER']***REMOVED*** ***REMOVED***add_user_data['name']***REMOVED***\n "
                     f"***REMOVED***MESSAGES['INFO_USAGE']***REMOVED*** ***REMOVED***add_user_data['limit']***REMOVED*** GB\n***REMOVED***MESSAGES['INFO_REMAINING_DAYS']***REMOVED*** ***REMOVED***add_user_data['usage_days']***REMOVED*** ***REMOVED***MESSAGES['DAY']***REMOVED***",
                     reply_markup=confirm_add_user_markup())
    bot.register_next_step_handler(message, confirm_add_user)


# Add User - Confirm to add user
def confirm_add_user(message):
    if message.text == KEY_MARKUP['CANCEL']:
        bot.send_message(message.chat.id, MESSAGES['CANCEL_ADD_USER'], reply_markup=main_menu_keyboard_markup())
        return
    if message.text == KEY_MARKUP['CONFIRM']:
        msg_wait = bot.send_message(message.chat.id, MESSAGES['WAIT'])
        res = api.add_user(name=add_user_data['name'], usage_limit_GB=add_user_data['limit'],
                           package_days=add_user_data['usage_days'])
        if res:
            bot.send_message(message.chat.id, MESSAGES['SUCCESS_ADD_USER'], reply_markup=main_menu_keyboard_markup())
            usr = api.user_info(res)
            if not usr:
                bot.send_message(message.chat.id, MESSAGES['ERROR_USER_NOT_FOUND'])
                return
            msg = user_info_template(usr, MESSAGES['NEW_USER_INFO'])
            bot.delete_message(message.chat.id, msg_wait.message_id)
            bot.send_message(message.chat.id, msg, reply_markup=user_info_markup(usr['uuid']),
                             parse_mode=ParseMode.HTML)

        else:
            bot.send_message(message.chat.id, MESSAGES['ERROR_UNKNOWN'], reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['CANCEL_ADD_USER'], reply_markup=main_menu_keyboard_markup())


def start():
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.infinity_polling()
