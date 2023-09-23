# Crontab
import argparse
from config import CLIENT_TOKEN

# use argparse to get the arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", action="store_true", help="Backup the panel")
    parser.add_argument("--backup-bot", action="store_true", help="Backup the bot")
    parser.add_argument("--reminder", action="store_true", help="Send reminder to users")
    args = parser.parse_args()

    # run the functions based on the arguments
    if args.backup:
        from Cronjob.backup import cron_backup
        cron_backup()

    elif args.reminder:
        if CLIENT_TOKEN:
            from Cronjob.reminder import cron_reminder
            cron_reminder()
    
    elif args.backup_bot:
        from Cronjob.backupBot import cron_backup_bot
        cron_backup_bot()


# To run this file, use this command:
# python3 crontab.py --backup
# python3 crontab.py --reminder
