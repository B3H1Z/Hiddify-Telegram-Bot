from Utils.utils import all_configs_settings, backup_json_bot
from AdminBot.bot import bot
from config import ADMINS_ID

# Send backup file to admins
def cron_backup_bot():
    file_name = backup_json_bot()
    if file_name:
        for admin_id in ADMINS_ID:
            bot.send_document(admin_id, open(file_name, 'rb'), caption="🤖Bot Backup")