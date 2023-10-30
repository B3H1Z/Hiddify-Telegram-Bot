from AdminBot.bot import bot
from config import ADMINS_ID
from Utils.utils import full_backup,all_configs_settings
import logging
try:
    bot.remove_webhook()
except:
    pass

def cron_backup():
    zip_file_name = full_backup()
    if not zip_file_name:
        logging.error("Backup failed")
        return
    settings = all_configs_settings()
    if not settings['panel_auto_backup']:
        return
    for admin_id in ADMINS_ID:
        bot.send_document(admin_id, open(zip_file_name, 'rb'), caption="🤖Backup",disable_notification=True)
    
    