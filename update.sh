#!/bin/bash
# shellcheck disable=SC2034
target_version="5.0.0"

# Define text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m' # Reset text color

# Function to display colored messages
function display_message() {
  echo -e "$1"
}

# Function to gracefully stop the bot
function stop_bot() {
  display_message "${GREEN}Stopping the bot gracefully...${RESET}"
  pkill -15 -f hiddifyTelegramBot.py
}

# Function to reinstall the bot
function reinstall_bot() {
  display_message "${YELLOW}This version is deprecated, and you need to reinstall the bot.${RESET}"

  # Ask for confirmation
  read -r -p "Do you want to reinstall the bot? [y/N] " response
  case "$response" in
    [yY][eE][sS]|[yY])
      display_message "Reinstalling the bot..."

      # Change to the installation directory
      cd /opt || {
        display_message "${RED}Failed to change directory to /opt.${RESET}"
        exit 1
      }

      # Remove the old bot
      rm -rf /opt/Hiddify-Telegram-Bot

      # Run the installation script
      bash -c "$(curl -Lfo- https://raw.githubusercontent.com/B3H1Z/Hiddify-Telegram-Bot/main/install.sh)"

      display_message "${GREEN}Bot has been reinstalled.${RESET}"
      ;;
    *)
      display_message "Bot has not been reinstalled."
      ;;
  esac
}


branch="main"
if [ "$0" == "--pre-release" ]; then
    branch="pre-release"
fi
echo "Selected branch: $branch"

# Function to update and restart the bot
function update_bot() {
  display_message "${GREEN}Updating the bot...${RESET}"
  git stash
  if git pull origin "$branch"; then
    nohup python3 hiddifyTelegramBot.py >>bot.log 2>&1 &
    display_message "${GREEN}Bot has been updated and restarted.${RESET}"
  else
    if git pull --rebase origin "$branch"; then
      nohup python3 hiddifyTelegramBot.py >>bot.log 2>&1 &
      display_message "${GREEN}Bot has been updated and restarted.${RESET}"
    else
      display_message "${RED}Failed to update the bot. Check the Git repository for errors.${RESET}"
      exit 1
    fi
    display_message "${RED}Failed to update the bot. Check the Git repository for errors.${RESET}"
    exit 1
  fi
}

## Stop the bot gracefully before proceeding
#stop_bot

# Wait for a few seconds
display_message "Please wait for 5 seconds ..."
sleep 5

# If version.py does not exist, offer to reinstall the bot; otherwise, update it
if [ ! -f /opt/Hiddify-Telegram-Bot/version.py ]; then
  reinstall_bot
else
  update_bot
fi
