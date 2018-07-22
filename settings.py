# settings.py - Let's user manage bot settings and reactions

# import config and mongodb connection from bot.py
from bot import config, mongo

# discord imports
import discord
from discord.ext import commands


class ReactCog:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("Settings cog loaded successfuly")

    @commands.command(name='add')
    @commands.guild_only()
    async def add_keyword(self, ctx, *, arg=None):
        if arg is None:
            await ctx.channel.send("You must specify arguments. Propper syntax is `,add keyword emoji`.")
            return

        args = arg.split(' ')
        if len(args) < 2:
            await ctx.channel.send("You must provide two arguments. Propper syntax is `,add keyword emoji`.")
            return

        keyword = args[0]
        reaction = None

        valid = True

        # Check if the emoji is a custom emoji
        if("<" in args[1]):
            # Get ID by splitting by :, then removing trailing >
            parts = args[1].split(":")

            emoji_id = parts[2][:-1]
            emojis = list(ctx.guild.emojis)

            #Assume emoji isn't legit
            valid = False

            #Check if the ID is actually legit
            for emoji in emojis: #Convert tuple of emojis to list, cast emojis to strings, join list into a string then split string by space
                if str(emoji.id) == emoji_id:
                    valid = True
                    break
            
            reaction = emoji_id
            
        else:
            # Check to make sure the emoji is actually an emoji. Valid unicode emojis are non ascii, and can be 2 characters long (fucking multicharacter emojis). 
            if len(args[1]) > 2: # If there is definately more than one character 
                valid = False 

            if len(args[1].encode('ascii', 'ignore')) != 0: # If the word contains any ascii characters
                valid = False 

            reaction = args[1]

        if not valid:
            await ctx.channel.send("Invalid emoji provided. If you think you are seeing this in error, contact the bot owner.")
            return

        # reaction is probably valid. Find and update the guild's document
        mongo["guilds"].update_one({"guild_id": ctx.guild.id}, {"$addToSet": {"message_reacts": {"word": keyword, "reaction": reaction}}})
        await ctx.channel.send("Emoji added :)")
    async def on_message(self, message):
        # Get guild from mongo

        guildData = mongo["guilds"].find({"guild_id": message.guild.id})[0]

        for value in guildData["message_reacts"]:
            if value["word"] in message.content:
                await message.add_reaction(value["reaction"])

def setup(bot):
    bot.add_cog(ReactCog(bot))