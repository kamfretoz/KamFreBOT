import asyncio
import inspect
import re
import unicodedata
import urllib
import time
import random
import math
from pytz import timezone
from datetime import datetime
import safygiphy
import urbandict
import PyDictionary

from libneko import pag, converters
import discord
from discord.ext import commands

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pingeries = {}
        self.lock = asyncio.Lock()
        self.user2context = {}
        self.dictionary = PyDictionary.PyDictionary()


    @commands.command()
    async def code(self, ctx, *, msg):
        """Write text in code format."""
        await ctx.message.delete()
        await ctx.send("```" + msg.replace("`", "") + "```")


    @commands.command()
    async def charinfo(self, ctx, *, char: str):
        """Shows you information about a number of characters."""
        if len(char) > 15:
            return await ctx.send('Too many characters ({}/15)'.format(len(char)))

        fmt = '`\\U{0:>08}`: `\\N{{{1}}}` - `{2}` - <http://www.fileformat.info/info/unicode/char/{0}>'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)

        await ctx.send('\n'.join(map(to_string, char)))

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
                value=f"Member Count: {x.member_count}\nID: {x.id}",
                inline=False,
            )
        await ctx.send(embed=servlist, content=None)

    @commands.command(hidden=True)
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
                max_lines=24,
                substitutions=[lambda s: s.replace("`", "′")],
            )
            p.add_line(f"# -*-*- Source for {command} {object_type}  -*-*-")
            p.disable_truncation()
            for line in code.split("\n"):
                p.add_line(line)
            p.start(ctx)
        except:
            await ctx.send("No source was found...")

    @commands.command(aliases=["uc", "uni"])
    async def uniconvert(self, ctx, *, msg: str):
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
    @commands.cooldown(rate=3, per=1800.0)
    @commands.command(hidden=True, aliases=["pingmachine", "pingspam"], enabled=True)
    @commands.guild_only()
    async def pingstorm(self, ctx, user: discord.Member, amount: int = 5):
        """Ping specified user number of times, 5 if no amount specified, Maximum amount is 200. (Cooldown: 1 use per 60 mins, Use wisely.)"""
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
                        if amount > 200:
                            await ctx.send(
                                "**WARNING:** **Maximum allowed amount is 200.**"
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
    # ~~Scrapped for now until~~ i can figure out how to do the customizeable timezone. EDIT: I DID IT! HURRAHH!
    @commands.command(aliases=["time","date","now"])
    async def clock(self, ctx, location = "UTC"):
        """Show current time. [p]time <timezone>\n for timezone list see: http://tiny.cc/on60iz"""
        time_fmt = "%I:%M:%S %p"
        date_fmt = "%A, %d %B %Y"
        
        try:
            now = datetime.now(timezone(location))

            time = now.strftime(time_fmt)
            date = now.strftime(date_fmt)

            clock = discord.Embed(color=0xC0C0C0)
            clock.add_field(name="🕓 Current Time", value=time, inline=False)
            clock.add_field(name="📆 Current Date", value=date, inline=False)
            clock.add_field(name="🌐 Timezone", value=location, inline=False)
            await ctx.send(embed=clock, content=f"⏰ Tick.. Tock..")
        except:
            await ctx.send(":warning: **Warning!** An Error Occured.\nMake sure that the syntax is correct and i have the permission.\nfor timezone list see: http://tiny.cc/on60iz")


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
    async def gif(self, ctx, *, query):
        """find a gif
        Usage: gif <query>"""
        g = safygiphy.Giphy()
        gif = g.random(tag=query)
        em = discord.Embed()
        em.set_image(url=str(gif.get("data", {}).get("image_original_url")))
        try:
            await ctx.send(embed=em)
        except discord.HTTPException:
            await ctx.send("Unable to send the messages, make sure i have access to embed.")



    @commands.command(aliases=["a2b"])
    async def ascii2bin(self, ctx, *, string):
        """
        Converts the ASCII string to binary.
        Any UTF-8 characters are removed.
        """
        if string == "^":
            prev = await self._get_prev(ctx)
            if not prev:
                return
            else:
                string = prev.content
        return await self._ascii2bin(ctx, string=string)
    @commands.command(aliases=["b2a"])
    async def bin2ascii(self, ctx, *, string):
        """
        Converts the binary string to ASCII.
        """
        if string == "^":
            prev = await self._get_prev(ctx)
            if not prev:
                return
            else:
                string = prev.content
        return await self._bin2ascii(ctx, string=string)
    async def _ascii2bin(self, ctx, *, string):
        string = "".join(c for c in string if 0 <= ord(c) < 0xFFFF)
        if not string:
            return await ctx.send("No valid ASCII characters given.", delete_after=10)
        binaries = [bin(ord(c))[2:11].rjust(8, "0") for c in string]
        await ctx.send(" ".join(binaries).replace("@", "@" + chr(0xFFF0)))
    async def _bin2ascii(self, ctx, *, string):
        string = "".join(c for c in string if c not in " \t\r\n")
        if not all(c in "01" for c in string):
            print(string)
            return await ctx.send("Not binary input...", delete_after=10)
        zeros = math.ceil(len(string) / 8)
        string = string.rjust(zeros, "0")
        chars = []
        for i in range(0, len(string), 8):
            chars.append(chr(int(string[i : i + 8], 2)))
        text = "".join(chars)
        await ctx.send(text)
    async def _get_prev(self, ctx):
        # Get the previous message.
        history = await ctx.channel.history(limit=3).flatten()
        try:
            # Sometimes discord bugs out and sends the message we just sent; other times it wont...
            for i, m in enumerate(list(history)):
                if m.id == ctx.message.id:
                    del history[i]
        except ValueError:
            pass
        if len(history) < 2 or not history[-1].content:
            await ctx.send("I can't seem to find a message...", delete_after=10)
            return None
        else:
            return history[0]

#
#      DISABLED FOR NOW AS THERE IS A BUG.
#
#    @commands.command(brief="Searches the Urban Dictionary for a term",aliases=["ud"], disabled=True)
#    async def urban(self, ctx, *, word: str):
#        "Browse Urban Dictionary."
#        try:
#            defi = urbandict.define(word)
#            definition = defi[0]["def"]
#            example = defi[0]["example"]
#            ud = discord.Embed(title=f":mag: {word}", description=definition, color=0x25332)
#            ud.add_field(name=":bulb: Example", value=example, inline=False)
#            ud.set_footer(
#                text="Urban Dictionary API",
#                icon_url="https://vignette.wikia.nocookie.net/logopedia/images/a/a7/UDAppIcon.jpg/revision/latest?cb=20170422211150",
#            )
#            ud.set_thumbnail(
#                url="https://vignette.wikia.nocookie.net/logopedia/images/a/a7/UDAppIcon.jpg/revision/latest?cb=20170422211150"
#            )
#            await ctx.send(embed=ud, content=None)
#
#        except urllib.error.HTTPError:
#            await ctx.send(
#            embed=discord.Embed(
#                description=f":mag_right: No Definition Found."
#            )
#        )

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

    @commands.command(name="channels", hidden=True)
    @commands.is_owner()
    async def allchannel(self, ctx, serverid: int = None):
        """Shows ALL Channels on the chosen server. Use Wisely!"""
        if serverid is None:
            server = ctx.guild
        else:
            server = discord.utils.get(self.bot.guilds, id=serverid)
            if server is None:
                return await ctx.send("Server not found!")
        
        e = discord.Embed(title=f"**{server.name}**\'s Channel list.")

        voice = ""
        text = ""
        categories = ""

        for channel in server.voice_channels:
            voice += f"\U0001f508 {channel}\n"
        for channel in server.categories:
            categories += f"\U0001f4da {channel}\n"
        for channel in server.text_channels:
            text += f"\U0001f4dd {channel}\n"

        if len(server.text_channels) > 0:
            e.add_field(name="Text Channels", value=f"```{text}```")
        if len(server.categories) > 0:
            e.add_field(name="Categories", value=f"```{categories}```")
        if len(server.voice_channels) > 0:
            e.add_field(name="Voice Channels", value=f"```{voice}```")

        try:
            await ctx.send(embed=e)
        except discord.HTTPException:
            await ctx.send("⚠️ Unable to send the embed. Make sure that you have allowed the Embed Permission! (OR the embed itself is maybe too long to be displayed)")


    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, *, question):
        """Interactively creates a poll with the following question.
        To vote, use reactions!
        """

        # a list of messages to delete when we're all done
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send(f'Say poll option or {ctx.prefix}cancel to publish poll.'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f'{ctx.prefix}cancel'):
                break

            answers.append((to_emoji(i), entry.clean_content))

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass # oh well

        answer = '\n'.join(f'{keycap}: {content}' for keycap, content in answers)
        actual_poll = await ctx.send(f'{ctx.author} asks: {question}\n\n{answer}')
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('Missing the question.')

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: str):
        """Makes a poll quickly.
        The first argument is the question and the rest are the choices.
        """

        if len(questions_and_choices) < 3:
            return await ctx.send('Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 21:
            return await ctx.send('You can only have up to 20 choices.')

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send('Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(to_emoji(e), v) for e, v in enumerate(questions_and_choices[1:])]

        try:
            await ctx.message.delete()
        except:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.send(f'{ctx.author} asks: {question}\n\n{body}')
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.command()
    async def ranint(self, ctx, a: int, b: int):
        """Usage: *ranint [least number][greatest number]. RanDOM!"""
        if a is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        if b is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        else:
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Your randomized number:')
            em.description = random.randint(a,b)
            await ctx.send(embed=em)

    @commands.command()
    async def timer(self, ctx, timer):
        """Counts down till it's over! Usage: *timer [time in secs]"""
        try:
            float(timer)
        except ValueError:
            await ctx.send("UH OH! Timer did not start. Usage: *timer [time in secs]. Make sure the time is a *whole number*.")
        else:
            await ctx.send("Timer started and rolling! :timer:")
            await asyncio.sleep(float(timer))
            await ctx.send("TIME'S UP! :clock:")

def setup(bot):
    bot.add_cog(Utilities(bot))
    print("Utilities Module has been loaded.")