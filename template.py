# Description: This file contains all the templates used in the bot.
from config import LANG

KEY_MARKUP = ***REMOVED***
    'EN': ***REMOVED***
        'CONFIRM': '✅Confirm',
        'CANCEL': '❌Cancel',
        'USERS_LIST': '👤Users Management',
        'USERS_SEARCH': '🔍Search User',
        'ADD_USER': '➕Add User',
        'SERVER_BACKUP': '📥Panel Backup',
        'SERVER_STATUS': '📈Server Status',
        'NEXT_PAGE': '➡️',
        'PREV_PAGE': '⬅️',
        'CONFIGS_USER': 'Configs',
        'EDIT_USER': 'Edit User',
        'DELETE_USER': 'Delete User',
        'EDIT_NAME': '👤Edit Name',
        'EDIT_USAGE': '📊Edit Usage',
        'RESET_USAGE': '🔄Reset Usage',
        'EDIT_DAYS': '📆Edit Days',
        'RESET_DAYS': '🔄Reset Days',
        'EDIT_COMMENT': '📝Edit Comment',
        'UPDATE_MESSAGE': '🔄Update Message',
        'BACK': '🔙Back',
        'CONFIGS_DIR': 'Configs',
        'CONFIGS_SUB': 'Subscription Link',
        'CONFIGS_SUB_B64': 'Subscription Link b64',
        'CONFIGS_CLASH': 'Clash Subscription',
        'CONFIGS_HIDDIFY': 'Hiddify Subscription',
        'SEARCH_USER_NAME': 'Search by Name',
        'SEARCH_USER_UUID': 'Search by UUID',
        'SEARCH_USER_CONFIG': 'Search by Config',

    ***REMOVED***,
    'FA': ***REMOVED***
        'CONFIRM': '✅تأیید',
        'CANCEL': '❌لغو',
        'USERS_LIST': '👤مدیریت کاربران',
        'USERS_SEARCH': '🔍جستجوی کاربر',
        'ADD_USER': '➕افزودن کاربر',
        'SERVER_BACKUP': '📥بکاپ پنل',
        'SERVER_STATUS': '📈وضعیت سرور',
        'NEXT_PAGE': '➡️',
        'PREV_PAGE': '⬅️',
        'CONFIGS_USER': 'کانفیگ ها',
        'EDIT_USER': 'ویرایش کاربر',
        'DELETE_USER': 'حذف کاربر',
        'EDIT_NAME': '👤ویرایش نام',
        'EDIT_USAGE': '📊ویرایش حجم',
        'RESET_USAGE': '🔄بازنشانی حجم',
        'EDIT_DAYS': '📆ویرایش مدت',
        'RESET_DAYS': '🔄بازنشانی مدت',
        'EDIT_COMMENT': '📝ویرایش یادداشت',
        'UPDATE_MESSAGE': '🔄به‌روزرسانی پیام',
        'BACK': '🔙بازگشت',
        'CONFIGS_DIR': 'کانفیگ',
        'CONFIGS_SUB': 'لینک اشتراک',
        'CONFIGS_SUB_B64': 'لینک اشتراک b64',
        'CONFIGS_CLASH': 'اشتراک Clash',
        'CONFIGS_HIDDIFY': 'اشتراک Hiddify',
        'SEARCH_USER_NAME': 'جستجو با نام',
        'SEARCH_USER_UUID': 'جستجو با UUID',
        'SEARCH_USER_CONFIG': 'جستجو با کانفیگ',
    ***REMOVED***
***REMOVED***

# Response Messages Template
MESSAGES = ***REMOVED***
    'EN': ***REMOVED***
        'WELCOME': "Welcome to Hiddify Management Bot.",
        'ERROR_INVALID_NUMBER': "❌Only numbers are allowed!",
        'ERROR_USER_NOT_FOUND': "❌User not found",
        'ERROR_INVALID_COMMAND': "❌Invalid command",
        'ERROR_UNKNOWN': "❌Unknown error",
        'ERROR_CONFIG_NOT_FOUND': '❌Config not found',
        'SUCCESS_USER_DELETED': "✅User deleted",
        'SUCCESS_USER_EDITED': "✅User edited",
        'SUCCESS_USER_ADDED': "✅User added",
        'SUCCESS_USER_USAGE_EDITED': "✅Usage limit edited to:",
        'SUCCESS_USER_DAYS_EDITED': "✅Days edited to:",
        'SUCCESS_USER_NAME_EDITED': "✅Name edited to:",
        'SUCCESS_USER_COMMENT_EDITED': "✅Comment edited to:",
        'SUCCESS_ADD_USER': "✅User added",
        'SUCCESS_SEARCH_USER': "✅User found",
        'WAIT': "Please wait...",
        'CANCELED': "❌Canceled",
        'CANCEL_ADD_USER': "❌Add User Canceled",
        'ADD_USER_NAME': "Please enter the name of the user: ",
        'ADD_USER_COMMENT': "Please enter the comment of the user: ",
        'ADD_USER_USAGE_LIMIT': "Please enter the usage limit of the user (GB): ",
        'ADD_USER_DAYS': "Please enter the days of package: ",
        'ENTER_NEW_USAGE_LIMIT': "Please enter new usage limit (GB): ",
        'ENTER_NEW_DAYS': "Please enter new limit: ",
        'ENTER_NEW_NAME': "Please enter new name: ",
        'ENTER_NEW_COMMENT': "Please enter new comment: ",
        'RESET_USAGE': "✅Usage limit reset",
        'RESET_DAYS': "✅Days reset",
        'ADD_USER_CONFIRM': "Please confirm the information:",
        'ERROR_NOT_ADMIN': "❌You are not admin!",
        'NEW_USER_INFO': "[New User Info]",
        'EDITED_USER_INFO': "[User Info Updated]",
        'GB': 'GB',
        'DAY': 'Day',
        'INFO_USAGE': '📊Usage:',
        'INFO_REMAINING_DAYS': '📆Remaining Days:',
        'INFO_LAST_CONNECTION': '📶Last Connection:',
        'INFO_COMMENT': '📝Comment:',
        'INFO_USER': '👤Name:',
        'HEADER_USERS_LIST': '👤Users List',
        'HEADER_USERS_LIST_MSG': 'ℹ️You can see the list of users and their information here.',
        'NUM_USERS': '🟢Number of users: ',
        'NUM_USERS_ONLINE': '🔵Online users: ',
        'SEARCH_USER': 'Please select the search method',
        'SEARCH_USER_NAME': 'Please enter the name of the user: ',
        'SEARCH_USER_UUID': 'Please enter the UUID of the user: ',
        'SEARCH_USER_CONFIG': 'Please enter one of the config of the user: ',
        'SEARCH_RESULT': '[Search Result]',

    ***REMOVED***,
    'FA': ***REMOVED***
        'WELCOME': "به ربات مدیریت Hiddify خوش آمدید.",
        'ERROR_INVALID_NUMBER': "❌تنها اعداد مجاز هستند!",
        'ERROR_USER_NOT_FOUND': "❌کاربر یافت نشد",
        'ERROR_INVALID_COMMAND': "❌فرمان نامعتبر",
        'ERROR_UNKNOWN': "❌خطای ناشناخته",
        'ERROR_CONFIG_NOT_FOUND': '❌کانفیگ یافت نشد',
        'SUCCESS_USER_DELETED': "✅کاربر حذف شد",
        'SUCCESS_USER_EDITED': "✅کاربر ویرایش شد",
        'SUCCESS_USER_ADDED': "✅کاربر اضافه شد",
        'SUCCESS_USER_USAGE_EDITED': "✅محدودیت استفاده کاربر ویرایش شد به:",
        'SUCCESS_USER_DAYS_EDITED': "✅روزها ویرایش شد به:",
        'SUCCESS_USER_NAME_EDITED': "✅نام ویرایش شد به:",
        'SUCCESS_USER_COMMENT_EDITED': "✅یادداشت ویرایش شد به:",
        'SUCCESS_ADD_USER': "✅کاربر اضافه شد",
        'SUCCESS_SEARCH_USER': "✅کاربر یافت شد",
        'WAIT': "لطفاً منتظر بمانید...",
        'CANCELED': "❌لغو شد",
        'CANCEL_ADD_USER': "❌افزودن کاربر لغو شد",
        'ADD_USER_NAME': "لطفاً نام کاربر را وارد کنید: ",
        'ADD_USER_COMMENT': "لطفاً نظر کاربر را وارد کنید: ",
        'ADD_USER_USAGE_LIMIT': "لطفاً محدودیت استفاده کاربر (GB) را وارد کنید: ",
        'ADD_USER_DAYS': "لطفاً تعداد روز بسته‌ی کاربر را وارد کنید: ",
        'ENTER_NEW_USAGE_LIMIT': "لطفاً محدودیت استفاده جدید (GB) را وارد کنید: ",
        'ENTER_NEW_DAYS': "لطفاً محدودیت جدید را وارد کنید: ",
        'ENTER_NEW_NAME': "لطفاً نام جدید را وارد کنید: ",
        'ENTER_NEW_COMMENT': "لطفاً یادداشت جدید را وارد کنید: ",
        'RESET_USAGE': "✅محدودیت استفاده بازنشانی شد",
        'RESET_DAYS': "✅روزها بازنشانی شد",
        'ADD_USER_CONFIRM': "لطفاً اطلاعات را تأیید کنید:",
        'ERROR_NOT_ADMIN': "❌شما ادمین نیستید!",
        'NEW_USER_INFO': "[اطلاعات کاربر جدید]",
        'EDITED_USER_INFO': "[اطلاعات کاربر به‌روزرسانی شد]",
        'GB': 'گیگابایت',
        'DAY': 'روز',
        'INFO_USAGE': '📊مصرف:',
        'INFO_REMAINING_DAYS': '📆انقضا:',
        'INFO_LAST_CONNECTION': '📶آخرین اتصال:',
        'INFO_COMMENT': '📝یادداشت:',
        'INFO_USER': '👤کاربر:',
        'HEADER_USERS_LIST': '👤لیست کاربران',
        'HEADER_USERS_LIST_MSG': 'ش️ما می‌توانید لیست کاربران و اطلاعات آن‌ها را اینجا مشاهده کنید',
        'NUM_USERS': '🟢تعداد کاربران: ',
        'NUM_USERS_ONLINE': '🔵کاربران آنلاین: ',
        'SEARCH_USER': 'لطفاً روش جستجو را انتخاب کنید',
        'SEARCH_USER_NAME': 'لطفاً نام کاربر را وارد کنید: ',
        'SEARCH_USER_UUID': 'لطفاً UUID کاربر را وارد کنید: ',
        'SEARCH_USER_CONFIG': 'لطفاً یکی از کانفیگ های کاربر را وارد کنید: ',
        'SEARCH_RESULT': '[نتیجه جستجو]',

    ***REMOVED***

***REMOVED***
BOT_COMMANDS = ***REMOVED***
    'EN': ***REMOVED***
        'START': 'start',
    ***REMOVED***,
    'FA': ***REMOVED***
        'START': 'شروع',
    ***REMOVED***
***REMOVED***

# Set Language of Messages
KEY_MARKUP = KEY_MARKUP[LANG]
MESSAGES = MESSAGES[LANG]
BOT_COMMANDS = BOT_COMMANDS[LANG]


# Single User Info Message Template
def user_info_template(usr, header=""):
    return f"""
***REMOVED***header***REMOVED***
***REMOVED***MESSAGES['INFO_USER']***REMOVED*** <a href='***REMOVED***usr['link']***REMOVED***'> ***REMOVED***usr['name']***REMOVED*** </a>
--------------------------------
***REMOVED***MESSAGES['INFO_USAGE']***REMOVED*** ***REMOVED***usr['usage']***REMOVED***
***REMOVED***MESSAGES['INFO_REMAINING_DAYS']***REMOVED*** ***REMOVED***usr['remaining_day']***REMOVED***
***REMOVED***MESSAGES['INFO_LAST_CONNECTION']***REMOVED*** ***REMOVED***usr['last_connection']***REMOVED***
***REMOVED***MESSAGES['INFO_COMMENT']***REMOVED*** ***REMOVED***usr['comment']***REMOVED***
            """


# Users List Message Template
def users_list_template(users, heder=""):
    # Number of Online Users
    online_users = 0
    for user in users:
        if user['last_connection'] == "Online":
            online_users += 1

    return f"""
***REMOVED***heder***REMOVED***
***REMOVED***MESSAGES['HEADER_USERS_LIST']***REMOVED***
***REMOVED***MESSAGES['HEADER_USERS_LIST_MSG']***REMOVED***
***REMOVED***MESSAGES['NUM_USERS']***REMOVED*** ***REMOVED***len(users)***REMOVED***
***REMOVED***MESSAGES['NUM_USERS_ONLINE']***REMOVED*** ***REMOVED***online_users***REMOVED*** 
"""


def configs_template(configs):
    messages = []
    result = []
    chunk_size = 5

    for config in configs:
        messages.append(f"<b>***REMOVED***config[1]***REMOVED***</b>\n<code>***REMOVED***config[0]***REMOVED***</code>\n")

    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i + chunk_size]
        result.append("\n".join(chunk))
    return result


def system_status_template(status):
    return f"""

< b > System
Status < / b >
--------------------------------
< b > CPU: < / b > ***REMOVED***status['cpu']***REMOVED*** %
< b > RAM: < / b > ***REMOVED***status['ram']***REMOVED*** %
< b > DISK: < / b > ***REMOVED***status['disk']***REMOVED*** %
"""
