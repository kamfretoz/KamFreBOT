#!/usr/bin/env python3

import time
import asyncio
import discord
import json
import os
import logging
import data.config as config
import glob
import sys
import subprocess
import traceback
import random
from textwrap import dedent
from discord.ext import commands

if os.name != "nt":
    import uvloop
    uvloop.install()

print("Importing Modules....[Success]")

# bootup logo, use the bootup_logo.txt to modify it


def bootsplash():
    if config.bootsplash is True:
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
bootsplash()

# setting up prefix
print("Retrieving the prefix from config.py ....[OK]")


def get_prefix(bot, message):
    """A callable Prefix for my bot."""
    prefix = config.prefix
    return commands.when_mentioned_or(*prefix)(bot, message)


# Bot client initialization
bot = commands.AutoShardedBot(command_prefix=get_prefix, description=config.desc, case_insensitive=True, intents=discord.Intents.all())

# Setting up logging
print("Setting Log files to system.log ...[Success]")
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(
    filename="system.log", encoding="utf-8", mode="a+")
handler.setFormatter(logging.Formatter(
    "{asctime}:{levelname}:{name}:{message}", style="{"))
logger.addHandler(handler)

# more logging stuff
setattr(bot, "logger", logging.getLogger("main.py"))

# Getting the bot basic data from an external file so that it can be shared easily without having to always
# black it out
print("Loading the TOKEN...[Success]")
with open("data/coin.json") as json_fp:
    classified = json.load(json_fp)  # Loading data from the json file
    TOKEN = classified["token"]  # Getting the token

# Load up cogs (Ugly implementation i know, at least it works for now...)
print("Loading all Cogs and Extensions...")
for extension in os.listdir("cogs"):
    if extension.endswith(".py"):
        try:
            bot.load_extension("cogs." + extension[:-3])
        except Exception as e:
            print("Failed to load extension {}\n{}: {}".format(
                extension, type(e).__name__, e))

bot.load_extension("libneko.extras.help")
bot.load_extension("libneko.extras.superuser")

# Listener setup                    [RESPONSE ON MENTION WAS A MISTAKE]
# @bot.listen("on_message")
# async def on_mention_reply_prefix(message: discord.Message) -> None:
#    """Replies the bot's prefix when mentioned"""
#    if bot.user.mentioned_in(message):
#        await message.channel.send(f"**Hello! My prefix is `{config.prefix[0]}`.**")


# Loading message
@bot.event
async def on_connect():
    print("Connected to Discord!")


#@bot.event
#async def on_resumed():
#    print("WARNING: connection error was occurred and Successfully Resumed/Reconnected the Session.")
#    print(f"Current time: {time.ctime()}")
#    print(
#        f"Still watching {len(bot.users)} users across {len(bot.guilds)} servers.")


@bot.event
async def on_ready():
    bot.loop.create_task(change_activities())
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
    print(
        f"List of servers i'm in ({len(bot.guilds)} Servers in total):\n===========================")
    for x in bot.guilds:
        print(f"{x.name} (ID: {x.id}) (Membert Count: {x.member_count})")
    print("===========================")


async def change_activities():
    """Quite self-explanatory. It changes the bot activities"""
    statuses = (discord.Status.online, discord.Status.idle, discord.Status.dnd)
    while True:  # Infinite loop
        # Pick a choice from 'playopt'.
        game = discord.Game(name=config.playing_status)
        # Watch out for how you import 'random.choice', as that might affect how this line needs to be written.
        # For more help refer to the Python Docs.
        watch = discord.Activity(
            type=discord.ActivityType.watching,
            name=config.watching_status
        )  # Pick a choice from 'watchopt'
        # Pick a choice from 'streamopt'
        stream = discord.Streaming(
            url=config.streaming_url, name=config.streaming_status)
        listen = discord.Activity(
            type=discord.ActivityType.listening, name=config.listening_status
        )  # Pick a choice from 'listenopt'
        kind = random.choice(
            [game, watch, listen, stream]
        )  # Pick a choice from all the possibilities: "Playing", "Watching", "Streaming", "Listening"
        # actually changes the status of the bots every (n) of a second
        for s in statuses:
            await bot.change_presence(activity=kind, status=s)
            await asyncio.sleep(config.status_timeout)

# About command


@bot.command()
async def about(ctx):
    """Information about this bot."""
    creator = (await bot.application_info()).owner
    about = discord.Embed(
        title=f"{config.botname}", description=f"{config.desc}", color=0xFFFFFF
    )
    about.add_field(name="GitHub Link.",
                    value=f"[Click Here!]({config.about_github_link})")
    about.set_thumbnail(url=config.about_thumbnail_img)
    about.set_footer(text=f"Made by {creator}")
    await ctx.send(embed=about)

###################################
# DEBUGGING and SYSTEM UTILITIES #
#################################


@bot.command(aliases=["reboot"])
@commands.is_owner()
async def restart(ctx):
    """Restarts the bot for updates"""
    openerr = None
    core = "main.py"
    await ctx.send("Restarting!")
    try:
        if sys.platform == "win32":
            os.startfile(core)
        else:
            openerr = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([openerr, core])
    except FileNotFoundError:
        await ctx.send("❌ Unable to open the file!\n Shutting Down.")
    await ctx.bot.close()
    sys.exit()


@bot.command(aliases=["poweroff", "shutdown", "kms", "altf4", "fuckmylife", "fml", "fuckoff"])
@commands.is_owner()
async def poweroof(ctx):
    """Turn the bot Off"""
    await ctx.send("Goodbye Cruel World...")
    await ctx.bot.close()
    exit()


@bot.command(aliases=["clist"])
@commands.is_owner()
async def loaded(ctx):
    """Shows loaded/unloaded cogs"""
    core_cogs = []
    cogs = [
        "cogs." + os.path.splitext(f)[0]
        for f in [os.path.basename(f) for f in glob.glob("cogs/*.py")]
    ]
    loaded = [x.__module__.split(".")[1] for x in bot.cogs.values()]
    unloaded = [c.split(".")[1] for c in cogs if c.split(".")[1] not in loaded]
    embed = discord.Embed(title="List of loaded cogs")
    cogs = [w.replace("cogs.", "") for w in cogs]
    for cog in loaded:
        if cog in cogs:
            core_cogs.append(cog)
    if core_cogs:
        embed.add_field(
            name="Loaded", value="\n".join(sorted(core_cogs)), inline=True
        )
    if unloaded:
        embed.add_field(
            name="Not Loaded", value="\n".join(sorted(unloaded)), inline=True
        )
    else:
        embed.add_field(name="Not Loaded", value="None!", inline=True)
    await ctx.send(embed=embed)


@bot.command(aliases=["clearconsole", "cc", "cls"])
@commands.is_owner()
async def clear(ctx):
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


# This one is for testing error messages only
@bot.command(aliases=["dummy", "error"])
@commands.is_owner()
async def crash(ctx):
    """Use to generate an error message for debugging purpose"""
    await ctx.send("Generating an Error Message..")
    raise ValueError('This is an Exception that are manually generated.')

# Bot and System control command


@bot.command(aliases=["load"])
@commands.is_owner()
async def loadcog(ctx, name):
    """
    Load the specified cog
    """
    async with ctx.typing():
        try:
            bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(f":gear: Successfully Loaded **{name}** Module!")


@bot.command(aliases=["unload"])
@commands.is_owner()
async def unloadcog(ctx, name):
    """
    Unload the specified cog
    """
    async with ctx.typing():
        try:
            bot.unload_extension(f"cogs.{name}")
        except Exception as ex:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(f":gear: Successfully Unloaded **{name}** Module!")


@bot.command(aliases=["reload"])
@commands.is_owner()
async def reloadcog(ctx, name):
    """
    Reload the specified cog
    """
    async with ctx.typing():
        try:
            bot.unload_extension(f"cogs.{name}")
            bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f"Extension cannot be found or it hasn't been loaded")
        else:
            await ctx.send(f":gear: Successfully Reloaded the **{name}** module!")


@bot.command(aliases=["reloadall"])
@commands.is_owner()
async def reloadallcogs(ctx):
    """
    Reload all cogs!
    """
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


@bot.command(aliases=["loadall"])
@commands.is_owner()
async def loadallcogs(ctx):
    async with ctx.typing():
        """
        Load all cogs
        """
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


@bot.command(aliases=["unloadall"])
@commands.is_owner()
async def unloadallcogs(ctx):
    """
    Unload all cogs
    """
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

print("\nEOF")
