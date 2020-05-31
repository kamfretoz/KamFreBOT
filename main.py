#!/usr/bin/env python3

import time
import asyncio
import discord
import quotes
import json
import os
import logging
import config
import sys
import subprocess
import traceback
import random
import libneko
from textwrap import dedent
from discord.ext import commands
from _datetime import datetime

print("Importing Modules....[Success]")

# bootup logo, use the bootup_logo.txt to modify it
def bootsplash():
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

print(f"Starting {config.botname}!")
#print(f"Welcome back {os.getlogin()}!")
bootsplash()

# setting up prefix
print("\nRetrieving the prefix from config.py ....[OK]")
def get_prefix(bot, message):
    """A callable Prefix for my bot."""
    prefix = config.prefix
    return commands.when_mentioned_or(*prefix)(bot, message)

# Bot client initialization
bot = commands.Bot(
    command_prefix=get_prefix, description=config.desc, case_insensitive=True
)

# Setting up logging
print("\nSetting Log files to system.log ...[Success]")
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename="system.log", encoding="utf-8", mode="a+")
handler.setFormatter(logging.Formatter("\n{asctime}:{levelname}:{name}:{message}", style="{"))
logger.addHandler(handler)

# more logging stuff
setattr(bot, "logger", logging.getLogger("main.py"))

# Getting the bot basic data from an external file so that it can be shared easily without having to always
# black it out
print("\nLoading the TOKEN...[Success]")
with open("coin.json") as json_fp:
    classified = json.load(json_fp)  # Loading data from the json file
    TOKEN = classified["token"]  # Getting the token

# Load up cogs (Ugly implementation i know, at least it works for now...)
print("Loading all Cogs and Extensions...")
for extension in os.listdir("cogs"):
    if extension.endswith(".py"):
        try:
            bot.load_extension("cogs." + extension[:-3])
        except Exception as e:
            print(
                "Failed to load extension {}\n{}: {}".format(
                    extension, type(e).__name__, e
                )
            )

bot.load_extension("libneko.extras.help")
bot.load_extension("libneko.extras.superuser")

# Listener setup                    [RESPONSE ON MENTION WAS A MISTAKE]
#@bot.listen("on_message")
#async def on_mention_reply_prefix(message: discord.Message) -> None:
#    """Replies the bot's prefix when mentioned"""
#    if bot.user.mentioned_in(message):
#        await message.channel.send(f"**Hello! My prefix is `{config.prefix[0]}`.**")


# Loading message
@bot.event
async def on_connect():
    print("\nConnected to Discord!")


@bot.event
async def on_resumed():
    print("WARNING: connection error was occurred and Successfully Resumed/Reconnected the Session.")
    print(f"Current time: {time.ctime()}")
    print(f"Still watching {len(bot.users)} users across {len(bot.guilds)} servers.")


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
        Current prefix: {config.prefix}
        Python Version: {sys.version[:6]}
        Discord.py Version: {discord.__version__}
        {bot.user.name} Version: {config.version}
        Watching {len(bot.users)} users across {len(bot.guilds)} servers.
        Logged in at {time.ctime()}
        ===========================
        """
        )
    )
    print(f"List of servers i'm in ({len(bot.guilds)} Servers in total):\n===========================")
    for x in bot.guilds:
        print(f"{x.name} (ID: {x.id}) (Membert Count: {x.member_count})")
    print("===========================")
    bot.loop.create_task(change_activities())

async def change_activities():
    """Quite self-explanatory. It changes the bot activities"""
    random.seed()
    statuses = (discord.Status.online, discord.Status.idle, discord.Status.dnd)
    while True:  # Infinite loop
        game = discord.Game(name=config.playing_status)  # Pick a choice from 'playopt'.
        # Watch out for how you import 'random.choice', as that might affect how this line needs to be written.
        # For more help refer to the Python Docs.
        watch = discord.Activity(
            type=discord.ActivityType.watching,
            name=config.playing_status
        )  # Pick a choice from 'watchopt'
        stream = discord.Streaming(url=config.streaming_url, name=config.streaming_status)  # Pick a choice from 'streamopt'
        listen = discord.Activity(
            type=discord.ActivityType.listening, name=config.listening_status
        )  # Pick a choice from 'listenopt'
        kind = random.choice(
            [game, watch, listen, stream]
        )  # Pick a choice from all the possibilities: "Playing", "Watching", "Streaming", "Listening"
        for s in statuses:
            await bot.change_presence(activity=kind, status=s)
            await asyncio.sleep(config.status_timeout)


# Main Exception Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        nocommand = discord.Embed(
            description=":warning: **Invalid Command!**"
            )
        nocommand.set_image(url="https://http.cat/404.jpg")
        await ctx.send(content=None, embed=nocommand, delete_after=5.0)
    elif isinstance(error, commands.errors.CheckFailure):
        nopermission = discord.Embed(
            description="**:warning: You don't have permissions to use that command.**"
        )
        nopermission.set_image(url="https://http.cat/403.jpg")
        await ctx.send(content=None, embed=nopermission, delete_after=5.0)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        missingargs = discord.Embed(
            description="**:warning: You are missing required arguments.**"
        )
        await ctx.send(content=None, embed=missingargs, delete_after=5.0)
    elif isinstance(error, commands.errors.BadArgument):
        badargument = discord.Embed(
            description="**:warning: You have given an invalid argument.**"
        )
        badargument.set_image(url="https://http.cat/400.jpg")
        await ctx.send(content=None, embed=badargument, delete_after=5.0)
    elif isinstance(error, commands.CommandOnCooldown):
        cooldownerr = discord.Embed(
            description=f"**:warning: That command is on cooldown. Please try again after {int(error.retry_after) + 1} second(s).**"
        )
        cooldownerr.set_image(url="https://http.cat/429.jpg")
        await ctx.send(embed=cooldownerr, content=None, delete_after=5.0)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        missperm = discord.Embed(
            description=f"**:warning: I don't have required permission to complete that command.**"
        )
        missperm.set_image(url="https://http.cat/403.jpg")
        await ctx.send(embed=missperm, content=None, delete_after=5.0)
    elif isinstance(error, commands.errors.TooManyArguments):
        toomanyargs = discord.Embed(
            description=f"**:warning: You have inputted too many arguments!**"
        )
        toomanyargs.set_image(url="https://http.cat/413.jpg")
        await ctx.send(embed=toomanyargs, content=None, delete_after=5.0)
    elif isinstance(error, commands.errors.DisabledCommand):
        ded = discord.Embed(description=f"**:warning: This command are disabled.**")
        ded.set_image(url="https://http.cat/410.jpg")
        await ctx.send(embed=ded, content=None, delete_after=5.0)

    elif isinstance(error, discord.Forbidden):
        missaccess = discord.Embed(
            description=f"**:no_entry_sign: I'm not allowed to do that!**"
        )
        missaccess.set_image(url="https://http.cat/401.jpg")
        await ctx.send(embed=missaccess, content=None, delete_after=5.0)
    elif isinstance(error, commands.errors.NotOwner):
        notowner = discord.Embed(description=f"**:warning: You are not my owner!**")
        notowner.set_image(url="https://http.cat/400.jpg")
        await ctx.send(embed=notowner, content=None, delete_after=5.0)

    elif isinstance(error, discord.NotFound):
        notfound = discord.Embed(
            description=f"**:warning: Can't find the target message!**")
        notfound.set_image(url="https://http.cat/404.jpg")
        await ctx.send(embed=notfound, content=None, delete_after=5.0)

    else:
        try:
            now = datetime.now()
            print(f"Ignoring exception in command {ctx.command.name}")
            trace = traceback.format_exception(type(error), error, error.__traceback__)
            print("".join(trace))
            errormsg = discord.Embed(title=f"🛑 An error occurred with the `{ctx.command.name}` command.", description=f"ℹ More Information:\n🖥 Server: {ctx.guild.name}\n📑 Channel: #{ctx.channel}\n👥 User: {ctx.message.author}\n🕓 At: {now.strftime('%B %d, %Y - %H:%M:%S')} GMT+7")
            errormsg.set_image(url="https://http.cat/500.jpg")
            await bot.get_channel(config.home).send(content=f"{random.choice(quotes.errors)}", embed=errormsg)
            await ctx.send(content=f"'{random.choice(quotes.errors)}'", embed=errormsg, delete_after=9.9)
            await bot.get_channel(config.home).send("📜 **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```")
            await ctx.send("📜 **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```", delete_after=10)
        except discord.HTTPException:
            fuckeduperr = discord.Embed(title="💥 An error occurred while displaying the previous error.")
            fuckeduperr.set_image(url="https://http.cat/500.jpg")
            await ctx.send(embed=fuckeduperr, delete_after=5)


# About command
@bot.command()
async def about(ctx):
    """Information about this bot."""
    creator = (await bot.application_info()).owner
    about = discord.Embed(
        title=f"{config.botname}", description=f"{config.desc}", color=0xFFFFFF
    )
    about.add_field(name="GitHub Link.", value=f"[Click Here!]({config.about_github_link})")
    about.set_thumbnail(url=config.about_thumbnail_img)
    about.set_footer(text=f"Made by {creator}")
    await ctx.send(embed=about)

###################################
# DEBUGGING and SYSTEM UTILITIES #
#################################

@bot.command(hidden=True, aliases=["reboot"])
@commands.is_owner()
async def restart(ctx):
    """Restarts the bot for updates"""
    openerr = None
    core = "main.py"
    await ctx.send("Restarting!")
    if sys.platform == "win32":
        os.startfile(core)
    else:
        openerr ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([openerr, core])
    await ctx.bot.logout()
    sys.exit()

@bot.command(hidden=True, aliases=["poweroff", "shutdown"])
@commands.is_owner()
async def poweroof(ctx):
    """Turn the bot Off"""
    await ctx.send("Goodbye Cruel World...")
    await ctx.bot.logout()
    exit(0)


@bot.command(hidden=True)
@commands.is_owner()
async def runningcog(ctx):
    """See what cogs are currently running"""
    cogslist = bot.cogs
    for cogs in cogslist:
        print(cogs)

    await ctx.send(bot.cogs)


# This one is for testing error messages only
@bot.command(hidden=True, aliases=["dummy"])
@commands.is_owner()
async def crash(ctx):
    """Use to generate an error message for debugging purpose"""
    await ctx.send("Generating an Error Message..")
    raise ValueError('This is an Exception that are manually generated.')



# Bot and System control command
@bot.command(hidden=True, aliases=["load"])
@commands.is_owner()
async def loadcog(ctx, name):
    async with ctx.typing():
        try:
            bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(f":gear: Successfully Loaded {name} Module!")


@bot.command(hidden=True, aliases=["unload"])
@commands.is_owner()
async def unloadcog(ctx, name):
    async with ctx.typing():
        try:
            bot.unload_extension(f"cogs.{name}")
        except Exception as ex:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(f":gear: Successfully Unloaded **{name}** Module!")


@bot.command(hidden=True, aliases=["reload"])
@commands.is_owner()
async def reloadcog(ctx, name):
    async with ctx.typing():
        try:
            bot.unload_extension(f"cogs.{name}")
            bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(f":gear: Successfully Reloaded the **{name}** module!")


@bot.command(hidden=True, aliases=["reloadall"])
@commands.is_owner()
async def reloadallcogs(ctx):
    async with ctx.typing():
        await ctx.send(":gear: Reloading all Cogs!")
        try:
            for extension in config.extensions:
                await ctx.send(f":gear: Unloading {extension} Module!", delete_after=5)
                bot.unload_extension(extension)
                await ctx.send(f":gear: Reloading {extension} Module!", delete_after=5)
                bot.load_extension(extension)
                await ctx.send(f":gear: Successfully Reloaded **{extension}** Module!")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(":gear: Successfully Reloaded all cogs!")


@bot.command(hidden=True, aliases=["loadall"])
@commands.is_owner()
async def loadallcogs(ctx):
    async with ctx.typing():
        await ctx.send(":gear: Loading all Cogs!")
        try:
            for extension in config.extensions:
                bot.load_extension(extension)
                await ctx.send(
                    f":gear: Successfully Loaded {extension} Module!", delete_after=5
                )
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(":gear: Successfully Loaded all cogs!")


@bot.command(hidden=True, aliases=["unloadall"])
@commands.is_owner()
async def unloadallcogs(self, ctx):
    async with ctx.typing():
        await ctx.send(":gear: Unloading all Cogs!")
        try:
            for extension in config.extensions:
                bot.unload_extension(extension)
                await ctx.send(
                    f":gear: Successfully Unloaded {extension}", delete_after=5
                )
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(":gear: Successfully Unloaded all cogs!")

## RUN THE WHOLE THING ##
bot.run(TOKEN)

print("EOF")
