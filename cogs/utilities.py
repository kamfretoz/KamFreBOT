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
import unicodedata
import urllib
import time
import random
import io
from math import floor, sqrt, trunc
from PIL import Image
import os
import operator
from pytz import timezone
from datetime import datetime
import safygiphy
import pytemperature
import qrcode
import requests
from io import BytesIO
from collections import deque
from textwrap import shorten
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

class DictObject(dict):
    def __getattr__(self, item):
        return self[item]

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pingeries = {}
        self.lock = asyncio.Lock()
        self.delsniped = {}
        self.editsniped = {}

    #Delete Snipe Listener (Setter)
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

                # print(f"server:{srvid}, channel:{chid}, author:{author}, content:{content}") #PRINTS ALL DELETED MESSAGES INTO THE CONSOLE (CAN BE SPAMMY)

                self.delsniped.update({
                    srvid : {
                        chid : {
                            'Sender':author,
                            'Mention':author_mention,
                            'Content':content,
                            'Attachment':file_attachment,
                            'Filename':attachment_name
                        }
                    }
                })
        except:
            pass

    #Edit Snipe Listener (Setter)
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
                #print(f"server:{srvid}, channel:{chid}, author:{author}, before:{msg_before}, after:{msg_after}")
                self.editsniped.update({
                    srvid : {
                        chid : {
                            'Sender':author,
                            'Mention':author_mention,
                            'Before':msg_before,
                            'After':msg_after
                        }
                    }
                })
        except:
            pass

    @commands.command(aliases=["sniped","snipe","delsnipe","dsnipe","ds","sn","s"])
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

            if len(msg) > 768:
                shorten(msg,width=756,placeholder="...")

            if "b!snipe" in msg:
                await ctx.message.delete()
                await ctx.send(embed=discord.Embed(description="⚠ No Message found! Perhaps you're too slow?"), delete_after=3)
                return
            if msg:
                await ctx.message.delete()
                emb = discord.Embed()
                emb.set_author(name="Sniped!", icon_url=author.avatar_url)
                emb.add_field(name="Author:", value=author_mention, inline=False)
                emb.add_field(name="Message:", value=msg)
                emb.set_footer(text=f"Sniped by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
                if attachment:
                    emb.add_field(name="Attachments",value=f"[{name}]({attachment})")
                    if str(name).endswith(".png") or str(name).endswith(".gif") or str(name).endswith(".jpg"):
                        emb.set_image(url=attachment)
                await ctx.send(embed=emb, delete_after=5)
            else:
                await ctx.message.delete()
                emb = discord.Embed(title="Sniped!")
                emb.add_field(name="Author:", value=author, inline=False)
                emb.add_field(name="Message:", value="Empty Message.",inline=False)
                emb.set_footer(text=f"Sniped by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
                if attachment:
                    emb.add_field(name="Attachments",value=f"[{name}]({attachment})", inline=False)
                    if str(name).endswith(".png") or str(name).endswith(".gif"):
                        emb.set_image(url=attachment)
                await ctx.send(embed=emb, delete_after=5)
            self.delsniped.popitem()
        except KeyError:
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(description="⚠ No Message found! Perhaps you're too slow?"), delete_after=3)
            return
        except discord.NotFound:
            pass

    @commands.command(aliases=["esnipe","esniped","es","e"])
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

            if len(before) > 768:
                shorten(before, width=756,placeholder="...")

            if len(after) > 768:
                shorten(after, width=756,placeholder="...")

            if before and after:
                await ctx.message.delete()
                emb = discord.Embed()
                emb.set_author(name="Sniped!", icon_url=author.avatar_url)
                emb.add_field(name="Author:", value=author_mention, inline=False)
                emb.add_field(name="Before:", value=before)
                emb.add_field(name="After:", value=after)
                await ctx.send(embed=emb, delete_after=5)
            else:
                await ctx.message.delete()
                emb = discord.Embed(title="Sniped!")
                emb.add_field(name="Author:", value=author, inline=False)
                emb.add_field(name="Before:", value="Empty Message.")
                emb.add_field(name="After:", value="Empty Message.")
                await ctx.send(embed=emb, delete_after=5)
            self.editsniped.popitem()
        except KeyError:
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(description="⚠ No Message found! Perhaps you're too slow?"))
            return
        except discord.NotFound:
            pass
    
    @commands.command(aliases=["codeblock"])
    async def code(self, ctx, *, msg = "Please Write Something!"):
        """Write text in code format."""
        await ctx.message.delete()
        await ctx.send("```" + msg.replace("`", "") + "```")

    @commands.command(aliases=["char"])
    async def charinfo(self, ctx, *, char: str):
        """Shows you information about a number of characters."""
        if len(char) > 15:
            return await ctx.send(f'Too many characters ({len(char)}/15)')

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
    @commands.command(hidden=True, aliases=["pingmachine", "pingspam"], enabled=False)
    @commands.guild_only()
    async def pingstorm(self, ctx, user: libneko.converters.InsensitiveMemberConverter, amount: int = 5):
        """Ping specified user number of times, 5 if no amount specified, Maximum amount is 200. (Cooldown: 1 use per 60 mins, Use wisely.)"""
        if user == ctx.bot.user:
            await ctx.send("HA! You think it'll work against me?? Nice Try.")
            user = ctx.message.author
            await asyncio.sleep(2)

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
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
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

    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
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
        Picks between multiple options!
        Options are separated by spaces; to include spaces in an option,
        you should put quotes around the option.
        """
        if not options or len(options) == 1:
            await ctx.send("Provide two or more options")
        else:
            await ctx.send(f"I pick **{random.choice(options)}**!")

    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    @commands.command()
    async def gif(self, ctx, *, query: str = "rickroll"):
        """find a gif
        Usage: gif <query>"""
        await ctx.trigger_typing()
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

    @commands.command(aliases=["math"])
    async def calc(self, ctx, *, calculation):
        """Simple calculator. Ex: [p]calc 2+2"""
        if len(calculation) > 20:
            await ctx.send(embed=discord.Embed(description="⚠ You can only input 16 characters at most!"))
            return
        equation = calculation.strip().replace("^", "**").replace("x", "*")
        try:
            if "=" in equation:
                left = eval(
                    equation.split("=")[0], {"__builtins__": None}, {"sqrt": sqrt}
                )
                right = eval(
                    equation.split("=")[1], {"__builtins__": None}, {"sqrt": sqrt}
                )
                answer = str(left == right)
            else:
                answer = str(eval(equation, {"__builtins__": None}, {"sqrt": sqrt}))
        except TypeError:
            return await ctx.send(embed=discord.Embed(description="⚠ Invalid calculation query."))
        except ZeroDivisionError:
            return await ctx.send(embed=discord.Embed(description="You must be joking."))

        em = discord.Embed(color=0xD3D3D3, title="Calculator")
        em.add_field(
            name="Input:",
            value=calculation.replace("**", "^").replace("x", "*"),
            inline=False,
        )
        em.add_field(name="Output:", value=answer, inline=False)
        await ctx.send(content=None, embed=em)
        await ctx.message.delete()

    @commands.command(aliases=["msgdump"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def messagedump(self, ctx, filename, limit, details="yes", reverse="no"):
        """Dump messages."""
        await ctx.message.delete()
        await ctx.send("Downloading messages...")
        if not os.path.isdir("data/message_dump"):
            os.mkdir("data/message_dump")
        with open(
            "data/message_dump/" + filename.rsplit(".", 1)[0] + ".txt",
            "w+",
            encoding="utf-8",
        ) as f:
            if reverse == "yes":
                if details == "yes":
                    async for message in ctx.message.channel.history(limit=int(limit)):
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
        await ctx.send("Finished downloading!")
    
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    @commands.command(aliases=["getcolor","color","getcolour"])
    async def colour(self, ctx, *, colour_codes: str):
        """Posts color of given hex"""
        colour_codes = colour_codes.split()
        size = (60, 80) if len(colour_codes) > 1 else (200, 200)
        if len(colour_codes) > 5:
            return await ctx.send("Sorry, 5 colour codes maximum")
        for colour_code in colour_codes:
            if not colour_code.startswith("#"):
                colour_code = "#" + colour_code
            image = Image.new("RGB", size, colour_code)
            with io.BytesIO() as file:
                image.save(file, "PNG")
                file.seek(0)
                await ctx.send(
                    "Colour with hex code {}:".format(colour_code),
                    file=discord.File(file, "colour_file.png"),
                )

    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    @commands.command(aliases=["channels","allchannel"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def allchannels(self, ctx, serverid: int = None):
        """Shows ALL Channels on this server."""
        if serverid is None:
            server = ctx.guild
        else:
            server = discord.utils.get(self.bot.guilds, id=serverid)
            if server is None:
                await ctx.send("Server not found!")
                return
        
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

    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    @commands.command(aliases=["members"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def allmembers(self, ctx, serverid: int = None):
        """Get all members in this server"""
        if serverid is None:
            server = ctx.guild
        else:
            server = discord.utils.get(self.bot.guilds, id=serverid)
            if server is None:
                return await ctx.send("Server not found!")
                return

        bots = ""
        bots_amount = 0
        members = ""
        members_amount = 0
        total = 0
        everything =""

        for x in server.members:
            if x.bot is True:
                bots += f"[BOT][{x.id}]\t{x}\n"
                bots_amount += 1
                total += 1
            else:
                members += f"[USER][{x.id}]\t{x}\n"
                members_amount += 1
                total += 1

        loading = await ctx.send(embed=discord.Embed(title="Please Wait..."), delete_after=3)
        everything = f"Server: {server.name}\nID: {server.id}\nMember Amount: {members_amount}\nBot Amount: {bots_amount}\nTotal: {total}\n\nMember List:\n{members + bots}"        
        data = BytesIO(everything.encode('utf-8'))
        await ctx.send(content=f"**{server.name}'s Member List**", file=discord.File(data, filename=f"{server.name}_Member_Lists.txt"))
        await loading.delete()

    @commands.command(aliases=["allrole","roles"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def allroles(self, ctx, serverid: int = None):
        """Get all roles in current server"""
        allroles = ""

        if serverid is None:
            server = ctx.guild
        else:
            server = discord.utils.get(self.bot.guilds, id=serverid)
            if server is None:
                await ctx.send("Server not found!")
                return

        async with ctx.typing():
            for num, role in enumerate(sorted(server.roles, reverse=True), start=1):
                allroles += f"[{str(num).zfill(2)}] {role.id}\t[ Users: {len(role.members)} ]\t{role.name}\t\r\n"
                loading = await ctx.send(embed=discord.Embed(title="Please Wait..."), delete_after=3)
                data = BytesIO(allroles.encode('utf-8'))
                await ctx.send(content=f"Roles in **{server.name}**", file=discord.File(data, filename=f"{server.name}_Role_Lists.txt"))
                await loading.delete()

    @commands.command(aliases=["discriminator","tagnum","tags"])
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

    @commands.has_permissions(add_reactions=True)
    @commands.command()
    async def poll(self, ctx, *, msg: commands.clean_content):
        """Create a poll using reactions. [p]help poll for more information.
        [p]poll <question> | <answer> | <answer> - Create a poll. You may use as many answers as you want, placing a pipe | symbol in between them.
        Example:
        [p]poll What is your favorite anime? | Steins;Gate | Naruto | Attack on Titan | Shrek
        You can also use the "time" flag to set the amount of time in seconds the poll will last for.
        Example:
        [p]poll What time is it? | HAMMER TIME! | SHOWTIME! | time=10
        """
        await ctx.message.delete()
        options = msg.split(" | ")
        time = [x for x in options if x.startswith("time=")]
        if time:
            time = time[0]
        if time:
            options.remove(time)
        if len(options) <= 1:
            return await ctx.send("You must have 2 options or more.")
        if len(options) >= 11:
            return await ctx.send("You must have 9 options or less.")
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
        poll_msg = await ctx.send(confirmation_msg)
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
        await ctx.send(end_msg)

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing the question.')
            return

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

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: commands.clean_content):
        """Makes a poll quickly.
        The first argument is the question and the rest are the choices.
        """

        def to_emoji(c):
            base = 0x1f1e6
            return chr(base + c)

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
        if a is None or b is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        else:
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Your randomized number:')
            em.description = random.randint(a,b)
            await ctx.send(embed=em)

    @commands.command(aliases=["qr"])
    async def qrmaker(self, ctx, *, data: str):
        """Allows you to make a custom QR Code"""
        if not os.path.isdir("data/qrcodes"):
            os.mkdir("data/qrcodes")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"data/qrcodes/QR_{ctx.author.name}_{ctx.message.id}.png")
        await ctx.send(f"{ctx.author.mention}", file=discord.File(f"data/qrcodes/QR_{ctx.author.name}_{ctx.message.id}.png"))
        # os.remove(f"data/qrcodes/QR_{ctx.author.name}_{ctx.message.id}.png") #Feel free to disable the removal

    @commands.command(aliases=["qrinv"])
    @commands.guild_only()
    @commands.has_permissions(create_instant_invite=True)
    async def qrinvite(self, ctx, age: int = 86400, uses: int = 0, temp: bool = False):
        """
        Allows you to create a QR Code of the invite link of this server
        Make sure to adjust the available options to suite your need!
        Set the `age` (defaults to 1 day) and `uses` argument to 0 to make a permanent link (default behavior)
        """
        if not os.path.isdir("data/qrcodes"):
            os.mkdir("data/qrcodes")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )

        link = await ctx.channel.create_invite(max_age = age, max_uses = uses, temporary = temp)
        qr.add_data(link)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"data/qrcodes/QR_{ctx.author.name}_{ctx.message.id}.png")
        await ctx.send(f"{ctx.author.mention}", file=discord.File(f"data/qrcodes/QR_{ctx.author.name}_{ctx.message.id}.png"))
        os.remove(f"data/qrcodes/QR_{ctx.author.name}_{ctx.message.id}.png") #Feel free to disable the removal


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
    async def mock(self, ctx, *, txt: commands.clean_content):
        lst = [str.upper, str.lower]
        newText = await commands.clean_content().convert(ctx, ''.join(random.choice(lst)(c) for c in txt))
        if len(newText) <= 900:
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
            if len(result) <= 256:
                await ctx.send(result)
            else:
                try:
                    await ctx.author.send(result)
                    await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
                except Exception:
                    await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")
        else:
            await ctx.send("```fix\nError: The number can only be from 1 to 5```")

    @commands.command(aliases=["rev"])
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

    @commands.command(aliases=["ascii2hex","a2h"])
    async def texttohex(self, ctx, *, txt: str):
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

    @commands.command(aliases=["hex2ascii","h2a"])
    async def hextotext(self, ctx, *, txt: str):
        try:
            cleanS = await commands.clean_content().convert(ctx, bytearray.fromhex(txt).decode())
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/hexadecimal/#data**")
            return
        if len(cleanS) <= 479:
            await ctx.send(f"```{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```{cleanS}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["ascii2bin","a2b"])
    async def texttobinary(self, ctx, *, txt: str):
        try:
            cleanS = await commands.clean_content().convert(ctx, ' '.join(format(ord(x), 'b') for x in txt))
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data**")
            return
        if len(cleanS) <= 479:
            await ctx.send(f"```fix\n{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```fix\n{cleanS}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(aliases=["bin2ascii","b2a"])
    async def binarytotext(self, ctx, *, txt: str):
        try:
            cleanS = await commands.clean_content().convert(ctx, ''.join([chr(int(txt, 2)) for txt in txt.split()]))
        except Exception as e:
            await ctx.send(f"**Error: `{e}`. This probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data**")
            return
        if len(cleanS) <= 479:
            await ctx.send(f"```{cleanS}```")
        else:
            try:
                await ctx.author.send(f"```{cleanS}```")
                await ctx.send(f"**{ctx.author.mention} The output too was too large, so I sent it to your DMs! :mailbox_with_mail:**")
            except Exception:
                await ctx.send(f"**{ctx.author.mention} There was a problem, and I could not send the output. It may be too large or malformed**")

    @commands.command(hidden=True)
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
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
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
        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured! Make sure the IP and the formatting are correct!"))
        except KeyError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured! Make sure the IP and the formatting are correct!"))

    @commands.group(invoke_without_command=True, aliases=["mrs"])
    async def morse(self, ctx):
        """
        Converts ASCII Characters to Morse code and Vice Versa.
        """
        mainemb = discord.Embed(description="This command can help you translate morse codes.\nHere are the available commands:")
        mainemb.add_field(name="ASCII to Morse conversion", value="`[p]morse a2m [text]`")
        mainemb.add_field(name="Morse to ASCII conversion", value="`[p]morse m2a [text]`")
        await ctx.send(embed=mainemb)

    @morse.command(name="m2a", brief = "Convert Morse code to ASCII", aliases=["morse2ascii"])
    async def morse2ascii(self, ctx, * , text:commands.clean_content = None):
        if text is None:
            await ctx.send(embed=discord.Embed(description="⚠ Please specify the input."))
            return

        inverseMorseAlphabet = dict((v, k) for (k, v) in morseAlphabet.items())

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
    async def ascii2morse(self, ctx, * ,text: commands.clean_content = None):
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
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def nationality(self, ctx, * ,name: str = None):
        """
        This command predicts the nationality of a person given their name.
        API Provided by: `https://nationalize.io/`
        """

        if name is None:
            await ctx.send(embed=discord.Embed(description="Please input the name."))
            return

        await ctx.trigger_typing()

        fin_name = name.replace(" ","+")

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.nationalize.io/?name={fin_name}') as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                
        try:
            answer = data["name"]
            country = data.country[0].country_id
            probability = data.country[0].probability
        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured! Cannot determine the result."))
            return
            
        percentage = float(probability) * 100
        floorPercentage = floor(percentage)

        emb = discord.Embed(description="Predict the nationality of a name!", color = ctx.author.color, timestamp = datetime.utcnow())
        emb.add_field(name="Name", value=answer.title())
        emb.add_field(name="Country", value=f"{country} :flag_{country.lower()}:")
        emb.add_field(name="Probability", value=f"{floorPercentage}%")
        emb.set_footer(text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(aliases=["wth"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def weather(self, ctx, *, city: str = None):
        """
        A command to check weather status
        API Provided by: OpenWeatherMap.org
        """

        if city is None:
            await ctx.send(embed=discord.Embed(description="Please provide the city name!"))
            return

        await ctx.trigger_typing()

        with open("cogs/data/weather_api_key.json") as json_fp:
            classified = json.load(json_fp)
            key = classified["key"]

        locate = city.replace(" ", "+")

        def degToCompass(deg): # https://stackoverflow.com/a/7490772 https://www.windfinder.com/wind/windspeed.htm
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

        def metertokilometer(meter): # https://www.asknumbers.com/meters-to-km.aspx
            km = meter * 0.001
            return km

        def wind_condition(wind_speed): # In Meter/second https://www.windfinder.com/wind/windspeed.htm
            if wind_speed > 0 and wind_speed < 0.2:
                return "Calm"
            elif wind_speed > 0.3 and wind_speed < 1.5:
                return "Light Air"
            elif wind_speed > 1.6 and wind_speed < 3.3:
                return "Light Breeze"
            elif wind_speed > 3.4 and wind_speed < 5.4:
                return "Gentle Breeze"
            elif wind_speed > 5.5 and wind_speed < 7.9:
                return "Moderate Breeze"
            elif wind_speed > 8.0 and wind_speed < 10.7:
                return "Fresh Breeze"
            elif wind_speed > 10.8 and wind_speed < 13.8:
                return "Strong Breeze"
            elif wind_speed > 13.9 and wind_speed < 17.1:
                return "Near Gale"
            elif wind_speed > 17.2 and wind_speed < 20.7:
                return "Gale"
            elif wind_speed > 20.8 and wind_speed < 24.4:
                return "Severe Gale"
            elif wind_speed > 24.5 and wind_speed < 28.4:
                return "Strong Storm"
            elif wind_speed > 28.5 and wind_speed < 32.6:
                return "Violent Storm"
            elif wind_speed > 32.7:
                return "Hurricane"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://api.openweathermap.org/data/2.5/weather?q={locate}&appid={key}&units=metric") as resp:
                    resp.raise_for_status()
                    data = json.loads(await resp.read(), object_hook=DictObject)
                    

            code = data.cod

            if code is not 200:
                msg = data.message
                if code is 404:
                    await ctx.send(embed=discord.Embed(description="City cannot be found!"))
                    return
                elif code is 401:
                    await ctx.send(embed=discord.Embed(description="Invalid API Key!"))
                    return
                else:
                    await ctx.send(embed=discord.Embed(description=f"An Error Occured! `{msg}` (Code: `{code}`)"))
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
            temp_f =  pytemperature.c2f(temp_c)
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
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured while parsing the data."))
            return
        except KeyError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error Occured while parsing the data."))
            return
        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status == 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status == 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status >= 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access the REST API, it may be down or inaccessible at the moment."))
                return
            else:
                await ctx.send(embed=discord.Embed(description="⚠ Undefined Error."))
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
        elif temp_c < 2:
            colours = discord.Colour(0x0000FF)
        else:
            colours = discord.Colour(0x36393E)

        def emovisibconf(mtr):
            if mtr > 8000:
                return "😀"
            elif mtr < 8000 and mtr > 7000:
                return "🙂"
            elif mtr < 6000 and mtr > 5000:
                return "😐"
            elif mtr < 4000 and mtr > 3000:
                return "🙁"
            elif mtr < 3000 and mtr > 2500:
                return "😧"
            elif mtr < 2000 and mtr > 1500:
                return "😨"
            elif mtr < 1000 and mtr > 500:
                return "😱"
            elif mtr < 499:
                return "💀"
            else:
                return "🤔"


        calculated_sunrise = datetime.fromtimestamp(sunrise + timezone_offset)
        calculated_sunset = datetime.fromtimestamp(sunset + timezone_offset)

        embed = discord.Embed(title="Weather Information", timestamp=datetime.utcnow(), color=colours)
        embed.set_thumbnail(url=icon)

        embed.add_field(name="🏙 City Name", value=cityname, inline=False)
        embed.add_field(name="🏳 Country ID", value=f"{countryid} {country_flags}", inline=False)
        embed.add_field(name="🌻 Weather Status", value=status, inline=False)
        embed.add_field(name="ℹ Condition", value=description.title(), inline=False)
        embed.add_field(name="🌐 Longitude", value=lon, inline=True)
        embed.add_field(name="🌐 Latitude", value=lat, inline=True)
        embed.add_field(name="🌄 Sunrise", value=f"{calculated_sunrise} (UTC)", inline=True)
        embed.add_field(name="🌇 Sunset", value=f"{calculated_sunset} (UTC)", inline=True)
        embed.add_field(name="🌡 Current Temperature", value=f"{temp_c} °C ({temp_f} °F)", inline=True)
        embed.add_field(name="🌡 Feels Like", value=f"{feels_c} °C ({feels_f} °F)", inline=True)
        embed.add_field(name="🌡 Min Temperature", value=f"{t_min_c} °C ({t_min_f} °F)", inline=True)
        embed.add_field(name="🌡 Max Temperature", value=f"{t_max_c} °C ({t_max_f} °F)", inline=True)
        embed.add_field(name="☁ Cloudiness", value=f"{clouds}%", inline=True)
        embed.add_field(name="🍃Atmospheric Pressure", value=f"{pressure} hPa", inline=True)
        embed.add_field(name="🌬 Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="👀 Visibility", value=f"{vis} Meter ({metertokilometer(vis)} KM) {emovisibconf(vis)}", inline=True)
        embed.add_field(name="💨 Wind Speed", value=f"{wind} m/sec ({wind_condition(wind)})", inline=True)
        embed.add_field(name="🧭 Wind Direction", value=f"{wind_degree}° {wind_direction}", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="define",aliases=["definition", "dictionary"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _define(self, ctx, *, arg):
        msg = await ctx.send("Looking for a definition...")
        try:
            #--Connect to unofficial Google Dictionary API and get results--#
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.dictionaryapi.dev/api/v1/entries/en/{arg}') as r:
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
                    embed = discord.Embed(title=f":blue_book: Google Definition for {word}", color=0x8253c3)
                    #--Then we add see if the variables are defined and if they are, those variables to an embed and send it back to Discord--#
                    if origin == None:
                        pass
                    else:
                        embed.add_field(name="Origin:", value=origin, inline=False)
                    if noun_def == None:
                        pass
                    else:
                        if noun_eg == None:
                            embed.add_field(name="As a Noun:", value=f"**Definition:** {noun_def}", inline=False)
                        else:
                            embed.add_field(name="As a Noun:", value=f"**Definition:** {noun_def}\n**Example:** {noun_eg}", inline=False)
                    if verb_def == None:
                        pass
                    else:
                        if verb_eg == None:
                            embed.add_field(name="As a Verb:", value=f"**Definition:** {verb_def}", inline=False)
                        else:
                            embed.add_field(name="As a Verb:", value=f"**Definition:** {verb_def}\n**Example:** {verb_eg}", inline=False)
                    if prep_def == None:
                        pass
                    else:
                        if prep_eg == None:
                            embed.add_field(name="As a Preposition:", value=f"**Definition:** {prep_def}", inline=False)
                        else:
                            embed.add_field(name="As a Preposition:", value=f"**Definition:** {prep_def}\n**Example:** {prep_eg}", inline=False)
                    if adverb_def == None:
                        pass
                    else:
                        if adverb_eg == None:
                            embed.add_field(name="As an Adverb:", value=f"**Definition:** {adverb_def}", inline=False)
                        else:
                            embed.add_field(name="As a Adverb:", value=f"**Definition:** {adverb_def}\n**Example:** {adverb_eg}", inline=False)
                    if adject_def == None:
                        pass
                    else:
                        if adject_eg == None:
                            embed.add_field(name="As an Adjective:", value=f"**Definition:** {adject_def}", inline=False)
                        else:
                            embed.add_field(name="As an Adjective:", value=f"**Definition:** {adject_def}\n**Example:** {adject_eg}", inline=False)
                    if pronoun_def == None:
                        pass
                    else:
                        if pronoun_eg == None:
                            embed.add_field(name="As a Pronoun:", value=f"**Definition:** {pronoun_def}", inline=False)
                        else:
                            embed.add_field(name="As a Pronoun:", value=f"**Definition:** {pronoun_def}\n**Example:** {pronoun_eg}", inline=False)
                    if exclaim_def == None:
                        pass
                    else:
                        if exclaim_eg == None:
                            embed.add_field(name="As an Exclamation:", value=f"**Definition:** {exclaim_def}", inline=False)
                        else:
                            embed.add_field(name="As an Exclamation:", value=f"**Definition:** {exclaim_def}\n**Example:** {exclaim_eg}", inline=False)
                    if poss_determ_def == None:
                        pass
                    else:
                        if poss_determ_eg == None:
                            embed.add_field(name="As a Possessive Determiner:", value=f"**Definition:** {poss_determ_def}", inline=False)
                        else:
                            embed.add_field(name="As a Possessive Determiner:", value=f"**Definition:** {poss_determ_def}\n**Example:** {poss_determ_eg}", inline=False)
                    if abbrev_def == None:
                        pass
                    else:
                        if abbrev_eg == None:
                            embed.add_field(name="As an Abbreviation:", value=f"**Definition:** {abbrev_def}", inline=False)
                        else:
                            embed.add_field(name="As an Abbreviation:", value=f"**Definition:** {abbrev_def}\n**Example:** {abbrev_eg}", inline=False)
                    if crossref_def == None:
                        pass
                    else:
                        if crossref_eg == None:
                            embed.add_field(name="As a Cross-Reference:", value=f"**Definition:** {crossref_def}", inline=False)
                        else:
                            embed.add_field(name="As a Cross-Reference:", value=f"**Definition:** {crossref_def}\n**Example:** {crossref_eg}", inline=False)
                    await msg.edit(content='',embed=embed)
        except:
            #--Send error message if command fails, as it's assumed a definition isn't found--#
            await msg.edit(content=":x: Sorry, I couldn't find that word. Check your spelling and try again.")

def setup(bot):
    bot.add_cog(Utilities(bot))
    print("Utilities Module has been loaded.")
    