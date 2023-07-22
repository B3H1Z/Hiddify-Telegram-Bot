#!/bin/bash

# Set the Python app name and version
APP_NAME="Hiddify-Telegram-Bot"
APP_VERSION="0.1.0"

# Set the GitHub repository URL
GITHUB_REPO="https://github.com/B3H1Z/Hiddify-Telegram-Bot.git"

# Define the installation directory
INSTALL_DIR="/usr/local/$APP_NAME"

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is required, please install it first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &>/dev/null; then
    echo "pip3 is required, please install it first."
    exit 1
fi

# Clone the GitHub repository to a temporary directory
TMP_DIR=$(mktemp -d)
git clone "$GITHUB_REPO" "$TMP_DIR" --branch "$APP_VERSION" --depth 1

# Install the Python app
pip3 install -r "$TMP_DIR/requirements.txt" --target "$INSTALL_DIR"

# Clean up temporary directory
rm -rf "$TMP_DIR"

# Create a symlink to the installed app in /usr/local/bin
ln -s "$INSTALL_DIR/bin/hidi-bot" "/usr/local/bin/hidi-bot"

echo "Installation complete."