import os
import json
from config import LANG
from Utils.utils import all_configs_settings

FOLDER = "Json"
MSG_FILE = "messages.json"
BTN_FILE = "buttons.json"
CMD_FILE = "commands.json"

settings = all_configs_settings()

with open(os.path.join(os.path.dirname(__file__), FOLDER, MSG_FILE), encoding='utf-8') as f:
    MESSAGES = json.load(f)
MESSAGES = MESSAGES[LANG]
if settings['msg_user_start']:
    MESSAGES['WELCOME'] = settings['msg_user_start']

with open(os.path.join(os.path.dirname(__file__), FOLDER, BTN_FILE), encoding='utf-8') as f:
    KEY_MARKUP = json.load(f)
KEY_MARKUP = KEY_MARKUP[LANG]

with open(os.path.join(os.path.dirname(__file__), FOLDER, CMD_FILE), encoding='utf-8') as f:
    BOT_COMMANDS = json.load(f)
BOT_COMMANDS = BOT_COMMANDS[LANG]
