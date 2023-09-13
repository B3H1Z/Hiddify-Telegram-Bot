# Description: This file contains all the reply and inline keyboard markups used in the bot.
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from AdminBot.content import KEY_MARKUP
from AdminBot.content import MESSAGES
from config import CLIENT_TOKEN
from Utils.utils import all_configs_settings, rial_to_toman


# Main Menu Reply Keyboard Markup
def main_menu_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['USERS_LIST']))
    markup.add(KeyboardButton(KEY_MARKUP['USERS_SEARCH']), KeyboardButton(KEY_MARKUP['ADD_USER']))
    if CLIENT_TOKEN:
        markup.add(KeyboardButton(KEY_MARKUP['USERS_BOT_MANAGEMENT']))
    markup.add()
    markup.add(KeyboardButton(KEY_MARKUP['SERVER_STATUS']), KeyboardButton(KEY_MARKUP['ABOUT_BOT']),
               KeyboardButton(KEY_MARKUP['SERVER_BACKUP']))

    return markup


# Users List Inline Keyboard Markup
def users_list_markup(users, page=1):
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


# Add User Reply Keyboard Markup
def while_add_user_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['CANCEL']))
    return markup


# Edit User Reply Keyboard Markup
def while_edit_user_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
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
    settings = all_configs_settings()
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_DIR'], callback_data=f"conf_dir:{uuid}"))
    if settings['hiddify_v8_feature']:
        markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB_AUTO'], callback_data=f"conf_sub_auto:{uuid}"))

    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB'], callback_data=f"conf_sub_url:{uuid}"),
               InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB_B64'], callback_data=f"conf_sub_url_b64:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_CLASH'], callback_data=f"conf_clash:{uuid}"),
               InlineKeyboardButton(KEY_MARKUP['CONFIGS_HIDDIFY'], callback_data=f"conf_hiddify:{uuid}"))
    if settings['hiddify_v8_feature']:
        markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SING_BOX'], callback_data=f"conf_sub_sing_box:{uuid}"),
                   InlineKeyboardButton(KEY_MARKUP['CONFIGS_FULL_SING_BOX'],
                                        callback_data=f"conf_sub_full_sing_box:{uuid}"))

    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_user_panel:{uuid}"))

    return markup


# Subscription Configs Inline Keyboard Markup
def sub_user_list_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Vless', callback_data=f"conf_dir_vless:{uuid}"))
    markup.add(InlineKeyboardButton('Vmess', callback_data=f"conf_dir_vmess:{uuid}"))
    markup.add(InlineKeyboardButton('Trojan', callback_data=f"conf_dir_trojan:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_user_panel:{uuid}"))
    return markup


# Search User Inline Keyboard Markup
def search_user_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_NAME'], callback_data=f"search_name:name"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_UUID'], callback_data=f"search_uuid:uuid"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_USER_CONFIG'], callback_data=f"search_config:config"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEARCH_EXPIRED_USERS'], callback_data=f"search_expired:expired"))
    return markup


# Users Bot Management - Inline Keyboard Markup
def users_bot_management_markup(value=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(KEY_MARKUP['USERS_BOT_ORDERS_STATUS'], callback_data=f"users_bot_orders_status:None"),
        InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SUB_STATUS'], callback_data=f"users_bot_sub_status:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_ADD_PLAN'], callback_data=f"users_bot_add_plan:None"),
               InlineKeyboardButton(KEY_MARKUP['USERS_BOT_DEL_PLAN'], callback_data=f"users_bot_list_plans:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SEND_MESSAGE_TO_USERS'],
                                    callback_data=f"users_bot_send_msg_users:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_OWNER_INFO'], callback_data=f"users_bot_owner_info:None"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS'], callback_data=f"users_bot_settings:None"))
    return markup


# Users Bot Management - Settings - Inline Keyboard Markup
def users_bot_management_settings_markup(settings):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    status_hyperlink = "✅" if settings['visible_hiddify_hyperlink'] else "❌"
    status_three_rand = "✅" if settings['three_random_num_price'] else "❌"
    status_panel_v8 = "✅" if settings['hiddify_v8_feature'] else "❌"
    status_force_join = "✅" if settings['force_join_channel'] else "❌"
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_SHOW_HIDI_LINK']} | {status_hyperlink}",
                                    callback_data=f"users_bot_settings_hyperlink:{settings['visible_hiddify_hyperlink']}"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_PNL_V8_FEATURES']} | {status_panel_v8}",
                                    callback_data=f"users_bot_settings_panel_v8:{settings['hiddify_v8_feature']}"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_SHOW_THREE_RAND']} | {status_three_rand}",
                                    callback_data=f"users_bot_settings_three_rand_price:{settings['three_random_num_price']}"))
    markup.add(InlineKeyboardButton(f"{KEY_MARKUP['USERS_BOT_SETTINGS_CHANNEL_ّFORCE_JOIN']} | {status_force_join}",
                                    callback_data=f"users_bot_settings_force_join:{settings['force_join_channel']}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_MIN_DEPO'],
                                    callback_data=f"users_bot_settings_min_depo:{settings['min_deposit_amount']}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['USERS_BOT_SETTINGS_CHANNEL_ID'],
                                    callback_data=f"users_bot_settings_channel_id:{settings['channel_id']}"))
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


# Users Bot Management - Plans List - Inline Keyboard Markup
def plans_list_markup(plans):
    markup = InlineKeyboardMarkup(row_width=1)
    keys = []
    for plan in plans:
        if plan['status']:
            keys.append(InlineKeyboardButton(
                f"{plan['size_gb']}{MESSAGES['GB']} | {plan['days']}{MESSAGES['DAY']} | {rial_to_toman(plan['price'])} {MESSAGES['TOMAN']}",
                callback_data=f"users_bot_del_plan:{plan['id']}"))
    if len(keys) == 0:
        return None
    markup.add(*keys)
    return markup
