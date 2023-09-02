import datetime

from AdminBot.templates import configs_template
from config import *
from UserBot.markups import *
from UserBot.templates import *
from UserBot.messages import MESSAGES
from UserBot.buttons import KEY_MARKUP
from UserBot.commands import BOT_COMMANDS
import telebot
import Utils.utils as utils
from Shared.common import admin_bot
from telebot.types import ForceReply

# TELEGRAM_DB.create_user_table()
# Initialize Bot
bot = telebot.TeleBot(CLIENT_TOKEN, parse_mode="HTML")
admin_bot = admin_bot()

# Bot Start Commands
try:
    bot.set_my_commands([
        telebot.types.BotCommand("/start", BOT_COMMANDS['START']),
    ])
except telebot.apihelper.ApiTelegramException as e:
    if e.result.status_code == 401:
        logging.error("Invalid Telegram Bot Token!")
        exit(1)


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


def next_step_subscription_status_1(message):
    uuid = type_of_subscription(message.text)
    if not uuid:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_INFO_NOT_FOUND'])
        return
    user_data = ADMIN_DB.find_user(uuid=uuid)
    user_data = utils.users_to_dict(user_data)
    user_data = utils.dict_process(user_data)
    if user_data:
        user_data = user_data[0]
        bot.send_message(message.chat.id,
                         f"{MESSAGES['CONFIRM_SUBSCRIPTION_QUESTION']}\n{MESSAGES['NAME']} <b>{user_data['name']}</b>",
                         reply_markup=confirm_subscription_markup(user_data['uuid']))
    else:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_INFO_NOT_FOUND'],
                         reply_markup=main_menu_keyboard_markup())


def buy_plan_info(message, plan):
    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, plan_info_template(plan), reply_markup=confirm_buy_plan_markup(plan['id']))


order_info = {}


def buy_plan_confirm(message, plan):
    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    owner_info = USERS_DB.select_owner_info()[0]
    if not owner_info:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    price = replace_last_three_with_random(str(plan['price']))
    order_info['price'] = price
    bot.send_message(message.chat.id,
                     owner_info_template(plan, owner_info['card_number'], owner_info['card_owner'], price),
                     reply_markup=send_screenshot_markup(plan_id=plan['id']))


def next_step_send_screenshot(message, plan):
    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    # check is it image
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, MESSAGES['ERROR_TYPE_SEND_SCREENSHOT'])
        return

    # ask for name
    bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_NAME'])
    order_id = random.randint(1000000, 9999999)
    # save image in Receiptions Folder
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    path = os.path.join(os.getcwd(), 'UserBot', 'Receiptions', f"{message.chat.id}-{order_id}.jpg")
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.register_next_step_handler(message, next_step_send_name, plan, path, order_id)


def next_step_send_name(message, plan, path, order_id):
    if not plan:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    name = message.text
    # send it for admin bot

    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    paid_amount = order_info['price']
    payment_method = "Card"
    status = USERS_DB.add_order(order_id, message.chat.id, name, plan['id'], paid_amount, payment_method, path,
                                created_at)
    if status:
        for ADMIN in ADMINS_ID:
            admin_bot.send_photo(ADMIN, open(path, 'rb'),
                                 caption=payment_received_template(plan, name, paid_amount, order_id,
                                                                   MESSAGES['NEW_PAYMENT_RECEIVED'],
                                                                   MESSAGES['PAYMENT_ASK_TO_CONFIRM']),
                                 reply_markup=confirm_payment_by_admin(order_id))
        bot.send_message(message.chat.id, MESSAGES['WAIT_FOR_ADMIN_CONFIRMATION'],
                         reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())


def next_step_to_qr(message):
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


def next_step_link_subscription_1(message):
    if not message.text:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                         reply_markup=main_menu_keyboard_markup())
        return
    if is_it_cancel(message):
        bot.send_message(message.chat.id, MESSAGES['CANCELLED'],
                         reply_markup=main_menu_keyboard_markup())
        return
    uuid = utils.is_it_config_or_sub(message.text)
    if uuid:
        # check is it already subscribed
        is_it_subscribed = USERS_DB.find_non_order_subscriptions(uuid=uuid)
        if is_it_subscribed:
            bot.send_message(message.chat.id, MESSAGES['ALREADY_SUBSCRIBED'],
                             reply_markup=main_menu_keyboard_markup())
            return
        non_sub_id = random.randint(10000000, 99999999)
        status = USERS_DB.add_non_order_subscriptions(non_sub_id,message.chat.id, uuid)
        if status:
            bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_CONFIRMED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_INFO_NOT_FOUND'],
                         reply_markup=main_menu_keyboard_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    value = data[1]
    if key == 'confirm_subscription':
        edit_status = USERS_DB.add_non_order_subscriptions(call.message.chat.id, value)
        if edit_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_CONFIRMED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())

    elif key == 'cancel_subscription':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['CANCEL_SUBSCRIPTION'],
                         reply_markup=main_menu_keyboard_markup())

    elif key == 'unlink_subscription':
        delete_status = USERS_DB.delete_non_order_subscriptions(telegram_id=call.message.chat.id)
        if delete_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_UNLINKED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())

    elif key == 'plan_selected':
        plan = USERS_DB.find_plan(id=value)[0]
        if not plan:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())
            return
        buy_plan_info(call.message, plan)

    elif key == 'confirm_buy_plan':
        plan = USERS_DB.find_plan(id=value)[0]
        # bot.send_message(call.message.chat.id, MESSAGES['PLAN_ADD_NAME']),
        buy_plan_confirm(call.message, plan)

    elif key == 'send_screenshot':
        bot.send_message(call.message.chat.id, MESSAGES['REQUEST_SEND_SCREENSHOT'])
        plan = USERS_DB.find_plan(id=value)[0]
        bot.register_next_step_handler(call.message, next_step_send_screenshot, plan)

    elif key == 'configs_list':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_url_user_list_markup(value))

    elif key == 'conf_dir':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=sub_user_list_markup(value))
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
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_SUB']}\n{sub['sub_link']}",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Base64 Subscription Configs Callback
    elif key == "conf_sub_url_b64":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_SUB_B64']}\n{sub['sub_link_b64']}",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Subscription Configs For Clash Callback
    elif key == "conf_clash":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_CLASH']}\n{sub['clash_configs']}",
                         reply_markup=main_menu_keyboard_markup())
    # User Configs - Subscription Configs For Hiddify Callback
    elif key == "conf_hiddify":
        sub = utils.sub_links(value)
        if not sub:
            bot.send_message(call.message.chat.id, MESSAGES['ERROR_UNKNOWN'])
            return
        bot.send_message(call.message.chat.id, f"{KEY_MARKUP['CONFIGS_HIDDIFY']}\n{sub['hiddify_configs']}",
                         reply_markup=main_menu_keyboard_markup())

    elif key == "back_to_user_panel":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=user_info_markup(value))

    else:
        bot.answer_callback_query(call.id, MESSAGES['ERROR_INVALID_COMMAND'])


# Bot Start Message
@bot.message_handler(commands=['start'])
def start(message):
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


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SUBSCRIPTION_STATUS'])
def subscription_status(message):
    user_telegram_data = USERS_DB.find_user(telegram_id=message.chat.id)
    if user_telegram_data:
        user_telegram_data = user_telegram_data[0]
        user_non_order_datas = USERS_DB.find_non_order_subscriptions(telegram_id=user_telegram_data['telegram_id'])
        user_payment_datas = USERS_DB.find_order(telegram_id=user_telegram_data['telegram_id'])

        if user_non_order_datas:
            # user_non_order_datas = user_non_order_datas[0]
            for user_non_order_data in user_non_order_datas:
                sub_id = user_non_order_data['id']
                user_info = ADMIN_DB.find_user(uuid=user_non_order_data['uuid'])
                if user_info:
                    # user_info = user_info[0]
                    user_non_order_data = utils.users_to_dict(user_info)
                    user_non_order_data = utils.dict_process(user_non_order_data)
                    user_non_order_data = user_non_order_data[0]
                    if user_non_order_data:
                        api_user_data = user_info_template(sub_id,user_non_order_data, MESSAGES['INFO_USER'])
                        bot.send_message(message.chat.id, api_user_data,
                                         reply_markup=user_info_markup(user_non_order_data['uuid']))

        if user_payment_datas:
            for user_payment_data in user_payment_datas:
                if user_payment_data:
                    if user_payment_data['approved']:
                        order_info = USERS_DB.find_order_subscription(order_id=user_payment_data['id'])
                        if order_info:
                            order_info = order_info[0]
                            non_sub_id = order_info['id']
                            user_info = ADMIN_DB.find_user(uuid=order_info['uuid'])
                            if user_info:
                                user_info = utils.users_to_dict(user_info)
                                user_info = utils.dict_process(user_info)
                                user_info = user_info[0]
                                if user_info:
                                    api_user_data = user_info_template(non_sub_id,user_info, MESSAGES['INFO_USER'])
                                    bot.send_message(message.chat.id, api_user_data,
                                                     reply_markup=user_info_markup(user_info['uuid']))

            return

        bot.send_message(message.chat.id, MESSAGES['ENTER_SUBSCRIPTION_INFO'])
        bot.register_next_step_handler(message, next_step_subscription_status_1)

    else:
        bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'], reply_markup=main_menu_keyboard_markup())


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['BUY_SUBSCRIPTION'])
def buy_subscription(message):
    plans = USERS_DB.select_plans()
    if not plans:
        bot.send_message(message.chat.id, MESSAGES['PLANS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    plan_markup = plans_list_markup(plans)
    if not plan_markup:
        bot.send_message(message.chat.id, MESSAGES['PLANS_NOT_FOUND'], reply_markup=main_menu_keyboard_markup())
        return
    bot.send_message(message.chat.id, MESSAGES['PLANS_LIST'], reply_markup=plan_markup)


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['TO_QR'])
def to_qr(message):
    bot.send_message(message.chat.id, MESSAGES['REQUEST_SEND_TO_QR'])
    bot.register_next_step_handler(message, next_step_to_qr)


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['HELP_GUIDE'])
def help_guide(message):
    bot.send_message(message.chat.id, connection_help_template(), reply_markup=main_menu_keyboard_markup())


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SEND_TICKET'])
def send_ticket(message):
    owner_info = USERS_DB.select_owner_info()[0]
    bot.send_message(message.chat.id, support_template(owner_info), reply_markup=main_menu_keyboard_markup())


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['LINK_SUBSCRIPTION'])
def link_subscription(message):
    bot.send_message(message.chat.id, MESSAGES['ENTER_SUBSCRIPTION_INFO'], reply_markup=cancel_markup())
    bot.register_next_step_handler(message, next_step_link_subscription_1)


def start():
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.infinity_polling()
