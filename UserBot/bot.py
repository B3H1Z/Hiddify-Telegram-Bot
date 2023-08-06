import api
from UserBot.markup import *
from config import *
import telebot
from UserBot.template import *

# Initialize Bot
bot = telebot.TeleBot(CLIENT_TOKEN, parse_mode="HTML")

# Bot Start Commands
try:
    bot.set_my_commands([
        telebot.types.BotCommand("/start", BOT_COMMANDS['START']),
    ])
except telebot.apihelper.ApiTelegramException as e:
    if e.result.status_code == 401:
        logging.error("Invalid Telegram Bot Token!")
        exit(1)


# Check is it UUID, Config or Subscription Link
def type_of_subscription(text):
    if text.startswith("vmess://"):
        config = text.replace("vmess://", "")
        config = api.base64decoder(config)
        if not config:
            return False
        uuid = config['id']
    else:
        uuid = api.extract_uuid_from_config(text)
    return uuid


def next_step_subscription_status_1(message):
    uuid = type_of_subscription(message.text)
    if not uuid:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_INFO_NOT_FOUND'])
        return
    user_data = DB.find_user(uuid=uuid)
    user_data = api.users_to_dict(user_data)
    user_data = api.dict_process(user_data)
    if user_data:
        user_data = user_data[0]
        bot.send_message(message.chat.id,
                         f"{MESSAGES['CONFIRM_SUBSCRIPTION_QUESTION']}\n{MESSAGES['NAME']} <b>{user_data['name']}</b>",
                         reply_markup=confirm_subscription_markup(user_data['uuid']))
    else:
        bot.send_message(message.chat.id, MESSAGES['SUBSCRIPTION_INFO_NOT_FOUND'],
                         reply_markup=main_menu_keyboard_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id, MESSAGES['WAIT'])
    # Split Callback Data to Key(Command) and UUID
    data = call.data.split(':')
    key = data[0]
    uuid = data[1]
    if key == 'confirm_subscription':
        add_status = TELEGRAM_DB.add_user(telegram_id=call.message.chat.id, uuid=uuid)
        if add_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_CONFIRMED'],reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())

    elif key == 'cancel_subscription':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, MESSAGES['CANCEL_SUBSCRIPTION'],
                         reply_markup=main_menu_keyboard_markup())

    elif key == 'unlink_subscription':
        delete_status = TELEGRAM_DB.delete_user(telegram_id=call.message.chat.id)
        if delete_status:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, MESSAGES['SUBSCRIPTION_UNLINKED'],
                             reply_markup=main_menu_keyboard_markup())
        else:
            bot.send_message(call.message.chat.id, MESSAGES['UNKNOWN_ERROR'],
                             reply_markup=main_menu_keyboard_markup())


# Bot Start Message
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, MESSAGES['WELCOME'], reply_markup=main_menu_keyboard_markup())


@bot.message_handler(func=lambda message: message.text == KEY_MARKUP['SUBSCRIPTION_STATUS'])
def subscription_status(message):
    user_telegram_data = TELEGRAM_DB.find_user(only_one=True, telegram_id=message.chat.id)
    if user_telegram_data:
        user_data = DB.find_user(uuid=user_telegram_data[1])
        user_data = api.users_to_dict(user_data)
        user_data = api.dict_process(user_data)
        if user_data:
            api_user_data = user_info_template(user_data[0],MESSAGES['INFO_USER'])
            bot.send_message(message.chat.id, api_user_data, reply_markup=user_info_markup())
        else:
            bot.send_message(message.chat.id, MESSAGES['UNKNOWN_ERROR'], reply_markup=main_menu_keyboard_markup())
    else:
        bot.send_message(message.chat.id, MESSAGES['ENTER_SUBSCRIPTION_INFO'])
        bot.register_next_step_handler(message, next_step_subscription_status_1)


def start():
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.infinity_polling()
