from Utils.utils import *
from UserBot.bot import bot
from config import CLIENT_TOKEN
from UserBot.templates import package_size_end_soon_template, package_days_expire_soon_template

ALERT_PACKAGE_GB = 3
ALERT_PACKAGE_DAYS = 3


def alert_package_gb(package_remaining_gb):
    if package_remaining_gb <= ALERT_PACKAGE_GB:
        return True
    return False


def alert_package_days(package_remaining_days):
    if package_remaining_days <= ALERT_PACKAGE_DAYS:
        return True
    return False


def cron_reminder():
    if not CLIENT_TOKEN:
        return

    telegram_users = USERS_DB.select_users()
    if telegram_users:
        for user in telegram_users:
            user_telegram_id = user['telegram_id']
            user_subscriptions_list = non_order_user_info(user_telegram_id) + order_user_info(user_telegram_id)
            if user_subscriptions_list:
                for user_subscription in user_subscriptions_list:
                    package_days = user_subscription.get('remaining_day', 0)
                    package_gb = user_subscription.get('usage', {}).get('remaining_usage_GB', 0)
                    sub_id = user_subscription.get('sub_id')
                    if package_days == 0:
                        continue
                    if alert_package_gb(package_gb):
                        bot.send_message(user_telegram_id, package_size_end_soon_template(sub_id, package_gb))
                    if alert_package_days(package_days):
                        bot.send_message(user_telegram_id, package_days_expire_soon_template(sub_id, package_days))
