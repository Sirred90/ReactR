# react.py - Finds keywords and reacts

# import config from bot.py
from bot import config

# discord imports
import discord
from discord.ext import commands

class ReactCog:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("React cog loaded successfuly")

    async def on_message(self, message):
        if "duck" in message.content:
            await message.add_reaction('🦆')

def setup(bot):
    bot.add_cog(ReactCog(bot))