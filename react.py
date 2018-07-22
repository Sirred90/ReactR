# react.py - Finds keywords and reacts

# import config and mongodb connection from bot.py
from bot import config, mongo

# discord imports
import discord
from discord.ext import commands


class ReactCog:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("React cog loaded successfuly")

    async def on_message(self, message):
        # Get guild from mongo

        guildData = mongo["reactions"].find({"guild_id": message.guild.id})[0]

        for value in guildData["message_reacts"]:
            if value["word"] in message.content:
                await message.add_reaction(value["reaction"])

def setup(bot):
    bot.add_cog(ReactCog(bot))