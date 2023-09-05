<p align="center">
  <a href="https://github.com/mtashani/Hiddify-Telegram-Bot" target="_blank" rel="noopener noreferrer">
    <img width="200" height="200" src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/icon.png?raw=True" alt="Hidy Bot">
  </a>
</p>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README-FA.md">فارسی</a>
<br>
  <a href="https://t.me/HidyBotGroup">Telegram Group</a>

</p>
<h1 align="center">Hidy Bot</h1>

Hidy Bot is a Telegram bot that allows you to manage your Hiddify panel directly from Telegram.

Install Hidy Bot on the **SAME SERVER** as your Hiddify panel.

**Please note:** This project is currently in BETA, and we are actively working to make it even better. If you encounter any bugs or issues, we appreciate your feedback and bug reports.

> Disclaimer: This bot is **not official** and is not affiliated with Hiddify team.

## Features
- [x] Add users
- [x] Remove users
- [x] Edit user details
- [x] View users list
- [x] Search users (by name, configuration, UUID)
- [x] Show user information (name, traffic, date, etc.)
- [x] Display user configs and subscription links
- [x] Get a backup of your panel + Auto send
- [x] View server status (RAM, CPU, disk)
- [x] Multi language (English, Persian)
- [x] Client bot
- [x] and more...
## To do list
- [ ] Empty
## Installation

To install the bot, run the following command:

```bash
sudo bash -c "$(curl -Lfo- https://raw.githubusercontent.com/mtashani/Hiddify-Telegram-Bot/main/install.sh)"
```
<br>

Make sure you have the following information ready:

1. `Admin Telegram Number ID` : Get it from [User info bot](https://t.me/userinfobot) (Example: `123456789`)
2. `Admin Telgram Bot Token` : Get it from [BotFather](https://t.me/BotFather) (
   Example: `1234567890:ABCdEfGhIjKlMnOpQrStUvWxYz`)
3. `Hiddify Panel URL` : The url of your Hiddify panel (
   Example: `https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4`) <b>exactly like this
   pattern!</b>
4. `Bot Language` : Options are `en` and `fa` [default is `fa`]
5. Optional: `Client(Users) Telegram Bot Token` : Get it from [BotFather](https://t.me/BotFather) (
   Example: `1234567890:ABCdEfGhIjKlMnOpQrStUvWxYz`) if you want set up a bot for your users


Now you can use the bot in Telegram by sending the `/start` command.




## Commands
- ### Update bot
```bash
cd /opt/Hiddify-Telegram-Bot/ && curl -fsSL -o /opt/Hiddify-Telegram-Bot/update.sh https://raw.githubusercontent.com/mtashani/Hiddify-Telegram-Bot/main/update.sh && chmod +x /opt/Hiddify-Telegram-Bot/update.sh && bash /opt/Hiddify-Telegram-Bot/update.sh
```
- ### Restart bot
```bash
cd /opt/Hiddify-Telegram-Bot/ && chmod +x restart.sh && ./restart.sh
```
- ### Stop bot
```bash
pkill -9 -f hiddifyTelegramBot.py
```
- ### Get bot logs
```bash
cat /opt/Hiddify-Telegram-Bot/Logs/hidyBot.log
```
- ### Get bot configs
```bash
cat /opt/Hiddify-Telegram-Bot/config.json
```
- ### Change bot configs
```bash
cd /opt/Hiddify-Telegram-Bot/ && python3 config.py && chmod +x restart.sh && ./restart.sh
```
- ### Reinstall bot
```bash
cd /opt/ && rm -rf /opt/Hiddify-Telegram-Bot/ && sudo bash -c "$(curl -Lfo- https://raw.githubusercontent.com/mtashani/Hiddify-Telegram-Bot/main/install.sh)"
```

## Screenshots
#### Users Bot
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-1.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-2.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-3.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-4.jpg?raw=True" width=35% height=35%>
#### Admin Bot
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-1.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-2.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-6.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-8.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-5.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-3.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-4.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/mtashani/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-7.jpg?raw=True" width=35% height=35%>
