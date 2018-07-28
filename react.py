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

    async def add_react(self, message, reaction):
        try:
            # Check if reaction is an id (throws error if it isn't an int)
            int(reaction)

            guild_emojis = list(message.guild.emojis)

            for emoji in guild_emojis:
                if str(emoji.id) == reaction:
                    try:
                        await message.add_reaction(emoji)
                    except discord.errors.HTTPException:
                        pass

        except ValueError:
            # Emoji isn't id, assume it's unicode
            await message.add_reaction(reaction)

    async def check_string(self, message, string, reactions):
        for value in reactions["message_reacts"]:
            if value["word"] in string.lower():
                 await self.add_react(message, value["reaction"])

    async def on_message(self, message):
        # Get guild from mongo

        guildData = mongo["guilds"].find({"guild_id": message.guild.id})[0]

        await self.check_string(message, message.content, guildData)

        for embed in message.embeds:
            if(isinstance(embed.title, str)):
                await self.check_string(message, embed.title, guildData)
            if(isinstance(embed.description, str)):
                await self.check_string(message, embed.description, guildData)

            for field in embed.fields:
                if(isinstance(field.name, str)):
                    await self.check_string(message, field.name, guildData)
                if(isinstance(field.value, str)):
                    await self.check_string(message, field.value, guildData)

            
                

def setup(bot):
    bot.add_cog(ReactCog(bot))