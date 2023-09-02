#!/bin/bash

pkill -15 -f hiddifyTelegramBot.py

sleep 5

#If version.py is not exist, reinstall the bot
if [ ! -f /opt/Hiddify-Telegram-Bot/version.py ]; then
  # This version is deprecated
  # do you want to reinstall the bot?


  #ask for confirmation
  echo "This version is deprecated, you need to reinstall the bot."
  read -r -p "Do you want to reinstall the bot? [y/N] " response
  case "$response" in
    [yY][eE][sS]|[yY])
      # shellcheck disable=SC2164
      cd /opt || exit
      # Remove the old bot
      rm -rf /opt/Hiddify-Telegram-Bot
      # run install.sh
      bash -c "$(curl -Lfo- https://raw.githubusercontent.com/B3H1Z/Hiddify-Telegram-Bot/main/install.sh)"
      echo "Bot has been reinstalled."
      ;;
    *)
      echo "Bot has not been reinstalled."
      ;;
  esac
else
  echo "Updating the bot..."
  git stash
  if git pull origin main; then
    nohup python3 hiddifyTelegramBot.py >>bot.log 2>&1 &
    echo "Bot has been updated and restarted."
  else
    echo "Failed to update the bot. Check the Git repository for errors."
  fi
fi
