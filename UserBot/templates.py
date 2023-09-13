# Description: This file contains all the templates used in the bot.
from config import LANG
from UserBot.content import MESSAGES
from Utils.utils import rial_to_toman, toman_to_rial,all_configs_settings
from Database.dbManager import USERS_DB
# User Subscription Info Template
def user_info_template(sub_id, usr, header=""):
    settings = USERS_DB.find_bool_config(key='visible_hiddify_hyperlink')
    if settings:
        settings = settings[0]
        if settings['value']:
            user_name = f"<a href='{usr['link']}'> {usr['name']} </a>"
        else:
            user_name = usr['name']
    else:
        user_name = usr['name']
    if usr['enable'] == 1:
        status = MESSAGES['ACTIVE_SUBSCRIPTION_STATUS']
    else:
        status = MESSAGES['DEACTIVE_SUBSCRIPTION_STATUS']
    return f"""
{header}

{MESSAGES['USER_NAME']} {user_name}
{MESSAGES['INFO_USAGE']} {usr['usage']['current_usage_GB']} {MESSAGES['OF']} {usr['usage']['usage_limit_GB']} {MESSAGES['GB']}
{MESSAGES['INFO_REMAINING_DAYS']} {usr['remaining_day']} {MESSAGES['DAY_EXPIRE']}
{MESSAGES['SUBSCRIPTION_STATUS']} {status}
{MESSAGES['INFO_ID']} <code>{sub_id}</code>
"""


# Wallet Info Template
def wallet_info_template(balance):
    if balance == 0:
        return MESSAGES['ZERO_BALANCE']
    else:
        return f"""
         {MESSAGES['WALLET_INFO_PART_1']} {rial_to_toman(balance)} {MESSAGES['WALLET_INFO_PART_2']}
         """


# Plan Info Template
def plan_info_template(plan, header=""):
    return f"""
{header}
{MESSAGES['PLAN_INFO']}

{MESSAGES['PLAN_INFO_SIZE']} {plan['size_gb']} {MESSAGES['GB']}
{MESSAGES['PLAN_INFO_DAYS']} {plan['days']} {MESSAGES['DAY_EXPIRE']}
{MESSAGES['PLAN_INFO_PRICE']} {rial_to_toman(plan['price'])} {MESSAGES['TOMAN']}
"""


# Owner Info Template (For Payment)
def owner_info_template(card_number, card_holder_name, price, header=""):
    card_number = card_number if card_number else "-"
    card_holder_name = card_holder_name if card_holder_name else "-"

    if LANG == 'FA':
        return f"""
{header}

💰لطفا دقیقا مبلغ: <code>{price}</code> {MESSAGES['RIAL']}
💴معادل: {rial_to_toman(price)} {MESSAGES['TOMAN']}
💳را به شماره کارت: <code>{card_number}</code>
👤به نام <b>{card_holder_name}</b> واریز کنید.

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


# Payment Received Template - Send to Admin
def payment_received_template(payment, header="", footer=""):
    if LANG == 'FA':
        return f"""
{header}

شماره سفارش: <code>{payment['id']}</code>
نام کاربر: <b>{payment['user_name']}</b>
هزینه پرداخت شده: <b>{rial_to_toman(payment['payment_amount'])}</b> {MESSAGES['TOMAN']}
---------------------
⬇️درخواست افزایش موجودی کیف پول⬇️

{footer}
"""
    elif LANG == 'EN':
        return f"""
{header}

Order number: <b>{payment['id']}</b>
Registered name: <b>{payment['user_name']}</b>
Paid amount: <b>{payment['payment_amount']}</b> {MESSAGES['TOMAN']}
---------------------
⬇️Request to increase wallet balance⬇️

"""


# Help Guide Template
def connection_help_template(header=""):
    if LANG == 'FA':
        return f"""
{header}

⭕️ نرم افزار های مورد نیاز برای اتصال به کانفیگ
    
📥اندروید:
<a href='https://play.google.com/store/apps/details?id=com.v2ray.ang'>V2RayNG</a>
<a href='https://play.google.com/store/apps/details?id=ang.hiddify.com'>HiddifyNG</a>

📥آی او اس:
<a href='https://apps.apple.com/us/app/streisand/id6450534064'>Streisand</a>
<a href='https://apps.apple.com/us/app/foxray/id6448898396'>Foxray</a>
<a href='https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690'>V2box</a>

📥ویندوز:
<a href='https://github.com/MatsuriDayo/nekoray/releases'>Nekoray</a>
<a href='https://github.com/2dust/v2rayN/releases'>V2rayN</a>
<a href='https://github.com/hiddify/HiddifyN/releases'>HiddifyN</a>

📥مک و لینوکس:
<a href='https://github.com/MatsuriDayo/nekoray/releases'>Nekoray</a>
"""

    elif LANG == 'EN':
        return f"""
{header}

⭕️Required software for connecting to config

📥Android:
<a href='https://play.google.com/store/apps/details?id=com.v2ray.ang'>V2RayNG</a>
<a href='https://play.google.com/store/apps/details?id=ang.hiddify.com'>HiddifyNG</a>

📥iOS:
<a href='https://apps.apple.com/us/app/streisand/id6450534064'>Streisand</a>
<a href='https://apps.apple.com/us/app/foxray/id6448898396'>Foxray</a>
<a href='https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690'>V2box</a>

📥Windows:
<a href='https://github.com/MatsuriDayo/nekoray/releases'>Nekoray</a>
<a href='https://github.com/2dust/v2rayN/releases'>V2rayN</a>
<a href='https://github.com/hiddify/HiddifyN/releases'>HiddifyN</a>

📥Mac and Linux:
<a href='https://github.com/MatsuriDayo/nekoray/releases'>Nekoray</a>
"""


# Support Info Template
def support_template(owner_info, header=""):
    username = None
    owner_info = all_configs_settings()
    if owner_info:
        username = owner_info['support_username'] if owner_info['support_username'] else "-"
    else:
        username = "-"

    if LANG == 'FA':
        return f"""
{header}

📞پشتیبانی: {username}
"""

    elif LANG == 'EN':
        return f"""
{header}

📞Supporter: {username}
"""


# Alert Package Days Template
def package_days_expire_soon_template(sub_id, remaining_days):
    if LANG == 'FA':
        return f"""
تنها {remaining_days} روز تا اتمام اعتبار پکیج شما باقی مانده است.
لطفا برای خرید پکیج جدید اقدام کنید.
شناسه پکیج شما: <code>{sub_id}</code>
"""
    elif LANG == 'EN':
        return f"""
Only {remaining_days} days left until your package expires.
Please purchase a new package.
Your package ID: <code>{sub_id}</code>
"""


# Alert Package Size Template
def package_size_end_soon_template(sub_id, remaining_size):
    if LANG == 'FA':
        return f"""
تنها {remaining_size} گیگابایت تا اتمام اعتبار پکیج شما باقی مانده است.
لطفا برای تمدید پکیج اقدام کنید.

شناسه پکیج شما: <code>{sub_id}</code>
"""
    elif LANG == 'EN':
        return f"""
Only {remaining_size} GB left until your package expires.
Please renewal package.
Your package ID: <code>{sub_id}</code>
"""
