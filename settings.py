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

    @commands.command(name="list")
    @commands.guild_only()
    async def list_emoji(self, ctx, *, arg=None):
        # Get reactions for guild
        guild_data = mongo["guilds"].find({"guild_id": ctx.guild.id})[0]
        
        embed = discord.Embed(title=f"Reactions for *{ctx.guild.name}*", color=0x53C1DE)

        reaction_list = ""

        for value in guild_data["message_reacts"]:

            # Assume reaction is unicode
            reaction_text = value['reaction']
            try:
                int(value['reaction'])
                for emoji in list(ctx.guild.emojis):
                    if str(emoji.id) == value['reaction']:
                        reaction_text = str(emoji)
                        break

            except Exception:
                pass

            reaction_list += f"{value['word']}: {reaction_text}\n"
             
        embed.add_field(name="Keywoard reactions", value=reaction_list, inline=False)

        await ctx.channel.send(embed = embed)

    @commands.command(name="remove")
    @commands.guild_only()
    async def remove_react(self, ctx, *, arg=None):
        # Get reactions for guild
        if arg is None:
            await ctx.channel.send("A keyword must be provided.")
            return

        mongo["guilds"].update_one({"guild_id": ctx.guild.id}, {"$pull": {"message_reacts": {"message_reacts.$.word": arg}}})


def setup(bot):
    bot.add_cog(ReactCog(bot))