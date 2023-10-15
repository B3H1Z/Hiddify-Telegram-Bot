#!/bin/bash
# shellcheck disable=SC2034
target_version="5.8.2"

# Define text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m' # Reset text color
install_dir="/opt/Hiddify-Telegram-Bot"

# Function to display colored messages
function display_message() {
  echo -e "$1"
}

# Function to gracefully stop the bot
function stop_bot() {
  display_message "${GREEN}Stopping the bot gracefully...${RESET}"
  pkill -15 -f hiddifyTelegramBot.py
}

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

# current_version_first_part=$(echo "current_version" | cut -d '.' -f 1)
# target_version_first_part=$(echo "target_version" | cut -d '.' -f 1)

# if [ "$current_version_first_part" = "4" ] && [ "$target_version_first_part" = "5" ]; then
#     echo "Version is 4, running update.py to update to version 5."
#     python3 /opt/Hiddify-Telegram-Bot/update.py --update-v4-v5
#     echo "Update.py has been run."
# else
#     echo "Version is not 4."
# fi
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
    pip install -r requirements.txt || display_error_and_exit "Failed to install requirements."
    nohup python3 hiddifyTelegramBot.py >>bot.log 2>&1 &
    display_message "${GREEN}Bot has been updated and restarted.${RESET}"
  else
    if git pull --rebase origin "$branch"; then
      pip install -r requirements.txt || display_error_and_exit "Failed to install requirements."
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

# get backup of Database/hidyBot.db
function get_backup() {
  display_message "${GREEN}Getting backup of Database/hidyBot.db...${RESET}"
  if cp /opt/Hiddify-Telegram-Bot/Database/hidyBot.db /opt/Hiddify-Telegram-Bot/Database/hidyBot.db.bak; then
    display_message "${GREEN}Backup of Database/hidyBot.db has been taken.${RESET}"
  else
    display_message "${RED}Failed to get backup of Database/hidyBot.db.${RESET}"
  fi
}

# Stop the bot gracefully before proceeding
stop_bot

# Wait for a few seconds
display_message "Please wait for 5 seconds ..."
sleep 5
# If version.py does not exist, offer to reinstall the bot; otherwise, update it
if [ ! -f /opt/Hiddify-Telegram-Bot/version.py ]; then
  reinstall_bot
else

  current_version=$(python3 /opt/Hiddify-Telegram-Bot/version.py --version)  
  get_backup
  update_bot

  # Add cron job for reboot
  add_cron_job_if_not_exists "@reboot cd $install_dir && ./restart.sh"

  # Add cron job to run every 6 hours
  add_cron_job_if_not_exists "0 */6 * * * cd $install_dir && python3 crontab.py --backup"

  # Add cron job to run at 12:00 PM daily
  add_cron_job_if_not_exists "0 12 * * * cd $install_dir && python3 crontab.py --reminder"

  echo -e "${YELLOW}Current version: $current_version${RESET}"
  echo -e "${YELLOW}Target version: $target_version${RESET}"
  
  if python3 /opt/Hiddify-Telegram-Bot/update.py --current-version "$current_version" --target-version "$target_version"; then
      echo "update.py has been run."
  else
      echo "update.py has not been run."
      exit 1
  fi
  
fi
