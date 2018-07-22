# bot.py - Entry point of bot

# misc imports
import json
import sys

# discord imports
import discord
from discord.ext import commands

# load config
config = {}
try:
    f = open("config.json", 'r')
    config = json.load(f)
    f.close()
except:
    print("Failed to load config. Run setup.py to create config file, if config file exists ensure it is a valid JSON")
    sys.exit()

def get_prefix(bot, message):
    # TODO: Configurable prefixes
    
    # Use @bot or prefix to activate bot
    return commands.when_mentioned_or(',')(bot, message)

bot = commands.Bot(command_prefix=get_prefix)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} - {bot.user.id}")

    
if __name__ == '__main__':
    bot.load_extension('react')
    bot.run(config["bot_token"], bot=True)