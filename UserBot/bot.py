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
from Utils.api import api

# TELEGRAM_DB.create_user_table()
# Initialize Bot
bot = telebot.TeleBot(CLIENT_TOKEN, parse_mode="HTML")
bot.remove_webhook()
admin_bot = admin_bot()
BASE_URL = urlparse(PANEL_URL).scheme + "://" + urlparse(PANEL_URL).netloc
# Bot Start Commands
try:
    bot.set_my_commands([
        telebot.types.BotCommand("/start", BOT_COMMANDS['START']),
    ])
except telebot.apihelper.ApiTelegramException as e:
    if e.result.status_code == 401:
        logging.error("Invalid Telegram Bot Token!")
        exit(1)


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


# ----------------------------------- Buy Plan Area -----------------------------------
charge_wallet = {}
renew_subscription_dict = {}


# Next Step Buy Plan - Confirm
# def buy_plan_confirm(message: Message, plan):
#     if not plan:
#         bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
#                          reply_markup=main_menu_keyboard_markup())
#         return
#     owner_info = USERS_DB.select_owner_info()[0]
#     if not owner_info:
#         bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
#                          reply_markup=main_menu_keyboard_markup())
#         return
#     price = utils.replace_last_three_with_random(str(plan['price']))
#     order_info['price'] = price
#     bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
#                           text=owner_info_template(owner_info['card_number'], owner_info['card_owner'], price),
#                           reply_markup=send_screenshot_markup(plan_id=plan['id']))


# Next Step Buy From Wallet - Confirm
def buy_from_wallet_confirm(message: Message, plan):
    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    if not wallet:
        # Wallet not created
        bot.send_message(message.chat.id, MESSAGES['LACK_OF_WALLET_BALANCE'])

    if wallet:
        wallet = wallet[0]
        if plan['price'] > wallet['balance']:
            bot.send_message(message.chat.id, MESSAGES['LACK_OF_WALLET_BALANCE'])
            return
        else:
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
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())

    wallet = wallet[0]
    plan_info = USERS_DB.find_plan(id=plan_id)
    if not plan_info:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    plan_info = plan_info[0]
    if plan_info['price'] > wallet['balance']:
        bot.send_message(message.chat.id, MESSAGES['LACK_OF_WALLET_BALANCE'])
        del renew_subscription_dict[message.chat.id]
        return

    user = ADMIN_DB.find_user(uuid=uuid)
    if not user:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    user_info = utils.users_to_dict(user)
    if not user_info:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    user_info_process = utils.dict_process(user_info)
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

    if user_info_process['remaining_day'] <= 0 or user_info_process['usage']['remaining_usage_GB'] <= 0:
        new_usage_limit = plan_info['size_gb']
        new_package_days = plan_info['days']
        ADMIN_DB.reset_package_usage(uuid=uuid)
        ADMIN_DB.reset_package_days(uuid=uuid)
    else:
        new_usage_limit = user_info['usage_limit_GB'] + plan_info['size_gb']
        new_package_days = user_info['package_days'] + plan_info['days']

    edit_status = ADMIN_DB.edit_user(uuid=uuid, usage_limit_GB=new_usage_limit, package_days=new_package_days)
    if not edit_status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    bot.send_message(message.chat.id, MESSAGES['SUCCESSFUL_RENEWAL'], reply_markup=main_menu_keyboard_markup())
    link = f"{BASE_URL}/{urlparse(PANEL_URL).path.split('/')[1]}/{uuid}/"
    user_name = f"<a href='{link}'> {user_info_process['name']} </a>"
    for ADMIN in ADMINS_ID:
        #admin_bot.send_message(ADMIN, f"{MESSAGES['ADMIN_NOTIFY_NEW_RENEWAL']} {user_name} {MESSAGES['SUBSCRIPTION']}\n{MESSAGES['ORDER_ID']} {order_id}")
        admin_bot.send_message(ADMIN, f"{MESSAGES['ADMIN_NOTIFY_NEW_RENEWAL']} {user_name} {MESSAGES['SUBSCRIPTION']}\n{MESSAGES['ORDER_ID']} {order_id}")

    # Apply Plan
    # bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'], reply_markup=cancel_markup())
    # bot.register_next_step_handler(message, next_step_send_name_for_renewal_from_wallet, info)


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

    # bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'])

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    path = os.path.join(os.getcwd(), 'UserBot', 'Receiptions', f"{message.chat.id}-{charge_wallet['id']}.jpg")
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)

    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payment_method = "Card"

    status = USERS_DB.add_payment(charge_wallet['id'], message.chat.id,
                                  charge_wallet['amount'], payment_method, path,
                                  message.from_user.full_name,
                                  created_at)
    if status:
        payment = USERS_DB.find_payment(id=charge_wallet['id'])
        if not payment:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        payment = payment[0]
        for ADMIN in ADMINS_ID:
            admin_bot.send_photo(ADMIN, open(path, 'rb'),
                                 caption=payment_received_template(payment),
                                 reply_markup=confirm_payment_by_admin(charge_wallet['id']))
        bot.send_message(message.chat.id, MESSAGES['WAIT_FOR_ADMIN_CONFIRMATION'],
                         reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())


# Next Step Buy Plan - Send Name

# def next_step_send_name(message, plan, path, order_id):
#     print(plan)
#     if is_it_cancel(message):
#         return
#
#     if not plan:
#         bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
#                          reply_markup=main_menu_keyboard_markup())
#         return
#     name = message.text
#     while is_it_command(message):
#         message = bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'])
#         bot.register_next_step_handler(message, next_step_send_name, plan, path, order_id)
#         return
#     # send it for admin bot
#     print(plan)
#     created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#     status = USERS_DB.add_order(order_id, message.chat.id, name, plan['id'], created_at)
#     sub_id = random.randint(1000000, 9999999)
#     if not status:
#         bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
#                          reply_markup=main_menu_keyboard_markup())
#         return
#
#     uuid = ADMIN_DB.add_default_user(order_info['user_name'], plan['days'], plan['size_gb'],
#                                      int(PANEL_ADMIN_ID))
#     if not uuid:
#         bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
#                          reply_markup=main_menu_keyboard_markup())
#         return
#
#     ordered_sub = USERS_DB.add_order_subscription(sub_id, order_id, uuid)
#     # if status:
#     #     for ADMIN in ADMINS_ID:
#     #         admin_bot.send_photo(ADMIN, open(path, 'rb'),
#     #                              caption=payment_received_template(plan, name, paid_amount, order_id,
#     #                                                                MESSAGES['NEW_PAYMENT_RECEIVED'],
#     #                                                                MESSAGES['PAYMENT_ASK_TO_CONFIRM']),
#     #                              reply_markup=confirm_payment_by_admin(order_id))
#     #     bot.send_message(message.chat.id, MESSAGES['WAIT_FOR_ADMIN_CONFIRMATION'],
#     #                      reply_markup=main_menu_keyboard_markup())
#     # else:
#     #     bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
#     #                      reply_markup=main_menu_keyboard_markup())


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

    value = ADMIN_DB.add_default_user(name, plan['days'], plan['size_gb'],
                                      int(PANEL_ADMIN_ID))
    if not value:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    sub_id = random.randint(1000000, 9999999)
    add_sub_status = USERS_DB.add_order_subscription(sub_id, order_id, value)
    if not add_sub_status:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    status = USERS_DB.add_order(order_id, message.chat.id, name, plan['id'], created_at)

    if not status:
        bot.send_message(message.chat.id,
                         f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}",
                         reply_markup=main_menu_keyboard_markup())
        return
    wallet = USERS_DB.find_wallet(telegram_id=message.chat.id)
    if wallet:
        wallet = wallet[0]
        wallet_balance = int(wallet['balance']) - int(paid_amount)
        user_info = USERS_DB.edit_wallet(message.chat.id, balance=wallet_balance)
        if not user_info:
            bot.send_message(message.chat.id,
                             f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}",
                             reply_markup=main_menu_keyboard_markup())
            return
    bot.send_message(message.chat.id,
                     f"{MESSAGES['PAYMENT_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {order_id}",
                     reply_markup=main_menu_keyboard_markup())
    link = f"{BASE_URL}/{urlparse(PANEL_URL).path.split('/')[1]}/{value}/"
    user_name = f"<a href='{link}'> {name} </a>"
    for ADMIN in ADMINS_ID:
        admin_bot.send_message(ADMIN, f"{MESSAGES['ADMIN_NOTIFY_NEW_SUB']} {user_name} {MESSAGES['ADMIN_NOTIFY_CONFIRM']}\n{MESSAGES['ORDER_ID']} {order_id}")


# ----------------------------------- Get Free Test Area -----------------------------------
# Next Step Get Free Test - Send Name
def next_step_send_name_for_get_free_test(message: Message):
    if is_it_cancel(message):
        return
    name = message.text
    while is_it_command(message):
        message = bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'])
        bot.register_next_step_handler(message, next_step_send_name_for_get_free_test)
        return

    test_user_days = 1
    test_user_size_gb = 1
    test_user_comment = "Free Test User"

    uuid = ADMIN_DB.add_default_user(name, test_user_days, test_user_size_gb, int(PANEL_ADMIN_ID), test_user_comment)
    if not uuid:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    non_order_id = random.randint(1000000, 9999999)
    non_order_status = USERS_DB.add_non_order_subscription(non_order_id, message.chat.id, uuid)
    if not non_order_status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    edit_user_status = USERS_DB.edit_user(message.chat.id, test_account=True)
    print(edit_user_status)
    if not edit_user_status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['GET_FREE_CONFIRMED'],
                     reply_markup=main_menu_keyboard_markup())
    link = f"{BASE_URL}/{urlparse(PANEL_URL).path.split('/')[1]}/{value}/"
    user_name = f"<a href='{link}'> {name} </a>"
    for ADMIN in ADMINS_ID:
        admin_bot.send_message(ADMIN, f"{MESSAGES['ADMIN_NOTIFY_NEW_FREE_TEST']} {user_name} {MESSAGES['ADMIN_NOTIFY_CONFIRM']}\n{MESSAGES['ORDER_ID']} {order_id}")
    # created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    # # plan_id = 0
    #
    # # paid_amount = 0
    # order_id = random.randint(1000000, 9999999)
    #
    # value = ADMIN_DB.add_default_user(name, days, size_gb,
    #                                   int(PANEL_ADMIN_ID))
    # if not value:
    #     bot.send_message(message.chat.id,
    #                      f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}")
    #     return
    # sub_id = random.randint(1000000, 9999999)
    # add_sub_status = USERS_DB.add_order_subscription(sub_id, order_id, value)
    # if not add_sub_status:
    #     bot.send_message(message.chat.id,
    #                      f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}")
    #     return
    # status = USERS_DB.add_order(order_id, message.chat.id, name, plan_id, paid_amount, payment_method, path,
    #                             created_at, True)
    # if not status:
    #     bot.send_message(message.chat.id,
    #                      f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}")
    #     return
    #
    # user_info = USERS_DB.edit_user(message.chat.id, get_free=True)
    # if not user_info:
    #     bot.send_message(message.chat.id,
    #                      f"{MESSAGES['UNKNOWN_ERROR']}\n{MESSAGES['ORDER_ID']} {order_id}")
    #     return
    # bot.send_message(message.chat.id,
    #                  f"{MESSAGES['GET_FREE_CONFIRMED']}\n{MESSAGES['ORDER_ID']} {order_id}")


# ----------------------------------- To QR Area -----------------------------------
# Next Step QR - QR Code
def next_step_to_qr(message: Message):
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
        is_it_subscribed = USERS_DB.find_non_order_subscription(uuid=uuid)
        if is_it_subscribed:
            bot.send_message(message.chat.id, MESSAGES['ALREADY_SUBSCRIBED'],
                             reply_markup=main_menu_keyboard_markup())
            return
        non_sub_id = random.randint(10000000, 99999999)
        status = USERS_DB.add_non_order_subscription(non_sub_id, message.chat.id, uuid)
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
        bot.send_message(message.chat.id, f"{MESSAGES['INCREASE_WALLET_BALANCE_AMOUNT']}\n{MESSAGES['MINIMUM_DEPOSIT_AMOUNT']}: "
                                          f"{rial_to_toman(minimum_deposit_amount)} {MESSAGES['TOMAN']}", reply_markup=cancel_markup())
        bot.register_next_step_handler(message, next_step_increase_wallet_balance)
        return
    settings = utils.all_configs_settings()
    if not settings:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return

    # # order_info['price'] = price
    # settings = USERS_DB.select_bool_config()
    # if not settings:
    #     bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
    #                      reply_markup=main_menu_keyboard_markup())
    #     return
    # settings = utils.settings_config_to_dict(settings)

    # if not settings:
    #     bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
    #                      reply_markup=main_menu_keyboard_markup())
    #     return

    charge_wallet['amount'] = str(amount)
    if settings['three_random_num_price'] == 1:
        charge_wallet['amount'] = utils.replace_last_three_with_random(str(amount))

    charge_wallet['id'] = random.randint(1000000, 9999999)

    # Send 0 to identify wallet balance charge
    bot.send_message(message.chat.id,
                     owner_info_template(settings['card_number'], settings['card_holder'], charge_wallet['amount']),
                     reply_markup=send_screenshot_markup(plan_id=charge_wallet['id']))


# ----------------------------------- Callback Query Area -----------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    value = data[1]

    # ----------------------------------- Link Subscription Area -----------------------------------
    # Confirm Link Subscription
    if key == 'confirm_subscription':
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

    # Confirm To Buy Plan
    # elif key == 'confirm_buy_plan':
    #     plan = USERS_DB.find_plan(id=value)[0]
    #     buy_plan_confirm(call.message, plan)

    # Confirm To Buy From Wallet
    elif key == 'confirm_buy_from_wallet':
        plan = USERS_DB.find_plan(id=value)[0]
        buy_from_wallet_confirm(call.message, plan)
    elif key == 'confirm_renewal_from_wallet':
        plan = USERS_DB.find_plan(id=value)[0]
        renewal_from_wallet_confirm(call.message)
    # Ask To Send Screenshot
    elif key == 'send_screenshot':
        bot.send_message(call.message.chat.id, MESSAGES['REQUEST_SEND_SCREENSHOT'])
        bot.register_next_step_handler(call.message, next_step_send_screenshot, charge_wallet)
        # else:
        #     plan = USERS_DB.find_plan(id=value)[0]
        #     bot.register_next_step_handler(call.message, next_step_send_screenshot, plan)

    # ----------------------------------- User Subscriptions Info Area -----------------------------------
    # Unlink non-order subscription
    elif key == 'unlink_subscription':
        delete_status = USERS_DB.delete_non_order_subscriptions(uuid=value)
        if delete_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_UNLINKED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())

    elif key == 'update_info_subscription':
        sub = utils.find_order_subscription_by_uuid(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return

        user = ADMIN_DB.find_user(uuid=sub['uuid'])
        if not user:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        user = utils.dict_process(utils.users_to_dict(user))[0]
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=user_info_template(sub['id'], user, MESSAGES['INFO_USER']),
                                  reply_markup=user_info_markup(sub['uuid']))
        except:
            pass

    # ----------------------------------- wallet Area -----------------------------------
    # INCREASE WALLET BALANCE
    elif key == 'increase_wallet_balance':
        bot.send_message(call.message.chat.id, MESSAGES['INCREASE_WALLET_BALANCE_AMOUNT'], reply_markup=cancel_markup())

        bot.register_next_step_handler(call.message, next_step_increase_wallet_balance)


    elif key == 'renewal_subscription':
        renew_subscription_dict[call.message.chat.id] = {
            'uuid': None,
            'plan_id': None,
        }
        plans = USERS_DB.select_plans()
        if not plans:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        renew_subscription_dict[call.message.chat.id]['uuid'] = value
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=plans_list_markup(plans, renewal=True))

    elif key == 'renewal_plan_selected':
        plan = USERS_DB.find_plan(id=value)[0]
        if not plan:
            bot.send_message(call.message.chat.id, MESSAGES['PLANS_NOT_FOUND'],
                             reply_markup=main_menu_keyboard_markup())
            return
        renew_subscription_dict[call.message.chat.id]['plan_id'] = plan['id']
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=plan_info_template(plan),
                              reply_markup=confirm_buy_plan_markup(plan['id'], renewal=True))

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
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_user_list_markup(value))
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


    # ----------------------------------- Back Area -----------------------------------
    # Back To User Menu
    elif key == "back_to_user_panel":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=user_info_markup(value))

    # Back To Plans
    elif key == "back_to_plans":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        buy_subscription(call.message)

    # Delete Message
    elif key == "del_msg":
        bot.delete_message(call.message.chat.id, call.message.message_id)

    # Invalid Command
    else:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_INVALID_COMMAND'])


# Bot Start Message Handler
@bot.message_handler(commands=['start'])
def start(message: Message):
    if USERS_DB.find_user(telegram_id=message.chat.id):
        bot.send_message(message.chat.id, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())
        return
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = USERS_DB.add_user(telegram_id=message.chat.id, created_at=created_at)
    if not status:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())


# If user is not in users table, request /start
@bot.message_handler(func=lambda message: not USERS_DB.find_user(telegram_id=message.chat.id))
def not_in_users_table(message: Message):
    bot.send_message(message.chat.id, MESSAGES['REQUEST_START'])


# User Subscription Status Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SUBSCRIPTION_STATUS'])
def subscription_status(message: Message):
    non_order_subs = utils.non_order_user_info(message.chat.id)
    order_subs = utils.order_user_info(message.chat.id)

    if not non_order_subs and not order_subs:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return

    if non_order_subs:
        for non_order_sub in non_order_subs:
            if non_order_sub:
                api_user_data = user_info_template(non_order_sub['sub_id'], non_order_sub, MESSAGES['INFO_USER'])
                bot.send_message(message.chat.id, api_user_data,
                                 reply_markup=user_info_non_sub_markup(non_order_sub['uuid']))
    if order_subs:
        for order_sub in order_subs:
            if order_sub:
                api_user_data = user_info_template(order_sub['sub_id'], order_sub, MESSAGES['INFO_USER'])
                bot.send_message(message.chat.id, api_user_data,
                                 reply_markup=user_info_markup(order_sub['uuid']))


# User Buy Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['BUY_SUBSCRIPTION'])
def buy_subscription(message: Message):
    plans = USERS_DB.select_plans()
    if not plans:
        bot.send_message(message.chat.id, MESSAGES['PLANS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    plan_markup = plans_list_markup(plans)
    if not plan_markup:
        bot.send_message(message.chat.id, MESSAGES['PLANS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['PLANS_LIST'], reply_markup=plan_markup)


# Config To QR Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['TO_QR'])
def to_qr(message: Message):
    bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_TO_QR'])
    bot.register_next_step_handler(message, next_step_to_qr)


# Help Guide Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['HELP_GUIDE'])
def help_guide(message: Message):
    bot.send_message(message.chat.id, connection_help_template(), reply_markup=main_menu_keyboard_markup())


# Ticket To Support Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SEND_TICKET'])
def send_ticket(message: Message):
    owner_info = USERS_DB.find_str_config(key="support_username")
    bot.send_message(message.chat.id, support_template(owner_info), reply_markup=main_menu_keyboard_markup())


# Link Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['LINK_SUBSCRIPTION'])
def link_subscription(message: Message):
    bot.send_message(message.chat.id, MESSAGES['ENTER_SUBSCRIPTION_INFO'], reply_markup=cancel_markup())
    bot.register_next_step_handler(message, next_step_link_subscription)


# User Buy Subscription Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['WALLET'])
def wallet_balance(message: Message):
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
def wallet_balance(message: Message):
    users = USERS_DB.find_user(telegram_id=message.chat.id)
    if users:
        user = users[0]
        if user['test_account']:
            bot.send_message(message.chat.id, MESSAGES['ALREADY_RECEIVED_FREE'],
                             reply_markup=main_menu_keyboard_markup())
            return
        else:
            bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'], reply_markup=cancel_markup())
            bot.register_next_step_handler(message, next_step_send_name_for_get_free_test)


# Cancel Message Handler
@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['CANCEL'])
def wallet_balance(message: Message):
    bot.send_message(message.chat.id, MESSAGES['CANCELED'], reply_markup=main_menu_keyboard_markup())


# Start
def start():
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.infinity_polling()
