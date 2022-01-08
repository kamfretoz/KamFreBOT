#!/usr/bin/env python3

import time
import discord
import os
import logging
import dotenv
import glob
import re
import sys
import traceback
from textwrap import dedent
from discord.ext import commands
from libneko import pag
from modules.http import HttpCogBase

if os.name != "nt":
    import uvloop
    uvloop.install()

print("Importing Modules....[Success]")

# Firing up the envs
dotenv.load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")
prefix = os.environ.get("BOT_PREFIX")
desc = os.environ.get("BOT_DESC")
ver = os.environ.get("BOT_VERSION")
splash = os.environ.get("BOT_SPLASH")

# bootup logo, use the bootup_logo.txt to modify it
def bootsplash():
    if splash is True:
        try:
            bootlogo = open("bootup_logo.txt", "r")
            while True:
                logo = bootlogo.readline()
                print(logo, end="")
                time.sleep(0.10)
                if not logo:
                    bootlogo.close()
                    break
        except:
            print("Unable to display the bootsplash sequence!")
            pass
        finally:
            bootlogo.close()


print(f"Starting Bot!")
bootsplash()

# setting up prefix
print("Retrieving the prefix from .env ....[OK]")



# Bot client initialization
bot = commands.AutoShardedBot(command_prefix=prefix, description=desc, case_insensitive=True, intents=discord.Intents.all(), strip_after_prefix=True)

# Setting up logging
print("Setting Log files to system.log ...[Success]")
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# more logging stuff
setattr(bot, "logger", logging.getLogger("main.py"))

# Getting the bot basic data from an external file so that it can be shared easily without having to always
# black it out

# Load up cogs
print("Loading all Cogs and Extensions...")
for file in glob.iglob("cogs/*.py"):
    try:
        bot.load_extension("cogs.{}".format(re.split(r"/|\\", file)[-1][:-3]))
    except Exception as e:
        print(f"Failed to load {file} \n{type(e).__name__}: {e}")
        
bot.load_extension("libneko.extras.help")
bot.load_extension("libneko.extras.superuser")

# Loading message
@bot.event
async def on_connect():
    print("Connected to Discord!")

@bot.event
async def on_ready():
    creator = (await bot.application_info()).owner
    setattr(bot, "creator", creator)
    print(
        dedent(
            f"""
        Welcome to {bot.user.name} !
        ===========================
        ID: {bot.user.id}
        Creator: {creator}
        Current prefix: {prefix}
        Python Version: {sys.version[:6]}
        Discord.py Version: {discord.__version__}
        {bot.user.name} Version: {ver}
        Watching {len(bot.users)} users across {len(bot.guilds)} servers.
        Logged in at {time.ctime()}
        ===========================
        """
        )
    )


###################################
# DEBUGGING and SYSTEM UTILITIES #
##################################
class BotUtils(HttpCogBase):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.message = "**⚙️ Extension `{name}` {result}**"
        self.results = {
            "loaded": "loaded!",
            "unloaded": "unloaded!",
            "reloaded": "reloaded!",
            "already_loaded": "is already loaded!",
            "not_loaded": "is not loaded.",
            "not_found": "not found.",
        }


    async def set_extension(self, ctx:commands.Context, name:str, action:str):
        """Base function for loading/unloading/reloading extensions."""
        name = name.replace(" ", "_").lower()
        action = action.lower()
        try:
            if action == "reload":
                try:
                    bot.unload_extension(f"cogs.{name}")
                    bot.load_extension(f"cogs.{name}")
                except commands.errors.ExtensionNotLoaded:
                    bot.load_extension(f"cogs.{name}")
                    action = "load"
            elif action == "load":
                bot.load_extension(f"cogs.{name}")
            else:
                bot.unload_extension(f"cogs.{name}")
        except commands.errors.ExtensionAlreadyLoaded:
            result = "already_loaded"
        except commands.errors.ExtensionNotLoaded:
            result = "not_loaded"
        except commands.errors.ExtensionNotFound:
            result = "not_found"
        except:
            await ctx.send(f"Exception:```py\n{traceback.format_exc(1980)}\n```")
            return
        else:
            result = action + "ed"

        await ctx.send(self.message.format(name=name, result=self.results[result]))
    
    async def set_extensions(self, ctx, action:str):
        """Function for loading/unloading/reloading all the extensions."""
        for file in glob.iglob("extensions/*.py"):
            name = re.split(r"/|\\", file)[-1][:-3]
            await self.set_extension(ctx, name, action=action)

    @commands.is_owner()
    @commands.command(aliases=["load_cog", "loadcog", "load"])
    async def load_extension(self, ctx, *, name:str):
        """Loads the specified extension/cog."""
        await self.set_extension(ctx, name, action="load")

    @commands.is_owner()
    @commands.command(aliases=["load_all", "loadall"])
    async def load_all_extensions(self, ctx):
        """Loads all available extensions/cogs."""
        async with ctx.typing():
            await self.set_extensions(ctx, action="load")

    @commands.is_owner()
    @commands.command(aliases=["unload_cog", "unloadcog", "unload"])
    async def unload_extension(self, ctx, *, name:str):
        """Unloads the specified extension/cog."""
        await self.set_extension(ctx, name, action="unload")

    @commands.is_owner()
    @commands.command(aliases=["unload_all", "unloadall"])
    async def unload_all_extensions(self, ctx):
        """Unloads all available extensions/cogs."""
        async with ctx.typing():
            await self.set_extensions(ctx, action="unload")

    @commands.is_owner()
    @commands.command(aliases=["reload_cog", "reloadcog", "reload"])
    async def reload_extension(self, ctx, *, name:str):
        """Reloads the specified extension/cog."""
        await self.set_extension(ctx, name, action="reload")

    @commands.is_owner()
    @commands.command(aliases=["reload_all", "reloadall"])
    async def reload_all_extensions(self, ctx):
        """Reloads all available extensions/cogs."""
        async with ctx.typing():
            await self.set_extensions(ctx, action="reload")

    @commands.command()
    @commands.is_owner()
    async def setbotname(self, ctx, *, name:str):
        """Renames the bot"""
        await bot.user.edit(username=name)
        await ctx.send(f"I now identify as '{name}'")

    @commands.command()
    @commands.is_owner()
    async def setbotavatar(self, ctx, *, url:str=None):
        """Changes the bot's avatar"""
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        elif url is None:
            await ctx.send("Please specify an avatar url if you did not attach a file")
            return
        try:
            session = self.acquire_session()
            async with session.get(url.strip("<>"), timeout = 10) as image:
                await bot.user.edit(avatar=await image.read())
        except Exception as e:
            await ctx.send("Unable to change avatar: {}".format(e))
            return
        await ctx.send(":eyes:")
        
    @commands.command(aliases=["servlist"])
    @commands.is_owner()
    async def serverlist(self, ctx):
        """Shows a list of servers that the bot is in along with member count"""
        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            servlist = discord.Embed(
                title=f"Servers that I am in", description=page, color=0x00FF00)
            servlist.set_footer(
                text=f"{len(self.bot.guilds)} Servers in total.")
            return servlist

        navi = pag.EmbedNavigatorFactory(factory=main_embed)
        servers = []
        for guild in self.bot.guilds:
            servers.append(f"**{guild.name}** (ID:{guild.id})")

        navi += "\n".join(servers)
        navi.start(ctx)
        
    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx, id: int = None):
        "Leave from a server"
        if id:
            guild = self.bot.get_guild(id)
        else:
            guild = ctx.guild
        await ctx.reply(f"Leaving from {guild.name}...")
        await guild.leave()
        await ctx.send("👍")
    # This one is for testing error messages only
    @commands.command(aliases=["dummy", "error"])
    @commands.is_owner()
    async def crash(self, ctx):
        """Use to generate an error message for debugging purpose"""
        await ctx.send("Generating an Error Message..")
        raise ValueError('This is an Exception that are manually generated.')
    
    @commands.command(aliases=["clearconsole", "cc", "cls"])
    @commands.is_owner()
    async def clear(self, ctx):
        """Clear the console."""
        if os.name == "nt":
            os.system("cls")
        else:
            try:
                os.system("clear")
            except Exception:
                for _ in range(100):
                    print()
        message = "Logged in as %s." % bot.user
        uid_message = "User id: %s." % bot.user.id
        separator = "-" * max(len(message), len(uid_message))
        print(separator)
        try:
            print(message)
        except:  # some bot usernames with special chars fail on shitty platforms
            print(message.encode(errors="replace").decode())
        print(uid_message)
        print(separator)
        await ctx.send("Console cleared successfully.")
        
    @commands.guild_only()
    @commands.command(aliases=["shard"])
    @commands.is_owner()
    async def shardid(self, ctx):
        """Display what shard you're on and count how many total shards exist"""
        await ctx.send(f"You are on Shard ID #{ctx.guild.shard_id} out of {bot.shard_count} Shards")

    @commands.command(aliases=["hardreboot","restart"])
    @commands.is_owner()
    async def hardrestart(self, ctx):
        """Restarts the bot for updates"""
        await ctx.reply("Restarting bot...")
        await ctx.bot.close()
        os.system("clear")
        os.execv(sys.executable, ['python3'] + sys.argv)

    @commands.command(aliases=["poweroff", "shutdown", "kms", "altf4", "fuckmylife", "fml", "fuckoff"])
    @commands.is_owner()
    async def poweroof(self, ctx):
        """Turn the bot Off"""
        await ctx.send("Shutting Down...")
        await ctx.bot.close()
        sys.exit()

bot.add_cog(BotUtils(bot))
print("Bot Toolbox has been loaded.")

## RUN THE WHOLE THING ##
bot.run(TOKEN)

print("\nEOF")
