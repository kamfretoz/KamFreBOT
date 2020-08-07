"""
MIT License
Copyright (c) 2018 Koyagami
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
import asyncio
import aiohttp
import data.config as config
import inspect
import re
import unicodedata
import urllib
import time
import random
import math
import io
import functools
import os
import operator
from bs4 import BeautifulSoup
from pytz import timezone
from datetime import datetime
import safygiphy
import urbandict
import pytemperature
import PyDictionary
import qrcode
import requests
from io import BytesIO
from collections import deque
import string
import json

import libneko
from libneko import pag, converters
import discord
from discord.ext import commands

morseAlphabet = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    " ": "/",
    "1" : ".----",
    "2" : "..---",
    "3" : "...--",
    "4" : "....-",
    "5" : ".....",
    "6" : "-....",
    "7" : "--...",
    "8" : "---..",
    "9" : "----.",
    "0" : "-----",
    ".": ".-.-.-",
    ",": "--..--",
    ":": "---...",
    "?": "..--..",
    "'": ".----.",
    "-": "-....-",
    "/": "-..-.",
    "@": ".--.-.",
    "=": "-...-"
}

inverseMorseAlphabet = dict((v, k) for (k, v) in morseAlphabet.items())

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

class DictObject(dict):
    def __getattr__(self, item):
        return self[item]

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
        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            servlist = discord.Embed(title=f"Servers that I am in", description=page, color=0x00FF00)
            servlist.set_footer(text=f"{len(self.bot.guilds)} Servers in total.")
            return servlist
        
        navi = pag.EmbedNavigatorFactory(factory=main_embed)
        servers = ""
        for guild in self.bot.guilds:
                servers += f'{guild.name}\n'

        navi += servers
        navi.start(ctx)
        

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

    # pingstorm command
    @commands.cooldown(rate=2, per=1800.0, type=commands.BucketType.guild)
    @commands.max_concurrency(number=1, per=commands.BucketType.guild, wait=False)
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
                        if amount > 100:
                            await ctx.send(
                                "**WARNING:** **Maximum allowed amount is 100.**"
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
    @commands.group(invoke_without_command=True, aliases=["time","date","now"])
    async def clock(self, ctx, * ,location: str = "UTC"):
        """
        Show current time. [p]time <timezone>
        For timezone list, use [p]clock list
        """

        loc = location.replace(" ", "_")
        time_fmt = "%I:%M:%S %p"
        date_fmt = "%A, %d %B %Y"
        
        try:
            now = datetime.now(timezone(loc))

            time = now.strftime(time_fmt)
            date = now.strftime(date_fmt)

            clock = discord.Embed(color=0xC0C0C0)
            clock.add_field(name="🕓 Current Time", value=time, inline=False)
            clock.add_field(name="📆 Current Date", value=date, inline=False)
            clock.add_field(name="🌐 Timezone", value=loc.title(), inline=False)
            await ctx.send(embed=clock, content=f"⏰ Tick.. Tock..")
        except:
            err = discord.Embed(title="⚠ **Warning!** An Error Occured.", description="Make sure that the timezone format is correct and is also available.\nThe Correct format is for example: `America/New_York` \nFor timezone list, use [p]clock list")
            await ctx.send(embed = err)

    @clock.command(name="list", aliases=["timezone","timezones","lists","tz","tzs"], brief="Vew the list of available timezones")
    async def clock_list(self, ctx):
        """Shows the list of available timezones"""
        @pag.embed_generator(max_chars=2048)
        def emb(paginator, page, page_index):
            embed = discord.Embed(title="🌐 Available Timezones:", description=f"```{page}```")
            return embed

        with open("cogs/data/timezones.txt") as tzs:
            lists = tzs.read()
        
        navi = pag.EmbedNavigatorFactory(factory=emb)
        navi += lists
        navi.start(ctx)


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
    async def gif(self, ctx, *, query: str = "rickroll"):
        """find a gif
        Usage: gif <query>"""
        try:
            g = safygiphy.Giphy()
            gif = g.random(tag=query)
            em = discord.Embed()
            em.set_image(url=str(gif.get("data", {}).get("image_original_url")))
            await ctx.send(embed=em)
        except AttributeError:
            await ctx.send("An Error Occured! Please try again later.")
            return
        except discord.HTTPException:
            await ctx.send("Unable to send the messages, make sure i have access to embed.")
            return

#      DISABLED FOR NOW AS THERE IS A BUG WHERE IT ONLY SHOWS FEW WORDS AT MOST.

    @commands.command(aliases=["ud","urbandict"], disabled=True)
    async def urban(self, ctx, *, word: str = None):
        "Browse Urban Dictionary."
        if word is None:
            await ctx.send(embed=discord.Embed(description="Please specify the word to define!"))
            return

        await ctx.trigger_typing()

        try:
            defi = urbandict.define(word)
            definition = defi[0]["def"]
            example = defi[0]["example"]
            ud = discord.Embed(title=f":mag: {word}", description=f"```{definition}```", color=0x25332)
            ud.add_field(name=":bulb: Example", value=f"```{example}```", inline=False)
            ud.set_footer(
                text="Urban Dictionary API",
                icon_url="https://vignette.wikia.nocookie.net/logopedia/images/a/a7/UDAppIcon.jpg/revision/latest?cb=20170422211150",
            )
            await ctx.send(embed=ud, content=None)

        except urllib.error.HTTPError:
            await ctx.send(
            embed=discord.Embed(
                description=f":mag_right: No Definition Found."
            )
        )

    @commands.command(name="define", aliases=["def","defi"])
    async def _define(self, ctx, *, term: str):
        """Defines a word."""
        formatted = f"**Definition of `{term}`**\n"

        async with ctx.typing():
            definition = self.dictionary.meaning(term)
            if definition is None:
                await ctx.send("⛔ No definition found for that term.")
            else:
                for t in definition:
                    formatted += f"{t}:\n```css\n"
                    for subdef in definition[t]:
                        formatted += f"- {subdef}"
                    formatted += "\n```\n"
                await ctx.send(formatted)

    @commands.command(aliases=["channels","allchannel"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def allchannels(self, ctx):
        """Shows ALL Channels on this server."""
        server = ctx.guild
        #if serverid is None:
        #    server = ctx.guild
        #else:
        #    server = discord.utils.get(self.bot.guilds, id=serverid)
        #    if server is None:
        #        return await ctx.send("Server not found!")
        
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
            loading = await ctx.send(embed=discord.Embed(title="Please Wait..."), delete_after=3)
            everything = f"Text Channels:\n{text}\nCategories:\n{categories}\nVoice Channels:\n{voice}"
            data = BytesIO(everything.encode('utf-8'))
            await ctx.send(content=f"**{ctx.guild.name}'s Channel List**", file=discord.File(data, filename=f"{ctx.guild.name}_Channel_Lists.txt"))
            await loading.delete()

    @commands.command(aliases=["members"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def allmembers(self, ctx):
        """Get all members in this server"""
        bots = ""
        bots_amount = 0
        members = ""
        members_amount = 0
        total = 0
        everything =""

        for x in ctx.guild.members:
            if x.bot is True:
                bots += f"[BOT][{x.id}]\t{x}\n"
                bots_amount += 1
                total += 1
            else:
                members += f"[USER][{x.id}]\t{x}\n"
                members_amount += 1
                total += 1

        loading = await ctx.send(embed=discord.Embed(title="Please Wait..."), delete_after=3)
        everything = f"Member Amount: {members_amount}\nBot Amount: {bots_amount}\nTotal: {total}\n\nMember List:\n{members + bots}"        
        data = BytesIO(everything.encode('utf-8'))
        await ctx.send(content=f"**{ctx.guild.name}'s Member List**", file=discord.File(data, filename=f"{ctx.guild.name}_Member_Lists.txt"))
        await loading.delete()

    @commands.command(aliases=["discriminator","tagnum","tag"])
    @commands.guild_only()
    async def discrim(self, ctx, tag: str = None):
        """Allows you to see whose member has the certain Discriminator/Tag!"""

        if tag is None:
            await ctx.send(embed=discord.Embed(description="⚠ Please enter the desired tag number!"))
            return

        elif len(tag) is not 4 or tag.isdigit() is False:
            await ctx.send(embed=discord.Embed(description="⚠ Please enter the correct format!"))
            return

        else:
        
            member_list = ""
    
            @pag.embed_generator(max_chars=2048)
            def main_embed(paginator, page, page_index):
                emb = discord.Embed(title=f"Users who has Tag Number: #**{tag}**", description = page, color=0x00FF00)
                return emb
    
            page = pag.EmbedNavigatorFactory(factory=main_embed)
            
            duplicates = deque()
            for x in self.bot.get_all_members():
                if x.discriminator == tag:
                    if x.id not in duplicates:
                        duplicates.append(x.id)
                        member_list += f"{str(x)}\n"
                    
            if member_list is not "":
                page += member_list
                page.start(ctx)
            else:
                await ctx.send(embed=discord.Embed(description="ℹ No user found!"))

    @commands.command(aliases=["allrole","roles"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def allroles(self, ctx):
        """Get all roles in current server"""
        allroles = ""
        async with ctx.typing():
            for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
                allroles += f"[{str(num).zfill(2)}] {role.id}\t[ Users: {len(role.members)} ]\t{role.name}\t\r\n"
            try:
                embroles = discord.Embed(title=f"Roles in **{ctx.guild.name}**", description=f"```{allroles}```")
                await ctx.send(embed=embroles)
            except discord.HTTPException:
                loading = await ctx.send(embed=discord.Embed(title="Please Wait..."), delete_after=3)
                data = BytesIO(allroles.encode('utf-8'))
                await ctx.send(content=f"Roles in **{ctx.guild.name}**", file=discord.File(data, filename=f"{ctx.guild.name}_Role_Lists.txt"))
                await loading.delete()

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
            messages.append(await ctx.send(f'Say poll option or type `cancel` to publish poll.'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f'cancel'):
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
    async def randint(self, ctx, a: int, b: int):
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

    @commands.command(aliases=["cd","timer"])
    @commands.cooldown(rate=2, per=600, type=commands.BucketType.guild)
    @commands.max_concurrency(number=1, per=commands.BucketType.guild, wait=False)
    async def countdown(self, ctx, timer: int = None):
        """Create a timer with the given time."""
        if timer is None:
            await ctx.send(
                embed=discord.Embed(
                    description=":watch: Please enter the time!",
                    color=discord.Colour.red(),
                )
            )
        else:
            if timer <= 0:
                await ctx.send(
                    embed=discord.Embed(
                        description=":octagonal_sign: That's not a valid time!",
                        color=discord.Colour.red(),
                    )
                )
            elif timer > 1000:
                await ctx.send(
                    embed=discord.Embed(
                        description=":octagonal_sign: That time is too big! It must be between 1 and 1000",
                        color=discord.Colour.red(),
                    )
                )
            else:
                msg = await ctx.send(
                    embed=discord.Embed(
                        description="**Starting countdown!**",
                        color=discord.Colour.orange(),
                    )
                )
                loop = ctx.bot.loop
                await asyncio.sleep(0.5)
                stop = "\N{BLACK SQUARE FOR STOP}"
                await msg.add_reaction(stop)
                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add",
                        timeout=timer + 2,
                        check=lambda r, u: u == ctx.author and r.emoji in (stop),
                    )
                except asyncio.TimeoutError:
                    pass
                finally:
                    await msg.delete()
                for t in range(timer, 0, -1):
                    mins, secs = divmod(t, 60)
                    ctx.bot.loop.create_task(
                        msg.edit(
                            embed=discord.Embed(
                                description=f"**{mins:,}:{secs:02}**",
                                color=discord.Colour.orange(),
                            )
                        )
                    )
                    await asyncio.sleep(1)
                await msg.edit(
                    embed=discord.Embed(
                        description=":watch::exclamation: Time's up!",
                        color=discord.Colour.red(),
                    )
                )
                ping = await ctx.send(ctx.author.mention)
                await ping.delete()

    @commands.command(aliases=["qr"])
    async def qrmaker(self, ctx, *, data: str):
        """Allows you to make a custom QR Code"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qrcodes/QR.png")
        await ctx.send(f"{ctx.author.mention}", file=discord.File("qrcodes/QR.png"))
        os.remove("qrcodes/QR.png") #Feel free to disable the removal

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(create_instant_invite=True)
    async def qrinvite(self, ctx, age: int = 86400, uses: int = 0, temp: bool = False):
        """
        Allows you to create a QR Code of the invite link of this server
        Make sure to adjust the available options to suite your need!
        Set the `age` (defaults to 1 day) and `uses` argument to 0 to make a permanent link
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )

        link = await ctx.channel.create_invite(max_age = age, max_uses = uses, temporary = temp)
        qr.add_data(link)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qrcodes/QR.png")
        await ctx.send(f"{ctx.author.mention}", file=discord.File("qrcodes/QR.png"))
        os.remove("qrcodes/QR.png") #Feel free to disable the removal


    @commands.command(aliases=["whoisplaying"])
    @commands.guild_only()
    async def whosplaying(self, ctx, *, game: str):
        """Shows who's playing a specific game"""
        if len(game) <= 1:
            await ctx.send("```The game should be at least 2 characters long...```", delete_after=5.0)
            return

        guild = ctx.message.guild
        members = guild.members
        playing_game = ""
        count_playing = 0

        for member in members:
            if not member:
                continue
            if not member.activity or not member.activity.name:
                continue
            if member.bot:
                continue
            if game.lower() in member.activity.name.lower():
                count_playing += 1
                if count_playing <= 15:
                    emote = random.choice(["🌜", "🔆", "🌞", "🌙", "🌛"])
                    playing_game += f"{emote} {member.name}#{member.discriminator} ({member.mention}) ({member.activity.name})\n"

        if playing_game == "":
            await ctx.send("```Search results:\nNo users are currently playing that game.```")
        else:
            msg = playing_game
            if count_playing > 15:
                showing = f"(Showing 15/{count_playing})"
            else:
                showing = f"({count_playing})"

            em = discord.Embed(description=msg, colour=discord.Colour(value=0x36393e))
            em.set_author(name=f"""Who's playing "{game}"? {showing} User(s) in total.""")
            await ctx.send(embed=em)

    @commands.command(aliases=["currentgame"])
    @commands.guild_only()
    async def currentgames(self, ctx):
        """Shows the most played games right now"""
        guild = ctx.message.guild
        members = guild.members

        freq_list = {}
        for member in members:
            if not member:
                continue
            if not member.activity or not member.activity.name:
                continue
            if member.bot:
                continue
            if member.activity.name not in freq_list:
                freq_list[member.activity.name] = 0
            freq_list[member.activity.name] += 1

        sorted_list = sorted(freq_list.items(),
                             key=operator.itemgetter(1),
                             reverse=True)

        if not freq_list:
            await ctx.send("```Search results:\nNo users are currently playing any games. Odd...```")
        else:
            # Create display and embed
            msg = ""
            max_games = min(len(sorted_list), 10)

            em = discord.Embed(description=msg, colour=discord.Colour(value=0x36393e))
            for i in range(max_games):
                game, freq = sorted_list[i]
                if int(freq_list[game]) < 2:
                    amount = "1 person"
                else:
                    amount = f"{int(freq_list[game])} people"
                em.add_field(name=game, value=amount)
            em.set_thumbnail(url=guild.icon_url)
            em.set_footer(text="Do [p]whosplaying <game> to see whos playing a specific game")
            em.set_author(name="Top games being played right now in the server:")
            await ctx.send(embed=em)

    @commands.command(aliases=['drunkify'])
    async def mock(self, ctx, *, txt):
        lst = [str.upper, str.lower]
        newText = await commands.clean_content().convert(ctx, ''.join(random.choice(lst)(c) for c in txt))
        if len(newText) <= 512:
            await ctx.send(newText)
        else:
            try:
                await ctx.author.send(newText)
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command()
    async def expand(self, ctx,  num: int, *, txt: commands.clean_content):
        spacing = ""
        if num > 0 and num <= 5:
            for _ in range(num):
                spacing+=" "
            result = spacing.join(txt)
            if len(result) <= 200:
                await ctx.send(result)
            else:
                try:
                    await ctx.author.send(result)
                    await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
                except Exception:
                    await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")
        else:
            await ctx.send("```fix\nError: The number can only be from 1 to 5```")

    @commands.command()
    async def reverse(self, ctx, *, txt: commands.clean_content):
        result = await commands.clean_content().convert(ctx, txt[::-1])
        if len(result) <= 350:
            await ctx.send(f"{result}")
        else:
            try:
                await ctx.author.send(f"{result}")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["ascii2hex"])
    async def texttohex(self, ctx, *, txt):
        try:
            hexoutput = await commands.clean_content().convert(ctx, (" ".join("{:02x}".format(ord(c)) for c in txt)))
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/hexadecimal/#data**")
        if len(hexoutput) <= 479:
            await ctx.send(f"```fix\n{hexoutput}```")
        else:
            try:
                await ctx.author.send(f"```fix\n{hexoutput}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["hex2ascii"])
    async def hextotext(self, ctx, *, txt: str):
        try:
            cleanS = await commands.clean_content().convert(ctx, bytearray.fromhex(txt).decode())
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/hexadecimal/#data**")
        if len(cleanS) <= 479:
            await ctx.send(f"```{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```{cleanS}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["ascii2bin"])
    async def texttobinary(self, ctx, *, txt: str):
        try:
            cleanS = await commands.clean_content().convert(ctx, ' '.join(format(ord(x), 'b') for x in txt))
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data**")
        if len(cleanS) <= 479:
            await ctx.send(f"```fix\n{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```fix\n{cleanS}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["bin2ascii"])
    async def binarytotext(self, ctx, *, txt: str):
        try:
            cleanS = await commands.clean_content().convert(ctx, ''.join([chr(int(txt, 2)) for txt in txt.split()]))
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data**")
        if len(cleanS) <= 479:
            await ctx.send(f"```{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```{cleanS}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command()
    @commands.is_owner()
    async def nickscan(self, ctx):
        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            embed = discord.Embed(title=f'Servers I Have Nicknames In', description=page)
            return embed

        nicks = pag.EmbedNavigatorFactory(factory=main_embed)

        message = ""
        for guild in self.bot.guilds:
            if guild.me.nick != None:
                message += f'{guild.name} | {guild.me.nick}\n'
                
        nicks += message
        nicks.start(ctx)


    @commands.command(aliases=["ipinfo","ipaddr"])
    async def ip(self, ctx, ip: str = None):
        """
        Find out the information of an IP Address
        API Provided by: https://ipapi.co/
        """
        if ip is None:
            await ctx.send(embed=discord.Embed(description="⚠ Please Specify the IP Address!"))
            return

        if ip == "0.0.0.0" or ip == "127.0.0.1":
            await ctx.send(embed=discord.Embed(description="You have played yourself. Wait... You can't!"))
            return

        await ctx.trigger_typing()

        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://ipapi.co/{ip}/json/') as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    await session.close()

            ipaddr = data["ip"]
            city = data["city"]
            region = data["region"]
            region_code = data["region_code"]
            country = data["country"]
            country_name = data["country_name"]
            country_code_iso3 = data["country_code_iso3"]
            continent_code = data["continent_code"]
            in_eu = data["in_eu"]
            postal = data["postal"]
            latitude = data["latitude"]
            longitude = data["longitude"]
            country_timezone = data["timezone"]
            utc_offset = data["utc_offset"]
            dial_code = data["country_calling_code"]
            currency = data["currency"]
            languages = data["languages"]
            organization = data["org"]
            asn = data["asn"]

            embd = discord.Embed(title="IP Information", color=ctx.author.color, timestamp=datetime.utcnow())
            embd.add_field(name="IP Address:", value=ipaddr, inline=False)
            embd.add_field(name="ISP Name/Organization:", value=organization, inline=False)
            embd.add_field(name="City:", value=city, inline=False)
            embd.add_field(name="Regional Area:", value=region)
            embd.add_field(name="Region Code:", value=region_code, inline=False)
            embd.add_field(name="Country:", value=country, inline=False)
            embd.add_field(name="Country Name:", value=country_name, inline=False)
            embd.add_field(name="Country Code (ISO):", value=country_code_iso3, inline=False)
            embd.add_field(name="Language Spoken:", value=languages, inline=False)
            embd.add_field(name="Continent Code:", value=continent_code, inline=False)
            embd.add_field(name="Is country a member of European Union (EU)?", value=in_eu, inline=False)
            embd.add_field(name="Postal Code:", value=postal, inline=False)
            embd.add_field(name="Latitude Coordinate:", value=latitude, inline=False)
            embd.add_field(name="Longitude Coordinate:", value=longitude, inline=False)
            embd.add_field(name="Timezone:", value=country_timezone, inline=False)
            embd.add_field(name="UTC Offset:", value=utc_offset, inline=False)
            embd.add_field(name="Country Dial Code:", value=dial_code, inline=False)
            embd.add_field(name="Currency:", value=currency, inline=False)
            embd.add_field(name="Autonomous System Number:", value=asn, inline=False)
            embd.set_footer(text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

            await ctx.send(embed=embd)
        except:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured! Make sure the IP and the formatting are correct!"))
        finally:
            await session.close()

    @commands.group(invoke_without_command=True, aliases=["mrs"])
    async def morse(self, ctx):
        """
        Converts ASCII Characters to Morse code and Vice Versa.
        """
        mainemb = discord.Embed(description="This command can help you translate morse codes.\nHere are the available command:")
        mainemb.add_field(name="ASCII to Morse conversion", value="`[p]morse a2m [text]`")
        mainemb.add_field(name="Morse to ASCII conversion", value="`[p]morse m2a [text]`")
        await ctx.send(embed=mainemb)

    @morse.command(name="m2a", brief = "Convert Morse code to ASCII", aliases=["morse2ascii"])
    async def morse2ascii(self, ctx, * , text:str = None):
        if text is None:
            await ctx.send(embed=discord.Embed(description="⚠ Please specify the input."))
            return

        messageSeparated = text.split(' ')
        decodeMessage = ''
        for char in messageSeparated:
            if char in inverseMorseAlphabet:
                decodeMessage += inverseMorseAlphabet[char]
            else:
                # CNF = Character not found
                decodeMessage += '<CHARACTER NOT FOUND>'
        await ctx.send(embed=discord.Embed(title="Morse to ASCII Conversion:", description=decodeMessage, timestamp=datetime.utcnow()))

    @morse.command(name="a2m", brief = "Convert ASCII into Morse Code", aliases=["ascii2morse"])
    async def ascii2morse(self, ctx, * ,text: str = None):
        if text is None:
            await ctx.send(embed=discord.Embed(description="⚠ Please specify the input."))
            return

        encodedMessage = ""
        for char in text[:]:
            if char.upper() in morseAlphabet:
                encodedMessage += morseAlphabet[char.upper()] + " "
            else:
                encodedMessage += '<CHARACTER NOT FOUND>'
        await ctx.send(embed=discord.Embed(title="ASCII to Morse Conversion:", description=encodedMessage, timestamp=datetime.utcnow()))

    @commands.command(aliases=["nationalize"])
    async def nationality(self, ctx, * ,name: str = None):
        """
        This command predicts the nationality of a person given their name.
        API Provided by: `https://nationalize.io/`
        """
        await ctx.trigger_typing()

        fin_name = name.replace(" ","+")

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.nationalize.io/?name={fin_name}') as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                await session.close()
        try:
            answer = data["name"]
            country = data.country[0].country_id
            probability = data.country[0].probability
        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured! Cannot determine the result."))
            return
        finally:
            await session.close()


        emb = discord.Embed(description="Predict the nationality of a name!", color = ctx.author.color, timestamp = datetime.utcnow())
        emb.add_field(name="Name", value=answer.title())
        emb.add_field(name="Country", value=country)
        emb.add_field(name="Probability", value=probability)
        emb.set_footer(text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=emb)

    @commands.command()
    async def weather(self, ctx, *, city: str = None):
        """
        A command to check weather status
        API Provided by: OpenWeatherMap
        """

        if city is None:
            await ctx.send(embed=discord.Embed(description="Please provide the city name!"))
            return

        await ctx.trigger_typing()

        with open("cogs/data/weather_api_key.json") as json_fp:
            classified = json.load(json_fp)
            key = classified["key"]

        locate = city.replace(" ", "+")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://api.openweathermap.org/data/2.5/weather?q={locate}&appid={key}") as resp:
                    resp.raise_for_status()
                    data = json.loads(await resp.read(), object_hook=DictObject)
                    await session.close()

            cityname = data.name
            countryid = data.sys.country
            status = data.weather[0].main
            description = data.weather[0].description
            lon = data.coord.lon
            lat = data.coord.lat
            temp = int(pytemperature.k2c(data.main.temp))
            feels = int(pytemperature.k2c(data.main.feels_like))
            t_min = int(pytemperature.k2c(data.main.temp_min))
            t_max = int(pytemperature.k2c(data.main.temp_max))
            pressure = data.main.pressure
            humidity = data.main.humidity
            vis = data.visibility
            wind = data.wind.speed
            wind_degree = data.wind.deg
            icon = f"http://openweathermap.org/img/wn/{data.weather[0].icon}@2x.png"
        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured while parsing the data."))
            return
        except KeyError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured while parsing the data."))
            return
        except aiohttp.client_exceptions.ClientResponseError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured! That City cannot be found."))
            return
        finally:
            await session.close()

        embed = discord.Embed(title="Weather Information", timestamp=datetime.utcnow(), color=ctx.author.color)
        embed.set_thumbnail(url=icon)

        embed.add_field(name="City Name", value=cityname, inline=False)
        embed.add_field(name="Country ID", value=countryid, inline=False)
        embed.add_field(name="Weather Status", value=status, inline=False)
        embed.add_field(name="Description", value=description.title(), inline=False)
        embed.add_field(name="Longitude", value=lon, inline=True)
        embed.add_field(name="Latitude", value=lat, inline=True)
        embed.add_field(name="Temperature", value=f"{temp}°C", inline=True)
        embed.add_field(name="Feels Like", value=f"{feels}°C", inline=True)
        embed.add_field(name="Min Temperature", value=f"{t_min}°C", inline=True)
        embed.add_field(name="Max Temperature", value=f"{t_max}°C", inline=True)
        embed.add_field(name="Pressure", value=f"{pressure} atm", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Visibility", value=f"{vis} m", inline=True)
        embed.add_field(name="Wind", value=f"{wind} m/sec", inline=True)
        embed.add_field(name="Wind Direction", value=f"{wind_degree}°", inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utilities(bot))
    print("Utilities Module has been loaded.")