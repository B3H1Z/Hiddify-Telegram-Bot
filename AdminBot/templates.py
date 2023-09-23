# Description: This file contains all the templates used in the bot.
from config import LANG, VERSION
from AdminBot.messages import MESSAGES


# Single User Info Message Template
def user_info_template(usr, header=""):
    if not usr['comment']:
        usr['comment'] = "-"
    if usr['remaining_day'] == 0:
        usr['remaining_day'] = MESSAGES['USER_TIME_EXPIRED']
    else:
        usr['remaining_day'] = f"{usr['remaining_day']} {MESSAGES['DAY_EXPIRE']}"

    return f"""
{header}
{MESSAGES['INFO_USER']} <a href='{usr['link']}'> {usr['name']} </a>
--------------------------------
{MESSAGES['INFO_USAGE']} {usr['usage']['current_usage_GB']} {MESSAGES['OF']} {usr['usage']['usage_limit_GB']} {MESSAGES['GB']}
{MESSAGES['INFO_REMAINING_DAYS']} {usr['remaining_day']}
{MESSAGES['INFO_LAST_CONNECTION']} {usr['last_connection']}
{MESSAGES['INFO_COMMENT']} {usr['comment']}
"""


# Users List Message Template
def users_list_template(users, heder=""):
    # Number of Online Users
    online_users = 0
    for user in users:
        if user['last_connection'] == "Online" or user['last_connection'] == "آنلاین":
            online_users += 1

    return f"""
{heder}
{MESSAGES['HEADER_USERS_LIST']}
{MESSAGES['HEADER_USERS_LIST_MSG']}
{MESSAGES['NUM_USERS']} {len(users)}
{MESSAGES['NUM_USERS_ONLINE']} {online_users} 
"""


# Configs List Message Template
def configs_template(configs):
    messages = []
    result = []
    chunk_size = 5

    for config in configs:
        messages.append(f"<b>{config[1]}</b>\n<code>{config[0]}</code>\n")

    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i + chunk_size]
        result.append("\n".join(chunk))
    return result


# System Status Message Template
def system_status_template(status):
    return f"""
<b> System Status </b>
--------------------------------
<b> CPU: </b> {status['cpu']}%
<b> RAM: </b> {status['ram']}%
<b> DISK: </b> {status['disk']}%
"""


# Last Online Time Template
def last_online_time_template(last_online_time):
    if last_online_time.days >= 30:
        return f"{last_online_time.days // 30} {MESSAGES['MONTH']} {MESSAGES['AGO']} "
    elif last_online_time.days >= 7:
        return f"{last_online_time.days // 7} {MESSAGES['WEEK']} {MESSAGES['AGO']}"
    elif last_online_time.days > 0:
        return f"{last_online_time.days} {MESSAGES['DAY']} {MESSAGES['AGO']}"
    elif last_online_time.seconds > 3600:
        return f"{last_online_time.seconds // 3600} {MESSAGES['HOUR']} {MESSAGES['AGO']}"
    elif last_online_time.seconds <= 5 * 60:
        return f"{MESSAGES['ONLINE']}"
    elif last_online_time.seconds > 60:
        return f"{last_online_time.seconds // 60} {MESSAGES['MINUTE']} {MESSAGES['AGO']}"
    else:
        return MESSAGES['NEVER']


# Owner Info Message Template
def owner_info_template(username, card_number_card, card_name):
    username = username if username else "-"
    card_number_card = card_number_card if card_number_card else "-"
    card_name = card_name if card_name else "-"
    if LANG == 'FA':
        return f"""
<b> اطلاعات مالک </b>
--------------------------------
<b> نام کاربری پشتیبان: </b> {username}
<b> شماره کارت بانکی: </b> {card_number_card}
<b> نام صاحب حساب بانکی: </b> {card_name}
"""
    elif LANG == 'EN':
        return f"""
<b> Owner Info </b>
--------------------------------
<b> Telegram Support Username: </b> {username} 
<b> Bank Card Number: </b> {card_number_card}
<b> Bank Card Name: </b> {card_name}
"""


# About Bot Message Template
def about_template():
    if LANG == 'FA':
        return f"""
🤖هیدی بات، راحت تر از همیشه!

<a href='https://github.com/B3H1Z/Hiddify-Telegram-Bot'> لینک پروژه </a>|<a href='https://t.me/HidyBotGroup'> گروه پشتیبانی </a>

این پروژه به صورت رایگان توسعه داده شده و جهت ادامه توسعه رایگان، حمایت مالی شما میتواند انگیزه بخش باشد❤️

📌حمایت مالی:
TRX: <code>TSTtpPFgzNhXgDRpZLKkjHvoHC6CtQA8V9</code>

DOGE: <code>DGfd18UX9vazdyMj1bTsVSufSbQvEMvT56</code>

USDT: <code>0xB1120148eB1c34C4Dd4c531f558B6D5708c40623</code>

BNB: <code>bnb13fevgfzjp4am2ejvk7ly2xdpdldhz5xwd350a2</code>

نسخه: {VERSION}
"""
    elif LANG == 'EN':
        return f"""
🤖Hiddify Bot, Easier than ever!

<a href='https://github.com/B3H1Z/Hiddify-Telegram-Bot'> Project </a>|<a href='https://t.me/HidyBotGroup'> Support Group </a>

This project is developed for free and your financial support can be motivating for further development❤️

📌Financial Support:
TRX: <code>TSTtpPFgzNhXgDRpZLKkjHvoHC6CtQA8V9</code>

DOGE: <code>DGfd18UX9vazdyMj1bTsVSufSbQvEMvT56</code>

USDT: <code>0xB1120148eB1c34C4Dd4c531f558B6D5708c40623</code>

BNB: <code>bnb13fevgfzjp4am2ejvk7ly2xdpdldhz5xwd350a2</code>

Version: {VERSION}
"""
