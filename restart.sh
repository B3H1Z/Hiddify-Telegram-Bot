#!/bin/bash

# Define text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m' # Reset text color

# Function to display error messages and exit
function display_error_and_exit() {
  echo -e "${RED}Error: $1${RESET}"
  exit 1
}

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
  display_error_and_exit "Python 3 is required. Please install it and try again."
fi

# Stop the bot gracefully using SIGTERM (signal 15)
echo -e "${GREEN}Stopping the bot gracefully...${RESET}"
pkill -15 -f hiddifyTelegramBot.py

# Wait for a few seconds to allow the bot to terminate
echo "Please wait for 5 seconds ..."
sleep 5

# Start the bot and redirect output to a log file
echo -e "${GREEN}Starting the bot...${RESET}"
nohup python3 /opt/Hiddify-Telegram-Bot/hiddifyTelegramBot.py >> /opt/Hiddify-Telegram-Bot/bot.log 2>&1 &

echo -e "${GREEN}Bot has been restarted.${RESET}"
