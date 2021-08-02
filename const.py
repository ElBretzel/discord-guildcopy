import os
import sys

import pytz

OS_SLASH = "\\" if sys.platform == "win32" else "/"
DIRECTORY = os.path.abspath(os.path.dirname(__file__))
KEY_FILE = "key.txt"
KEY_DIRECTORY = os.path.join(DIRECTORY, KEY_FILE)
PREFIX = '§'
TIMEZONE = pytz.timezone('Europe/Paris')
pytz.all_timezones