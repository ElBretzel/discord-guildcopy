import os
import sys
import json

import pytz


################################ EDIT THIS PART AS YOU WISH ################################

KEY_FILE = "key.txt"
LANGUAGE_FILE = "language.json"
PREFIX = '§'
LOCALIZATION = "Europe/Paris" # Please copy the exact name in the TZ Database field you want -> https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
ICON_URL = "https://www.emoji.co.uk/files/mozilla-emojis/symbols-mozilla/12051-heavy-exclamation-mark-symbol.png" # The image displayed before the footer (must be a png / jpg / jpeg / gif /bitmap AND a HTTP(s) url)
MESSAGE_LIMIT = None # If set to None, the bot will fetch all the messages sent in the guild (not recommended for a old or populated guild). If set to any numeral number, the bot will fetch all the last messages in a channel until the number you have chosen. 
LANGUAGE_USED = "french" # Please look the file language.json for supported language

############## DO NOT EDIT THE CODE BELOW IF YOU DON'T KNOW WHAT YOU'RE DOING ##############


OS_SLASH = "\\" if sys.platform == "win32" else "/"
DIRECTORY = os.path.abspath(os.path.dirname(__file__))
KEY_DIRECTORY = os.path.join(DIRECTORY, KEY_FILE)
LANGUAGE_DIRECTORY = os.path.join(DIRECTORY, LANGUAGE_FILE)
TIMEZONE = pytz.timezone(LOCALIZATION)
with open(LANGUAGE_DIRECTORY, "r", encoding="utf-8") as f:
    LANGUAGE = json.load(f)
MAIN_LANGUAGE = LANGUAGE[LANGUAGE_USED]