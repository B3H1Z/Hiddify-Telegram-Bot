#!/bin/bash
# Define text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m' # Reset text color
7
HIDY_BOT_ID="@HidyBotGroup"
# Function to display error messages and exit
function display_error_and_exit() {
  echo -e "${RED}Error: $1${RESET}"
  echo -e "${YELLOW}${HIDY_BOT_ID}${RESET}"
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

echo -e "${GREEN}Step 1: Cloning the repository and changing directory...${RESET}"

repository_url="https://github.com/B3H1Z/Hiddify-Telegram-Bot.git"
install_dir="/opt/Hiddify-Telegram-Bot"

branch="main"

if [ "$0" == "--pre-release" ]; then
    branch="pre-release"
fi

echo "Selected branch: $branch"

if [ -d "$install_dir" ]; then
  echo "Directory $install_dir exists."
else
  git clone -b "$branch" "$repository_url" "$install_dir" || display_error_and_exit "Failed to clone the repository."
fi

cd "$install_dir" || display_error_and_exit "Failed to change directory."

echo -e "${GREEN}Step 2: Installing requirements...${RESET}"
pip install -r requirements.txt || display_error_and_exit "Failed to install requirements."


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
  local current_crontab

  # Normalize the cron job formatting (remove extra spaces)
  cron_job=$(echo "$cron_job" | sed -e 's/^[ \t]*//' -e 's/[ \t]*$//')

  # Check if the cron job already exists in the current user's crontab
  current_crontab=$(crontab -l 2>/dev/null || true)

  if [[ -z "$current_crontab" ]]; then
    # No existing crontab, so add the new cron job
    (echo "$cron_job") | crontab -
  elif ! (echo "$current_crontab" | grep -Fq "$cron_job"); then
    # Cron job doesn't exist, so append it to the crontab
    (echo "$current_crontab"; echo "$cron_job") | crontab -
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
