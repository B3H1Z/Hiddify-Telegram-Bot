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
    markup.add(KeyboardButton(KEY_MARKUP['LINK_SUBSCRIPTION']), KeyboardButton(KEY_MARKUP['WALLET']))
    markup.add(KeyboardButton(KEY_MARKUP['BUY_SUBSCRIPTION']), KeyboardButton(KEY_MARKUP['FREE_TEST']))
    markup.add(KeyboardButton(KEY_MARKUP['TO_QR']), KeyboardButton(KEY_MARKUP['SEND_TICKET']),
               KeyboardButton(KEY_MARKUP['HELP_GUIDE']))
    return markup


def user_info_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_LIST'], callback_data=f"configs_list:{uuid}"))
    return markup


def user_info_non_sub_markup(uuid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(KEY_MARKUP['CONFIGS_LIST'], callback_data=f"configs_list:{uuid}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['UNLINK_SUBSCRIPTION'], callback_data=f"unlink_subscription:{uuid}"))
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
    markup.add(InlineKeyboardButton(KEY_MARKUP['BUY_FROM_WALLET'], callback_data=f"confirm_buy_from_wallet:{plan_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['BACK'], callback_data=f"back_to_plans:None"))
    return markup


def send_screenshot_markup(plan_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['SEND_SCREENSHOT'], callback_data=f"send_screenshot:{plan_id}"))
    markup.add(InlineKeyboardButton(KEY_MARKUP['CANCEL'], callback_data=f"del_msg:{plan_id}"))
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

def wallet_info_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(KEY_MARKUP['INCREASE_WALLET_BALANCE'], callback_data=f"INCREASE_WALLET_BALANCE:wallet"))
    return markup
