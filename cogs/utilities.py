import asyncio
import inspect
import unicodedata
import time
import random
import io
from math import floor, sqrt, trunc
from PIL import Image
import os
from operator import pow, truediv, mul, add, sub, itemgetter
import pytz
from pytz import timezone
from datetime import datetime
import safygiphy
import pytemperature
import qrcode
from io import BytesIO
from collections import deque
from re import match
import json
import base64
import ciso8601
import urllib
import textwrap

import libneko
from libneko import pag, converters
import discord
from discord.ext import commands

from modules.http import HttpCogBase
from modules.dictobj import DictObject
from utils.time import format_seconds

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
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
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

# To retrieve KSoft.Si API KEY
with open("cogs/data/ksoft-api_key.json") as json_fp:
    classified = json.load(json_fp)
    ksoft_key = classified["key"]


class Utilities(HttpCogBase):
    def __init__(self, bot):
        self.bot = bot
        self.pingeries = {}
        self.lock = asyncio.Lock()
        self.delsniped = {}
        self.editsniped = {}
        self.loop = asyncio.get_event_loop()

    # Delete Snipe Listener (Setter)
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            if not message.author.bot:
                srvid = message.guild.id
                chid = message.channel.id
                author_mention = message.author.mention
                author = message.author
                content = message.content

                try:
                    attachment_name = message.attachments[0].filename
                    file_attachment = message.attachments[0].proxy_url
                    # print(f"attachment: {file_attachment}")
                except IndexError:
                    # print("No Attachment")
                    file_attachment = None
                    attachment_name = None
                # Log Stuff
                # print(f"server:{srvid}, channel:{chid}, author:{author}, content:{content}") #PRINTS ALL DELETED MESSAGES INTO THE CONSOLE (CAN BE SPAMMY)

                self.delsniped.update({
                    srvid: {
                        chid: {
                            'Sender': author,
                            'Mention': author_mention,
                            'Content': content,
                            'Attachment': file_attachment,
                            'Filename': attachment_name
                        }
                    }
                })
        except:
            pass

    # Edit Snipe Listener (Setter)
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            if not before.author.bot:
                srvid = before.guild.id
                chid = before.channel.id
                author = before.author
                author_mention = before.author.mention
                msg_before = before.content
                msg_after = after.content
                # Log Stuff
                #print(f"server:{srvid}, channel:{chid}, author:{author}, before:{msg_before}, after:{msg_after}")
                self.editsniped.update({
                    srvid: {
                        chid: {
                            'Sender': author,
                            'Mention': author_mention,
                            'Before': msg_before,
                            'After': msg_after
                        }
                    }
                })
        except:
            pass

    @commands.command(aliases=["sniped", "snipe", "delsnipe", "dsnipe", "ds", "sn", "s"])
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    @commands.guild_only()
    async def deletesnipe(self, ctx):
        """
        Allows you to see recently deleted message in the current channel.
        But you need to be quick because the deleted message won't last long!
        Please do not spam this command!
        """
        try:
            author = self.delsniped[ctx.guild.id][ctx.channel.id]["Sender"]
            author_mention = self.delsniped[ctx.guild.id][ctx.channel.id]["Mention"]
            msg = self.delsniped[ctx.guild.id][ctx.channel.id]["Content"]
            attachment = self.delsniped[ctx.guild.id][ctx.channel.id]["Attachment"]
            name = self.delsniped[ctx.guild.id][ctx.channel.id]["Filename"]

            if msg:
                await ctx.message.delete()
                emb = discord.Embed(description=f"{msg}")
                emb.set_author(name="Sniped!", icon_url=author.avatar_url)
                emb.add_field(name="Author:",value=author_mention, inline=False)
                emb.set_footer(
                    text=f"Sniped by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
                if attachment:
                    emb.add_field(name="Attachments",value=f"[{name}]({attachment})")
                    if str(name).endswith(".png") or str(name).endswith(".gif") or str(name).endswith(".jpg") or str(name).endswith(".jpeg"):
                        emb.set_image(url=attachment)
                await ctx.send(embed=emb, delete_after=5)
            else:
                await ctx.message.delete()
                emb = discord.Embed(title="Sniped!")
                emb.add_field(name="Author:", value=author, inline=False)
                emb.add_field(name="Message:",value="Empty Message.", inline=False)
                emb.set_footer(
                    text=f"Sniped by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
                if attachment:
                    emb.add_field(name="Attachments",value=f"[{name}]({attachment})", inline=False)
                    if str(name).endswith(".png") or str(name).endswith(".gif"):
                        emb.set_image(url=attachment)
                await ctx.send(embed=emb, delete_after=5)
            try:
                self.delsniped.popitem()
            except:
                pass
        except KeyError:
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(description="⚠ No Message found! Perhaps you're too slow?"), delete_after=3)
            return
        except discord.NotFound:
            pass

    @commands.command(aliases=["esnipe", "esniped", "es", "e"])
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    @commands.guild_only()
    async def editsnipe(self, ctx):
        """
        Similar to deletesnipe, this command allows you to see edited message.
        Please do not spam this command as well!
        """
        try:
            author = self.editsniped[ctx.guild.id][ctx.channel.id]["Sender"]
            author_mention = self.editsniped[ctx.guild.id][ctx.channel.id]["Mention"]
            before = self.editsniped[ctx.guild.id][ctx.channel.id]["Before"]
            after = self.editsniped[ctx.guild.id][ctx.channel.id]["After"]

            if before and after:
                await ctx.message.delete()
                emb = discord.Embed()
                emb.set_author(name="Sniped!", icon_url=author.avatar_url)
                emb.add_field(name="Author:",value=author_mention, inline=False)
                emb.add_field(name="Before:", value=before)
                emb.add_field(name="After:", value=after)
                emb.set_footer(
                    text=f"Sniped by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=emb, delete_after=5)
                self.editsniped.popitem()
            else:
                await ctx.message.delete()
                emb = discord.Embed(title="Sniped!")
                emb.add_field(name="Author:", value=author, inline=False)
                emb.add_field(name="Before:", value="Empty Message.")
                emb.add_field(name="After:", value="Empty Message.")
                emb.set_footer(
                    text=f"Sniped by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=emb, delete_after=5)
                self.editsniped.popitem()
        except KeyError:
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(description="⚠ No Message found! Perhaps you're too slow?"), delete_after=3)
            return
        except discord.NotFound:
            pass

    @commands.command(aliases=["code"])
    async def codeblock(self, ctx, *, msg="I am Codeblock!"):
        """Write text in code format."""
        await ctx.message.delete()
        await ctx.reply("```" + msg.replace("`", "") + "```")

    @commands.command(aliases=["char"])
    async def charinfo(self, ctx, *, char: str):
        """Shows you information about a number of characters."""
        if len(char) > 15:
            return await ctx.reply(f'Too many characters ({len(char)}/15)')

        fmt = '`\\U{0:>08}`: `\\N{{{1}}}` - `{2}` -  http://www.fileformat.info/info/unicode/char/{0}'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)

        await ctx.reply('\n'.join(map(to_string, char)))

    @commands.command(aliases=["source", "rtfc"])
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
            await ctx.reply("No source was found...")

    @commands.command(aliases=["uc", "uni"])
    async def uniconvert(self, ctx, *, msg: str):
        """Convert to unicode emoji if possible. Ex: [p]uni :eyes:"""
        await ctx.reply("`" + msg.replace("`", "") + "`")

    # pingstorm command
    @commands.cooldown(rate=2, per=1800.0, type=commands.BucketType.guild)
    @commands.max_concurrency(number=1, per=commands.BucketType.guild, wait=False)
    @commands.command(hidden=True, aliases=["pingmachine", "pingspam","spamping"])
    @commands.guild_only()
    async def pingstorm(self, ctx, user: libneko.converters.InsensitiveMemberConverter, amount: int = 5):
        """Ping specified user number of times, 5 if no amount specified, Maximum amount is 200. (Cooldown: 1 use per 60 mins, Use wisely.)"""
        if user == ctx.bot.user:
            await ctx.reply("HA! You think it'll work against me?? Nice Try.")
            user = ctx.message.author
            await asyncio.sleep(2)

        if not self.lock.locked():
            async with self.lock:
                await ctx.send("Ping Machine Initializing in 3 seconds!")                
                await asyncio.sleep(3)
                await ctx.send("Begin!")

                async def ping_task(self):
                    ping = 0
                    while ping < int(amount):
                        if amount > 200:
                            await ctx.reply(
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
            
    @commands.command(hidden=True, aliases=["stopping"])
    @commands.guild_only()
    async def pingstop(self, ctx, user: libneko.converters.InsensitiveMemberConverter):
        pinged = self.pingeries.get(f"{user.id}@{ctx.guild.id}")
        if pinged is None:
            return await ctx.reply(
                embed=discord.Embed(
                    description=f"{user.mention} is not being pinged!",
                    color=discord.Colour.red(),
                )
            )
        await ctx.reply(f"Stopping the pings for {user.mention} on {ctx.guild.name}")
        del self.pingeries[f"{user.id}@{ctx.guild.id}"]
        
        

    # Betterping command
    @commands.command(aliases=["pong"])
    async def ping(self, ctx):
        """Check current connection status."""
        start = time.monotonic()

        if ctx.invoked_with == "ping":
            msg = await ctx.reply(f":ping_pong: Pong!")
        else:
            msg = await ctx.reply(f":ping_pong: Ping!")

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
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @commands.group(invoke_without_command=True, aliases=["time", "date", "now"])
    async def clock(self, ctx, *, location: str = "UTC"):
        """
        Show current time. [p]time <timezone>
        For timezone list, use [p]clock list
        """

        loc = location.replace(" ", "_")
        if "/" not in loc:
            loc = "_".join([word.capitalize() for word in loc.split("_")])
            for x in pytz.all_timezones:
                if loc == x.split("/")[-1]:
                    loc = x
                    break

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
            await ctx.reply(embed=clock, content=f"⏰ Tick.. Tock..")
        except:
            err = discord.Embed(title="⚠ **Warning!** An Error Occured.",
                                description="""Make sure that the timezone format is correct and is also available.
                                            Take the following examples for formatting: `New York`, `America/New_York` 
                                            For timezone list, use [p]clock list""")
            await ctx.reply(embed=err)

    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    @clock.command(name="list", aliases=["timezone", "timezones", "lists", "tz", "tzs"], brief="Vew the list of available timezones")
    async def clock_list(self, ctx):
        """Shows the list of available timezones"""
        @pag.embed_generator(max_chars=2048)
        def emb(paginator, page, page_index):
            embed = discord.Embed(
                title="🌐 Available Timezones:", description=f"```{page}```")
            return embed

        with open("cogs/data/timezones.txt") as tzs:
            lists = tzs.read()

        navi = pag.EmbedNavigatorFactory(factory=emb)
        navi += lists
        navi.start(ctx)

    @commands.command()
    async def pick(self, ctx, *options: converters.clean_content):
        """
        Picks between multiple options!
        Options are separated by spaces; to include spaces in an option,
        you should put quotes around the option.
        """
        if not options or len(options) == 1:
            await ctx.reply("Provide two or more options")
        else:
            await ctx.reply(f"I pick **{random.choice(options)}**!")

    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    @commands.command()
    async def gif(self, ctx, *, query: str = "rickroll"):
        """find a gif
        Usage: gif <query>"""
        await ctx.trigger_typing()
        try:
            g = safygiphy.Giphy()
            gif = g.search(tag=query)
            em = discord.Embed()
            em.set_image(
                url=str(gif.get("data", {}).get("image_original_url")))
            await ctx.reply(embed=em)
        except AttributeError:
            await ctx.reply("An Error Occured! Please try again later.")
            return
        except discord.HTTPException:
            await ctx.reply("Unable to send the messages, make sure i have access to embed.")
            return

    # https://levelup.gitconnected.com/3-ways-to-write-a-calculator-in-python-61642f2e4a9a
    @commands.command(aliases=["math"])
    async def calc(self, ctx, *, calculation):
        """Simple calculator. Ex: [p]calc 2+2"""
        calculation.strip()
        
        operators = {
            '+': add,
            '-': sub,
            '*': mul,
            '/': truediv,
            '^': pow
        }

        def calculate(s):
            if s.isdigit():
                return float(s)
            for c in operators.keys():
                left, operator, right = s.partition(c)
                if operator in operators:
                    return operators[operator](calculate(left), calculate(right))

        em = discord.Embed(color=0xD3D3D3, title="Calculator")
        try:
            em.add_field(name="Input:", value=calculation, inline=False,)
            em.add_field(name="Output:", value=str(calculate(calculation.replace(
                "**", "^").replace("x", "*").replace(" ", "").strip())), inline=False)
        except Exception as e:
            return await ctx.reply(embed=discord.Embed(description=f"An Error Occured! **{e}**"))
        await ctx.reply(content=None, embed=em)
        await ctx.message.delete()

    @commands.command(name="sqrt", aliases=["squareroot"])
    async def sqroot(self, ctx, x: float):
        """Calculate the squareroot of a given number"""
        try:
            out = sqrt(x)
        except Exception as e:
            return await ctx.reply(embed=discord.Embed(description=f"An Error Occured! **{e}**"))

        em = discord.Embed(color=0xD3D3D3, title="Square Root (√)")
        em.add_field(name="Input:", value=f"√{x}", inline=False,)
        em.add_field(name="Output:", value=out, inline=False)
        await ctx.reply(content=None, embed=em)
        try:
            await ctx.message.delete()
        except:
            pass

    @commands.command(aliases=["msgdump"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def messagedump(self, ctx, filename, limit: int = 50, details="yes", reverse="yes"):
        """Dump messages into a text file."""
        await ctx.reply("Now downloading messages...")
        if not os.path.isdir("data/message_dump"):
            os.mkdir("data/message_dump")
            
        with open("data/message_dump/" + filename.rsplit(".", 1)[0] + ".txt","w+",encoding="utf-8",) as f:
            if reverse == "yes":
                if details == "yes":
                    async for message in ctx.message.channel.history(limit=limit):
                        f.write(
                            "<{} at {} on {}> {}\n".format(
                                message.author.name,
                                message.created_at.strftime("%d %b %Y"),
                                message.created_at.strftime("%H:%M:%S"),
                                message.content,
                            )
                        )

                else:
                    async for message in ctx.message.channel.history(limit=int(limit)):
                        f.write(message.content + "\n")
            else:
                if details == "yes":
                    async for message in ctx.message.channel.history(
                        limit=int(limit), oldest_first=True
                    ):
                        f.write(
                            "<{} at {} on {}> {}\n".format(
                                message.author.name,
                                message.created_at.strftime("%d %b %Y"),
                                message.created_at.strftime("%H:%M:%S"),
                                message.content,
                            )
                        )

                else:
                    async for message in ctx.message.channel.history(
                        limit=int(limit), oldest_first=True
                    ):
                        f.write(message.content + "\n")
                        
        await ctx.reply("Finished downloading!")
        
        with open("data/message_dump/" + filename.rsplit(".", 1)[0] + ".txt","r",encoding="utf-8",) as dump:
            await ctx.reply(file=discord.File(dump), content="Here is the message dump.")

    @commands.cooldown(rate=2, per=3, type=commands.BucketType.user)
    @commands.command(aliases=["getcolor", "colour", "getcolour"])
    async def color(self, ctx, *, colour_codes: str):
        """Posts color of given hex"""
        colour_codes = colour_codes.split()
        size = (60, 80) if len(colour_codes) > 1 else (200, 200)
        if len(colour_codes) > 5:
            return await ctx.reply("Sorry, 5 colour codes maximum")
        for colour_code in colour_codes:
            if not colour_code.startswith("#"):
                colour_code = "#" + colour_code
            image = Image.new("RGB", size, colour_code)
            with io.BytesIO() as file:
                image.save(file, "PNG")
                file.seek(0)
                await ctx.reply(
                    f"Colour with hex code `{colour_code}`:",
                    file=discord.File(file, "colour_file.png"),
                )

    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    @commands.command(aliases=["channels", "allchannel"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def allchannels(self, ctx):
        """
        Shows ALL Channels on this server.
        Can only be used by server owner.
        """
        if ctx.author == ctx.guild.owner:
            server = ctx.guild
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
                await ctx.reply(embed=e)
            except discord.HTTPException:
                loading = await ctx.reply(embed=discord.Embed(title="Please Wait..."), delete_after=3)
                everything = f"Text Channels:\n{text}\nCategories:\n{categories}\nVoice Channels:\n{voice}"
                data = BytesIO(everything.encode('utf-8'))
                await ctx.reply(content=f"**{ctx.guild.name}'s Channel List**", file=discord.File(data, filename=f"{ctx.guild.name}_Channel_Lists.txt"))
                await loading.delete()

    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    @commands.command(aliases=["members"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def allmembers(self, ctx):
        """
        Get all members on the current server
        Can only be used by server owner.
        """
        if ctx.author == ctx.guild.owner:
            server = ctx.guild
            bots = ""
            bots_amount = 0
            members = ""
            members_amount = 0
            total = 0
            everything = ""

            for x in server.members:
                if x.bot is True:
                    bots += f"[BOT][{x.id}]\t{x}\n"
                    bots_amount += 1
                    total += 1
                else:
                    members += f"[USER][{x.id}]\t{x}\n"
                    members_amount += 1
                    total += 1

            loading = await ctx.reply(embed=discord.Embed(title="⌛ Please Wait..."), delete_after=3)
            everything = f"Server: {server.name}\nServer ID: {server.id}\nMember Amount: {members_amount}\nBot Amount: {bots_amount}\nTotal: {total}\n\nMember List:\n{members + bots}"
            data = BytesIO(everything.encode('utf-8'))
            await ctx.reply(content=f"**{server.name}'s Member List**", file=discord.File(data, filename=f"{server.name}_Member_Lists.txt"))
            await loading.delete()

    @commands.cooldown(rate=1, per=600, type=commands.BucketType.guild)
    @commands.command(aliases=["allrole", "roles"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def allroles(self, ctx):
        """
        Get all roles in current server
        Can only be used by server owner.
        """
        if ctx.author == ctx.guild.owner:
            allroles = ""
            server = ctx.guild
            async with ctx.typing():
                for num, role in enumerate(sorted(server.roles, reverse=True), start=1):
                    allroles += f"[{str(num).zfill(2)}] {role.id}\t[ Users: {len(role.members)} ]\t{role.name}\t\r\n"
                data = BytesIO(allroles.encode('utf-8'))
                await ctx.reply(content=f"Roles in **{server.name}**", file=discord.File(data, filename=f"{server.name}_Role_Lists.txt"))

    @commands.command(aliases=["discriminator", "tagnum", "tags"])
    @commands.guild_only()
    async def discrim(self, ctx, tag: str = None):
        """Allows you to see whose user has the certain Discriminator/Tag!"""

        if tag is None:
            await ctx.reply(embed=discord.Embed(description="⚠ Please enter the desired tag number!"))
            return

        elif len(tag) > 4 or tag.isdigit() is False:
            await ctx.reply(embed=discord.Embed(description="⚠ Please enter the correct format!"))
            return

        else:
            member_list = []

            @pag.embed_generator(max_chars=2048)
            def main_embed(paginator, page, page_index):
                emb = discord.Embed(
                    title=f"Users who has Tag Number: #**{tag}**", description=page, color=0x00FF00)
                return emb

            page = pag.EmbedNavigatorFactory(factory=main_embed)

            duplicates = deque()
            for x in self.bot.get_all_members():
                if x.discriminator == tag:
                    if x.id not in duplicates:
                        duplicates.append(x.id)
                        member_list.append(str(x))

            if member_list:
                page += "\n".join(member_list)
                page.start(ctx)
            else:
                await ctx.reply(embed=discord.Embed(description="ℹ No user found!"))

    @commands.cooldown(rate=2, per=3, type=commands.BucketType.user)
    @commands.has_permissions(add_reactions=True)
    @commands.command()
    async def poll(self, ctx, *, opt: commands.clean_content):
        """Create a poll using reactions. [p]help poll for more information.
        [p]poll <question> | <answer> | <answer> - Create a poll. You may use as many answers as you want, placing a pipe | symbol in between them.
        Example:
        [p]poll What is your favorite anime? | Steins;Gate | Naruto | Attack on Titan | Shrek
        You can also use the "time" flag to set the amount of time in seconds the poll will last for.
        Example:
        [p]poll What time is it? | HAMMER TIME! | SHOWTIME! | time=15
        """
        await ctx.message.delete()
        options = opt.split(" | ")
        time = [x for x in options if x.startswith("time=")]
        if time:
            time = time[0]
        if time:
            options.remove(time)
        if len(options) <= 1:
            return await ctx.reply("You must have 2 options or more.")
        if len(options) >= 11:
            return await ctx.reply("You must have 9 options or less.")
        if time:
            time = int(time.strip("time="))
        else:
            time = 30
        emoji = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
        to_react = []
        confirmation_msg = "**{}?**:\n\n".format(options[0].rstrip("?"))
        for idx, option in enumerate(options[1:]):
            confirmation_msg += "{} - {}\n".format(emoji[idx], option)
            to_react.append(emoji[idx])
        confirmation_msg += "\n\nYou have {} seconds to vote!".format(time)
        poll_msg = await ctx.reply(confirmation_msg)
        for emote in to_react:
            await poll_msg.add_reaction(emote)
        await asyncio.sleep(time)
        async for message in ctx.message.channel.history():
            if message.id == poll_msg.id:
                poll_msg = message
        results = {}
        for reaction in poll_msg.reactions:
            if reaction.emoji in to_react:
                results[reaction.emoji] = reaction.count - 1
        end_msg = "The poll is over. The results:\n\n"
        for result in results:
            end_msg += "{} {} - {} votes\n".format(
                result, options[emoji.index(result) + 1], results[result]
            )
        top_result = max(results, key=lambda key: results[key])
        if len([x for x in results if results[x] == results[top_result]]) > 1:
            top_results = []
            for key, value in results.items():
                if value == results[top_result]:
                    top_results.append(options[emoji.index(key) + 1])
            end_msg += "\nThe victory is tied between: {}".format(
                ", ".join(top_results)
            )
        else:
            top_result = options[emoji.index(top_result) + 1]
            end_msg += f"\n**{top_result}** is the winner!"
        await ctx.reply(end_msg)

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply('Missing the question.')
            return

    @commands.cooldown(rate=2, per=3, type=commands.BucketType.user)
    @commands.command()
    async def canirun(self, ctx, command: str):
        """
        See if you can run a certain command
        """
        command = ctx.bot.get_command(command)
        if command is None:
            return await ctx.reply("That command does not exist...", delete_after=5)
        try:
            can_run = await command.can_run(ctx)
        except Exception as ex:
            await ctx.reply(
                "You cannot run the command here, because: "
                f"`{type(ex).__name__}: {ex!s}`"
            )
        else:
            await ctx.reply(
                f'You {can_run and "can" or "cannot"} run this ' "command here."
            )

    @commands.cooldown(rate=2, per=3, type=commands.BucketType.user)
    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: commands.clean_content):
        """
        Makes a poll quickly.
        The first argument is the question and the rest are the choices.
        if you need to have spaces between the question and the choices, enclose them in double quotes ("")
        """

        def to_emoji(c):
            base = 0x1f1e6
            return chr(base + c)

        if len(questions_and_choices) < 3:
            return await ctx.reply('Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 21:
            return await ctx.reply('You can only have up to 20 choices.')

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.reply('Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(to_emoji(e), v)
                   for e, v in enumerate(questions_and_choices[1:])]

        try:
            await ctx.message.delete()
        except:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.reply(f'{ctx.author} asks: {question}\n\n{body}')
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.command()
    async def randint(self, ctx, a: int, b: int):
        """Usage: *ranint [least number][greatest number]. RanDOM!"""
        if a is None or b is None:
            await ctx.reply("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        else:
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Your randomized number:')
            em.description = random.randint(a, b)
            await ctx.reply(embed=em)

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
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
        with BytesIO() as file:
                img.save(file, "PNG")
                file.seek(0)
                await ctx.reply(f"{ctx.author.mention}", file=discord.File(file, f"QR_{ctx.author.name}_{ctx.message.id}.png"))

    @commands.command(aliases=["qrinv"])
    @commands.guild_only()
    @commands.has_permissions(create_instant_invite=True)
    async def qrinvite(self, ctx, age: int = 86400, uses: int = 0, temp: bool = False):
        """
        Allows you to create a QR Code of the invite link of this server
        Make sure to adjust the available options to suite your need!
        Set the `age` (defaults to 1 day) and `uses` argument to 0 to make a permanent link (default behavior)
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
        with BytesIO() as file:
                img.save(file, "PNG")
                file.seek(0)
                await ctx.reply(f"{ctx.author.mention}, here is the QR Code Invite of {ctx.guild.name}", file=discord.File(file, f"QR_{ctx.author.name}_{ctx.guild.name}.png"))

    @commands.command(aliases=["whoisplaying"])
    @commands.guild_only()
    async def whosplaying(self, ctx, *, game: str):
        """Shows who's playing a specific game"""
        if len(game) <= 1:
            await ctx.reply("```The game should be at least 2 characters long...```", delete_after=5.0)
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
            await ctx.reply("```Search results:\nNo users are currently playing that game.```")
        else:
            msg = playing_game
            if count_playing > 15:
                showing = f"(Showing 15/{count_playing})"
            else:
                showing = f"({count_playing})"

            em = discord.Embed(
                description=msg, colour=discord.Colour(value=0x36393e))
            em.set_author(
                name=f"""Who's playing "{game}"? {showing} User(s) in total.""")
            await ctx.reply(embed=em)

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

        sorted_list = sorted(freq_list.items(),key=itemgetter(1),reverse=True)

        if not freq_list:
            await ctx.reply("```Search results:\nNo users are currently playing any games. Odd...```")
        else:
            # Create display and embed
            msg = ""
            max_games = min(len(sorted_list), 10)

            em = discord.Embed(
                description=msg, colour=discord.Colour(value=0x36393e))
            for i in range(max_games):
                game, freq = sorted_list[i]
                if int(freq_list[game]) < 2:
                    amount = "1 person"
                else:
                    amount = f"{int(freq_list[game])} people"
                em.add_field(name=game, value=amount)
            em.set_thumbnail(url=guild.icon_url)
            em.set_footer(
                text="Do [p]whosplaying <game> to see whos playing a specific game")
            em.set_author(
                name="Top games being played right now in the server:")
            await ctx.reply(embed=em)

    @commands.command(aliases=['drunkify'])
    async def mock(self, ctx, *, txt: commands.clean_content):
        """
        iTS SpElleD sQl!!

        """
        lst = [str.upper, str.lower]
        newText = await commands.clean_content().convert(ctx, ''.join(random.choice(lst)(c) for c in txt))
        if len(newText) <= 900:
            await ctx.reply(newText)
        else:
            try:
                await ctx.author.send(newText)
                await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command()
    async def expand(self, ctx,  gap: int, *, txt: commands.clean_content):
        """
        E X P A N D the T E X T
        """
        spacing = ""
        if gap > 0 and gap <= 5:
            for _ in range(gap):
                spacing += " "
            result = spacing.join(txt)
            if len(result) <= 256:
                await ctx.reply(result)
            else:
                try:
                    await ctx.author.send(result)
                    await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
                except Exception:
                    await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")
        else:
            await ctx.reply("```fix\nError: The number can only be from 1 to 5```")

    @commands.command(aliases=["rev"])
    async def reverse(self, ctx, *, txt: commands.clean_content):
        """
        txeT eht esreveR
        """
        result = await commands.clean_content().convert(ctx, txt[::-1])
        if len(result) <= 350:
            await ctx.reply(f"{result}")
        else:
            try:
                await ctx.author.send(f"{result}")
                await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["ascii2hex", "a2h"])
    async def texttohex(self, ctx, *, txt: str):
        """
        Converts ASCII characters into Hexadecimal value
        """
        try:
            hexoutput = await commands.clean_content().convert(ctx, (" ".join("{:02x}".format(ord(c)) for c in txt)))
        except Exception as e:
            await ctx.reply(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/hexadecimal/#data**")
        if len(hexoutput) <= 479:
            await ctx.reply(f"```fix\n{hexoutput}```")
        else:
            try:
                await ctx.author.send(f"```fix\n{hexoutput}```")
                await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["hex2ascii", "h2a"])
    async def hextotext(self, ctx, *, txt: str):
        """
        Converts Hexadecimal value into ASCII characters
        """
        try:
            cleanS = await commands.clean_content().convert(ctx, bytearray.fromhex(txt).decode())
        except Exception as e:
            await ctx.reply(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/hexadecimal/#data**")
            return
        if len(cleanS) <= 479:
            await ctx.reply(f"```{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```{cleanS}```")
                await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["ascii2bin", "a2b"])
    async def texttobinary(self, ctx, *, txt: str):
        """
        Converts ASCII characters into Binary
        """
        try:
            cleanS = await commands.clean_content().convert(ctx, ' '.join(format(ord(x), 'b') for x in txt))
        except Exception as e:
            await ctx.reply(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data**")
            return
        if len(cleanS) <= 479:
            await ctx.reply(f"```fix\n{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```fix\n{cleanS}```")
                await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["bin2ascii", "b2a"])
    async def binarytotext(self, ctx, *, txt: str):
        """
        Converts Binary into ASCII Characters
        """
        try:
            cleanS = await commands.clean_content().convert(ctx, ''.join([chr(int(txt, 2)) for txt in txt.split()]))
        except Exception as e:
            await ctx.reply(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data**")
            return
        if len(cleanS) <= 479:
            await ctx.reply(f"```{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```{cleanS}```")
                await ctx.reply(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.reply(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["ncs"])
    async def nickscan(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """
        See all the servers that you have nickname in (you need to be in the same server as the bot)
        You can also check other's nickname
        """

        if user is None:
            user = ctx.message.author

        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            embed = discord.Embed(
                title=f'Servers that {user.name} have nicknames in', description=page)
            return embed

        nicks = pag.EmbedNavigatorFactory(factory=main_embed)

        message = []
        for guild in self.bot.guilds:
            if user in guild.members:
                mem = guild.get_member(user.id)
                if mem.nick != None:
                    message.append(f'**{mem.nick}** ({guild.name})')

        nicks += "\n".join(message)
        nicks.start(ctx)

    @commands.command(aliases=["ipinfo", "ipaddr"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def ip(self, ctx, ip: str = None):
        """
        Find out the information of an IP Address
        API Provided by: https://ipapi.co/
        """
        if ip is None:
            return await ctx.reply(embed=discord.Embed(description="⚠ Please Specify the IP Address!"))
        
        await ctx.trigger_typing()
        ip_regex = '^(?!^0\.)(?!^10\.)(?!^100\.6[4-9]\.)(?!^100\.[7-9]\d\.)(?!^100\.1[0-1]\d\.)(?!^100\.12[0-7]\.)(?!^127\.)(?!^169\.254\.)(?!^172\.1[6-9]\.)(?!^172\.2[0-9]\.)(?!^172\.3[0-1]\.)(?!^192\.0\.0\.)(?!^192\.0\.2\.)(?!^192\.88\.99\.)(?!^192\.168\.)(?!^198\.1[8-9]\.)(?!^198\.51\.100\.)(?!^203.0\.113\.)(?!^22[4-9]\.)(?!^23[0-9]\.)(?!^24[0-9]\.)(?!^25[0-5]\.)(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$'
        
        ip_result = match(ip_regex, ip)
        if ip_result:
            session = self.acquire_session()
            async with session.get(f'https://ipapi.co/{ip}/json/') as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
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

            embd = discord.Embed(
                title="IP Information", color=ctx.author.color, timestamp=datetime.utcnow())
            embd.add_field(name="IP Address:", value=ipaddr, inline=False)
            embd.add_field(name="ISP Name/Organization:",value=organization, inline=False)
            embd.add_field(name="City:", value=city, inline=False)
            embd.add_field(name="Regional Area:", value=region)
            embd.add_field(name="Region Code:",value=region_code, inline=False)
            embd.add_field(name="Country:", value=country, inline=False)
            embd.add_field(name="Country Name:",value=country_name, inline=False)
            embd.add_field(name="Country Code (ISO):",value=country_code_iso3, inline=False)
            embd.add_field(name="Language Spoken:",value=languages, inline=False)
            embd.add_field(name="Continent Code:",value=continent_code, inline=False)
            embd.add_field(name="Is country a member of European Union (EU)?", value=in_eu, inline=False)
            embd.add_field(name="Postal Code:", value=postal, inline=False)
            embd.add_field(name="Latitude Coordinate:",value=latitude, inline=False)
            embd.add_field(name="Longitude Coordinate:",value=longitude, inline=False)
            embd.add_field(name="Timezone:",value=country_timezone, inline=False)
            embd.add_field(name="UTC Offset:", value=utc_offset, inline=False)
            embd.add_field(name="Country Dial Code:",value=dial_code, inline=False)
            embd.add_field(name="Currency:", value=currency, inline=False)
            embd.add_field(name="Autonomous System Number:",value=asn, inline=False)
            embd.set_footer(
                text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

            await ctx.reply(embed=embd)
        else:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error Occured! Make sure the IP and the formatting are correct!"))

    @commands.command(aliases=["m2a"])
    async def morse2ascii(self, ctx, *, text: commands.clean_content = None):
        """
        Convert Morse code to ASCII
        """
        if text is None:
            await ctx.reply(embed=discord.Embed(description="⚠ Please specify the input."))
            return

        inverseMorseAlphabet = dict((v, k) for (k, v) in morseAlphabet.items())

        messageSeparated = text.split(' ')
        decodeMessage = ''
        for char in messageSeparated:
            if char in inverseMorseAlphabet:
                decodeMessage += inverseMorseAlphabet[char]
            else:
                decodeMessage += '<ERROR>'
        await ctx.reply(embed=discord.Embed(title="Morse to ASCII Conversion:", description=decodeMessage, timestamp=datetime.utcnow()))

    @commands.command(aliases=["a2m"])
    async def ascii2morse(self, ctx, *, text: commands.clean_content = None):
        """
        Convert ASCII into Morse Code
        """
        if text is None:
            await ctx.reply(embed=discord.Embed(description="⚠ Please specify the input."))
            return

        encodedMessage = ""
        for char in text[:]:
            if char.upper() in morseAlphabet:
                encodedMessage += morseAlphabet[char.upper()] + " "
            else:
                encodedMessage += '<CHARACTER NOT FOUND>'
        await ctx.reply(embed=discord.Embed(title="ASCII to Morse Conversion:", description=encodedMessage, timestamp=datetime.utcnow()))

    @commands.command(aliases=["ascii2b64", "b64e"])
    async def base64encode(self, ctx, *, text: str = None):
        """
        Encode ASCII chars to Base64
        """
        if text == None:
            await ctx.reply(embed=discord.Embed(description="Please input the text!"))
            return

        try:
            sample_string = text
            sample_string_bytes = sample_string.encode("ascii")

            base64_bytes = base64.b64encode(sample_string_bytes)
            base64_string = base64_bytes.decode("ascii")
            await ctx.reply(embed=discord.Embed(description=f"```{base64_string}```"))
        except UnicodeEncodeError:
            await ctx.reply(embed=discord.Embed(description=f"⚠️ Unable to encode the text, possible unsupported characters are found."))

    @commands.command(aliases=["b642ascii", "b64d"])
    async def base64decode(self, ctx, text: str = None):
        """
        Decode Base64 chars to ASCII
        """
        if text == None:
            await ctx.reply(embed=discord.Embed(description="Please input the text!"))
            return

        try:
            base64_string = text
            base64_bytes = base64_string.encode("ascii")

            sample_string_bytes = base64.b64decode(base64_bytes)
            sample_string = sample_string_bytes.decode("ascii")
            await ctx.reply(embed=discord.Embed(description=f"```{sample_string}```"))
        except UnicodeDecodeError:
            await ctx.reply(embed=discord.Embed(description=f"⚠️ Unable to decode the text, possible unsupported characters are found."))

    @commands.command(aliases=["nationalize"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def nationality(self, ctx, *, name: str = None):
        """
        This command predicts the nationality of a person given their name.
        API Provided by: `https://nationalize.io/`
        """

        if name is None:
            await ctx.reply(embed=discord.Embed(description="Please input the name."))
            return

        await ctx.trigger_typing()

        parameters = {
            "name": name
        }
        session = self.acquire_session()
        async with session.get('https://api.nationalize.io/', params=parameters) as resp:
            resp.raise_for_status()
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            answer = data["name"]
            country = data.country[0].country_id
            probability = data.country[0].probability
        except IndexError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error Occured! Cannot determine the result."))
            return

        percentage = float(probability) * 100
        floorPercentage = floor(percentage)

        emb = discord.Embed(description="Predict the nationality of a name!",
                            color=ctx.author.color, timestamp=datetime.utcnow())
        emb.add_field(name="Name", value=answer.title())
        emb.add_field(name="Country",value=f"{country} :flag_{country.lower()}:")
        emb.add_field(name="Probability", value=f"{floorPercentage}%")
        emb.set_footer(
            text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

        await ctx.reply(embed=emb)

    @commands.command(aliases=["wth"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def weather(self, ctx, *, city: str = None):
        """
        A command to check weather status
        API Provided by: OpenWeatherMap.org
        """

        if city is None:
            await ctx.reply(embed=discord.Embed(description="Please provide the city name!"))
            return

        await ctx.trigger_typing()

        with open("cogs/data/weather_api_key.json") as json_fp:
            classified = json.load(json_fp)
            key = classified["key"]

        # https://stackoverflow.com/a/7490772 https://www.windfinder.com/wind/windspeed.htm
        def degToCompass(deg):
            val = int((deg/22.5)+.5)
            arr = [
                "North (N)",
                "North-Northeast (NNE)",
                "Northeast (NE)",
                "East-Northeast (ENE)",
                "East (E)",
                "East-Southeast (ESE)",
                "Southeast (SE)",
                "South-Southeast (SSE)",
                "South (S)",
                "South-Southwest (SSW)",
                "Southwest (SW)",
                "West-Southwest (WSW)",
                "West (W)",
                "West-Northwest (WNW)",
                "Northwest (NW)",
                "North-Northwest (NNW)"
            ]
            return arr[(val % 16)]

        def metertokilometer(meter):  # https://www.asknumbers.com/meters-to-km.aspx
            km = meter * 0.001
            trc = trunc(km)
            return trc

        def mpstokmh(mtr):  # https://www.mathworksheets4kids.com/solve/speed/conversion2.php
            mul = mtr * 18
            div = mul / 5
            trc = trunc(div)
            return trc

        # In Meter/second https://www.windfinder.com/wind/windspeed.htm
        def wind_condition(wind_speed):
            if wind_speed >= 0 and wind_speed <= 0.2:
                return "Calm"
            elif wind_speed >= 0.2 and wind_speed <= 1.5:
                return "Light Air"
            elif wind_speed >= 1.5 and wind_speed <= 3.3:
                return "Light Breeze"
            elif wind_speed >= 3.3 and wind_speed <= 5.4:
                return "Gentle Breeze"
            elif wind_speed >= 5.4 and wind_speed <= 7.9:
                return "Moderate Breeze"
            elif wind_speed >= 7.9 and wind_speed <= 10.7:
                return "Fresh Breeze"
            elif wind_speed >= 10.7 and wind_speed <= 13.8:
                return "Strong Breeze"
            elif wind_speed >= 13.8 and wind_speed <= 17.1:
                return "Near Gale"
            elif wind_speed >= 17.1 and wind_speed <= 20.7:
                return "Gale"
            elif wind_speed >= 20.7 and wind_speed <= 24.4:
                return "Severe Gale"
            elif wind_speed >= 24.4 and wind_speed <= 28.4:
                return "Strong Storm"
            elif wind_speed >= 28.4 and wind_speed <= 32.6:
                return "Violent Storm"
            elif wind_speed >= 32.6:
                return "Hurricane"

        try:
            parameters = {
                "q": city,
                "appid": key,
                "units": "metric"
            }
            session = self.acquire_session()  # do NOT async with on this line!!!
            async with session.get("http://api.openweathermap.org/data/2.5/weather", params=parameters) as resp:
                data = json.loads(await resp.read(), object_hook=DictObject)

            code = data.cod

            if code != 200:
                msg = data.message
                if code == 404:
                    await ctx.reply(embed=discord.Embed(description="City cannot be found!"))
                    return
                elif code == 401:
                    await ctx.reply(embed=discord.Embed(description="Invalid API Key!"))
                    return
                else:
                    await ctx.reply(embed=discord.Embed(description=f"An Error Occured! `{msg.capitalize()}` (Code: `{code}`)"))
                    return

            cityname = data.name
            countryid = data.sys.country
            country_flags = f":flag_{countryid.lower()}:"
            status = data.weather[0].main
            description = data.weather[0].description
            sunrise = data.sys.sunrise
            sunset = data.sys.sunset
            timezone_offset = data.timezone
            clouds = data.clouds.all
            lon = data.coord.lon
            lat = data.coord.lat
            temp_c = data.main.temp
            feels_c = data.main.feels_like
            t_min_c = data.main.temp_min
            t_max_c = data.main.temp_max
            temp_f = pytemperature.c2f(temp_c)
            feels_f = pytemperature.c2f(feels_c)
            t_min_f = pytemperature.c2f(t_min_c)
            t_max_f = pytemperature.c2f(t_max_c)
            pressure = data.main.pressure
            humidity = data.main.humidity
            vis = data.visibility
            wind = data.wind.speed
            wind_degree = data.wind.deg
            wind_direction = degToCompass(wind_degree)
            icon = f"http://openweathermap.org/img/wn/{data.weather[0].icon}@2x.png"
        except IndexError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error Occured while parsing the data."))
            return
        except KeyError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error Occured while parsing the data."))
            return

        colours = ""

        if temp_c > 36:
            colours = discord.Colour(0xFF0000)
        elif temp_c > 28:
            colours = discord.Colour(0xFFFF00)
        elif temp_c > 16:
            colours = discord.Colour(0x26D935)
        elif temp_c > 8:
            colours = discord.Colour(0x006BCE)
        elif temp_c > 2:
            colours = discord.Colour(0xB4CFFA)
        elif temp_c <= 2:
            colours = discord.Colour(0x0000FF)
        else:
            colours = discord.Colour(0x36393E)

        calculated_sunrise = datetime.fromtimestamp(sunrise + timezone_offset)
        calculated_sunset = datetime.fromtimestamp(sunset + timezone_offset)

        embed = discord.Embed(title="Weather Information",timestamp=datetime.utcnow(), color=colours)
        embed.set_thumbnail(url=icon)
        embed.set_footer(text="Data provided by: OpenWeatherMap.org",icon_url="https://upload.wikimedia.org/wikipedia/commons/1/15/OpenWeatherMap_logo.png")

        embed.add_field(name="🏙 City", value=cityname, inline=False)
        embed.add_field(name="🏳 Country",
                        value=f"{countryid} {country_flags}", inline=False)
        embed.add_field(name="🌻 Weather", value=status, inline=False)
        embed.add_field(name="ℹ Condition",
                        value=description.title(), inline=False)
        embed.add_field(name="🌐 Longitude", value=lon, inline=True)
        embed.add_field(name="🌐 Latitude", value=lat, inline=True)
        embed.add_field(name="🌄 Sunrise",
                        value=f"{calculated_sunrise} (UTC)", inline=True)
        embed.add_field(name="🌇 Sunset",
                        value=f"{calculated_sunset} (UTC)", inline=True)
        embed.add_field(name="🌡 Current Temperature",
                        value=f"{temp_c} °C ({temp_f} °F)", inline=True)
        embed.add_field(name="🌡 Feels Like",
                        value=f"{feels_c} °C ({feels_f} °F)", inline=True)
        embed.add_field(name="🌡 Min Temperature",
                        value=f"{t_min_c} °C ({t_min_f} °F)", inline=True)
        embed.add_field(name="🌡 Max Temperature",
                        value=f"{t_max_c} °C ({t_max_f} °F)", inline=True)
        embed.add_field(name="☁ Cloudiness", value=f"{clouds}%", inline=True)
        embed.add_field(name="🍃Atmospheric Pressure",
                        value=f"{pressure} hPa", inline=True)
        embed.add_field(name="🌬 Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="👁️ Visibility",
                        value=f"{vis} Meter ({metertokilometer(vis)} KM)", inline=True)
        embed.add_field(
            name="💨 Wind Speed", value=f"{wind} m/sec | {mpstokmh(wind)} km/h ({wind_condition(wind)})", inline=True)
        embed.add_field(name="🧭 Wind Direction",
                        value=f"{wind_degree}° {wind_direction}", inline=True)

        await ctx.reply(embed=embed)

    @commands.command(name="define", aliases=["definition", "dictionary", "def"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _define(self, ctx, *, word: str):
        msg = await ctx.reply("Looking for a definition...")
        try:
            #--Connect to unofficial Google Dictionary API and get results--#
            session = self.acquire_session()
            async with session.get(f'https://api.dictionaryapi.dev/api/v1/entries/en/{word}') as r:
                #--Now we decode the JSON and get the variables, replacing them with None if they fail to define--#
                result = await r.json()
                word = result[0]['word']
                try:
                    origin = result[0]['origin']
                except KeyError:
                    origin = None
                try:
                    noun_def = result[0]['meaning']['noun'][0]['definition']
                except KeyError:
                    noun_def = None
                try:
                    noun_eg = result[0]['meaning']['noun'][0]['example']
                except KeyError:
                    noun_eg = None
                try:
                    verb_def = result[0]['meaning']['verb'][0]['definition']
                except KeyError:
                    verb_def = None
                try:
                    verb_eg = result[0]['meaning']['verb'][0]['example']
                except KeyError:
                    verb_eg = None
                try:
                    prep_def = result[0]['meaning']['preposition'][0]['definition']
                except KeyError:
                    prep_def = None
                try:
                    prep_eg = result[0]['meaning']['preposition'][0]['example']
                except KeyError:
                    prep_eg = None
                try:
                    adverb_def = result[0]['meaning']['adverb'][0]['definition']
                except KeyError:
                    adverb_def = None
                try:
                    adverb_eg = result[0]['meaning']['adverb'][0]['example']
                except KeyError:
                    adverb_eg = None
                try:
                    adject_def = result[0]['meaning']['adjective'][0]['definition']
                except KeyError:
                    adject_def = None
                try:
                    adject_eg = result[0]['meaning']['adjective'][0]['example']
                except KeyError:
                    adject_eg = None
                try:
                    pronoun_def = result[0]['meaning']['pronoun'][0]['definition']
                except KeyError:
                    pronoun_def = None
                try:
                    pronoun_eg = result[0]['meaning']['pronoun'][0]['example']
                except KeyError:
                    pronoun_eg = None
                try:
                    exclaim_def = result[0]['meaning']['exclamation'][0]['definition']
                except KeyError:
                    exclaim_def = None
                try:
                    exclaim_eg = result[0]['meaning']['exclamation'][0]['example']
                except KeyError:
                    exclaim_eg = None
                try:
                    poss_determ_def = result[0]['meaning']['possessive determiner'][0]['definition']
                except KeyError:
                    poss_determ_def = None
                try:
                    poss_determ_eg = result[0]['meaning']['possessive determiner'][0]['example']
                except KeyError:
                    poss_determ_eg = None
                try:
                    abbrev_def = result[0]['meaning']['abbreviation'][0]['definition']
                except KeyError:
                    abbrev_def = None
                try:
                    abbrev_eg = result[0]['meaning']['abbreviation'][0]['example']
                except KeyError:
                    abbrev_eg = None
                try:
                    crossref_def = result[0]['meaning']['crossReference'][0]['definition']
                except KeyError:
                    crossref_def = None
                try:
                    crossref_eg = result[0]['meaning']['crossReference'][0]['example']
                except KeyError:
                    crossref_eg = None
                embed = discord.Embed(
                    title=f":blue_book: Google Definition for {word}", color=0x8253c3)
                #--Then we add see if the variables are defined and if they are, those variables to an embed and send it back to Discord--#
                if origin == None:
                    pass
                else:
                    embed.add_field(name="Origin:", value=origin, inline=False)
                if noun_def == None:
                    pass
                else:
                    if noun_eg == None:
                        embed.add_field(
                            name="As a Noun:", value=f"**Definition:** {noun_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As a Noun:", value=f"**Definition:** {noun_def}\n**Example:** {noun_eg}", inline=False)
                if verb_def == None:
                    pass
                else:
                    if verb_eg == None:
                        embed.add_field(
                            name="As a Verb:", value=f"**Definition:** {verb_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As a Verb:", value=f"**Definition:** {verb_def}\n**Example:** {verb_eg}", inline=False)
                if prep_def == None:
                    pass
                else:
                    if prep_eg == None:
                        embed.add_field(
                            name="As a Preposition:", value=f"**Definition:** {prep_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As a Preposition:", value=f"**Definition:** {prep_def}\n**Example:** {prep_eg}", inline=False)
                if adverb_def == None:
                    pass
                else:
                    if adverb_eg == None:
                        embed.add_field(
                            name="As an Adverb:", value=f"**Definition:** {adverb_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As a Adverb:", value=f"**Definition:** {adverb_def}\n**Example:** {adverb_eg}", inline=False)
                if adject_def == None:
                    pass
                else:
                    if adject_eg == None:
                        embed.add_field(
                            name="As an Adjective:", value=f"**Definition:** {adject_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As an Adjective:", value=f"**Definition:** {adject_def}\n**Example:** {adject_eg}", inline=False)
                if pronoun_def == None:
                    pass
                else:
                    if pronoun_eg == None:
                        embed.add_field(
                            name="As a Pronoun:", value=f"**Definition:** {pronoun_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As a Pronoun:", value=f"**Definition:** {pronoun_def}\n**Example:** {pronoun_eg}", inline=False)
                if exclaim_def == None:
                    pass
                else:
                    if exclaim_eg == None:
                        embed.add_field(
                            name="As an Exclamation:", value=f"**Definition:** {exclaim_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As an Exclamation:", value=f"**Definition:** {exclaim_def}\n**Example:** {exclaim_eg}", inline=False)
                if poss_determ_def == None:
                    pass
                else:
                    if poss_determ_eg == None:
                        embed.add_field(name="As a Possessive Determiner:",
                                        value=f"**Definition:** {poss_determ_def}", inline=False)
                    else:
                        embed.add_field(name="As a Possessive Determiner:",
                                        value=f"**Definition:** {poss_determ_def}\n**Example:** {poss_determ_eg}", inline=False)
                if abbrev_def == None:
                    pass
                else:
                    if abbrev_eg == None:
                        embed.add_field(
                            name="As an Abbreviation:", value=f"**Definition:** {abbrev_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As an Abbreviation:", value=f"**Definition:** {abbrev_def}\n**Example:** {abbrev_eg}", inline=False)
                if crossref_def == None:
                    pass
                else:
                    if crossref_eg == None:
                        embed.add_field(
                            name="As a Cross-Reference:", value=f"**Definition:** {crossref_def}", inline=False)
                    else:
                        embed.add_field(
                            name="As a Cross-Reference:", value=f"**Definition:** {crossref_def}\n**Example:** {crossref_eg}", inline=False)
                await msg.edit(content='', embed=embed)
        except:
            #--Send error message if command fails, as it's assumed a definition isn't found--#
            await msg.edit(content=":x: Sorry, I couldn't find that word. Check your spelling and try again.")

    @commands.command(aliases=["curr"])
    async def currency(self, ctx, origin: str, destination: str, amount: int):
        """
        Convert currencies from one to another
        For the list of acceptable format go to: https://en.wikipedia.org/wiki/ISO_4217#Active_codes
        """
        head = {
            "Authorization": ksoft_key
        }
        params = {
            "from": origin,
            "to": destination,
            "value": amount
        }
        session = self.acquire_session()
        async with session.get('https://api.ksoft.si/kumo/currency', headers=head, params=params) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)
        try:
            prt = data.pretty
        except KeyError:
            code = data.code
            msg = data.message
            await ctx.reply(embed=discord.Embed(description=f"⚠ An Error Occured! **{msg.capitalize()}** (Code: {code})"))
            return

        emb = discord.Embed(timestamp=datetime.utcnow())
        emb.add_field(
            name=f"Conversion from {origin.upper()} to {destination.upper()}", value=prt)
        emb.set_footer(icon_url="https://cdn.ksoft.si/images/Logo128.png",text="Data provided by: KSoft.Si")
        await ctx.reply(embed=emb)

    @commands.command(aliases=["lyric", "ly", "lrc"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def lyrics(self, ctx, *, search = None):
        """A command to find lyrics easily!"""
        if not search: # if user hasnt given an argument, throw a error and come out of the command
            embed = discord.Embed(
                title = "No search argument!",
                description = "You havent entered anything, so i couldnt find lyrics!"
            )
            return await ctx.reply(embed = embed)
            # ctx.reply is available only on discord.py version 1.6.0, if you have a version lower than that use ctx.reply

        song = urllib.parse.quote(search) # url-encode the song provided so it can be passed on to the API

        parameters = {
            "title" : song
        }

        session = self.acquire_session()
        async with session.get(f'https://some-random-api.ml/lyrics', params = parameters) as jsondata: # define jsondata and fetch from API
            if not 300 > jsondata.status >= 200: # if an unexpected HTTP status code is recieved from the website, throw an error and come out of the command
                return await ctx.reply(f'Received poor status code of {jsondata.status}')
            lyricsData = await jsondata.json() # load the json data into its json form

        error = lyricsData.get('error')
        if error: # checking if there is an error recieved by the API, and if there is then throwing an error message and returning out of the command
            return await ctx.reply(f'Recieved unexpected error: {error}')

        songLyrics = lyricsData['lyrics'] # the lyrics
        songArtist = lyricsData['author'] # the author's name
        songTitle = lyricsData['title'] # the song's title
        songThumbnail = lyricsData['thumbnail']['genius'] # the song's picture/thumbnail

        # sometimes the song's lyrics can be above 4096 characters, and if it is then we will not be able to send it in one single message on Discord due to the character limit
        # this is why we split the song into chunks of 4096 characters and send each part individually
        for chunk in textwrap.wrap(songLyrics, 4096, replace_whitespace = False):
            embed = discord.Embed(
                title = f"{songArtist} - {songTitle}",
                description = chunk,
                color = discord.Color.blurple(),
                timestamp = datetime.utcnow()
            )
            embed.set_thumbnail(url = songThumbnail)
            await ctx.reply(embed = embed)

    @commands.command(aliases=["cvd", "covid19"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def covid(self, ctx, *, country: str = None):
        """
        View COVID-19 Statistic for a Country.
        Accepted values are **Country name** or **Alpha-2 ISO Code**.
        """
        if country is None:
            await ctx.reply(embed=discord.Embed(description=f"Please specify the country!"))
            return
        elif len(country) > 16:
            await ctx.reply(embed=discord.Embed(description=f"Only 16 chacarcters are allowed."))
            return

        await ctx.trigger_typing()
        head = {
            "accept": "application/json"
        }
        session = self.acquire_session()
        async with session.get(f"https://covid2019-api.herokuapp.com/v2/country/{country.replace(' ', '_')}", headers=head) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            loc = data.data.location
            confirm = data.data.confirmed
            dead = data.data.deaths
            rec = data.data.recovered
            act = data.data.active
        except KeyError:
            await ctx.reply(embed=discord.Embed(description=f"⚠ An Error Occured! **Location not found!**"))
            return

        if rec == 0:
            rec = "Unknown"
            
        if act == 0:
            act = "Unknown"

        ts = data.ts

        emb = discord.Embed(
            description=f"COVID-19 Statistics for **{loc}**", timestamp=datetime.fromtimestamp(ts))
        emb.set_footer(text="Last updated:")
        emb.set_thumbnail(
            url="https://i1.wp.com/news.power102fm.com/wp-content/uploads/2020/03/coronavirus-png-image-hd-covid-19-1885x1653-1.png")
        emb.set_image(
            url="https://i.ibb.co/rfjn4zP/file-20200803-24-50u91u.png")
        emb.add_field(name="Confirmed", value=confirm, inline=False)
        emb.add_field(name="Deaths", value=dead, inline=False)
        emb.add_field(name="Recovered", value=rec, inline=False)
        emb.add_field(name="Active Cases", value=act, inline=False)
        await ctx.reply(embed=emb)

    @commands.command(aliases=["cd", "timer"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.max_concurrency(number=1, per=commands.BucketType.guild, wait=False)
    async def countdown(self, ctx, time: int = 3):
        """
        A Simple countdown timer
        """
        if time > 3600:
            return await ctx.reply("Maximum duration is 1 hour (3600 seconds)")
        msg = await ctx.reply(content="Preparing...")
        await asyncio.sleep(3)
        iteration = time
        while iteration:
            mins, secs = divmod(iteration, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            emb = discord.Embed(description=timer)
            await msg.edit(embed=emb, content=None)
            await asyncio.sleep(1)
            iteration -= 1
        await msg.edit(content="**End!**", embed=None)

    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def scp(self, ctx, query: str = None):
        """
        SCP Database, Requires Access Clearance Level 4 or Higher.
        """
        if query is None:
            return await ctx.reply(embed=discord.Embed(description=f":x: ERROR: **Please insert your query.**"))

        await ctx.trigger_typing()

        msg = await ctx.send(f"💿 Accessing Database... Please Wait.")

        params = {
            "q": query,
        }
        session = self.acquire_session()
        async with session.get('https://crom-dev.avn.sh/search', params=params) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            scp_url = data.url
        except KeyError:
            return await msg.edit(embed=discord.Embed(description=f":x: ERROR: **Entry not found.**"), content=None)
        scp_title = data.title

        scp_rating = data.rating
        scp_image = data.image

        scp_firstseen = data.first_seen_at
        scp_lastupdated = data.last_updated_at

        emb = discord.Embed(
            title=f"Database entry for {scp_title}", timestamp=datetime.utcnow())

        try:
            scp_name = data.scp_title
            emb.add_field(
                name="Name", value=f"[{scp_name}]({scp_url})", inline=False)
        except:
            pass

        if scp_image is not None:
            emb.set_image(url=scp_image)

        emb.set_thumbnail(url="https://i.ibb.co/PxGsCJT/scp.png")

        try:
            scp_class = data.object_class
            emb.add_field(name="Object Classification",value=scp_class, inline=False)
        except KeyError:
            pass

        emb.add_field(name="Dated", value=ciso8601.parse_datetime(
            scp_firstseen).strftime("%B %d, %Y"), inline=True)

        emb.set_footer(
            text=f"Last Updated: {ciso8601.parse_datetime(scp_lastupdated).strftime('%B %d, %Y')} | Rating: {scp_rating}")

        await msg.edit(embed=emb, content=None)

    @commands.command(aliases=["animesearch", "ani"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(number=1, per=commands.BucketType.guild, wait=False)
    async def anisearch(self, ctx):
        """
        Find animes by screenshot! just send the image and the bot will try to find it for you!
        API Used: https://soruly.github.io/trace.moe-api/
        """
        await ctx.trigger_typing()

        # First we get the image from the attachment
        try:
            attachment = ctx.message.attachments[0]
            fp = BytesIO()
            await attachment.save(fp)
        except IndexError:
            await ctx.reply(embed=discord.Embed(description="⚠ You haven't supplied any image!"))
            return

        img = Image.open(fp)
        if not img.mode == 'RGB':
            img = img.convert('RGB')
        
        # Secondly we convert it to jpg to save space
        image_file = BytesIO()
        img.save(image_file, format="JPEG",optimize=True,quality=80)
        image_file.seek(0)
        
        # Then we send the image to the API
        session = self.acquire_session()
        async with session.post("https://api.trace.moe/search?cutBorders",data=image_file.read(),headers={"Content-Type": "image/jpeg"}) as resp:
            data = json.loads(await resp.read())
        
        # Then we parse the response from the API
        try:
            anilist = data["result"][0]["anilist"]
            filename = data["result"][0]["filename"]
            episode = data["result"][0]["episode"]
            start = data["result"][0]["from"]
            end = data["result"][0]["to"]
            similarity = data["result"][0]["similarity"]
            image = data["result"][0]["image"]
        except:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
        
        emb = discord.Embed(title="Anime Finder")
        emb.add_field(name="AniList ID", value=anilist)
        emb.add_field(name="File Name", value=filename, inline=False)
        emb.add_field(name="Episode Number", value=episode or "Unknown")
        emb.add_field(name="Start", value=format_seconds(start))
        emb.add_field(name="End", value=format_seconds(end))
        emb.add_field(name="Similarity Score", value=similarity)
        emb.set_image(url=image)
        
        # Then we send it
        await ctx.reply(embed=emb)

    @commands.group(aliases=["mal", "anime"], invoke_without_command=True)
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.guild)
    async def myanimelist(self, ctx, *, name: str = None):
        """
        Find anime information from MyAnimeList!
        """
        data = None

        if name is None:
            await ctx.reply(embed=discord.Embed(description="Please specifiy the anime title to find!"))
            return

        if len(name) < 3:
            await ctx.reply(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        parameters = {
            "q": name,
            "limit": 1
        }
        session = self.acquire_session()
        async with session.get('https://api.jikan.moe/v3/search/anime', params=parameters, timeout=10) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            anime_id = data.results[0].mal_id
            anime_title = data.results[0].title
            anime_url = data.results[0].url
            anime_img = data.results[0].image_url
            anime_status = data.results[0].airing
            anime_synopsis = data.results[0].synopsis
            anime_type = data.results[0].type
            score = data.results[0].score
        except IndexError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return

        emb = discord.Embed(
            title="MyAnimeList Anime Information", timestamp=datetime.utcnow())

        if score == None or score == 0:
            score = "N/A"

        start = data.results[0].start_date
        end = data.results[0].end_date
        mem = data.results[0].members

        # Time zone converter (a few checks will depends on the presence of time_end value)
        try:
            time_start = ciso8601.parse_datetime(start)
            formatted_start = time_start.strftime("%B %d, %Y")
        except TypeError:
            formatted_start = "Unknown"
        try:
            time_end = ciso8601.parse_datetime(end)
            formatted_end = time_end.strftime("%B %d, %Y")
        except TypeError:
            formatted_end = "Unknown"

        try:
            total_episode = data.results[0].episodes
            if total_episode == 0 or total_episode is None:
                total_episode = "Not yet determined"
        except TypeError:
            total_episode = "Not yet determined."

        if anime_status:
            anime_status = "Ongoing"
        elif not anime_status:
            if start is None:
                anime_status = "Not yet aired"
            else:
                anime_status = "Finished airing"

        # if len(anime_synopsis) > 1024:
        #    shorten(anime_synopsis,width=1020,placeholder="...")

        emb.set_image(url=anime_img)
        emb.set_thumbnail(
            url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        emb.set_footer(
            icon_url="https://jikan.moe/assets/images/logo/jikan.logo.png", text="Powered by: Jikan")
        emb.add_field(name="📝 Title",
                      value=f"[{anime_title}]({anime_url})", inline=False)
        if anime_synopsis:
            emb.add_field(name="ℹ Synopsis",
                          value=anime_synopsis, inline=False)
        else:
            emb.add_field(name="ℹ Synopsis",
                          value="No Synopsis Found.", inline=False)
        emb.add_field(name="⌛ Status", value=anime_status, inline=False)
        emb.add_field(name="📺 Type", value=anime_type, inline=False)
        emb.add_field(name="📅 First Air Date",
                      value=formatted_start, inline=False)
        emb.add_field(name="📅 Last Air Date",
                      value=formatted_end, inline=False)
        emb.add_field(name="💿 Episodes", value=total_episode, inline=True)
        emb.add_field(name="⭐ Score", value=f"{score}", inline=True)

        try:
            rate = data.results[0].rated
            if rate is None:
                rating = "Unknown"
            else:
                rating = {
                    'G': 'All Ages (G)',
                    'PG': 'Children (PG)',
                    'PG-13': 'Teens 13 or Older (PG-13)',
                    'R': '17+ Recommended, (Violence & Profanity) (R)',
                    'R+': 'Mild Nudity, (May also contain Violence & Profanity) (R+)',
                    'Rx': 'Hentai, (Extreme sexual content/Nudity) (Rx)'
                }.get(str(rate))
            emb.add_field(name="🔞 Rating", value=rating, inline=True)
        except IndexError:
            pass
        except AttributeError:
            pass
        except KeyError:
            pass

        emb.add_field(name="👥 Members", value=mem, inline=True)
        emb.add_field(name="💳 ID", value=anime_id, inline=True)

        await ctx.reply(embed=emb)

    @myanimelist.command(name="manga", brief="Find Manga information")
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist_manga(self, ctx, *, name: str = None):
        """
        Find manga information from MyAnimeList!
        """
        if name is None:
            await ctx.reply(embed=discord.Embed(description="Please specifiy the manga title to find!"))
            return

        if len(name) < 3:
            await ctx.reply(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        parameters = {
            "q": name,
            "limit": 1
        }
        session = self.acquire_session()
        async with session.get(f'https://api.jikan.moe/v3/search/manga', params=parameters, timeout=5) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        if not data.results:
            await ctx.reply(embed=discord.Embed(description="⚠ Not Found."))
            return

        try:
            manga_title = data.results[0].title
            manga_url = data.results[0].url
            img_url = data.results[0].image_url
            stat = data.results[0].publishing
            manga_synopsis = data.results[0].synopsis
            manga_type = data.results[0].type
            manga_chapters = data.results[0].chapters
            manga_volumes = data.results[0].volumes
            score = data.results[0].score
            pub_date = data.results[0].start_date
            memb = data.results[0].members
            manga_id = data.results[0].mal_id
            time_start = ciso8601.parse_datetime(pub_date)
            formatted_start = time_start.strftime("%B %d, %Y")
        except IndexError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return
        except KeyError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return

        if stat is True:
            stat = "Ongoing"
        elif not stat:
            stat = "Finished"

        if manga_volumes is None or manga_volumes == 0:
            manga_volumes = "Unknown"

        if manga_chapters is None or manga_chapters == 0:
            manga_chapters = "Unknown"

        # if len(manga_synopsis) > 768:
        #    shorten(manga_synopsis,width=756,placeholder="...")

        emb = discord.Embed(
            title="MyAnimeList Manga Information", timestamp=datetime.utcnow())
        emb.set_image(url=img_url)
        emb.set_thumbnail(
            url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        emb.set_footer(
            icon_url="https://jikan.moe/assets/images/logo/jikan.logo.png", text="Powered By: Jikan")
        emb.add_field(name="📑 Title",value=f"[{manga_title}]({manga_url})", inline=False)

        if manga_synopsis:
            emb.add_field(name="ℹ Synopsis",value=manga_synopsis, inline=False)
        else:
            emb.add_field(name="ℹ Synopsis",value="No Synopsis Found.", inline=False)

        emb.add_field(name="⏳ Status", value=stat, inline=False)
        emb.add_field(name="📁 Type", value=manga_type, inline=False)
        emb.add_field(name="📅 Publish Date",value=formatted_start, inline=False)
        emb.add_field(name="📚 Volumes", value=manga_volumes, inline=True)
        emb.add_field(name="📰 Chapters", value=manga_chapters, inline=True)
        emb.add_field(name="⭐ Score", value=f"{score}", inline=True)
        emb.add_field(name="👥 Members", value=memb, inline=True)
        emb.add_field(name="💳 ID", value=manga_id, inline=True)

        await ctx.reply(embed=emb)

    @myanimelist.command(name="character", brief="Find character information", aliases=["chara", "char"])
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist_chara(self, ctx, *, name: str = None):
        """
        Find character information from MyAnimeList!
        """
        if name is None:
            await ctx.reply(embed=discord.Embed(description="Please specifiy the character name to find!"))
            return

        if len(name) < 3:
            await ctx.reply(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        parameters = {
            "q": name,
            "limit": 1
        }
        session = self.acquire_session()
        async with session.get(f'https://api.jikan.moe/v3/search/character', params=parameters, timeout=5) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            char_id = data.results[0].mal_id
            char_url = data.results[0].url
            char_img = data.results[0].image_url
            char_name = data.results[0].name
        except UnboundLocalError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return
        except IndexError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return
        except KeyError:
            await ctx.reply(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return

        emb = discord.Embed(
            title="MyAnimeList Character Information", timestamp=datetime.utcnow())
        emb.set_image(url=char_img)
        emb.set_thumbnail(
            url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        emb.set_footer(
            icon_url="https://jikan.moe/assets/images/logo/jikan.logo.png", text="API used: Jikan")
        emb.add_field(
            name="👤 Name", value=f"[{char_name}]({char_url})", inline=False)

        try:
            alt_name = data.results[0].alternative_names[0]
            emb.add_field(name="👥 Alternative Name",
                        value=f"{alt_name}", inline=False)
        except IndexError:
            pass

        try:
            char_anime_name = data.results[0].anime[0].name
            char_anime_url = data.results[0].anime[0].url
            emb.add_field(name="📺 Animeography",
                        value=f"[{char_anime_name}]({char_anime_url})", inline=False)
        except IndexError:
            pass

        try:
            char_manga_name = data.results[0].manga[0].name
            char_manga_url = data.results[0].manga[0].url
            emb.add_field(name="📚 Mangaography",
                        value=f"[{char_manga_name}]({char_manga_url})", inline=False)
        except IndexError:
            pass

        emb.add_field(name="💳 ID", value=char_id, inline=True)

        await ctx.reply(embed=emb)

def setup(bot):
    bot.add_cog(Utilities(bot))
    print("Utilities Module has been loaded.")
