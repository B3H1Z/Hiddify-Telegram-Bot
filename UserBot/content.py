import os
import json
from config import LANG

MSG_FILE = "Json/messages.json"
BTN_FILE = "Json/buttons.json"
CMD_FILE = "Json/commands.json"

with open(os.path.join(os.path.dirname(__file__), MSG_FILE), encoding='utf-8') as f:
    MESSAGES = json.load(f)
MESSAGES = MESSAGES[LANG]

with open(os.path.join(os.path.dirname(__file__), BTN_FILE), encoding='utf-8') as f:
    KEY_MARKUP = json.load(f)
KEY_MARKUP = KEY_MARKUP[LANG]

with open(os.path.join(os.path.dirname(__file__), CMD_FILE), encoding='utf-8') as f:
    BOT_COMMANDS = json.load(f)
BOT_COMMANDS = BOT_COMMANDS[LANG]
