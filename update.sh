#!/bin/bash


pkill -15 -f hiddifyTelegramBot.py

sleep 5

if git pull; then
    nohup python3 hiddifyTelegramBot.py >> bot.log 2>&1 &
    echo "Bot has been updated and restarted."
else
    echo "Failed to update the bot. Check the Git repository for errors."
fi