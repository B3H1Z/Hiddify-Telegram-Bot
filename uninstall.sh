#!/bin/bash

# Define text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m' # Reset text color

HIDY_BOT_ID="@HidyBotGroup"
INSTALL_DIR="/opt/Hiddify-Telegram-Bot"

# Function to display error messages and exit
function display_error_and_exit() {
  echo -e "${RED}Error: $1${RESET}"
  echo -e "${YELLOW}${HIDY_BOT_ID}${RESET}"
  exit 1
}

echo -e "${GREEN}Uninstalling the Hiddify-Telegram-Bot...${RESET}"

# Check if the installation directory exists
if [ -d "$INSTALL_DIR" ]; then
  # Stop the running bot if it's still running
  if pgrep -f "python3 hiddifyTelegramBot.py" >/dev/null; then
    echo -e "${GREEN}Stopping the bot...${RESET}"
    pkill -9 -f "hiddifyTelegramBot.py"
  fi

  # Remove cron jobs
  echo -e "${GREEN}Removing cron jobs...${RESET}"
  crontab -l | grep -v "$INSTALL_DIR" | crontab -

  # Remove the installation directory
  echo -e "${GREEN}Removing the installation directory...${RESET}"
  rm -rf "$INSTALL_DIR"

  echo -e "${GREEN}Uninstallation complete.${RESET}"
else
  display_error_and_exit "The installation directory does not exist. Nothing to uninstall."
fi
