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


def setup(bot):
    bot.add_cog(AdminCog(bot))