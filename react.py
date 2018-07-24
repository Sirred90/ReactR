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

        guildData = mongo["guilds"].find({"guild_id": message.guild.id})[0]

        for value in guildData["message_reacts"]:
            if value["word"] in message.content.lower():
                try:
                    # Check if reaction is an id (throws error if it isn't an int)
                    int(value["reaction"])

                    guild_emojis = list(message.guild.emojis)

                    for emoji in guild_emojis:
                        if str(emoji.id) == value["reaction"]:
                            print("Trying to add?")
                            try:
                                await message.add_reaction(emoji)
                            except discord.errors.HTTPException:
                                pass

                except ValueError:
                    # Emoji isn't id, assume it's unicode
                    await message.add_reaction(value["reaction"])

def setup(bot):
    bot.add_cog(ReactCog(bot))