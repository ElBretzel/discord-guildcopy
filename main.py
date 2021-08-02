import os
import sys
import glob

import discord
from discord.ext import commands

from database import DBManager
from const import *

with open(KEY_DIRECTORY, 'r') as f:
    key = f.read()

sys.path.insert(1, DIRECTORY)
os.chdir(DIRECTORY)

default_intents = discord.Intents.default()
default_intents.members = True
default_intents.typing = False
default_intents.presences = False

class Bot(commands.Bot):
    def __init__(self, command_prefix, token, intents):
        self.token = token
        super().__init__(command_prefix, intents = intents, reconnect = True)

    def load_commands(self):
        cogs_file = glob.iglob(f"cogs{OS_SLASH}**.py")
        for c in cogs_file:
            files = c.split(f"{OS_SLASH}")[1][:-3]
            print(f"Starting {files}.")
            self.load_extension(f"cogs.{files}")

    def start_bot(self):
        print(f"Starting cogs...")
        self.load_commands()
        print("Done!")
        print(f"Starting database...")
        DBManager()
        print("Done!")
        print(f"Starting bot...")
        self.run(self.token)

    async def on_ready(self):
        print(f"Bot ready!")

if __name__ == '__main__':
    bot = Bot(command_prefix = PREFIX, token = key, intents = default_intents)
    bot.start_bot()
