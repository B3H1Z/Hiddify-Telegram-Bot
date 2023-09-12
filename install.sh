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

# Check if Git is installed
if ! command -v git &>/dev/null; then
  display_error_and_exit "Git is not installed. Please install Git and try again."
fi

# Check if Python 3 and pip are installed
if ! command -v python3 &>/dev/null || ! command -v pip &>/dev/null; then
  display_error_and_exit "Python 3 and pip are required. Please install them and try again."
fi

if [ "$1" == "pre-release" ]; then
  branch="pre-release"
  echo -e "${RED}Installing pre-release version...${RED}"
else
  branch="main" # Default branch
fi

echo -e "${GREEN}Step 1: Cloning the repository and changing directory...${RESET}"
echo -e "${RED}Branch: ${branch}${RED}"
echo -e "${RED}${1}${RED}"
repository_url="https://github.com/B3H1Z/Hiddify-Telegram-Bot.git"
install_dir="/opt/Hiddify-Telegram-Bot"

if [ -d "$install_dir" ]; then
  echo "Directory $install_dir exists."
else
  git clone -b "$branch" "$repository_url" "$install_dir" || display_error_and_exit "Failed to clone the repository."
fi

cd "$install_dir" || display_error_and_exit "Failed to change directory."

echo -e "${GREEN}Step 2: Installing requirements...${RESET}"
if ! pip install -q -r requirements.txt 2>&1 | grep -q "AttributeError: module 'lib' has no attribute 'X509_V_FLAG_CB_ISSUER_CHECK'"; then
  echo -e "${RED}Failed to install requirements. Removing existing pyopenssl and reinstalling...${RESET}"

  # Remove existing pyopenssl using your original command
  if ! sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; then
    display_error_and_exit "Failed to remove existing pyopenssl. Please check for errors and try again."
  fi

  # Install pyopenssl
  if ! sudo pip3 install pyopenssl; then
    display_error_and_exit "Failed to install pyopenssl. Please check for errors and try again."
  else
    echo -e "${GREEN}pyopenssl has been installed.${RESET}"
  fi
fi


echo -e "${GREEN}Step 3: Preparing ...${RESET}"
logs_dir="$install_dir/Logs"
receiptions_dir="$install_dir/UserBot/Receiptions"

create_directory_if_not_exists() {
  if [ ! -d "$1" ]; then
    echo "Creating directory $1"
    mkdir -p "$1"
  fi
}

create_directory_if_not_exists "$logs_dir"
create_directory_if_not_exists "$receiptions_dir"

chmod +x "$install_dir/restart.sh"
chmod +x "$install_dir/update.sh"

echo -e "${GREEN}Step 4: Running config.py to generate config.json...${RESET}"
python3 config.py || display_error_and_exit "Failed to run config.py."

echo -e "${GREEN}Step 5: Running the bot in the background...${RESET}"
nohup python3 hiddifyTelegramBot.py >>/opt/Hiddify-Telegram-Bot/bot.log 2>&1 &

echo -e "${GREEN}Step 6: Adding cron jobs...${RESET}"

add_cron_job_if_not_exists() {
  local cron_job="$1"
  if ! crontab -l | grep -q "$cron_job"; then
    (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
  fi
}

# Add cron job for reboot
add_cron_job_if_not_exists "@reboot cd $install_dir && ./restart.sh"

# Add cron job to run every 6 hours
add_cron_job_if_not_exists "0 */6 * * * cd $install_dir && python3 crontab.py --backup"

# Add cron job to run at 12:00 PM daily
add_cron_job_if_not_exists "0 12 * * * cd $install_dir && python3 crontab.py --reminder"

echo -e "${GREEN}Waiting for a few seconds...${RESET}"
sleep 5

if pgrep -f "python3 hiddifyTelegramBot.py" >/dev/null; then
  echo -e "${GREEN}The bot has been started successfully.${RESET}"
  echo -e "${GREEN}Send [/start] in Telegram bot.${RESET}"
else
  display_error_and_exit "Failed to start the bot. Please check for errors and try again."
fi