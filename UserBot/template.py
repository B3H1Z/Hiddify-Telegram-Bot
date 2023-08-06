# Description: This file contains all the templates used in the bot.
from config import LANG

KEY_MARKUP = {
    'EN': {
        'BACK': '🔙Back',
        'SUBSCRIPTION_STATUS': '📊Subscription Status',
        'YES': '✅Yes',
        'NO': '❌No',
        'UNLINK_SUBSCRIPTION': '🔗Unlink Subscription',

    },
    'FA': {
        'BACK': '🔙بازگشت',
        'SUBSCRIPTION_STATUS': '📊وضعیت اشتراک',
        'YES': '✅بله',
        'NO': '❌خیر',
        'UNLINK_SUBSCRIPTION': '🔗لغو اشتراک',
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
