# Description: This file contains all the templates used in the bot.
import random
import string

from config import LANG

KEY_MARKUP = {
    'EN': {
        'BACK': '🔙Back',
        'SUBSCRIPTION_STATUS': '📊Subscription Status',
        'YES': '✅Yes',
        'NO': '❌No',
        'UNLINK_SUBSCRIPTION': '🔗Unlink Subscription',
        'BUY_SUBSCRIPTION': '🔗Buy Subscription',
        'BUY_PLAN': '🔗Buy',
        'SEND_SCREENSHOT': '✅I paid, send receipt',
        'CANCEL': '❌Cancel',

    },
    'FA': {
        'BACK': '🔙بازگشت',
        'SUBSCRIPTION_STATUS': '📊وضعیت اشتراک',
        'YES': '✅بله',
        'NO': '❌خیر',
        'UNLINK_SUBSCRIPTION': '🔗لغو اشتراک',
        'BUY_SUBSCRIPTION': '🔗خرید اشتراک',
        'BUY_PLAN': '🔗خرید',
        'SEND_SCREENSHOT': '✅پرداخت کردم، ارسال رسید',
        'CANCEL': '❌لغو',
    }
}

# Response Messages Template
MESSAGES = {
    'EN': {
        'WELCOME': "Welcome to Users Bot",
        'INFO_USER': '📄Your Subscription Info',
        'INFO_USAGE': '📊Usage:',
        'INFO_REMAINING_DAYS': '⏳Remaining Days:',
        'OF': 'of',
        'GB': 'GB',
        'DAY_EXPIRE': 'Days',
        'CONFIRM_SUBSCRIPTION_QUESTION': 'Is this your subscription?',
        'NAME': 'Name:',
        'CANCEL_SUBSCRIPTION': 'Subscription not confirmed',
        'SUBSCRIPTION_CONFIRMED': 'Your subscription has been confirmed. Now you can get your subscription status.',
        'WAIT': 'Please wait...',
        'UNKNOWN_ERROR': 'Unknown error! Contact the bot developer.',
        'ENTER_SUBSCRIPTION_INFO': 'Please enter your subscription info\n One of the configs, uuid or subscription link',
        'SUBSCRIPTION_INFO_NOT_FOUND': 'Subscription info not found!',
        'SUBSCRIPTION_UNLINKED': 'Subscription unlinked!',
        'USER_NAME': '👤Name:',
        'PLANS_LIST': '📋Plans List:',
        'PLANS_NOT_FOUND': 'Plans not found!',
        'PLAN_ADD_NAME': 'Please enter your name:',
        'SUBSCRIPTION_SUCCESS_ADDED': 'Your subscription has been successfully added.',
        'PLAN_INFO': '📄Plan Info:',
        'PLAN_SIZE': 'Size:',
        'PLAN_DAYS': 'Days:',
        'PLAN_PRICE': 'Price:',
        'TOMAN': 'T',
        'REQUEST_SEND_SCREENSHOT': 'Please send your payment receipt.',
        'ERROR_TYPE_SEND_SCREENSHOT': 'Please send your payment receipt as a photo!',
        'REQUEST_SEND_NAME': 'Please send your name.',
        'NO_SUBSCRIPTION': 'You have no subscription!',

    },
    'FA': {
        'WELCOME': "به ربات کاربران خوش آمدید",
        'INFO_USER': '📄اطلاعات اشتراک شما',
        'INFO_USAGE': '📊میزان استفاده:',
        'INFO_REMAINING_DAYS': '⏳زمان باقی مانده:',
        'OF': 'از',
        'GB': 'گیگابایت',
        'DAY_EXPIRE': 'روز',
        'CONFIRM_SUBSCRIPTION_QUESTION': 'آیا این اشتراک شماست؟',
        'NAME': 'نام:',
        'CANCEL_SUBSCRIPTION': 'اشتراک تایید نشد',
        'SUBSCRIPTION_CONFIRMED': 'اشتراک شما تایید شد. حالا میتوانید وضعیت اشتراک خود را دریافت کنید.',
        'WAIT': 'لطفا صبر کنید...',
        'UNKNOWN_ERROR': 'خطای ناشناخته! با توسعه دهنده ربات در تماس باشید.',
        'ENTER_SUBSCRIPTION_INFO': 'لطفا اطلاعات اشتراک خود را وارد کنید\n یکی از کانفیگ ها، uuid یا لینک اشتراک',
        'SUBSCRIPTION_INFO_NOT_FOUND': 'اطلاعات اشتراک یافت نشد!',
        'USER_NOT_FOUND': 'کاربر یافت نشد.',
        'SUBSCRIPTION_UNLINKED': 'اشتراک لغو شد!',
        'USER_NAME': '👤نام:',
        'PLANS_LIST': '📋لیست پلن ها:',
        'PLANS_NOT_FOUND': 'پلنی یافت نشد!',
        'PLAN_ADD_NAME': 'لطفا نام خود را وارد کنید:',
        'SUBSCRIPTION_SUCCESS_ADDED': 'اشتراک شما با موفقیت اضافه شد.',
        'PLAN_INFO': '📋اطلاعات پلن انتخاب شده',
        'PLAN_INFO_SIZE': 'حجم پلن:',
        'PLAN_INFO_PRICE': 'قیمت پلن:',
        'PLAN_INFO_DAYS': 'زمان پلن:',
        'TOMAN': 'تومان',
        'REQUEST_SEND_SCREENSHOT': 'لطفا رسید پرداخت خود را در زیر این پیام ارسال کنید.',
        'ERROR_TYPE_SEND_SCREENSHOT': 'لطفا رسید پرداخت خود را به صورت عکس ارسال کنید!',
        'REQUEST_SEND_NAME': 'لطفا نام خود را ارسال کنید.',
        'NO_SUBSCRIPTION': 'شما هیچ اشتراکی ندارید.',
    }

}
BOT_COMMANDS = {
    'EN': {
        'START': 'start',
    },
    'FA': {
        'START': 'شروع',
    }
}

# Set Language of Messages
KEY_MARKUP = KEY_MARKUP[LANG]
MESSAGES = MESSAGES[LANG]
BOT_COMMANDS = BOT_COMMANDS[LANG]


def user_info_template(usr, header=""):
    return f"""
{header}

{MESSAGES['USER_NAME']} <a href='{usr['link']}'> {usr['name']} </a>
{MESSAGES['INFO_USAGE']} {usr['usage']['current_usage_GB']} {MESSAGES['OF']} {usr['usage']['usage_limit_GB']} {MESSAGES['GB']}
{MESSAGES['INFO_REMAINING_DAYS']} {usr['remaining_day']} {MESSAGES['DAY_EXPIRE']}
            """


def plan_info_template(plan, header=""):
    return f"""
{header}
{MESSAGES['PLAN_INFO']}

{MESSAGES['PLAN_INFO_SIZE']} {plan['size']} {MESSAGES['GB']}
{MESSAGES['PLAN_INFO_DAYS']} {plan['days']} {MESSAGES['DAY_EXPIRE']}
{MESSAGES['PLAN_INFO_PRICE']} {plan['price']} {MESSAGES['TOMAN']}
"""


def replace_last_three_with_random(input_string):
    if len(input_string) < 3:
        return input_string  # Not enough characters to replace

    random_numbers = ''.join(random.choice(string.digits) for _ in range(3))
    modified_string = input_string[:-3] + random_numbers
    return modified_string


def owner_info_template(plan, card_number, card_holder_name, header=""):
    price = replace_last_three_with_random(str(plan['price']))
    if LANG == 'FA':
        return f"""
{header}

💰لطفا دقیقا مبلغ: <code>{price}</code> {MESSAGES['TOMAN']}
💳را به شماره کارت: <code>{card_number}</code>
به نام <b>{card_holder_name}</b> واریز کنید.

❗️بعد از واریز مبلغ، اسکرین شات از تراکنش را برای ما ارسال کنید.
"""
    elif LANG == 'EN':
        return f"""
{header}

💰Please pay exactly: <code>{price}</code> {MESSAGES['TOMAN']}
💳To card number: <code>{card_number}</code>
Card owner <b>{card_holder_name}</b>

❗️After paying the amount, send us a screenshot of the transaction.
"""