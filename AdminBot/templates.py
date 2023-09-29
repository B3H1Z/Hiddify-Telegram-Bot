# Description: This file contains all the templates used in the bot.
from config import LANG, VERSION, API_PATH
from AdminBot.content import MESSAGES
from Utils import api, utils 

# Single User Info Message Template
def user_info_template(usr, server, header=""):
    if not usr['comment']:
        usr['comment'] = "-"
    if usr['remaining_day'] == 0:
        usr['remaining_day'] = MESSAGES['USER_TIME_EXPIRED']
    else:
        usr['remaining_day'] = f"{usr['remaining_day']} {MESSAGES['DAY_EXPIRE']}"

    return f"""
{header}
{MESSAGES['INFO_USER']} <a href='{usr['link']}'> {usr['name']} </a>
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['SERVER']} {server['title']}
{MESSAGES['INFO_USAGE']} {usr['usage']['current_usage_GB']} {MESSAGES['OF']} {usr['usage']['usage_limit_GB']} {MESSAGES['GB']}
{MESSAGES['INFO_REMAINING_DAYS']} {usr['remaining_day']}
{MESSAGES['INFO_LAST_CONNECTION']} {usr['last_connection']}
{MESSAGES['INFO_COMMENT']} {usr['comment']}
"""

# Server Info Message Template
def server_info_template(server, plans, header=""):
    plans_num = 0
    user_index = 0
    URL = server['url'] + API_PATH
    users_list = api.select(URL)
    if users_list:
        user_index = len(users_list)
    if plans:
        for plan in plans:
            if plan['status']:
                if plan['server_id'] == server['id']:
                    plans_num += 1

    return f"""
{header}
{MESSAGES['INFO_SERVER']} <a href='{server['url']}/admin'> {server['title']} </a>
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['INFO_SERVER_USER_NUMBER']} {user_index} {MESSAGES['OF']} {server['user_limit']}
{MESSAGES['INFO_SERVER_USER_PLAN']} {plans_num}
"""
# Server Info Message Template
def plan_info_template(plan, orders, header=""):
    num_orders = 0
    if orders:
        for order in orders:
            num_orders += 1
    sale = num_orders * plan['price']
    return f"""
{header}
{MESSAGES['INFO_PLAN_ID']} {plan['id']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['INFO_PLAN_USAGE']} {plan['size_gb']} 
{MESSAGES['INFO_PLAN_DAYS']} {plan['days']} 
{MESSAGES['INFO_PLAN_PRICE']} {utils.rial_to_toman(plan['price'])} 
{MESSAGES['INFO_PLAN_NUM_ORDER']} {num_orders} 
{MESSAGES['INFO_PLAN_TOTAL_SALE']} {utils.rial_to_toman(sale)} 
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

<a href='https://github.com/B3H1Z/Hiddify-Telegram-Bot'> لینک پروژه </a>

<a href='https://t.me/HidyBotGroup'> گروه پشتیبانی </a> | <a href='https://t.me/HidyBotChannel'> کانال اطلاع رسانی </a>

این پروژه به صورت رایگان توسعه داده شده و جهت ادامه توسعه رایگان، حمایت های شما میتواند انگیزه بخش باشد❤️

نسخه: {VERSION}
"""
    elif LANG == 'EN':
        return f"""
🤖Hiddify Bot, Easier than ever!

<a href='https://github.com/B3H1Z/Hiddify-Telegram-Bot'> Project </a>|<a href='https://t.me/HidyBotGroup'> Support Group </a>

This project is developed for free and your financial support can be motivating for further development❤️

Version: {VERSION}
"""
