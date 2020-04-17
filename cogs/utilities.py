import asyncio
import inspect
import re
import unicodedata
import urllib
import time
from pytz import timezone
from datetime import datetime

from libneko import pag, converters
import discord
from discord.ext import commands

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pingeries = {}
        self.lock = asyncio.Lock()
        self.user2context = {}

    @commands.command()
    async def code(self, ctx, *, msg):
        """Write text in code format."""
        await ctx.message.delete()
        await ctx.send("```" + msg.replace("`", "") + "```")


    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters."""
        if len(characters) > 15:
            return await ctx.send('Too many characters ({}/15)'.format(len(characters)))

        fmt = '`\\U{0:>08}`: `\\N{{{1}}}` - `{2}` - <http://www.fileformat.info/info/unicode/char/{0}>'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)

        await ctx.send('\n'.join(map(to_string, characters)))

    @commands.command(aliases=["servlist"])
    async def serverlist(self, ctx):
        """Shows a list of servers that the bot is in along with member count"""
        servlist = discord.Embed(color=0x00FF00)
        servlist.set_author(
            name=f"Servers that I am in. ({len(self.bot.guilds)} Servers in total)",
            icon_url=ctx.bot.user.avatar_url,
        )
        for x in self.bot.guilds:
            servlist.add_field(
                name=f"{x.name}",
                value=f"Member Count: {x.member_count}\n",
                inline=False,
            )
        await ctx.send(embed=servlist, content=None)

    @commands.command()
    @commands.is_owner()
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
            await ctx.send("No source was found...")

    @commands.command()
    async def uni(self, ctx, *, msg: str):
        """Convert to unicode emoji if possible. Ex: [p]uni :eyes:"""
        await ctx.send("`" + msg.replace("`", "") + "`")

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, query):
        """Search YouTube video from the given query"""
        query_string = urllib.parse.urlencode({"search_query": query})
        html_content = urllib.request.urlopen(
            "http://www.youtube.com/results?" + query_string
        )
        search_results = re.findall(
            'href=\\"\\/watch\\?v=(.{11})', html_content.read().decode()
        )
        await ctx.send("http://www.youtube.com/watch?v=" + search_results[0])

    # pingstorm command
    @commands.cooldown(rate=1, per=1800.0)
    @commands.command(hidden=True, aliases=["pingmachine", "pingspam"], enabled=True)
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
                        await ctx.send(
                            f"{user.mention} - {ping + 1}/{amount}"
                        )
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

        if ctx.invoked_with == "ping":
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
    # Scrapped for now until i can figure out how to do the customizeable timezone. EDIT: I DID IT!
    @commands.command(aliases=["time","date","now"])
    async def clock(self, ctx, loc = "Asia/Jakarta"):
        """Show current time. [p]time <timezone>\n for timezone list see: http://tiny.cc/on60iz"""
        if loc is None:
            await ctx.send(":warning: **Warning!** Please provide the timezone you would like to check. (See the list of Valid Timezone: http://tiny.cc/on60iz)")
        else:
            time_fmt = "%I:%M:%S %p"
            date_fmt = "%A %d. %B %Y"
            
            try:
                now = datetime.now(timezone(loc))
    
                time = now.strftime(time_fmt)
                date = now.strftime(date_fmt)
    
                clock = discord.Embed(color=0xC0C0C0)
                clock.add_field(name=":clock3: Current Time:", value=time, inline=False)
                clock.add_field(name="📆 Current Date", value=date, inline=False)
                clock.set_footer(text=f"Showing the timezone for {loc}\nfor timezone list see: http://tiny.cc/on60iz")
                await ctx.send(embed=clock, content=f":alarm_clock: Tick.. Tock..")
            except:
                await ctx.send(":warning: **Warning!** Please provide the correct timezone value. (See the list of Valid Timezone: http://tiny.cc/on60iz)")

def setup(bot):
    bot.add_cog(Utilities(bot))
    print("Utilities Module has been loaded.")