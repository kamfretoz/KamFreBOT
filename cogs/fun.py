import asyncio
import random
import time

import discord
import libneko
import requests
from discord.ext import commands
from libneko import embeds


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.jynxed = {}

    @commands.command(aliases=["talk", "speak"])
    # @commands.bot_has_permissions(manage_messages=True)
    async def say(self, ctx, *, text=None):
        """Say whatever you typed in"""
        try:
            if text is None:
                await ctx.send("❓ What do you want me to say?", delete_after=5.0)
                await ctx.message.add_reaction("❓")
            else:
                await ctx.trigger_typing()
                await ctx.send(text)
                await ctx.message.delete()
        except:
            pass

    # Say to all members command
    @commands.command(
        aliases=["stoall"], hidden=True,
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def saytoall(self, ctx, *, text=None):
        """Send a message to every member on the server (Can only be used by Administrator)"""
        try:
            if text is None:
                await ctx.send("What do you want to me to send?")
                await ctx.message.add_reaction("❓")
            else:
                await ctx.send(f"Now Sending to {len(ctx.guild.members)} Users!")
                await ctx.message.add_reaction("✔")
                for users in ctx.guild.members:
                    if users.bot is False:
                        await users.send(text)
                        await asyncio.sleep(5)
        except discord.Forbidden:
            pass

    # Say Command with TTS
    @commands.command(aliases=["ttstalk", "speaktts"], hidden=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def saytts(self, ctx, *, text=None):
        """Say whatever you typed in, this time with TTS!"""
        if text is None:
            await ctx.send("❓ What do you want me to say?", delete_after=10.0)
            await ctx.message.add_reaction("❓")
        else:
            try:
                await ctx.message.delete()
                await ctx.trigger_typing()
                await ctx.send(content=text, tts=True)
            except discord.Forbidden:
                await ctx.author.send(
                    ":no_entry_sign: I'm not allowed to send message here!",
                    delete_after=10.0,
                )
            except discord.NotFound:
                await ctx.send(
                    ":grey_exclamation: ERROR: Original message not found! (404 UNKNOWN MESSAGE)"
                )
            except discord.ext.commands.BotMissingPermissions:
                await ctx.send(
                    "I don't have permission to delete the original message!",
                    delete_after=5.0,
                )

    @commands.command(aliases=["sto"])
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sayto(self, ctx, destination: discord.TextChannel, *, text=None):
        """Send whatever you want to specific channel"""
        if text is None:
            await ctx.send("What do you want me to say?", delete_after=10.0)
            await ctx.message.add_reaction("❓")
        else:
            try:
                await ctx.message.delete()
                await destination.trigger_typing()
                await destination.send(text)
            except discord.Forbidden:
                await ctx.send(
                    f"I'm not allowed to send a message on #{destination}!",
                    delete_after=10.0,
                )
            except discord.ext.commands.BotMissingPermissions:
                await ctx.send(
                    "I don't have permission to delete the original message!",
                    delete_after=5.0,
                )

    @commands.command(aliases=["send", "dm"])
    @commands.guild_only()
    async def sendto(
        self, ctx, target: libneko.converters.MemberConverter = None, *, text=None
    ):
        """Send whatever you want to a user's DM"""
        if text is None:
            await ctx.send("What do you want me to say?", delete_after=10.0)
            await ctx.message.add_reaction("❓")
        elif target is None:
            await ctx.send("Where do you want me to send it?", delete_after=10.0)
            await ctx.message.add_reaction("❓")
        else:
            try:
                await ctx.send("Sending Message!", delete_after=3.0)
                await target.send(text)
                await ctx.send("Message Sent!", delete_after=3.0)
                await ctx.message.delete()
            except discord.Forbidden:
                await ctx.send(
                    f"I'm not allowed to send a message to {target}!", delete_after=5.0
                )
            except discord.HTTPException:
                await ctx.send("Invalid User Specified!")

    # Flipcoin command
    @commands.cooldown(rate=3, per=3.0)
    @commands.command(aliases=["flipcoin", "coin"])
    async def coinflip(self, ctx):
        """Heads or Tails!"""
        choices = ["Head!", "Tail!"]
        # flip = discord.Embed(title="Flip The Coin!", color=0xFFFFFF)
        # flip.set_image(url=random.choice(choices))
        await ctx.send(random.choice(choices))

    # 8Ball Command
    @commands.command(name="8ball", aliases=["ball","8b"])
    async def ball(self, ctx, *, question: str):
        """Ask a question to the 8Ball!"""
        ps = {
            "psgood": [
                "Yes",
                "It is certain",
                "It is decidedly so",
                "Without a doubt",
                "Yes - definitely",
                "You may rely on it",
                "As I see it, yes",
                "Most likely",
                "Outlook good",
                "Signs point to yes",
            ],
            "psmed": [
                "Reply hazy, try again",
                "Ask again later",
                "Better not tell you now",
                "Cannot predict now",
                "Concentrate and ask again",
            ],
            "psbad": [
                "Don't count on it",
                "My reply is no",
                "My sources say no",
                "Outlook not so good",
                "Very doubtful",
            ],
        }

        choice = random.choice(random.choice(list(ps.values())))

        if choice in ps["psbad"]:
            color = discord.Color(0xFF0000)
        elif choice in ps["psmed"]:
            color = discord.Color(0xFFFF00)
        elif choice in ps["psgood"]:
            color = discord.Color(0x26D934)

        eightball = discord.Embed(color=color)
        eightball.add_field(name="Question:", value=question.capitalize())
        eightball.add_field(name="Answer:", value=f"{choice}.")
        eightball.set_author(
            name="The mighty 8-Ball", icon_url="https://i.imgur.com/Q9dxpTz.png"
        )
        await ctx.send(embed=eightball, content=None)

    @commands.command(hidden=True, aliases=["ily"])
    async def iloveyou(self, ctx):
        await ctx.send(f"{ctx.author.mention}, I love you too! :heart::heart::heart:")

    @commands.command(aliases=["rr"], brief="Never gonna give you up...")
    async def rickroll(self, ctx):
        rick = discord.Embed()
        rick.set_image(url="https://tenor.com/view/rick-roll-deal-with-it-rick-astley-never-gonna-give-you-up-gif-14204545")
        await ctx.send(embed=rick)

    @commands.command(
        aliases=["bg"], disabled=True, brief="Make your text 🇧 🇮 🇬"
    )
    async def bigtext(self, ctx, *, text: str):
        s = ""
        for char in text:
            if char.isalpha():
                s += f":regional_indicator_{char.lower()}: "
            elif char.isspace():
                s += "   "
        await ctx.send(s)

    @commands.command(aliases=["kitty", "kitten", "kat"], brief="Send cute cat pics")
    async def cat(self, ctx):
        r = requests.get("https://api.thecatapi.com/v1/images/search").json()
        url = r[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute kitty :D", color=color)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["doggie","doge"], brief="Send cute dog pics")
    async def dog(self, ctx):
        r = requests.get("https://api.thedogapi.com/v1/images/search").json()
        url = r[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute doggo!! :D", color=color)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["googleit", "searchit"])
    async def lmgtfy(self, ctx, *, query: str):
        """Search Google the fun way ;)"""
        result = f"http://lmgtfy.com/?q={query}"
        final = result.replace(" ", "+")
        gugel = discord.Embed(
            title=f"Searching for: **{query}**", description=f"[Click Here]({final})"
        )
        gugel.set_image(
            url="https://lmgtfy.com/assets/logo-color-small-70dbef413f591a3fdfcfac7b273791039c8fd2a5329e97c4bfd8188f69f0da34.png"
        )
        await ctx.send(embed=gugel, content=None)

    @commands.command(aliases=["succ"])
    async def zucc(self, ctx):
        """Gives you the zucc"""
        zuccy = discord.Embed()
        zuccy.set_image(
            url="https://pics.me.me/he-protec-he-attac-but-most-importantly-he-zucc-28716903.png"
        )
        await ctx.send(embed=zuccy, content="<:zucc:451945809144184862>")

    @commands.cooldown(rate=1, per=15, type=commands.BucketType.guild)
    @commands.command(
        name="curse", aliases=("oppugno", "jynx", "kutuk", "santet"), hidden=True
    )
    async def emoji_curse(
        self, ctx, user: discord.Member, emoji: discord.Emoji, *, text=None
    ):
        emoji = (
            self.bot.get_emoji(int(emoji.split(":")[2].strip(">")))
            if "<:" in emoji or "<a:" in emoji
            else emoji
        )
        cursed = self.jynxed.get(f"{user.id}@{ctx.guild.id}")
        if cursed is not None:
            await ctx.channel.send(
                embed=embeds.Embed(
                    description=f"{user.mention} sudah tersantet!",
                    color=discord.Colour.dark_purple(),
                )
            )
        else:
            try:
                await ctx.message.add_reaction(emoji)
            except:
                await ctx.send(
                    embed=embeds.Embed(
                        description=":octagonal_sign: Emoji tidak ditemukan!",
                        color=discord.Colour.red(),
                    )
                )
            else:

                def check(msg):
                    return ctx.guild.id == msg.guild.id and msg.author.id == user.id

                async def curse_task(self):
                    await ctx.channel.send(
                        embed=embeds.Embed(
                            description=f":purple_heart: {user.mention} telah disantet dengan {emoji}. Pengaruh nya akan hilang dalam 30 menit.",
                            color=discord.Colour.purple(),
                        )
                    )
                    start = time.monotonic()
                    while time.monotonic() - start < 1800:
                        if text is None:
                            # print(f"\n3rd\n{self.jynxed}")
                            msg = await self.bot.wait_for("message", check=check)
                            try:
                                await msg.add_reaction(emoji)
                            except:
                                pass
                        else:
                            # print(f"\n3rd\n{self.jynxed}")
                            msg = await self.bot.wait_for("message", check=check)
                            try:
                                await msg.add_reaction(emoji)
                                await ctx.send(f"<@{user.id}> {text}")
                            except:
                                pass

                    del self.jynxed[f"{user.id}@{ctx.guild.id}"]

                curse = self.bot.loop.create_task(curse_task(self))
                self.jynxed.update({f"{user.id}@{ctx.guild.id}": curse})

    @commands.command(
        name="bless", aliases=("ruqyah", "finitincantatem", "countercurse"), hidden=True
    )
    async def emoji_bless(self, ctx, user: discord.Member):
        """Cure someone from a curse"""
        cursed = self.jynxed.get(f"{user.id}@{ctx.guild.id}")
        if user == ctx.author and user != self.bot.creator:
            await ctx.send(
                embed=embeds.Embed(
                    description=":octagonal_sign: Anda tidak dapat me-ruqyah diri sendiri!",
                    color=discord.Colour.red(),
                )
            )
        elif cursed is not None:
            cursed.cancel()
            del self.jynxed[f"{user.id}@{ctx.guild.id}"]
            await ctx.send(
                embed=embeds.Embed(
                    description=f":green_heart: {user.mention} telah berhasil di ruqyah!",
                    color=discord.Colour.from_rgb(55, 147, 105),
                )
            )
        else:
            await ctx.send(
                embed=embeds.Embed(
                    description=f":octagonal_sign: {user.mention} Tidak sedang di santet!",
                    color=discord.Colour.red(),
                )
            )

def setup(bot):
    bot.add_cog(Fun(bot))
    print("Fun Module has been loaded.")
