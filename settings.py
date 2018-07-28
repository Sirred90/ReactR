# settings.py - Let's user manage bot settings and reactions

# import config and mongodb connection from bot.py
from bot import config, mongo

# discord imports
import discord
from discord.ext import commands

class SettingsCog:
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
    # Add command
    #
    #*******************************

    @commands.command(name='add', aliases=['a'], help="Adds a new keyword-reaction to this guild. `keyword` argument must be a string, `emoji` argument must be a single emoji.")
    @commands.guild_only()
    async def add_keyword(self, ctx, keyword: str, emoji: str):
        if not self.has_perms(ctx.author, ctx.channel):
            await ctx.channel.send("You do not have permissions to run that command.")
            return

        reaction = None
        valid = True

        # Check if the emoji is a custom emoji
        if("<" in emoji):
            # Get ID by splitting by :, then removing trailing >
            parts = emoji.split(":")

            emoji_id = parts[2][:-1]
            emojis = list(ctx.guild.emojis)

            #Assume emoji isn't legit
            valid = False

            #Check if the ID is actually legit
            for e in emojis: #Convert tuple of emojis to list, cast emojis to strings, join list into a string then split string by space
                if str(e.id) == emoji_id:
                    valid = True
                    break
            
            reaction = emoji_id
            
        else:
            # Check to make sure the emoji is actually an emoji. Valid unicode emojis are non ascii, and can be 2 characters long (fucking multicharacter emojis). 
            if len(emoji) > 2: # If there is definately more than one character 
                valid = False 

            if len(emoji.encode('ascii', 'ignore')) != 0: # If the word contains any ascii characters
                valid = False 

            reaction = emoji

        if not valid:
            await ctx.channel.send("Invalid emoji provided. If you think you are seeing this in error, contact the bot owner.")
            return

        # reaction is probably valid. Find and update the guild's document
        mongo["guilds"].update_one({"guild_id": ctx.guild.id}, {"$addToSet": {"message_reacts": {"word": keyword, "reaction": reaction}}})
        await ctx.channel.send("Emoji added :)")
    
    @add_keyword.error
    async def add_keyword_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.channel.send("You must specify arguments. Use `,help add` for more information.")
        else:
            raise(error)

    
    #*******************************
    # List command
    #
    #*******************************

    @commands.command(name="list", help="Lists all the keyword-reactions for this guild.")
    @commands.guild_only()
    async def list_emoji(self, ctx):
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

        if reaction_list == "":
            reaction_list = "There are no reactions defined yet, add one with `add keyword emoji`"
             
        embed.add_field(name="Keyword reactions", value=reaction_list, inline=False)

        await ctx.channel.send(embed = embed)

    #*******************************
    # Remove command
    #
    #*******************************

    @commands.command(name="remove", aliases=['r'], help="Removes all keyword-reactions where the keyword is the supplied argument.")
    @commands.guild_only()
    async def remove_keyword(self, ctx, *, keyword):
        if not self.has_perms(ctx.author, ctx.channel):
            await ctx.channel.send("You do not have permissions to run that command.")
            return

        # Get reactions for guild

        mongo["guilds"].update_one({"guild_id": ctx.guild.id}, {"$pull": {"message_reacts": {"word": keyword}}})
        await ctx.channel.send(f"Successfully removed all keyword reactions using '{keyword}'")

    @remove_keyword.error
    async def remove_keyword_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.channel.send("You must specify arguments. Use `,help remove` for more information.")
        else:
            raise(error)

    #*******************************
    # Addrole command
    #
    #*******************************

    @commands.command(name='addrole', aliases=['addroles', 'addr'], help="Allows a role to use admin commands. @mention role to add it, multiple roles can be mentioned.")
    @commands.guild_only()
    async def add_role(self, ctx, role: str):
        if not self.has_perms(ctx.author, ctx.channel):
            await ctx.channel.send("You do not have permissions to run that command.")
            return

        for role in ctx.message.role_mentions:
            mongo["guilds"].update_one({"guild_id": ctx.guild.id}, {"$addToSet": {"admin_roles": role.id}})

        await ctx.channel.send("Succesfully added role(s)")

    @add_role.error
    async def add_role_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.channel.send("You must specify a role. Use `,help addrole` for more information.")
        else:
            raise(error)

    #*******************************
    # Removerole command
    #
    #*******************************

    @commands.command(name='removerole', aliases=['removeroles', 'remover'], help="Disallows a role from using admin commands. @mention role to remove it, multiple roles can be mentioned.")
    @commands.guild_only()
    async def remove_role(self, ctx, role: str):
        if not self.has_perms(ctx.author, ctx.channel):
            await ctx.channel.send("You do not have permissions to run that command.")
            return

        for role in ctx.message.role_mentions:
            mongo["guilds"].update_one({"guild_id": ctx.guild.id}, {"$pull": {"admin_roles": role.id}})

        await ctx.channel.send("Succesfully removed role(s)")

    @remove_role.error
    async def remove_role_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.channel.send("You must specify a role. Use `,help addrole` for more information.")
        else:
            raise(error)

    #*******************************
    # listrole command
    #
    #*******************************

    @commands.command(name='listrole', aliases=['listroles', 'listr'], help="Lists all roles that have permission to modify the bot.")
    @commands.guild_only()
    async def list_role(self, ctx):
        if not self.has_perms(ctx.author, ctx.channel):
            await ctx.channel.send("You do not have permissions to run that command.")
            return

        admin_role_ids = []
        # Get guild data
        for x in mongo["guilds"].find({"guild_id": ctx.guild.id}, {"_id": 0, "admin_roles": 1}):
            for role_id in x["admin_roles"]:
                admin_role_ids.append(role_id)

        embed = discord.Embed(title=f"Admin roles for *{ctx.guild.name}*", color=0x53C1DE)

        role_list = ""

        for role in ctx.guild.roles:
            if role.id in admin_role_ids:
                role_list += f"{role}\n"

        if role_list == "":
            role_list = "There are no roles assigned, add one with ,addrole @role"

    
        embed.add_field(name=u"Admin:", value=role_list, inline=False)

        await ctx.channel.send(embed=embed)

    @list_role.error
    async def list_role_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.channel.send("You must specify a role. Use `,help addrole` for more information.")
        else:
            raise(error)

    #*******************************
    # settings command
    #
    #*******************************

    @commands.group(name='settings', help="Used to manage settings.")
    @commands.guild_only()
    async def settings(self, ctx):
        if ctx.invoked_subcommand is None:
            # Get settings from mongodb
            settings = dict(mongo["guilds"].find({"guild_id": ctx.guild.id}, {"_id": 0, "prefix": 1}).next())

            settingsString = ""

            for k,v in settings.items():
                settingsString += f"{k}: `{v}`"

            embed = discord.Embed(title=f"Settings for *{ctx.guild.name}*", color=0x53C1DE)
            embed.add_field(name=u"--------", value=settingsString, inline=False)

            await ctx.channel.send(embed = embed)


    @settings.command(name='prefix', help="Changes bot prefix to `pref`, leave pref blank to list current prefix.")
    async def settings_prefix(self, ctx, pref=None):
        if pref == None:
            # List current prefix
            prefix = mongo["guilds"].find({"guild_id": ctx.guild.id}, {"_id": 0, "prefix": 1}).next()["prefix"] # Get prefix from mongodb
            await ctx.channel.send(f"The current prefix is `{prefix}`")

        else:
            mongo["guilds"].update({"guild_id": ctx.guild.id}, {"$set": {"prefix": pref}})
            await ctx.channel.send(f"Prefix changed to `{pref}`")

def setup(bot):
    bot.add_cog(SettingsCog(bot))