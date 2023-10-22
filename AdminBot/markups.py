# Description: This file contains all the reply and inline keyboard markups used in the bot.
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from AdminBot.content import KEY_MARKUP
from AdminBot.content import MESSAGES
from config import CLIENT_TOKEN, HIDY_BOT_ID
from Utils.utils import all_configs_settings, rial_to_toman


# Main Menu Reply Keyboard Markup
def main_menu_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    #markup.add(KeyboardButton(KEY_MARKUP['USERS_LIST']))
    #markup.add(KeyboardButton(KEY_MARKUP['USERS_SEARCH']), KeyboardButton(KEY_MARKUP['ADD_USER']))
    markup.add(KeyboardButton(KEY_MARKUP['SERVERS_MANAGEMENT']))
    markup.add(KeyboardButton(KEY_MARKUP['USERS_SEARCH']))
    if CLIENT_TOKEN:
        markup.add(KeyboardButton(KEY_MARKUP['USERS_BOT_MANAGEMENT']))
    markup.add()
    markup.add(KeyboardButton(KEY_MARKUP['SERVER_STATUS']), KeyboardButton(KEY_MARKUP['ABOUT_BOT']),
               KeyboardButton(KEY_MARKUP['SERVER_BACKUP']))

    return markup

#----------------------------------Hiddify User ---------------------------------
# Users List Inline Keyboard Markup
def users_list_markup(server_id, users, page=1):
    markup = InlineKeyboardMarkup(row_width=3)
    USER_PER_PAGE = 20
    start = (page - 1) * USER_PER_PAGE
    end = start + USER_PER_PAGE
    keys = []

    for user in users[start:end]:
        status_tag = ""
        if user['last_connection'] == "Online" or user['last_connection'] == "آنلاین":
            status_tag = "🔵"
        else:
            status_tag = "🟡"
        if user['remaining_day'] == 0:
            status_tag = "🔴"
        if user['usage']['remaining_usage_GB'] <= 0:
            status_tag = "🔴️"

        keys.append(InlineKeyboardButton(f"{status_tag}|{user['name']}", callback_data=f"info:{user['uuid']}"))
    markup.add(*keys)
    if page < len(users) / USER_PER_PAGE:
        markup.add(InlineKeyboardButton(KEY_MARKUP['NEXT_PAGE'], callback_data=f"next:{page + 1}"), row_width=2)
    if page > 1:
        markup.add(InlineKeyboardButton(KEY_MARKUP['PREV_PAGE'], callback_data=f"next:{page - 1}"), row_width=1)
    if server_id != "None":
        markup.add(InlineKeyboardButton(KEY_MARKUP['ADD_USER'], callback_data=f"server_add_user:{server_id}"))
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_SEARCH'], callback_data=f"server_search_user:{server_id}"))
        markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_server_selected:{server_id}"))
    return markup


# Single User Inline Keyboard Markup
def user_info_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_USER'], callback_data=f"user_config:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_USER'], callback_data=f"user_edit:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['DELETE_USER'], callback_data=f"user_delete:{uuid}"))
    return markup


# Single User Edit Inline Keyboard Markup
def edit_user_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_NAME'], callback_data=f"user_edit_name:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_USAGE'], callback_data=f"user_edit_usage:{uuid}"),
               InlineKeyboardButton(KEY_MARKUP['RESET_USAGE'], callback_data=f"user_edit_reset_usage:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_DAYS'], callback_data=f"user_edit_days:{uuid}"),
               InlineKeyboardButton(KEY_MARKUP['RESET_DAYS'], callback_data=f"user_edit_reset_days:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_COMMENT'], callback_data=f"user_edit_comment:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['UPDATE_MESSAGE'], callback_data=f"user_edit_update:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_user_panel:{uuid}"))
    return markup


# # Add User Reply Keyboard Markup
# def while_add_user_markup():
#     markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     markup.add(KeyboardButton(KEY_MARKUP['CANCEL']))
#     return markup


# Edit User Reply Keyboard Markup
def while_edit_user_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['CANCEL']))
    return markup

def while_edit_skip_user_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['SKIP']))
    markup.add(KeyboardButton(KEY_MARKUP['CANCEL']))
    return markup

# Confirm Add User Reply Keyboard Markup
def confirm_add_user_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['CONFIRM']))
    markup.add(KeyboardButton(KEY_MARKUP['CANCEL']))
    return markup


# Subscription URL Inline Keyboard Markup
def sub_url_user_list_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_DIR'], callback_data=f"conf_dir:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB_AUTO'], callback_data=f"conf_sub_auto:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB'], callback_data=f"conf_sub_url:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB_B64'], callback_data=f"conf_sub_url_b64:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_CLASH'], callback_data=f"conf_clash:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_HIDDIFY'], callback_data=f"conf_hiddify:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SING_BOX'], callback_data=f"conf_sub_sing_box:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_FULL_SING_BOX'],
                                        callback_data=f"conf_sub_full_sing_box:{uuid}"))

    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_user_panel:{uuid}"))

    return markup


# Subscription Configs Inline Keyboard Markup
def sub_user_list_markup(uuid,configs):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if configs['vless']:
        markup.add(InlineKeyboardButton('Vless', callback_data=f"conf_dir_vless:{uuid}"))
    if configs['vmess']:
        markup.add(InlineKeyboardButton('Vmess', callback_data=f"conf_dir_vmess:{uuid}"))
    if configs['trojan']:
        markup.add(InlineKeyboardButton('Trojan', callback_data=f"conf_dir_trojan:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_sub_url_user_list:{uuid}"))
    return markup


# Search User Inline Keyboard Markup
def search_user_markup(server_id=None):
    callback_data = server_id if server_id else "None"
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_NAME'], callback_data=f"search_name:{callback_data}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_UUID'], callback_data=f"search_uuid:{callback_data}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_CONFIG'], callback_data=f"search_config:{callback_data}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_EXPIRED_USERS'], callback_data=f"search_expired:{callback_data}"))
    if server_id:
        markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_server_user_list:{server_id}"))
    return markup

#----------------------------------End Hiddify User ---------------------------------
#----------------------------------Bot User Management ------------------------------

# Users Bot Management - Inline Keyboard Markup
def users_bot_management_markup(value=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    # markup.add(
    #     InlineKeyboardButton(KEY_MARKUP['USERS_BOT_ORDERS_STATUS'], callback_data=f"users_bot_orders_status:None"),
    # markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_ADD_PLAN'], callback_data=f"users_bot_add_plan:None"),
    #            InlineKeyboardButton(KEY_MARKUP['USERS_BOT_DEL_PLAN'], callback_data=f"users_bot_list_plans:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BOT_USERS_MANAGEMENT'],
                                    callback_data=f"bot_users_list_management:None"))
    # markup.add(InlineKeyboardButton(KEY_MARKUP['ORDERS_MANAGEMENT'],
    #                                 callback_data=f"users_bot_orders_list_management:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['PAYMENT_MANAGEMENT'],
                                    callback_data=f"users_bot_payments_list_management:None"),
                                    InlineKeyboardButton(KEY_MARKUP['ORDERS_MANAGEMENT'],
                                    callback_data=f"users_bot_orders_list_management:None"),)
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SUB_STATUS'], callback_data=f"users_bot_sub_status:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SEND_MESSAGE_TO_USERS'],
                                    callback_data=f"users_bot_send_msg_users:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_OWNER_INFO'], callback_data=f"users_bot_owner_info:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS'], callback_data=f"users_bot_settings:None"))
    return markup

# Users Bot Users List Management - Inline Keyboard Markup
def users_bot_users_management_markup(value=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_LIST'], callback_data=f"bot_users_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USERS_BOT'], callback_data=f"search_users_bot:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_management_menu:None"))
    return markup

# Users Bot Search Method  - Inline Keyboard Markup
def users_bot_users_search_method_markup(value=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_NAME'], callback_data=f"bot_users_search_name:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_TELEGRAM_ID'], callback_data=f"bot_users_search_telegram_id:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_users_bot_users_management:None"))
    return markup

# Users List Inline Keyboard Markup
def bot_users_list_markup(users, page=1):
    markup = InlineKeyboardMarkup(row_width=3)
    USER_PER_PAGE = 20
    start = (page - 1) * USER_PER_PAGE
    end = start + USER_PER_PAGE
    keys = []
    for user in users[start:end]:
        name = user['full_name'] if user['full_name'] else user['telegram_id']
        keys.append(InlineKeyboardButton(f"{name}", callback_data=f"bot_user_info:{user['telegram_id']}"))
    markup.add(*keys)
    if page < len(users) / USER_PER_PAGE:
        markup.add(InlineKeyboardButton(KEY_MARKUP['NEXT_PAGE'], callback_data=f"bot_user_next:{page + 1}"), row_width=2)
    if page > 1:
        markup.add(InlineKeyboardButton(KEY_MARKUP['PREV_PAGE'], callback_data=f"bot_user_next:{page - 1}"), row_width=1)
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_bot_users_or_reffral_management:None"))
    return markup


# User Item List Inline Keyboard Markup
def bot_user_item_list_markup(items, page=1):
    markup = InlineKeyboardMarkup(row_width=3)
    USER_PER_PAGE = 20
    start = (page - 1) * USER_PER_PAGE
    end = start + USER_PER_PAGE
    keys = []
    for item in items[start:end]:
        keys.append(InlineKeyboardButton(f"{item['id']}", callback_data=f"bot_user_item_info:{item['id']}"))
    markup.add(*keys)
    if page < len(items) / USER_PER_PAGE:
        markup.add(InlineKeyboardButton(KEY_MARKUP['NEXT_PAGE'], callback_data=f"bot_user_item_next:{page + 1}"), row_width=2)
    if page > 1:
        markup.add(InlineKeyboardButton(KEY_MARKUP['PREV_PAGE'], callback_data=f"bot_user_item_next:{page - 1}"), row_width=1)
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_management_item_list:None"))
    return markup

# Users Bot Users info Management - Inline Keyboard Markup
def bot_user_info_markup(telegram_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['USER_SUB_LIST'], callback_data=f"bot_users_sub_user_list:{telegram_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['ORDERS_LIST'], callback_data=f"users_bot_orders_user_list:{telegram_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['PAYMENTS_LIST'], callback_data=f"users_bot_payments_user_list:{telegram_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_WALLET'], callback_data=f"users_bot_wallet_edit_balance:{telegram_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['RESET_TEST'], callback_data=f"users_bot_reset_test:{telegram_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BAN_USER'], callback_data=f"users_bot_ban_user:{telegram_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEND_MESSAGE'], callback_data=f"users_bot_send_message_by_admin:{telegram_id}"))
    # markup.add(InlineKeyboardButton(KEY_MARKUP['GIFT_LIST'], callback_data=f"users_bot_gifts_user_list:{telegram_id}"),
    #            InlineKeyboardButton(KEY_MARKUP['REFERRED_LIST'], callback_data=f"users_bot_referred_user_list:{telegram_id}"))
    #markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_management_menu:None"))
    return markup

# Users Bot Users List Management - Inline Keyboard Markup
def users_bot_orders_management_markup(value=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['ORDERS_LIST'], callback_data=f"users_bot_orders_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_ORDERS'], callback_data=f"search_orders:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_management_menu:None"))
    return markup

def confirm_payment_by_admin(payment_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(KEY_MARKUP['CONFIRM_PAYMENT'], callback_data=f"confirm_payment_by_admin:{payment_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['NO'], callback_data=f"cancel_payment_by_admin:{payment_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEND_MESSAGE'], callback_data=f"send_message_by_admin:{payment_id}"))
    return markup

def send_message_to_user_markup(admin_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['ANSWER'], callback_data=f"answer_to_admin:{admin_id}"))
    return markup

def change_status_payment_by_admin(payment_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(KEY_MARKUP['CHANGE_STATUS_PAYMENT'], callback_data=f"change_status_payment_by_admin:{payment_id}"))
    return markup

def confirm_change_status_payment_by_admin(payment_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(KEY_MARKUP['YES'], callback_data=f"confirm_change_status_payment_by_admin:{payment_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['NO'], callback_data=f"cancel_change_status_payment_by_admin:{payment_id}"))
    return markup

# Users Bot Payments List Management - Inline Keyboard Markup
def users_bot_payments_management_markup(value=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['APPROVED_PAYMENTS_LIST'],
                                    callback_data=f"bot_users_approved_payments_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['NON_APPROVED_PAYMENTS_LIST'],
                                    callback_data=f"users_bot_non_approved_payments_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['PENDING_PAYMENT_LIST'],
                                    callback_data=f"users_bot_pending_payments_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CARD_PAYMENT_LIST'],
                                    callback_data=f"users_bot_card_payments_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['DIGITAL_PAYMENT_LIST'], 
                                    callback_data=f"users_bot_digital_payments_list:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_PAYMENTS'], callback_data=f"search_payments:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_management_menu:None"))
    return markup

#----------------------------------Bot User Settings Management ------------------------------

# Users Bot Management - Settings - Inline Keyboard Markup
def users_bot_management_settings_markup(settings):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    status_hyperlink = "✅" if settings['visible_hiddify_hyperlink'] else "❌"
    status_three_rand = "✅" if settings['three_random_num_price'] else "❌"
    status_panel_auto_backup = "✅" if settings['panel_auto_backup'] else "❌"
    status_bot_auto_backup = "✅" if settings['bot_auto_backup'] else "❌"
    status_force_join = "✅" if settings['force_join_channel'] else "❌"
    status_buy_sub = "✅" if settings['buy_subscription_status'] else "❌"
    status_renewal_sub = "✅" if settings['renewal_subscription_status'] else "❌"

    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_SHOW_HIDI_LINK']} | {status_hyperlink}",
                                    callback_data=f"users_bot_settings_hyperlink:{settings['visible_hiddify_hyperlink']}"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_SHOW_THREE_RAND']} | {status_three_rand}",
                                    callback_data=f"users_bot_settings_three_rand_price:{settings['three_random_num_price']}"))
    
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_BUY_SUBSCRIPTION_STATUS']} | {status_buy_sub}",
                                    callback_data=f"users_bot_settings_buy_sub_status:{settings['buy_subscription_status']}"),
               InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_SUBSCRIPTION_STATUS']} | {status_renewal_sub}",
                                    callback_data= f"users_bot_settings_renewal_sub_status:{settings['renewal_subscription_status']}"))
    
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_CHANNEL_ّFORCE_JOIN']} | {status_force_join}",
                                    callback_data=f"users_bot_settings_force_join:{settings['force_join_channel']}"),
               InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_CHANNEL_ID'],
                                    callback_data=f"users_bot_settings_channel_id:{settings['channel_id']}"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_AUTO_BACKUP']} | {status_panel_auto_backup}",
                             callback_data=f"users_bot_settings_panel_auto_backup:{settings['panel_auto_backup']}"),)
            #    InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_BOT_AUTO_BACKUP']} | {status_bot_auto_backup}",
            #                         callback_data=f"users_bot_settings_bot_auto_backup:{settings['bot_auto_backup']}")
            #    )

    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_SET_WELCOME_MSG'],
                                    callback_data=f"users_bot_settings_set_welcome_msg:None"),
               InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_MANUAL'],
                                    callback_data="users_bot_settings_panel_manual_menu:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_SET_FAQ_MSG'],
                                    callback_data=f"users_bot_settings_faq_management:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_VISIBLE_SUBS'],
                                    callback_data=f"users_bot_settings_visible_sub_menu:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_TEST_SUB'],
                                    callback_data=f"users_bot_settings_test_sub_menu:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_NOTIF_REMINDER'],
                                    callback_data=f"users_bot_settings_notif_reminder_menu:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_MIN_DEPO'],
                                    callback_data=f"users_bot_settings_min_depo:{settings['min_deposit_amount']}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_METHOD'],
                                    callback_data=f"users_bot_settings_renewal_method_menu:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_RESET_FREE_TEST_LIMIT'],
                                    callback_data=f"users_bot_settings_reset_free_test_limit_question:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_BACKUP_BOT'],
                                    callback_data=f"users_bot_settings_backup_bot:None"),
               InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_RESTORE_BOT'],
                                    callback_data=f"users_bot_settings_restore_bot:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_management_menu:None"))
    return markup

# Users Bot Management - Settings - Renewal Method - Inline Keyboard Markup
def users_bot_management_settings_renewal_method_markup(settings):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    default, advanced, fairly = "❌", "❌", "❌"
    
    if settings['renewal_method'] == 1:
        default = "✅"
    elif settings['renewal_method'] == 2:
        advanced = "✅"
    elif settings['renewal_method'] == 3:
        fairly = "✅"
        
        
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_METHOD_DEFAULT']} | {default}",
                                    callback_data=f"users_bot_settings_renewal_method:1"),
                InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_METHOD_ADVANCED']} | {advanced}",
                                    callback_data=f"users_bot_settings_renewal_method:2"),
                InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_METHOD_FAIRLY']} | {fairly}",
                      callback_data=f"users_bot_settings_renewal_method:3"),
    )
               
    if settings['renewal_method'] == 2:
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_METHOD_ADVANCED_DAYS'],
                                        callback_data=f"users_bot_settings_renewal_method_advanced_days:None"))
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_RENEWAL_METHOD_ADVANCED_USAGE'],
                                        callback_data=f"users_bot_settings_renewal_method_advanced_usage:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_settings:None"))
    return markup

# Users Bot Management - Settings - Free Test - Inline Keyboard Markup
def users_bot_management_settings_test_sub_markup(settings):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    status_test_sub = "✅" if settings['test_subscription'] else "❌"
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_TEST_SUB']} | {status_test_sub}",
                                    callback_data=f"users_bot_settings_test_sub:test_subscription"))
    if settings['test_subscription']:
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_TEST_SUB_SIZE'],
                                        callback_data=f"users_bot_settings_test_sub_size:None"))
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_TEST_SUB_DAYS'],
                                        callback_data=f"users_bot_settings_test_sub_days:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_settings:None"))
    return markup

# Users Bot Management - Settings - Reminder Notificaation - Inline Keyboard Markup
def users_bot_management_settings_notif_reminder_markup(settings):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    status_test_sub = "✅" if settings['reminder_notification'] else "❌"
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_NOTIF_REMINDER']} | {status_test_sub}",
                                    callback_data=f"users_bot_settings_notif_reminder:reminder_notification"))
    if settings['reminder_notification']:
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_NOTIF_REMINDER_USAGE'],
                                        callback_data=f"users_bot_settings_notif_reminder_usage:None"))
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_NOTIF_REMINDER_DAYS'],
                                        callback_data=f"users_bot_settings_notif_reminder_days:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_settings:None"))
    return markup

# Users Bot Management - Settings - Subscription Links - Inline Keyboard Markup
def users_bot_management_settings_visible_sub_markup(settings):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    status_visible_conf_dir = "✅" if settings['visible_conf_dir'] else "❌"
    status_conf_sub_auto = "✅" if settings['visible_conf_sub_auto'] else "❌"
    status_conf_sub_url = "✅" if settings['visible_conf_sub_url'] else "❌"
    status_conf_sub_url_b64 = "✅" if settings['visible_conf_sub_url_b64'] else "❌"
    status_conf_clash = "✅" if settings['visible_conf_clash'] else "❌"
    status_conf_hiddify = "✅" if settings['visible_conf_hiddify'] else "❌"
    status_conf_sub_sing_box = "✅" if settings['visible_conf_sub_sing_box'] else "❌"
    status_conf_sub_full_sing_box = "✅" if settings['visible_conf_sub_full_sing_box'] else "❌"

    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_DIR']} | {status_visible_conf_dir}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_dir"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_SUB_AUTO']} | {status_conf_sub_auto}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_sub_auto"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_SUB']} | {status_conf_sub_url}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_sub_url"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_SUB_B64']} | {status_conf_sub_url_b64}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_sub_url_b64"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_CLASH']} | {status_conf_clash}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_clash"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_HIDDIFY']} | {status_conf_hiddify}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_hiddify"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_SING_BOX']} | {status_conf_sub_sing_box}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_sub_sing_box"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['CONFIGS_FULL_SING_BOX']} | {status_conf_sub_full_sing_box}",
                                    callback_data=f"users_bot_settings_visible_sub:visible_conf_sub_full_sing_box"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_settings:None"))
    return markup

# Users Bot Management - Settings - Manual - Inline Keyboard Markup
def users_bot_management_settings_panel_manual_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_MANUAL_ANDROID'],
                                    callback_data=f"users_bot_settings_panel_manual:msg_manual_android"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_MANUAL_IOS'],
                                    callback_data=f"users_bot_settings_panel_manual:msg_manual_ios"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_MANUAL_WIN'],
                                    callback_data=f"users_bot_settings_panel_manual:msg_manual_windows"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_MANUAL_MAC'],
                                    callback_data=f"users_bot_settings_panel_manual:msg_manual_mac"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_PANEL_MANUAL_LIN'],
                                    callback_data=f"users_bot_settings_panel_manual:msg_manual_linux"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_settings:None"))
    return markup

def users_bot_management_settings_faq_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    settings = all_configs_settings()
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_SET_FAQ_MESSAGE'],
                                    callback_data=f"users_bot_settings_set_faq_msg:None"))
    if settings['msg_faq']:
        markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_HIDE_FAQ'],
                                    callback_data=f"users_bot_settings_hide_faq:None"))
    return markup


# Users Bot Management - Edit Owner Info - Inline Keyboard Markup
def users_bot_edit_owner_info_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_OWNER_INFO_EDIT_USERNAME'],
                                    callback_data=f"users_bot_owner_info_edit_username:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_OWNER_INFO_EDIT_CARD_NUMBER'],
                                    callback_data=f"users_bot_owner_info_edit_card_number:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_OWNER_INFO_EDIT_CARD_NAME'],
                                    callback_data=f"users_bot_owner_info_edit_card_name:None"))
    return markup

def users_bot_management_settings_reset_free_test_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIRM'],
                                    callback_data=f"users_bot_management_settings_reset_free_test_confirm:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"users_bot_settings:None"))
    return markup

# Single Subscription Inline Keyboard Markup
def sub_search_info_markup(uuid,user):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_USER'], callback_data=f"user_config:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_USER'], callback_data=f"user_edit:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['DELETE_USER'], callback_data=f"user_delete:{uuid}"))
    name = user['full_name'] if user['full_name'] else user['telegram_id']
    markup.add(InlineKeyboardButton(f"{name}", callback_data=f"bot_user_info:{user['telegram_id']}"))
    return markup

#--------------------------------------End Bot User Management -----------------------------------
#----------------------------------End Bot User Settings Management ------------------------------
#-----------------------------------------Servers Management -------------------------------------

# Server Management - Server List - Inline Keyboard Markup
def servers_management_markup(servers):
    markup = InlineKeyboardMarkup(row_width=1)
    keys = []
    if servers:
        for server in servers:
            #if server['status']:
            keys.append(InlineKeyboardButton(f"{server['title']}",
                                             callback_data=f"server_selected:{server['id']}"))
    keys.append(InlineKeyboardButton(KEY_MARKUP['ADD_SERVER'],
                                     callback_data=f"add_server:None"))
    markup.add(*keys)
    return markup

# Server Management - Server Info - Inline Keyboard Markup
def server_selected_markup(server_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['SERVER_LIST_OF_USERS'],
                                    callback_data=f"server_list_of_users:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SERVER_LIST_OF_PLANS'],
                                    callback_data=f"server_list_of_plans:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['EDIT_SERVER'],
                                    callback_data=f"edit_server:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_server_management:None"))
    
    return markup

# Server Management - Server Delete - Inline Keyboard Markup
def server_delete_markup(server_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIRM'],
                                    callback_data=f"confirm_delete_server:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CANCEL'],
                                    callback_data=f"server_selected:{server_id}"))
    return markup


# Server Management - Server Edit - Inline Keyboard Markup
def server_edit_markup(server_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['SERVER_EDIT_TITLE'],
                                    callback_data=f"server_edit_title:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SERVER_EDIT_USER_LIMIT'],
                                    callback_data=f"server_edit_user_limit:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SERVER_EDIT_URL'],
                                    callback_data=f"server_edit_url:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['DELETE_SERVER'],
                                    callback_data=f"delete_server:{server_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_server_selected:{server_id}"))
    return markup

# Server Management - Plans List - Inline Keyboard Markup
def plans_list_markup(plans, server_id, delete_mode=False):
    markup = InlineKeyboardMarkup(row_width=1)
    plan_selected_callback_data = "users_bot_del_plan:" if delete_mode else "info_plan_selected:" 
    back_callback_data = "back_to_server_list_of_plans:" if delete_mode else "back_to_server_selected:"
    keys = []
    if plans:
        for plan in plans:
            keys.append(InlineKeyboardButton(
                f"{plan['size_gb']}{MESSAGES['GB']} | {plan['days']}{MESSAGES['DAY']} | {rial_to_toman(plan['price'])} {MESSAGES['TOMAN']}",
                callback_data = f"{plan_selected_callback_data}{plan['id']}"))
    if not delete_mode:
        keys.append(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_ADD_PLAN'], callback_data=f"users_bot_add_plan:{server_id}"))
        keys.append(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_DEL_PLAN'], callback_data=f"users_bot_list_plans:{server_id}"))
    keys.append(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"{back_callback_data}{server_id}"))
    markup.add(*keys)
    return markup

# Server Management - Plans List - Inline Keyboard Markup
def plan_info_selected_markup(server_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_server_list_of_plans:{server_id}"))
    return markup

#-------------------------------------End Servers Management -------------------------------------

def start_bot_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    bot_id = HIDY_BOT_ID.replace("@", "")
    markup.add(InlineKeyboardButton(KEY_MARKUP['SUPPORT_GROUP'], url=f"https://t.me/{bot_id}"))
    return markup
