__version__ = "v0.120A"
import config
import discord
import asyncio
import aiohttp
import json
import logging
import datetime
import traceback
import random
import quotes
import libneko  # Awesome lib btw, thanks Espy :)
import time
import os
import sys
from discord.ext import commands
from textwrap import dedent

print("Importing Modules....[Success]")

#
# INVITE: https://discordapp.com/oauth2/authorize?client_id=476753956127899651&scope=bot&permissions=1454898246
#

# bootup logo
def bootsplash():
    try:
        bootlogo = open("bootup_logo.txt", "r")
        while True:
            logo = bootlogo.readline()
            print(logo, end="")
            time.sleep(0.10)
            if not logo:
                break
    except:
        pass
    finally:
        bootlogo.close()


print(f"Starting {config.botname}!")
print(f"Welcome back {os.getlogin()}!")
bootsplash()

# Setting up logging
# print("\nSetting Log files to system.log ...[Success]")
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename="system.log", encoding="utf-8", mode="w")
# handler.setFormatter(
#    logging.Formatter("{asctime}:{levelname}:{name}:{message}", style="{")
# )
# logger.addHandler(handler)

# Getting your bot basic data from a external file so that you can share your code easily without having to always black it out
print("\nLoading the TOKEN...[Success]")
with open("coin.json") as json_fp:
    confidental = json.load(json_fp)  # Loading data from the json file
    TOKEN = confidental["token"]  # Getting the token


# setting up prefix
print("Retrieving the prefix from config.py ....[OK]")


def get_prefix(bot, message):
    """A callable Prefix for my bot."""
    prefix = config.prefix
    return commands.when_mentioned_or(*prefix)(bot, message)


bot = commands.Bot(
    command_prefix=get_prefix, description=config.desc, case_insensitive=True
)

# more logging stuff
setattr(bot, "logger", logging.getLogger("main.py"))


# Load up cogs and libneko
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

# Loading message
@bot.event
async def on_connect():
    print("\nConnected to Discord!")


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
        {bot.user.name} Version: {__version__}
        Watching {len(bot.users)} users across {len(bot.guilds)} servers.
        Logged in at {time.ctime()}
        ===========================
        """
        )
    )
    print(
        f"List of servers i'm in ({len(bot.guilds)} Servers in total):\n==========================="
    )
    for x in bot.guilds:
        print(f"{x.name} (Membert Count: {x.member_count})")
    print("===========================")
    bot.loop.create_task(change_activities())


async def change_activities():
    """Quite self-explanatory. It changes the bot activities"""
    timeout = 10  # The time between each change of status in seconds
    statuses = (discord.Status.online, discord.Status.idle, discord.Status.dnd)
    while True:  # Infinite loop
        game = discord.Game(name="Have a nice day! ^^")  # Pick a choice from 'playopt'.
        # Watch out for how you import 'random.choice', as that might affect how this line needs to be written.
        # For more help refer to the Python Docs.
        watch = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.users)} users across {len(bot.guilds)} servers.",
        )  # Pick a choice from 'watchopt'
        stream = discord.Streaming(
            url="", name=""
        )  # Pick a choice from 'streamopt'
        listen = discord.Activity(
            type=discord.ActivityType.listening, name="You ❤"
        )  # Pick a choice from 'listenopt'
        possb = random.choice(
            [game, watch, listen]
        )  # Pick a choice from all the possibilities: "Playing", "Watching", "Streaming", "Listening"
        for s in statuses:
            await bot.change_presence(activity=possb, status=s)
            await asyncio.sleep(timeout)


@bot.event
async def on_resumed():
    print(
        "\nWARNING: connection error was occured and Successfully Resumed/Reconnected the Session.\n"
    )
    print(f"\nCurrent time: {time.ctime()}")
    print(f"Still watching {len(bot.users)} users across {len(bot.guilds)} servers.")


# Main Exception Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        nocommand = discord.Embed(description=":warning: **Invalid Command!**")
        await ctx.send(content=None, embed=nocommand, delete_after=3)
    elif isinstance(error, commands.errors.CheckFailure):
        nopermission = discord.Embed(
            description="**:warning: You don't have permissions to use that command.**"
        )
        await ctx.send(content=None, embed=nopermission)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        missingargs = discord.Embed(
            description="**:warning: You are missing required arguments.**"
        )
        await ctx.send(content=None, embed=missingargs)
    elif isinstance(error, commands.errors.BadArgument):
        badargument = discord.Embed(
            description="**:warning: You have given an invalid argument.**"
        )
        await ctx.send(content=None, embed=badargument)
    elif isinstance(error, commands.CommandOnCooldown):
        cooldownerr = discord.Embed(
            description=f"**:warning: That command is on cooldown. Please try again after {int(error.retry_after) + 1} second(s).**"
        )
        await ctx.send(embed=cooldownerr, content=None)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        missperm = discord.Embed(
            description=f"**:warning: I don't have required permission to complete that command.**"
        )
        await ctx.send(embed=missperm, content=None)
    elif isinstance(error, commands.errors.TooManyArguments):
        toomanyargs = discord.Embed(
            description=f"**:warning: You have inputted too many arguments!**"
        )
        await ctx.send(embed=toomanyargs, content=None)
    elif isinstance(error, commands.errors.DisabledCommand):
        ded = discord.Embed(description=f"**:warning: This command are disabled.**")
        await ctx.send(embed=ded, content=None)
    elif isinstance(error, discord.Forbidden):
        missaccess = discord.Embed(
            description=f"**:no_entry_sign: I'm not allowed to send message there!**"
        )
        await ctx.send(embed=missaccess, content=None)
    elif isinstance(error, commands.errors.NotOwner):
        notowner = discord.Embed(description=f"**:warning: You are not my owner!**")
        await ctx.send(embed=notowner, content=None, delete_after=5.0)
    elif isinstance(error, discord.NotFound):
        notfound = discord.Embed(
            description=f"**:warning: Can't find the target message!**"
        )
        await ctx.send(embed=notfound, content=None, delete_after=5.0)
    else:
        try:
            print(f"Ignoring exception in command {ctx.command.name}")
            trace = traceback.format_exception(type(error), error, error.__traceback__)
            print("".join(trace))
            errormsg = discord.Embed(
                description=f":octagonal_sign:  An error occurred with the `{ctx.command.name}` command."
            )
            await ctx.send(content=f"'{random.choice(quotes.errors)}'", embed=errormsg)
            await ctx.send(
                ":scroll: **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```"
            )
        except discord.HTTPException:
            await ctx.send(
                ":boom: An error occurred while displaying the previous error."
            )

#This one is for testing error messages only
@bot.command(hidden=True, aliases=["dummy"])
@commands.is_owner()
async def crash(ctx):
    """Use to generate an error message for debugging purpose"""
    await ctx.send("Generating an Error Message..")
    div = 0 / 0
    await ctx.send(div)


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
            await ctx.send(f":gear: Successfully Loaded {name}")


@bot.command(hidden=True, aliases=["unload"])
@commands.is_owner()
async def unloadcog(ctx, name):
    async with ctx.typing():
        try:
            bot.unload_extension(f"cogs.{name}")
        except Exception as ex:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(f":gear: Successfully Unloaded **{name}**")


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
            await ctx.send(f":gear: Successfully Reloaded the **{name}** module")


@bot.command(hidden=True, aliases=["reloadall"])
@commands.is_owner()
async def reloadallcogs(ctx):
    async with ctx.typing():
        await ctx.send(":gear: Reloading all Cogs!")
        try:
            for extension in config.extensions:
                await ctx.send(f":gear: Unloading {extension}", delete_after=5)
                bot.unload_extension(extension)
                await ctx.send(f":gear: Reloading {extension}", delete_after=5)
                bot.load_extension(extension)
                await ctx.send(f":gear: Successfully Reloaded **{extension}**")
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
                    f":gear: Successfully Loaded {extension}", delete_after=5
                )
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send(":gear: Successfully Loaded all cogs!")


@bot.command(hidden=True, aliases=["unloadall"])
@commands.is_owner()
async def unloadallcogs(ctx):
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


@bot.command(brief="Fully restarts the bot", hidden=True, aliases=["reboot"])
@commands.is_owner()
async def restart(ctx):
    """Restarts the bot for updates"""
    await ctx.send("Restarting!")
    os.startfile("main.py")
    await ctx.bot.logout()
    sys.exit()


@bot.command(hidden=True)
@commands.is_owner()
async def runningcog(ctx):
    await ctx.send(bot.cogs)


@bot.command(hidden=True, aliases=["poweroff", "shutdown"])
@commands.is_owner()
async def poweroof(ctx):
    await ctx.send("Shutting Down!")
    await ctx.bot.logout()
    exit(0)


@bot.command(hidden=True, aliases=["syspoweroff"])
@commands.is_owner()
async def bundir(ctx):
    await ctx.message.delete()
    os.system("shutdown -s -t 3")
    await ctx.send("Shutting Down System!", delete_after=1)


@bot.command(hidden=True, aliases=["sysrestart"])
@commands.is_owner()
async def matisuri(ctx):
    await ctx.message.delete()
    os.system("shutdown -r -t 3")
    await ctx.send("Restarting the System!", delete_after=1)


@bot.command(hidden=True, aliases=["syssleep"])
@commands.is_owner()
async def molor(ctx):
    await ctx.message.delete()
    await ctx.send("Entering Sleep Mode!", delete_after=1)
    os.system("rundll32 powrprof.dll,SetSuspendState 0,1,0")


@bot.command(hidden=True, aliases=["syslock"])
@commands.is_owner()
async def gembok(ctx):
    await ctx.message.delete()
    os.system("rundll32 user32.dll, LockWorkStation")
    await ctx.send("Locking your Computer!", delete_after=1)

bot.run(TOKEN)
