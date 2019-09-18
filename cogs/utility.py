"""
MIT License
Copyright (c) 2018 Koyagami, Tmpod (XLR)
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import discord
import quotes
import config
import asyncio
import time
import calendar
import inspect
import os
import random
import json
import typing
from datetime import datetime
from dateutil.tz import gettz
import datetime as dt
from dateutil.tz import gettz
from discord.ext import commands
import re
import urllib
import urbandict
from libneko import converters, logging, pag
import inspect
import PyDictionary
from typing import Optional



class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pingeries = {}
        self.lock = asyncio.Lock()
        self.dictionary = PyDictionary.PyDictionary()
        self.user2context = {}

    # pingstorm command
    @commands.cooldown(rate=1, per=1800.0)
    @commands.command(
        hidden=True, aliases=["pingmachine", "pingspam"], enabled=True
    )
    @commands.guild_only()
    async def pingstorm(self, ctx, user: discord.Member, amount: int = 5):
        """Ping specified user number of times, 5 if no amount specified, Maximum amount is 999. (Cooldown: 1 use per 60 mins, Use wisely.)"""
        if not self.lock.locked():
            async with self.lock:
                loading = await ctx.send("Ping Machine Initializing in 3 seconds!")
                str(loading)
                await asyncio.sleep(3)
                start = await ctx.send("Begin!")
                str(start)

                async def ping_task(self):
                    ping = 0
                    while ping < int(amount):
                        if amount > 999:
                            await ctx.send(
                                "**WARNING:** **Maximum allowed amount is 999.**"
                            )
                            await ctx.message.add_reaction("❌")
                            break
                        await ctx.trigger_typing()
                        await ctx.send(f"{user.mention} Ping {ping + 1} out of {amount}")
                        ping += 1
                    await ctx.send("Finished!", delete_after=10.0)
                    await ctx.message.delete()
            ping = ctx.bot.loop.create_task(ping_task(self))
            self.pingeries.update({f"{user.id}@{ctx.guild.id}": ping})

    # Betterping command
    @commands.command(aliases=["pong"])
    async def ping(self, ctx):
        """Check current connection status."""
        start = time.monotonic()

        if ctx.invoked_with == 'ping':
            msg = await ctx.send(f":ping_pong: Pong!")
        else:
            msg = await ctx.send(f":ping_pong: Ping!")

        millis = (time.monotonic() - start) * 1000
        heartbeat = ctx.bot.latency * 1000

        if heartbeat > 1000:
            colours = discord.Colour(0xFF0000)
        elif heartbeat > 500:
            colours = discord.Colour(0xFFFF00)
        else:
            colours = discord.Colour(0x26D934)

        ping = discord.Embed(
            title="Current Ping:",
            description=f"```💓: {heartbeat:,.2f}ms\n💬: {millis:,.2f}ms.```",
            timestamp=datetime.utcnow(),
            color=colours,
        )
        await msg.edit(embed=ping)

    # time command
    # Scrapped for now until i can figure out how to do the customizeable timezone
    @commands.command(aliases=["time"])
    async def thetime(self, ctx):
        """Show current time."""
        now = datetime.now()
        time = now.strftime("%I:%M %p")
        date = now.strftime("%a, %d %b %Y")
        clock = discord.Embed(color=0xC0C0C0)
        clock.add_field(name=":clock3: Current System Time:", value=time, inline=False)
        clock.add_field(name="📆 Current Date", value=date, inline=False)
        await ctx.send(embed=clock, content="Tick.. Tock..")


    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, query):
        """"Search YouTube video from the given query"""
        query_string = urllib.parse.urlencode({"search_query": query})
        html_content = urllib.request.urlopen(
            "http://www.youtube.com/results?" + query_string
        )
        search_results = re.findall(
            'href=\\"\\/watch\\?v=(.{11})', html_content.read().decode()
        )
        await ctx.send("http://www.youtube.com/watch?v=" + search_results[0])

    @commands.command(aliases=["ud"])
    async def urban(self, ctx, *, word: str):
        "Browse Urban Dictionary."
        try:
            defi = urbandict.define(word)
            definition = defi[0]["def"]
            example = defi[0]["example"]
            ud = discord.Embed(title=f":mag: {word}", description=definition, color=0x25332)
            ud.add_field(name=":bulb: Example", value=example, inline=False)
            ud.set_footer(
                text="Urban Dictionary API",
                icon_url="https://vignette.wikia.nocookie.net/logopedia/images/a/a7/UDAppIcon.jpg/revision/latest?cb=20170422211150",
            )
            ud.set_thumbnail(
                url="https://vignette.wikia.nocookie.net/logopedia/images/a/a7/UDAppIcon.jpg/revision/latest?cb=20170422211150"
            )
            await ctx.send(embed=ud, content=None)

        except urllib.error.HTTPError:
            await ctx.send(
            embed=discord.Embed(
                description=f":mag_right: No Definition Found."
            )
        )

    @commands.command(aliases=["servlist"])
    async def serverlist(self, ctx):
        """Shows a list of servers that the bot is in along with member count"""
        servlist = discord.Embed(color=0x00ff00)
        servlist.set_author(name = f"Servers that I am in. ({len(self.bot.guilds)} Servers in total)", icon_url=ctx.bot.user.avatar_url)
        for x in self.bot.guilds:
            servlist.add_field(name=f"{x.name}", value=f"Member Count: {x.member_count}\n", inline=False)
        await ctx.send(embed = servlist, content=None)


    @commands.command()
    async def canirun(self, ctx, command):
        command = ctx.bot.get_command(command)
        if command is None:
            return await ctx.send("That command does not exist...", delete_after=5)
        try:
            can_run = await command.can_run(ctx)
        except Exception as ex:
            await ctx.send(
                "You cannot run the command here, because: "
                f"`{type(ex).__name__}: {ex!s}`"
            )
        else:
            await ctx.send(
                f'You {can_run and "can" or "cannot"} run this ' "command here."
            )

    @commands.command(name="define", aliases=["def"])
    async def _define(self, ctx, *, term: str):
        """Defines a word."""
        formatted = f"**Definition of `{term}`**\n"

        async with ctx.typing():
            definition = self.dictionary.meaning(term)
            if definition is None:
                await ctx.send(":no_entry_sign: No definition found for that term.")
            else:
                for t in definition:
                    formatted += f"{t}:\n```css\n"
                    for subdef in definition[t]:
                        formatted += f"- {subdef}"
                    formatted += "\n```\n"
                await ctx.send(formatted)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(aliases=["selfnick"])
    @commands.guild_only()
    async def selfnickname(self, ctx, * , newname: str = None):
        """Change my nickname, if omitted, removes it instead."""
        guild = ctx.guild
        if newname == None:
            await guild.me.edit(nick=None)
            await ctx.send(
            embed=discord.Embed(description=f"Successfully reset my nickname.")
            )
        elif len(newname) > 32:
            await ctx.send(
                embed=discord.Embed(description=f":warning: The new nickname must be 32 or fewer in length.")
            )
        else:
            await guild.me.edit(nick=newname)
            await ctx.send(
            embed=discord.Embed(description=f"Successfully changed my nickname to **{newname}**!")
            )

    @commands.command()
    async def pick(self, ctx, *options: converters.clean_content):
        """
        Options are separated by spaces; to include spaces in an option,
        you should put quotes around the option.
        """
        if not options or len(options) == 1:
            await ctx.send("Provide two or more options")
        else:
            await ctx.send(random.choice(options))

    @commands.command()
    async def rtfm(self, ctx, *, command):
        """Get the source code for a certain command, cog..."""
        try:
            try:
                command_obj = await converters.CommandConverter().convert(ctx, command)
                code = inspect.getsource(command_obj.callback)
                object_type = "command"
            except:
                try:
                    code = inspect.getsource(type(ctx.bot.cogs[command]))
                    object_type = "cog"
                except:
                    code = inspect.getsource(ctx.bot.extensions[command])
                    object_type = "extension"
            p = pag.StringNavigatorFactory(
                prefix="```py",
                suffix="```",
                max_lines=22,
                substitutions=[lambda s: s.replace("`", "′")],
            )
            p.add_line(f"# -*-*- Source for {command} {object_type}  -*-*-")
            p.disable_truncation()
            for line in code.split("\n"):
                p.add_line(line)
            p.start(ctx)
        except:
            self.log.exception("Failed to load source.")
            await ctx.send("No source was found...")


def setup(bot):
    bot.add_cog(Utility(bot))