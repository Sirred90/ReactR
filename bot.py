# bot.py - Entry point of bot

# misc imports
import json
import sys
import os

# discord imports
import discord
from discord.ext import commands

# mongodb
import pymongo

# load config
config = {}
try:
    f = open(os.path.dirname(os.path.realpath(__file__)) + "/config.json", 'r')
    config = json.load(f)
    f.close()
except:
    print("Failed to load config. Run setup.py to create config file, if config file exists ensure it is a valid JSON")
    sys.exit()

# connect to mongo
mongo = pymongo.MongoClient(f"mongodb+srv://{config['mongo_user']}:{config['mongo_pass']}@{config['mongo_host']}/test?retryWrites=true")["reactr"]

def get_prefix(bot, message):
    # TODO: Configurable prefixes
    
    # Use @bot or prefix to activate bot
    return commands.when_mentioned_or(',')(bot, message)

bot = commands.Bot(command_prefix=get_prefix)

def add_guild(guild_id):
    # Add the guild to the mongo db

    doc = {
        "guild_id": guild_id,
        "message_reacts": [],
        "user_reacts": [],
        "admin_roles": []
    }

    mongo["guilds"].insert_one(doc)
    print(f"Added guild {guild_id} to mongodb")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} - {bot.user.id}")

    # Check if the bot has joined any guilds since it was last launched
    for guild in bot.guilds:
        # See if reactions database contains a collection whose guild is the guild id
        guild_id = guild.id
        
        num = mongo["guilds"].count_documents({"guild_id": guild_id})

        if num == 0:
            add_guild(guild_id)
            
@bot.event
async def on_guild_join(guild):
    if mongo["guilds"].count_documents({"guild_id": guild.id}) == 0:
        add_guild(guild.id)

if __name__ == '__main__':
    bot.load_extension('react')
    bot.load_extension('settings')
    bot.run(config["bot_token"], bot=True)