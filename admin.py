# admin.py 

# settings.py - Let's user manage bot settings and reactions

# import config and mongodb connection from bot.py
from bot import config, mongo

# discord imports
import discord
from discord.ext import commands

def is_owner(ctx):
        return ctx.author.id == 240039475860733952

class AdminCog:
    def __init__(self, bot):
        self.bot = bot

    def has_perms(self, user, channel):
        if user.permissions_in(channel).administrator or user.id == 240039475860733952:
            return True

        user_roles = [role.id for role in user.roles]

        # Get guild data
        for x in mongo["guilds"].find({"guild_id": channel.guild.id}, {"_id": 0, "admin_roles": 1}):
            for role_id in x["admin_roles"]:
                if(role_id in user_roles):
                    return True

        return False

    async def on_ready(self):
        print("Settings cog loaded successfuly")

    #*******************************
    # Details command
    #
    #*******************************

    @commands.command(name="details", hidden = True)
    @commands.check(is_owner)
    @commands.guild_only()
    async def details(self, ctx):
        print("yes")
        embed = discord.Embed(title=f"Bot details", color=0x53C1DE)
        embed.add_field(name="Servers", value=f"Count: {len(self.bot.guilds)}")
        await ctx.channel.send(embed=embed)

    async def on_guild_join(self, guild):
        await self.bot.get_channel(471833598153195531).send(f"Joined guild {guild.name} - {guild.id}")

    
    #*******************************
    # Listserver command
    # Lists all the reactions for a server with id 'arg'
    #*******************************

    @commands.command(name="listserver", hidden=True)
    @commands.guild_only()
    async def list_emoji(self, ctx, arg):
        # Get reactions for guild
        guild_data = mongo["guilds"].find({"guild_id": arg})[0]
        
        embed = discord.Embed(title=f"Reactions for *{arg}*", color=0x53C1DE)

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

        if reaction_list == "":
            reaction_list = "There are no reactions defined yet, add one with `add keyword emoji`"
             
        embed.add_field(name="Keywoard reactions", value=reaction_list, inline=False)

        await ctx.channel.send(embed = embed)



def setup(bot):
    bot.add_cog(AdminCog(bot))