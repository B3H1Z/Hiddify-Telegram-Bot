#!/bin/bash

pkill -15 -f hidyBot.py

sleep 5

nohup python3 /opt/Hiddify-Telegram-Bot/hidyBot.py >> bot.log 2>&1 &
echo "Bot has been restarted."

