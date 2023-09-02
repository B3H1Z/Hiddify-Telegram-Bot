# Description: This file contains all the reply and inline keyboard markups used in the bot.
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from UserBot.buttons import KEY_MARKUP
from UserBot.messages import MESSAGES
from AdminBot.markups import sub_url_user_list_markup, sub_user_list_markup


# Main Menu Reply Keyboard Markup
def main_menu_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['SUBSCRIPTION_STATUS']))
    markup.add(KeyboardButton(KEY_MARKUP['LINK_SUBSCRIPTION']), KeyboardButton(KEY_MARKUP['BUY_SUBSCRIPTION']))
    markup.add(KeyboardButton(KEY_MARKUP['TO_QR']), KeyboardButton(KEY_MARKUP['SEND_TICKET']),
               KeyboardButton(KEY_MARKUP['HELP_GUIDE']))
    return markup


# Single User Inline Keyboard Markup
# def user_config_list_markup(uuid):
#     markup = InlineKeyboardMarkup()
#     markup.row_width = 2
#     markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_DIR'], callback_data=f"conf_dir:{uuid}"))
#     markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB'], callback_data=f"conf_sub_url:{uuid}"),
#                InlineKeyboardButton(KEY_MARKUP['CONFIGS_SUB_B64'], callback_data=f"conf_sub_url_b64:{uuid}"))
#     markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_CLASH'], callback_data=f"conf_clash:{uuid}"),
#                InlineKeyboardButton(KEY_MARKUP['CONFIGS_HIDDIFY'], callback_data=f"conf_hiddify:{uuid}"))
#     markup.add(InlineKeyboardButton(KEY_MARKUP['UNLINK_SUBSCRIPTION'], callback_data=f"unlink_subscription:None"))
#     return markup
#
#
# def sub_user_list_markup(uuid):
#     markup = InlineKeyboardMarkup()
#     markup.row_width = 1
#     markup.add(InlineKeyboardButton('Vless', callback_data=f"conf_dir_vless:{uuid}"))
#     markup.add(InlineKeyboardButton('Vmess', callback_data=f"conf_dir_vmess:{uuid}"))
#     markup.add(InlineKeyboardButton('Trojan', callback_data=f"conf_dir_trojan:{uuid}"))
#     markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_user_panel:{uuid}"))
#     return markup


def user_info_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_LIST'], callback_data=f"configs_list:{uuid}"))
    return markup


def confirm_subscription_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['YES'], callback_data=f"confirm_subscription:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['NO'], callback_data=f"cancel_subscription:{uuid}"))
    return markup


def confirm_buy_plan_markup(plan_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['BUY_PLAN'], callback_data=f"confirm_buy_plan:{plan_id}"))
    return markup


def send_screenshot_markup(plan_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEND_SCREENSHOT'], callback_data=f"send_screenshot:{plan_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CANCEL'], callback_data=f"cancel_buy_plan:{plan_id}"))
    return markup


def plans_list_markup(plans):
    markup = InlineKeyboardMarkup(row_width=1)
    keys = []
    for plan in plans:
        if plan['status']:
            keys.append(InlineKeyboardButton(
                f"{plan['size_gb']}{MESSAGES['GB']} | {plan['days']}{MESSAGES['DAY_EXPIRE']} | {plan['price']}{MESSAGES['TOMAN']}",
                callback_data=f"plan_selected:{plan['id']}"))
    if len(keys) == 0:
        return None
    markup.add(*keys)
    return markup


def confirm_payment_by_admin(order_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(KEY_MARKUP['CONFIRM_PAYMENT'], callback_data=f"confirm_payment_by_admin:{order_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['NO'], callback_data=f"cancel_payment_by_admin:{order_id}"))
    return markup


def cancel_markup():
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(KeyboardButton(KEY_MARKUP['CANCEL']))
    return markup
