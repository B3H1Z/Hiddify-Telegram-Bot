#!/bin/bash

pkill -15 -f hiddifyTelegramBot.py

sleep 5

nohup python3 /opt/Hiddify-Telegram-Bot/hiddifyTelegramBot.py >> bot.log 2>&1 &
echo "Bot has been restarted."

