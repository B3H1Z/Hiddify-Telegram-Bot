#!/bin/bash

# Function to display error messages and exit
function display_error_and_exit() {
    echo "Error: $1"
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

# Step 1: Clone the repository and change directory
echo "Step 1: Cloning the repository and changing directory..."
git clone https://github.com/B3H1Z/Hiddify-Telegram-Bot.git /opt/Hiddify-Telegram-Bot || display_error_and_exit "Failed to clone the repository."
cd /opt/Hiddify-Telegram-Bot || display_error_and_exit "Failed to change directory."

# Step 2: Install requirements
echo "Step 2: Installing requirements..."
pip install -r requirements.txt || display_error_and_exit "Failed to install requirements."

# Step 3: Run config.py to generate config.json
echo "Step 3: Running config.py to generate config.json..."
python3 config.py || display_error_and_exit "Failed to run config.py."

# Step 4: Run the bot in the background using nohup
echo "Step 4: Running the bot in the background..."
nohup python3 hiddifyTelegramBot.py >/dev/null 2>&1 &

# Step 5: Add cron job to start the bot on reboot
echo "Step 5: Adding cron job to start the bot on reboot..."
(crontab -l 2>/dev/null; echo "@reboot cd /opt/Hiddify-Telegram-Bot && ./restart.sh") | crontab -

# Wait for a few seconds to check if the bot started successfully
sleep 5

# Check if the bot process is running
if pgrep -f "python3 hiddifyTelegramBot.py" >/dev/null; then
    echo "Bot setup completed successfully!"
else
    display_error_and_exit "Failed to start the bot. Please check for errors and try again."
fi
