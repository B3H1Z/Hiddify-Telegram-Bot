import os
import json
from config import LANG

FOLDER = "Json"

MSG_FILE = "messages.json"
BTN_FILE = "buttons.json"
CMD_FILE = "commands.json"

with open(os.path.join(os.path.dirname(__file__),FOLDER, MSG_FILE), encoding='utf-8') as f:
    MESSAGES = json.load(f)
MESSAGES = MESSAGES[LANG]

with open(os.path.join(os.path.dirname(__file__),FOLDER, BTN_FILE), encoding='utf-8') as f:
    KEY_MARKUP = json.load(f)
KEY_MARKUP = KEY_MARKUP[LANG]

with open(os.path.join(os.path.dirname(__file__),FOLDER, CMD_FILE), encoding='utf-8') as f:
    BOT_COMMANDS = json.load(f)
BOT_COMMANDS = BOT_COMMANDS[LANG]
