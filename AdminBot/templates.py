# Description: This file contains all the templates used in the bot.
from config import LANG, VERSION, API_PATH
from AdminBot.content import MESSAGES
from Utils import api, utils 
import datetime
import urllib.parse


# Single User Info Message Template
def user_info_template(usr, server, header=""):
    if not usr['comment']:
        usr['comment'] = "-"
    if usr['remaining_day'] == 0:
        usr['remaining_day'] = MESSAGES['USER_TIME_EXPIRED']
    elif usr['remaining_day'] == 1:
        usr['remaining_day'] = MESSAGES['USER_LAST_DAY']
    else:
        usr['remaining_day'] = f"{usr['remaining_day']} {MESSAGES['DAY_EXPIRE']}"

    return f"""
{header}
{MESSAGES['INFO_USER_NAME']} <a href='{usr['link']}'> {usr['name']} </a>
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

# Plan Info Message Template
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
{MESSAGES['INFO_PLAN_PRICE']} {utils.rial_to_toman(plan['price'])} {MESSAGES['TOMAN']}
{MESSAGES['INFO_PLAN_DESC']} {plan['description']}
{MESSAGES['INFO_PLAN_NUM_ORDER']} {num_orders} 
{MESSAGES['INFO_PLAN_TOTAL_SALE']} {utils.rial_to_toman(sale)} {MESSAGES['TOMAN']}
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


# Bot Users List Message Template
def bot_users_list_template(users, wallets, orders, header=""):

    users_get_free = 0
    ordered_users = 0
    total_balance_wallets= 0
    if wallets:
        for wallet in wallets:
            total_balance_wallets += wallet['balance']
    if orders:
        for user in users:
            if user['test_subscription']:
                users_get_free += 1
            for order in orders:
                if order['telegram_id'] == user['telegram_id']:
                    ordered_users += 1
                    break
    else:
        for user in users:
            if user['test_subscription']:
                users_get_free += 1
        

    return f"""
{header}
<b>{MESSAGES['HEADER_USERS_LIST']}</b>
{MESSAGES['HEADER_USERS_LIST_MSG']}
{MESSAGES['NUM_USERS']} {len(users)}
{MESSAGES['NUM_GET_FREE_USERS']} {users_get_free}
{MESSAGES['NUM_ORDERED_USERS']} {ordered_users}
{MESSAGES['TOTAL_BALANCE_USERS']} {utils.rial_to_toman(total_balance_wallets)}{MESSAGES['TOMAN']}
"""

# Bot Users Info Message Template
def bot_users_info_template(user, orders, payments, wallet, non_order_subs, order_subs, plans, header=""):
    total_orders = 0
    total_payment = 0
    approved_payment = 0
    total_order_subs = 0
    total_non_order_subs = 0
    total_balance = 0
    total_valume = 0
    total_sales = 0
    if orders:
        total_orders = len(orders)
        if plans:
            for order in orders:
                for plan in plans:
                    if order['plan_id'] == plan['id']:
                        total_valume += plan['size_gb']
                        total_sales += plan['price']
                        break
    if payments:
        total_payment = len(payments)
        approved_payments = [payment for payment in payments if payment['approved'] == 1]
        if approved_payments:
            approved_payment = len(approved_payments)
    if non_order_subs:
        total_non_order_subs = len(non_order_subs)
    if order_subs:
        total_order_subs = len(order_subs)
    if wallet:
        total_balance = wallet['balance']
    name = user['full_name'] if user['full_name'] else user['telegram_id']
    username = f"@{user['username']}" if user['username'] else MESSAGES['NOT_SET']
    free_test_status = "✅" if user['test_subscription'] else "❌"

    return f"""
{header}
{MESSAGES['INFO_USER_NAME']}{name}
{MESSAGES['INFO_USER_USERNAME']}{username}
{MESSAGES['INFO_USER_NUM_ID']}{user['telegram_id']}
{MESSAGES['GET_FREE_TEST_STATUS']}{free_test_status}
{MESSAGES['WALLET_BALANCE']}{utils.rial_to_toman(total_balance)}{MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['NUM_ORDER_SUB']} {total_order_subs}
{MESSAGES['NUM_NON_ORDER_SUB']} {total_non_order_subs}
{MESSAGES['NUM_PAYMENTS']} {total_payment}
{MESSAGES['NUM_APPROVED_PAYMENTS']} {approved_payment}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['NUM_ORDERS']} {total_orders}
{MESSAGES['TOTAL_ORDERS_VALUME']} {total_valume}
{MESSAGES['TOTAL_ORDERS_SALES']} {utils.rial_to_toman(total_sales)}{MESSAGES['TOMAN']}
"""

# Bot Users Order Info Message Template
def bot_orders_info_template(order, plan, user, server, header=""):
    name = user['full_name'] if user['full_name'] else user['telegram_id']
    username = f"@{user['username']}" if user['username'] else MESSAGES['NOT_SET']

    return f"""
{header}
{MESSAGES['BOT_ORDER_ID']}<code>{order['id']}</code>
{MESSAGES['BOT_ORDER_DATE']}{order['created_at']}
{MESSAGES['INFO_USER_NAME']}<b>{name}</b>
{MESSAGES['INFO_USER_USERNAME']}{username}
{MESSAGES['INFO_USER_NUM_ID']}{user['telegram_id']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['ORDERED_VALUME']}{plan['size_gb']}
{MESSAGES['ORDERED_DAYS']}{plan['days']}
{MESSAGES['ORDERED_PRICE']}{utils.rial_to_toman(plan['price'])}{MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['SUB_NAME']}{order['user_name']}
{MESSAGES['SERVER']}{server['title']}
"""

# Payment Received Template - Send to Admin
def bot_payment_info_template(payment,user, header="", footer=""):
    #approved = "✅" if payment['approved'] else "❌"
    if payment['approved']: approved = "✅"
    elif payment['approved'] == False: approved = "❌"
    else: approved = "⏳"
    username = f"@{user['username']}" if user['username'] else MESSAGES['NOT_SET']
    name = user['full_name'] if user['full_name'] else user['telegram_id']
    return f"""
{header}

{MESSAGES['PAYMENTS_ID']} <code>{payment['id']}</code>
{MESSAGES['INFO_USER_NAME']} <b>{name}</b>
{MESSAGES['INFO_USER_USERNAME']} {username}
{MESSAGES['INFO_USER_NUM_ID']} {user['telegram_id']}
{MESSAGES['BOT_PAYMENT_DATE']} {payment['created_at']}
{MESSAGES['PAIED_AMOUNT']} <b>{utils.rial_to_toman(payment['payment_amount'])}</b> {MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['STATUS']} {approved}
{MESSAGES['PAYMENTS_METHOD']} {payment['payment_method']}

{footer}
"""

# Bot Users List Message Template
def bot_orders_list_template(orders, plans, header=""):

    total_orders = 0
    total_valume = 0
    total_sales = 0
    last30day = datetime.datetime.now() - datetime.timedelta(days=30)
    last30days_orders = [order for order in orders if datetime.datetime.strptime(order['created_at'], "%Y-%m-%d %H:%M:%S") >= last30day]
    last30days_num_orders = 0
    last30days_valume = 0
    last30days_sales = 0
    first_day_this_month = datetime.datetime.today().replace(day=1)
    this_month_orders = [order for order in orders if datetime.datetime.strptime(order['created_at'], "%Y-%m-%d %H:%M:%S") >= first_day_this_month]
    this_month_num_orders = 0
    this_month_valume = 0
    this_month_sales = 0
    if orders:
        total_orders = len(orders)
        if plans:
            for order in orders:
                for plan in plans:
                    if order['plan_id'] == plan['id']:
                        total_valume += plan['size_gb']
                        total_sales += plan['price']
                        break
    if last30days_orders:
        last30days_num_orders = len(last30days_orders)
        if plans:
            for order in last30days_orders:
                for plan in plans:
                    if order['plan_id'] == plan['id']:
                        last30days_valume += plan['size_gb']
                        last30days_sales += plan['price']
                        break
    if this_month_orders:
        this_month_num_orders = len(this_month_orders)
        if plans:
            for order in this_month_orders:
                for plan in plans:
                    if order['plan_id'] == plan['id']:
                        this_month_valume += plan['size_gb']
                        this_month_sales += plan['price']
                        break
        

    return f"""
{header}
<b>{MESSAGES['HEADER_ORDERS_LIST']}</b>
{MESSAGES['NUM_ORDERS']} {total_orders}
{MESSAGES['TOTAL_ORDERS_VALUME']} {total_valume}
{MESSAGES['TOTAL_ORDERS_SALES']} {utils.rial_to_toman(total_sales)}{MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['LAST_30DAYS_NUM_ORDERS']} {last30days_num_orders}
{MESSAGES['LAST_30DAYS_ORDERS_VALUME']} {last30days_valume }
{MESSAGES['LAST_30DAYS_ORDERS_SALES']} {utils.rial_to_toman(last30days_sales)}{MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['THIS_MONTH_NUM_ORDERS']} {this_month_num_orders}
{MESSAGES['THIS_MONTH_ORDERS_VALUME']} {this_month_valume}
{MESSAGES['THIS_MONTH_ORDERS_SALES']} {utils.rial_to_toman(this_month_sales)}{MESSAGES['TOMAN']}
"""

# Bot Users List Message Template
def bot_payments_list_template(payments, header=""):

    total_payments = 0
    total_amount = 0
    last30day = datetime.datetime.now() - datetime.timedelta(days=30)
    last30days_payments  = [payment for payment in payments if datetime.datetime.strptime(payment['created_at'], "%Y-%m-%d %H:%M:%S") >= last30day]
    last30days_num_payments = 0
    last30days_amount = 0
    first_day_this_month = datetime.datetime.today().replace(day=1)
    this_month_orders = [payment for payment in payments if datetime.datetime.strptime(payment['created_at'], "%Y-%m-%d %H:%M:%S") >= first_day_this_month]
    this_month_num_payments = 0
    this_month_amount = 0
    if payments:
        total_payments = len(payments)
        for payment in payments:
                total_amount += payment['payment_amount']

    if last30days_payments:
        last30days_num_payments = len(last30days_payments)
        for payment in last30days_payments:
                last30days_amount += payment['payment_amount']

    if this_month_orders:
        this_month_num_payments = len(this_month_orders)
        for payment in this_month_orders:
                this_month_amount += payment['payment_amount']
        

    return f"""
{header}
<b>{MESSAGES['HEADER_PAYMENT_LIST']}</b>
{MESSAGES['NUM_PAYMENTS']}{total_payments}
{MESSAGES['TOTAL_PAYMENTS_AMOUNT']}{utils.rial_to_toman(total_amount)}{MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['LAST_30DAYS_NUM_PAYMENTS']}{last30days_num_payments}
{MESSAGES['LAST_30DAYS_PAYMENTS_AMOUNT']}{utils.rial_to_toman(last30days_amount)}{MESSAGES['TOMAN']}
❖⬩╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍⬩❖
{MESSAGES['THIS_MONTH_NUM_PAYMENTS']}{this_month_num_payments}
{MESSAGES['THIS_MONTH_PAYMENTS_AMOUNT']}{utils.rial_to_toman(this_month_amount)}{MESSAGES['TOMAN']}
"""

# Configs List Message Template
def configs_template(configs):
    messages = []
    result = []
    chunk_size = 5

    for config in configs:
       messages.append(f"<b>{urllib.parse.unquote(config[1])}</b>\n<code>{config[0]}</code>\n")

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
