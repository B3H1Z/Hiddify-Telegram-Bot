from Utils.utils import backup_panel,all_configs_settings
from AdminBot.bot import bot
from config import ADMINS_ID

# Send backup file to admins
def cron_backup():
    file_name = backup_panel()
    settings = all_configs_settings()
    if not settings['panel_auto_backup']:
        return
    if file_name:
        for admin_id in ADMINS_ID:
            bot.send_document(admin_id, open(file_name, 'rb'),caption="🖥️Panel Backup",disable_notification=True)
