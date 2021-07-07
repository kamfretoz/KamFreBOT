import asyncio
import aiohttp
import time

from discord.ext import commands

from discord.ext.commands.core import command
import data.quotes as quotes
import discord
import libneko
import json
import ciso8601
import data.topics as topics
#import discord_argparse
from textwrap import shorten
from datetime import datetime
from random import randint, choice
from io import BytesIO
from libneko import embeds
from owoify import Owoifator
from vaporwavely import vaporipsum, vaporize


from modules.http import HttpCogBase
from modules.dictobj import DictObject

with open("cogs/data/ksoft-api_key.json") as json_fp:
    classified = json.load(json_fp)
    ksoft_key = classified["key"]


class Fun(HttpCogBase):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.jynxed = {}
        self.loop = asyncio.get_event_loop()

    @commands.command(aliases=["talk", "speak", "sy"])
    @commands.bot_has_permissions(manage_messages=True)
    async def say(self, ctx, *, text: commands.clean_content = None):
        """Say whatever you typed in"""
        try:
            if text is None:
                await ctx.send("❓ What do you want me to say?", delete_after=5.0)
                await ctx.message.add_reaction("❓")
            else:
                await ctx.message.delete()
                await ctx.trigger_typing()
                await ctx.send(text)
        except:
            pass

    @commands.command(aliases=["sghost", "sayg", "sg"])
    @commands.bot_has_permissions(manage_messages=True)
    async def sayghost(self, ctx, *, text: commands.clean_content = None):
        """Say whatever you typed in and immediately deletes it"""
        try:
            if text is None:
                await ctx.send("❓ What do you want me to say?", delete_after=5.0)
                await ctx.message.add_reaction("❓")
            else:
                await ctx.message.delete()
                await ctx.trigger_typing()
                await ctx.send(text, delete_after=1)
        except:
            pass

    # Say Command with TTS
    @commands.command(aliases=["ttstalk", "speaktts"], hidden=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def saytts(self, ctx, *, text=None):
        """Say whatever you typed in, this time with TTS!"""
        if text == None:
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

    @commands.command(aliases=["embedsay", "syd", "emb"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def sayembed(self, ctx, *, message: commands.clean_content = None):
        '''A command to embed messages quickly.'''
        if message is None:
            await ctx.send(discord.Embed(description="❓ What do you want me to say?", delete_after=5))
            await ctx.message.add_reaction("❓")
        else:
            await ctx.message.delete()
            em = discord.Embed(color=randint(0, 0xFFFFFF),
                               timestamp=datetime.utcnow())
            em.description = message
            em.set_footer(icon_url=ctx.message.author.avatar_url,
                          text=f"Sent by: {ctx.message.author}")
            await ctx.send(embed=em)

    @commands.command(aliases=["sto"])
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sayto(self, ctx, destination: discord.TextChannel, *, text=None):
        """Send whatever you want to specific channel"""
        if text == None:
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

    # Flipcoin command
    @commands.cooldown(rate=3, per=3.0)
    @commands.command(aliases=["flipcoin", "coin"], hidden=True)
    async def coinflip(self, ctx):
        """Heads or Tails!"""
        choices = ["https://i.imgur.com/vzcNPdF.png",
                   "https://i.imgur.com/9YBSnmr.png"]  # Put your custom coin image here.
        flip = discord.Embed(title="Flip The Coin!", color=0xFFFFFF)
        flip.set_image(url=choice(choices))
        await ctx.send(embed=flip)

    @commands.command(aliases=["bqt"], hidden=True)
    async def bobertquote(self, ctx):
        """Send a random Bobert Quote!"""
        choices = str(choice(quotes.bobert))
        embed_quote = discord.Embed(
            title="Bobert said...", description=f"{choices}")
        embed_quote.set_thumbnail(url="https://i.imgur.com/zcVN4q1.png")
        await ctx.send(embed=embed_quote)

    @commands.command(hidden=True)
    async def dance(self, ctx):
        """Bobert Dance!"""
        bdance = discord.Embed()
        bdance.set_image(url="https://i.imgur.com/1DEtTrQ.gif")
        await ctx.send(embed=bdance)

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ['❤', '💛', '💚', '💙', '💜', '♥']
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{choice(hearts)}")

    @commands.command(aliases=['tf'])
    async def textface(self, ctx, Type: str = None):
        """Get those dank/cool faces here. Type *textface list for a list."""
        if Type is None:
            await ctx.send('That is NOT one of the dank textfaces in here yet. Use: [p]textface [lenny/tableflip/shrug]')
        else:
            if Type.lower() == 'lenny':
                await ctx.send('( ͡° ͜ʖ ͡°)')
            elif Type.lower() == 'tableflip':
                await ctx.send('(ノಠ益ಠ)ノ彡┻━┻')
            elif Type.lower() == 'shrug':
                await ctx.send('¯\_(ツ)_/¯')
            elif Type.lower() == 'bignose':
                await ctx.send('(͡ ͡° ͜ つ ͡͡°)')
            elif Type.lower() == 'iwant':
                await ctx.send('ლ(´ڡ`ლ)')
            elif Type.lower() == 'musicdude':
                await ctx.send('ヾ⌐*_*ノ♪')
            elif Type.lower() == 'wot':
                await ctx.send('ლ,ᔑ•ﺪ͟͠•ᔐ.ლ')
            elif Type.lower() == 'bomb':
                await ctx.send('(´・ω・)っ由')
            elif Type.lower() == 'orlly':
                await ctx.send("﴾͡๏̯͡๏﴿ O'RLY?")
            elif Type.lower() == 'money':
                await ctx.send('[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]')
            elif Type.lower() == 'list':
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(color=color, title='List of Textfaces')
                em.description = 'Choose from the following: lenny, tableflip, shrug, bignose, iwant, musicdude, wot, bomb, orlly, money. Type *textface [face].'
                em.set_footer(
                    text="Don't you dare question my names for the textfaces.")
                await ctx.send(embed=em)
            else:
                await ctx.send('That is NOT one of the dank textfaces in here yet. Use [p]textface list to see a list of the textfaces.')

    @commands.command()
    async def hack(self, ctx, user: libneko.converters.InsensitiveMemberConverter = None):
        """Hack someone's account! Try it!"""
        if user is None:
            user = ctx.message.author

        gifs = [
            "https://thumbs.gfycat.com/LightheartedObviousBlowfish-size_restricted.gif",
            "https://media3.giphy.com/media/115BJle6N2Av0A/giphy.gif",
            "https://giffiles.alphacoders.com/119/119969.gif",
            "https://thumbs.gfycat.com/FlippantAdeptHatchetfish-size_restricted.gif",
            "https://media1.tenor.com/images/3d190af70cfeea404f796f869f46a3c3/tenor.gif",
            "https://media1.tenor.com/images/505ddb5e0b0e8c3e96b66e1469ef47c1/tenor.gif",
        ]
        gifemb = discord.Embed()
        gifemb.set_image(url=choice(gifs))
        msg = await ctx.send(embed=gifemb, content=f"Hacking! Target: {user}")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files... [▓▓    ]")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files... [▓▓▓   ]")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files... [▓▓▓▓▓ ]")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files COMPLETE! [▓▓▓▓▓▓]")
        await asyncio.sleep(2)
        await msg.edit(content="Retrieving Login Info... [▓▓▓    ]")
        await asyncio.sleep(3)
        await msg.edit(content="Retrieving Login Info... [▓▓▓▓▓ ]")
        await asyncio.sleep(3)
        await msg.edit(content="Retrieving Login Info... [▓▓▓▓▓▓ ]")
        await asyncio.sleep(4)
        await msg.edit(content=f"An error has occurred hacking {user}'s account. Please try again later. ❌")

    @commands.command(aliases=['animation', 'a'])
    async def anim(self, ctx, Type: str = None):
        """Animations! Usage: anim [type]. For a list, use [p]anim list."""
        if Type is None:
            await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type [p]anim list')
        else:
            if Type.lower() == 'wtf':
                msg = await ctx.send("```W```")
                await asyncio.sleep(1)
                await msg.edit(content="```WO```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT D```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA F```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA FU```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA FUK```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA FUK!```")
                await asyncio.sleep(1)
                await msg.edit(content="WOT DA FUK!")
            elif Type.lower() == 'mom':
                msg = await ctx.send("```Y```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO M```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO MO```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO MOM```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO MOM!```")
                await asyncio.sleep(1)
                await msg.edit(content="YO MOM!")
            elif Type.lower() == 'gethelp':
                msg = await ctx.send("```STOP!```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! G```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Ge```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get s```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get so```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get som```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get some```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get some HELP```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get some HELP!!!```")
                await asyncio.sleep(1)
                await msg.edit(content="STOP! Get some HELP!!!")
            elif Type.lower() == 'sike':
                msg = await ctx.send("```W```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wa```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wai```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait.```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait..```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait...```")
                await asyncio.sleep(1)
                await msg.edit(content="```SIKE!```")
                await asyncio.sleep(1)
                await msg.edit(content="SIKE!")
            elif Type.lower() == 'gitgud':
                msg = await ctx.send("```G```")
                await asyncio.sleep(1)
                await msg.edit(content="```Gi```")
                await asyncio.sleep(1)
                await msg.edit(content="```Git```")
                await asyncio.sleep(1)
                await msg.edit(content="```Git GUD!```")
                await asyncio.sleep(1)
                await msg.edit(content="Git GUD!")
            elif Type.lower() == 'clock':
                msg = await ctx.send(":clock12:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1230:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock130:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock2:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock230:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock3:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock330:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock4:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock430:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock5:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock530:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock6:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock630:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock7:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock730:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock8:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock830:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock9:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock930:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock10:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1030:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock11:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1130:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock12:")
            elif Type.lower() == 'mate':
                msg = await ctx.send("```Y```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye W```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WO```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WOT```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WOT M8```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WOT M8?!?!?!")
                await asyncio.sleep(1)
                await msg.edit(content="Ye WOT M8?!?!?!")
            elif Type.lower() == 'oj':
                msg = await ctx.send("```M```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mm```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm i```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it'```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's a```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's a ORANGE```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's a ORANGE JUICE```")
                await asyncio.sleep(1)
                await msg.edit(content="Mmm it's a ORANGE JUICE")
            elif Type.lower() == 'list':
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(
                    color=color, title="Current List of Awesome Animations:")
                em.description = "wtf (anim wtf), mom (anim mom), gethelp (anim gethelp), sike (anim sike), gitgud (anim gitgud), clock (anim clock), mate (anim mate), oj (anim oj)."
                em.set_footer(text="We will always be adding new animations!")
                await ctx.send(embed=em)
            else:
                await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type [p]anim list')

    # 8Ball Command
    @commands.command(name="8ball", aliases=["ball", "8b"])
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
            "psbad": [
                "Don't count on it",
                "My reply is no",
                "My sources say no",
                "Outlook not so good",
                "Very doubtful",
                "No",
            ],
        }
        choices = choice(choice(list(ps.values())))

        if choices in ps["psbad"]:
            color = discord.Color(0xFF0000)
        elif choices in ps["psgood"]:
            color = discord.Color(0x26D934)

        eightball = discord.Embed(color=color)
        eightball.add_field(
            name="Question:", value=question.capitalize(), inline=False)
        eightball.add_field(name="Answer:", value=f"{choices}.")
        eightball.set_author(name="The mighty 8-Ball")
        eightball.set_footer(
            text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        eightball.set_thumbnail(url="https://i.imgur.com/Q9dxpTz.png")
        await ctx.send(embed=eightball, content=None)

    @commands.command(hidden=True, aliases=["ily"])
    async def iloveyou(self, ctx):
        """
        ❤❤❤
        """
        await ctx.send(f"{ctx.author.mention}, I love you too! :heart::heart::heart:")

    @commands.command(aliases=["rr"], hidden=True)
    async def rickroll(self, ctx):
        """
        Never gonna give you up...
        """
        rick = discord.Embed()

        rick.set_image(
            url="https://i.kym-cdn.com/photos/images/original/000/041/494/1241026091_youve_been_rickrolled.gif")
        await ctx.send(embed=rick)

    @commands.command(aliases=["bg"])
    async def bigtext(self, ctx, *, text: str):
        """
        Make your text 🇧 🇮 🇬
        Only 1024 characters will be printed, due to limit imposed by Discord.
        """
        s = ""
        if len(text) >= 1024:
            shorten(text, width=1024)
        for char in text:
            if char.isalpha():
                s += f":regional_indicator_{char.lower()}: "
            elif char.isspace():
                s += "   "
        await ctx.send(s)

    @commands.command(aliases=["kitty", "kitten", "kat", "catto"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def cat(self, ctx):
        """
        Send cute cat pics.
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://api.thecatapi.com/v1/images/search') as resp:
            resp.raise_for_status()
            data = await resp.json()

        url = data[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(
            description="Here's a cute kitty :D", color=color, timestamp=datetime.utcnow())
        embed.set_footer(icon_url=ctx.message.author.avatar_url,
                         text=f"Requested by: {ctx.message.author}")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["doggie", "doge", "doggo"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def dog(self, ctx):
        """
        Send cute dog pics.
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://api.thedogapi.com/v1/images/search') as resp:
            resp.raise_for_status()
            data = await resp.json()

        url = data[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute doggo!! :D",
                              color=color, timestamp=datetime.utcnow())
        embed.set_footer(icon_url=ctx.message.author.avatar_url,
                         text=f"Requested by: {ctx.message.author}")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["foxes"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def fox(self, ctx):
        """
        Send cute fox pics.
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://randomfox.ca/floof/') as resp:
            resp.raise_for_status()
            data = await resp.json()

        image = data["image"]
        emb = discord.Embed(description="Here's a cute fox!! :D",
                            color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(icon_url=ctx.message.author.avatar_url,
                       text=f"Requested by: {ctx.message.author}")
        emb.set_image(url=image)
        await ctx.send(embed=emb)

    @commands.command()
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def shibe(self, ctx):
        """
        Send cute shibe pics.
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://shibe.online/api/shibes') as resp:
            resp.raise_for_status()
            data = await resp.json()

        img = data[0]
        emb = discord.Embed(description="Here's a cute shibe!! :D",
                            color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(icon_url=ctx.message.author.avatar_url,
                       text=f"Requested by: {ctx.message.author}")
        emb.set_image(url=img)
        await ctx.send(embed=emb)

    @commands.command(aliases=["catfact"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def catfacts(self, ctx):
        """
        Get a random cat facts!
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://cat-fact.herokuapp.com/facts/random') as resp:
            resp.raise_for_status()
            data = await resp.json()

        fact = data["text"]

        emb = discord.Embed(
            description=fact, color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_image(url="https://i.imgur.com/9RGJ5Ea.png")

        await ctx.send(embed=emb)

    @commands.command(aliases=["adv"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def advice(self, ctx):
        """
        Get a piece of Advice!
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get(f'https://api.adviceslip.com/advice') as resp:
            resp.raise_for_status()
            data = json.loads(await resp.read(), object_hook=DictObject)

        adv = data.slip.advice

        emb = discord.Embed(title="Here's some advice for you :)", description=adv,
                            color=ctx.author.color, timestamp=datetime.utcnow())
        await ctx.send(embed=emb)

    @commands.command(aliases=["randquote", "inspire", "qt"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def quote(self, ctx):
        """
        Get a random quote!
        """
        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://quote-garden.herokuapp.com/api/v2/quotes/random') as resp:
            resp.raise_for_status()
            data = await resp.json()

        quote = data["quote"]["quoteText"]
        author = data["quote"]["quoteAuthor"]

        emb = discord.Embed(
            description=quote, color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(text=f"Quote by: {author}")

        await ctx.send(embed=emb)

    @commands.command(aliases=["daddyjokes", "dadjoke", "djoke"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def dadjokes(self, ctx):
        """
        Send a Dad Joke (OK Boomer.)
        """
        await ctx.trigger_typing()
        head = {"Accept": "application/json",
                "User-Agent": "KamFreBOT(Discord.py) https://github.com/kamfretoz/KamFreBOT"
                }
        session = self.acquire_session()
        async with session.get('https://icanhazdadjoke.com/', headers=head) as resp:
            session.post
            resp.raise_for_status()
            data = await resp.json()

        jokes = data["joke"]

        emb = discord.Embed(title="Dad Joke!", description=jokes,
                            timestamp=datetime.utcnow(), color=ctx.author.color)
        emb.set_thumbnail(url="https://i.ibb.co/6WjYXsP/dad.jpg")

        await ctx.send(embed=emb)

    @commands.command(aliases=["chnorris", "chnr", "cn", "chuck"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def chucknorris(self, ctx):
        """
        You Didn't run this command, Chuck Norris throw this command at your face.
        """

        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://api.chucknorris.io/jokes/random') as resp:
            resp.raise_for_status()
            data = await resp.json()

        joke = data["value"]
        icon = data["icon_url"]

        emb = discord.Embed(
            description=joke, timestamp=datetime.utcnow(), color=0x8B0000)
        emb.set_thumbnail(url=icon)

        await ctx.send(embed=emb)

    @commands.command(aliases=["kw", "kanye"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def kanyewest(self, ctx):
        """
        Get a random Kanye West quote!
        """

        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://api.kanye.rest/') as resp:
            resp.raise_for_status()
            data = await resp.json()

        quote = data["quote"]

        emb = discord.Embed(title="Kanye West said:",
                            description=quote, timestamp=datetime.utcnow())
        emb.set_thumbnail(
            url="https://freepngimg.com/download/kanye_west/7-2-kanye-west-png.png")
        await ctx.send(embed=emb)

    @commands.command(aliases=["ts", "taylor"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def taylorswift(self, ctx):
        """
        Get a random Taylor Swift quote!
        """

        await ctx.trigger_typing()

        session = self.acquire_session()
        async with session.get('https://api.taylor.rest/') as resp:
            resp.raise_for_status()
            data = await resp.json()

        quote = data["quote"]

        emb = discord.Embed(title="Taylor Swift said:",
                            description=quote, timestamp=datetime.utcnow())
        emb.set_thumbnail(url="https://i.ibb.co/kH35WZX/taylor.png")
        await ctx.send(embed=emb)

    @commands.command(aliases=["succ"], hidden=True)
    async def zucc(self, ctx):
        """Gives you the zucc"""
        zuccy = discord.Embed()
        zuccy.set_image(
            url="https://pics.me.me/he-protec-he-attac-but-most-importantly-he-zucc-28716903.png"
        )
        await ctx.send(embed=zuccy, content="<:zucc:451945809144184862>")

    @commands.command(hidden=True, aliases=["pelota"])
    async def bola(self, ctx):
        """Bola"""
        def_bola = "https://i.ibb.co/87j54jp/bola.png"
        def_pelota = "https://cdn.discordapp.com/attachments/617178714173603867/743032290682077184/1597223408911.png"

        if ctx.invoked_with == "pelota":
            pel = discord.Embed()
            pel.set_image(url=def_pelota)
            await ctx.send(embed=pel)
            return

        bol = discord.Embed()
        bol.set_image(url=def_bola)
        await ctx.send(embed=bol)

    @commands.command(hidden=True)
    async def interject(self, ctx):
        """What you’re referring to as Linux, is in fact, GNyU/Linux, or as I’ve recentwy taken to cawwing it, GNyU pwus Linyux."""
        uwu = discord.Embed(
            description="||[Yes](https://www.youtube.com/watch?v=QXUSvSUsx80)||")
        uwu.set_image(
            url="https://i.ytimg.com/vi/QXUSvSUsx80/maxresdefault.jpg"
        )
        await ctx.send(embed=uwu)

    @commands.command(hidden=True, aliases=["banned"])
    async def banido(self, ctx):
        """You are Banned!"""
        ban = discord.Embed(description="You have been banned!")
        ban.set_image(
            url="https://media1.tenor.com/images/8a7663d1d754046373a5735fab9c14fa/tenor.gif"
        )
        await ctx.send(embed=ban)

    @commands.command(hidden=True, aliases=["distraction"])
    async def distract(self, ctx):
        """Really?"""
        dis = discord.Embed(description="You have been distracted.")
        dis.set_image(
            url="https://i.ibb.co/1ZHX2SZ/stickdancin.gif"
        )
        await ctx.send(embed=dis)

    @commands.command(hidden=True)
    @commands.cooldown(rate=2, per=3, type=commands.BucketType.user)
    async def slap(self, ctx, member: libneko.converters.InsensitiveMemberConverter = None):
        """IRC Style Trout Slap"""
        if member is None:
            await ctx.send("You have slapped yourself.")
        elif member.id == ctx.bot.user.id:
            await ctx.send(f'You rolled a Critical Fail...\nThe trout bounces off and rebounds on the attacker.')
            await ctx.send(f'{ctx.author.mention} '
                           f'you shoot yourself')
        else:
            await ctx.send(f'*slapping noises* I slapped you! '
                           f'{member.mention} ')

    @commands.command(hidden=True, aliases=["rw"])
    async def rewind(self, ctx):
        """Rewind the time!"""
        imgs = [
            "https://media1.tenor.com/images/d29dc08bce25f5de5051ad2f6d3b5a99/tenor.gif",
            "https://media1.tenor.com/images/3619126efbfc2d3f15eb60cabd6457ea/tenor.gif"
        ]
        rew = discord.Embed(description="YAAAAA IT'S REWIND TIME!")
        rew.set_image(
            url=choice(imgs)
        )
        await ctx.send(embed=rew)

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
    @commands.command(name="curse", aliases=("oppugno", "jynx", "kutuk", "santet"))
    async def emoji_curse(self, ctx, user: libneko.converters.InsensitiveMemberConverter = None, emoji: discord.Emoji = None):
        """
        Curse someone with an emoji for 30 minutes
        """
        if user is None and emoji is None:
            await ctx.send(embed=discord.Embed(description="Please specify who to curse and with what emoji!"))
            return

        if emoji is None:
            await ctx.send(embed=discord.Embed(description="Please specify what emoji to use!"))
            return

        if user.id == ctx.bot.user.id:
            user = ctx.message.author
            await ctx.send(embed=discord.Embed(description="HA! Nice try! But unfortunately i'm immune to the curse and so the curse goes back to sender!"))

        emoji = (
            self.bot.get_emoji(int(emoji.split(":")[2].strip(">")))
            if "<:" in emoji or "<a:" in emoji
            else emoji
        )
        cursed = self.jynxed.get(f"{user.id}@{ctx.guild.id}")
        if cursed is not None:
            await ctx.channel.send(
                embed=embeds.Embed(
                    description=f"{user.mention} is already cursed!",
                    color=discord.Colour.dark_purple(),
                )
            )
        else:
            try:
                await ctx.message.add_reaction(emoji)
            except:
                await ctx.send(
                    embed=embeds.Embed(
                        description=":octagonal_sign: Cannot find that emoji!",
                        color=discord.Colour.red(),
                    )
                )
            else:

                def check(msg):
                    return ctx.guild.id == msg.guild.id and msg.author.id == user.id

                async def curse_task(self):
                    await ctx.channel.send(
                        embed=embeds.Embed(
                            description=f":purple_heart: {user.mention} Has been cursed with {emoji}. The effect will fade away in 30 minutes.",
                            color=discord.Colour.purple(),
                        )
                    )
                    start = time.monotonic()
                    while time.monotonic() - start < 1800:
                        msg = await self.bot.wait_for("message", check=check)
                        try:
                            await msg.add_reaction(emoji)
                        except:
                            pass

                    del self.jynxed[f"{user.id}@{ctx.guild.id}"]

                curse = self.bot.loop.create_task(curse_task(self))
                self.jynxed.update({f"{user.id}@{ctx.guild.id}": curse})

    @commands.command(name="bless", aliases=("ruqyah", "finitincantatem", "countercurse"), hidden=False)
    async def emoji_bless(self, ctx, user: libneko.converters.InsensitiveMemberConverter):
        """Cure someone from a curse"""
        cursed = self.jynxed.get(f"{user.id}@{ctx.guild.id}")
        if user == ctx.author and user != self.bot.creator:
            await ctx.send(
                embed=embeds.Embed(
                    description=":octagonal_sign: You cannot counter-curse yourself",
                    color=discord.Colour.red(),
                )
            )
        elif cursed is not None:
            cursed.cancel()
            del self.jynxed[f"{user.id}@{ctx.guild.id}"]
            await ctx.send(
                embed=embeds.Embed(
                    description=f":green_heart: {user.mention} Has been blessed and the curse had faded away",
                    color=discord.Colour.from_rgb(55, 147, 105),
                )
            )
        else:
            await ctx.send(
                embed=embeds.Embed(
                    description=f":octagonal_sign: {user.mention} is not cursed!",
                    color=discord.Colour.red(),
                )
            )

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def xkcd(self, ctx, *, entry_number: int = None):
        """Post a random xkcd comic"""
        await ctx.trigger_typing()
        # Creates random number between 0 and 2190 (number of xkcd comics at time of writing) and queries xkcd
        headers = {"content-type": "application/json"}
        url = "https://xkcd.com/info.0.json"
        session = self.acquire_session()
        async with session.get(url, headers=headers) as response:
            xkcd_latest = await response.json()
            xkcd_max = xkcd_latest.get("num") + 1

        if entry_number is not None and int(entry_number) > 0 and int(entry_number) < xkcd_max:
            i = int(entry_number)
        else:
            i = randint(0, xkcd_max)
        headers = {"content-type": "application/json"}
        url = "https://xkcd.com/" + str(i) + "/info.0.json"
        session = self.acquire_session()
        async with session.get(url, headers=headers) as response:
            xkcd = await response.json()

        # Build Embed
        embed = discord.Embed()
        embed.title = xkcd["title"] + \
            " (" + xkcd["day"] + "/" + xkcd["month"] + "/" + xkcd["year"] + ")"
        embed.url = "https://xkcd.com/" + str(i)
        embed.description = xkcd["alt"]
        embed.set_image(url=xkcd["img"])
        embed.set_footer(text="Powered by xkcd")
        await ctx.send(embed=embed)

    @commands.command(aliases=["love", "lovemeter"])
    async def ship(self, ctx, name1: str = None, name2: str = None):
        """will it Sank or Sail?"""
        if name1 is None or name2 is None:
            await ctx.send(embed=discord.Embed(description="Who are you gonna ship?"))
            return

        shipnumber = randint(0, 100)

        # A Small Easter Egg for a server
        if name1 == "Oreo" and name2 == "TaylorSwift":
            shipnumber = 100

        if name1 == "Mixtape" and name2 == "Calliope":
            shipnumber = 100

        if name1 == "Prisma" and name2 == "Atticus":
            shipnumber = 100

        if name1 == "qwerty32" and name2 == "Penny":
            shipnumber = 100
        if name1 == "Vraptor" and name2 == "Sarah":
            shipnumber = 100
        if name1 == "IS8" and name2 == "Gumball":
            shipnumber = 100

        if 0 <= shipnumber <= 10:
            status = "Really low! {}".format(choice(["Friendzone ;(",
                                                     'Just "friends"',
                                                     '"Friends"',
                                                     "Little to no love ;(",
                                                     "There's barely any love ;("]))
        elif 10 < shipnumber <= 20:
            status = "Low! {}".format(choice(["Still in the friendzone",
                                              "Still in that friendzone ;(",
                                              "There's not a lot of love there... ;("]))
        elif 20 < shipnumber <= 30:
            status = "Poor! {}".format(choice(["But there's a small sense of romance from one person!",
                                               "But there's a small bit of love somewhere",
                                               "I sense a small bit of love!",
                                               "But someone has a bit of love for someone..."]))
        elif 30 < shipnumber <= 40:
            status = "Fair! {}".format(choice(["There's a bit of love there!",
                                               "There is a bit of love there...",
                                               "A small bit of love is in the air..."]))
        elif 40 < shipnumber <= 60:
            status = "Moderate! {}".format(choice(["But it's very one-sided OwO",
                                                   "It appears one sided!",
                                                   "There's some potential!",
                                                   "I sense a bit of potential!",
                                                   "There's a bit of romance going on here!",
                                                   "I feel like there's some romance progressing!",
                                                   "The love is getting there..."]))
        elif 60 < shipnumber <= 68:
            status = "Good! {}".format(choice(["I feel the romance progressing!",
                                               "There's some love in the air!",
                                               "I'm starting to feel some love!",
                                               "We are definitely getting there!!"]))

        elif shipnumber == 69:
            status = "Nice."

        elif 70 < shipnumber <= 80:
            status = "Great! {}".format(choice(["There is definitely love somewhere!",
                                                "I can see the love is there! Somewhere...",
                                                "I definitely can see that love is in the air",
                                                "Its getting more and more intense!!"]))
        elif 80 < shipnumber <= 90:
            status = "Over average! {}".format(choice(["Love is in the air!",
                                                       "I can definitely feel the love",
                                                       "I feel the love! There's a sign of a match!",
                                                       "There's a sign of a match!",
                                                       "I sense a match!",
                                                       "A few things can be improved to make this a match made in heaven!"]))
        elif 90 < shipnumber <= 99:
            status = "True love! {}".format(choice(["It's a match!",
                                                    "There's a match made in heaven!",
                                                    "It's definitely a match!",
                                                    "Love is truely in the air!",
                                                    "Love is most definitely in the air!"]))
        elif shipnumber == 100:
            status = "Forever lover! {}".format(
                choice(["Forever together and never be apart."]))

        else:
            status = "🤔"

        meter = "🖤🖤🖤🖤🖤🖤🖤🖤🖤🖤"

        if shipnumber <= 10:
            meter = "❤🖤🖤🖤🖤🖤🖤🖤🖤🖤"
        elif shipnumber <= 20:
            meter = "❤❤🖤🖤🖤🖤🖤🖤🖤🖤"
        elif shipnumber <= 30:
            meter = "❤❤❤🖤🖤🖤🖤🖤🖤🖤"
        elif shipnumber <= 40:
            meter = "❤❤❤❤🖤🖤🖤🖤🖤🖤"
        elif shipnumber <= 50:
            meter = "❤❤❤❤❤🖤🖤🖤🖤🖤"
        elif shipnumber <= 60:
            meter = "❤❤❤❤❤❤🖤🖤🖤🖤"
        elif shipnumber <= 70:
            meter = "❤❤❤❤❤❤❤🖤🖤🖤"
        elif shipnumber <= 80:
            meter = "❤❤❤❤❤❤❤❤🖤🖤"
        elif shipnumber <= 90:
            meter = "❤❤❤❤❤❤❤❤❤🖤"
        else:
            meter = "❤❤❤❤❤❤❤❤❤❤"

        if shipnumber <= 33:
            shipColor = 0xE80303
        elif 33 < shipnumber < 66:
            shipColor = 0xff6600
        elif 67 < shipnumber < 90:
            shipColor = 0x3be801
        else:
            shipColor = 0xee82ee

        emb = (discord.Embed(color=shipColor,
                             title="Love test for:",
                             timestamp=datetime.utcnow(),
                             description="**{0}** and **{1}** {2}".format(name1, name2, choice([
                                 ":sparkling_heart:",
                                 ":heart_decoration:",
                                 ":heart_exclamation:",
                                 ":heartbeat:",
                                 ":heartpulse:",
                                 ":hearts:",
                                 ":blue_heart:",
                                 ":green_heart:",
                                 ":purple_heart:",
                                 ":revolving_hearts:",
                                 ":yellow_heart:",
                                 ":two_hearts:"]))))
        emb.set_author(name="Shipping Machine!",
                       icon_url="http://moziru.com/images/kopel-clipart-heart-6.png")
        emb.add_field(name="Results:", value=f"{shipnumber}%", inline=True)
        emb.add_field(name="Status:", value=(status), inline=False)
        emb.add_field(name="Love Meter:", value=meter, inline=False)
        await ctx.send(embed=emb)

    @commands.command(aliases=['gay-scanner', 'gayscanner', 'gay', 'homo'])
    async def gay_scanner(self, ctx, *, user: str = None):
        """very mature command yes haha"""
        if not user:
            user = ctx.author.name

        gayness = randint(0, 100)

        if gayness <= 33:
            gayStatus = choice(["No homo",
                                "Wearing socks",
                                '"Only sometimes"',
                                "Straight-ish",
                                "No homo bro",
                                "Girl-kisser",
                                "Hella straight",
                                "Small amount of Homo detected."])
            gayColor = 0xFFC0CB
        elif 33 < gayness < 66:
            gayStatus = choice(["Possible homo",
                                "My gay-sensor is picking something up",
                                "I can't tell if the socks are on or off",
                                "Gay-ish",
                                "Looking a bit homo",
                                "lol half  g a y",
                                "safely in between for now",
                                "50:50"])
            gayColor = 0xFF69B4
        else:
            gayStatus = choice(["LOL YOU GAY XDDD FUNNY",
                                "HOMO ALERT",
                                "MY GAY-SESNOR IS OFF THE CHARTS",
                                "STINKY GAY",
                                "BIG GEAY",
                                "THE SOCKS ARE OFF",
                                "HELLA GAY",
                                "YES HOMO"])
            gayColor = 0xFF00FF

        meter = "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛"

        if gayness <= 10:
            meter = "🏳‍🌈⬛⬛⬛⬛⬛⬛⬛⬛⬛"
        elif gayness <= 20:
            meter = "🏳‍🌈🏳‍🌈⬛⬛⬛⬛⬛⬛⬛⬛"
        elif gayness <= 30:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈⬛⬛⬛⬛⬛⬛⬛"
        elif gayness <= 40:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈⬛⬛⬛⬛⬛⬛"
        elif gayness <= 50:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈⬛⬛⬛⬛⬛"
        elif gayness <= 60:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈⬛⬛⬛⬛"
        elif gayness <= 70:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈⬛⬛⬛"
        elif gayness <= 80:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈⬛⬛"
        elif gayness <= 90:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈⬛"
        else:
            meter = "🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈🏳‍🌈"

        emb = discord.Embed(
            description=f"Gayness for **{user}**", color=gayColor)
        emb.add_field(name="Gayness:", value=f"{gayness}% gay", inline=False)
        emb.add_field(name="Comment:",
                      value=f"{gayStatus} :kiss_mm:", inline=False)
        emb.add_field(name="Gay Meter:", value=meter, inline=False)
        emb.set_author(name="Gay-O-Meter™",
                       icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/ICA_flag.svg/2000px-ICA_flag.svg.png")
        await ctx.send(embed=emb)

    @commands.command()
    async def textmojify(self, ctx, *, text: str):
        """Convert text into emojis"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        if text != None:
            out = text.lower()
            text = out.replace(' ', '    ').replace('10', '\u200B:keycap_ten:')\
                      .replace('ab', '\u200B🆎').replace('cl', '\u200B🆑')\
                      .replace('0', '\u200B:zero:').replace('1', '\u200B:one:')\
                      .replace('2', '\u200B:two:').replace('3', '\u200B:three:')\
                      .replace('4', '\u200B:four:').replace('5', '\u200B:five:')\
                      .replace('6', '\u200B:six:').replace('7', '\u200B:seven:')\
                      .replace('8', '\u200B:eight:').replace('9', '\u200B:nine:')\
                      .replace('!', '\u200B❗').replace('?', '\u200B❓')\
                      .replace('vs', '\u200B🆚').replace('.', '\u200B🔸')\
                      .replace(',', '🔻').replace('a', '\u200B🅰')\
                      .replace('b', '\u200B🅱').replace('c', '\u200B🇨')\
                      .replace('d', '\u200B🇩').replace('e', '\u200B🇪')\
                      .replace('f', '\u200B🇫').replace('g', '\u200B🇬')\
                      .replace('h', '\u200B🇭').replace('i', '\u200B🇮')\
                      .replace('j', '\u200B🇯').replace('k', '\u200B🇰')\
                      .replace('l', '\u200B🇱').replace('m', '\u200B🇲')\
                      .replace('n', '\u200B🇳').replace('ñ', '\u200B🇳')\
                      .replace('o', '\u200B🅾').replace('p', '\u200B🅿')\
                      .replace('q', '\u200B🇶').replace('r', '\u200B🇷')\
                      .replace('s', '\u200B🇸').replace('t', '\u200B🇹')\
                      .replace('u', '\u200B🇺').replace('v', '\u200B🇻')\
                      .replace('w', '\u200B🇼').replace('x', '\u200B🇽')\
                      .replace('y', '\u200B🇾').replace('z', '\u200B🇿')
            try:
                await ctx.send(text)
            except Exception as e:
                await ctx.send(f'```{e}```')
        else:
            await ctx.send('Write something, reee!', delete_after=3.0)

    @commands.command(aliases=["topics"])
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def topic(self, ctx):
        """Kept running out of topic to talk about? This command might help you!"""
        await ctx.trigger_typing()
        choices = str(choice(topics.questions))
        embed = discord.Embed(title="Here is a question...",
                              description=f"{choices}", timestamp=datetime.utcnow())
        embed.set_footer(icon_url=ctx.message.author.avatar_url,
                         text=f"Requested by: {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["truths", "thetruth"])
    async def truth(self, ctx):
        """Spill out TheTruth!"""
        await ctx.trigger_typing()
        choices = str(choice(topics.truth))
        if choices not in topics.usedTruth:
            topics.usedTruth.append(choice)
            embed_quote = discord.Embed(
                title="Let's start a Truth game!", description=f"{choices}", timestamp=datetime.utcnow())
            embed_quote.set_footer(
                icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
            await ctx.send(embed=embed_quote)
            topics.usedTruth.popleft()

    @commands.command(aliases=["dares"])
    async def dare(self, ctx):
        """Are you up for the Dare?"""
        await ctx.trigger_typing()
        choices = str(choice(topics.dare))
        if choices not in topics.usedDare:
            topics.usedDare.append(choice)
            embed_quote = discord.Embed(
                title="Here is a Dare for you!", description=f"{choices}", timestamp=datetime.utcnow())
            embed_quote.set_footer(
                icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
            await ctx.send(embed=embed_quote)
            topics.usedDare.popleft()

    @commands.group(aliases=["mal", "anime"], invoke_without_command=True)
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist(self, ctx, *, name: str = None):
        """
        Find anime information from MyAnimeList!
        """
        data = None

        if name is None:
            await ctx.send(embed=discord.Embed(description="Please specifiy the anime title to find!"))
            return

        if len(name) < 3:
            await ctx.send(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        try:
            parameters = {
                "q": name,
                "limit": 1
            }
            session = self.acquire_session()
            async with session.get('https://api.jikan.moe/v3/search/anime', params=parameters, timeout=5) as resp:
                data = json.loads(await resp.read(), object_hook=DictObject)

        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status == 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status == 429:
                await ctx.send(embed=discord.Embed(description="⚠ We are being rate limited! calm your horses."))
                return
            if resp.status == 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status == 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access Jikan API, it may be down or inaccessible at the moment."))
                return
            elif resp.status == 503:
                await ctx.send(embed=discord.Embed(description="⚠ MyAnimeList is down at the moment, please try again later."))
                return

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
            await ctx.send(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
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

        await ctx.send(embed=emb)

    @myanimelist.command(name="manga", brief="Find Manga information")
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist_manga(self, ctx, *, name: str = None):
        """
        Find manga information from MyAnimeList!
        """
        if name is None:
            await ctx.send(embed=discord.Embed(description="Please specifiy the manga title to find!"))
            return

        if len(name) < 3:
            await ctx.send(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        try:
            parameters = {
                "q": name,
                "limit": 1
            }
            session = self.acquire_session()
            async with session.get(f'https://api.jikan.moe/v3/search/manga', params=parameters, timeout=5) as resp:
                data = json.loads(await resp.read(), object_hook=DictObject)

        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status == 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status == 429:
                await ctx.send(embed=discord.Embed(description="⚠ We are being rate limited! calm your horses."))
                return
            if resp.status == 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status == 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access Jikan API, it may be down or inaccessible at the moment."))
                return
            elif resp.status == 503:
                await ctx.send(embed=discord.Embed(description="⚠ MyAnimeList is down at the moment, please try again later."))
                return

        if not data.results:
            await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
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
            await ctx.send(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
            return
        except KeyError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
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
        emb.add_field(name="📑 Title",
                      value=f"[{manga_title}]({manga_url})", inline=False)

        if manga_synopsis:
            emb.add_field(name="ℹ Synopsis",
                          value=manga_synopsis, inline=False)
        else:
            emb.add_field(name="ℹ Synopsis",
                          value="No Synopsis Found.", inline=False)

        emb.add_field(name="⏳ Status", value=stat, inline=False)
        emb.add_field(name="📁 Type", value=manga_type, inline=False)
        emb.add_field(name="📅 Publish Date",
                      value=formatted_start, inline=False)
        emb.add_field(name="📚 Volumes", value=manga_volumes, inline=True)
        emb.add_field(name="📰 Chapters", value=manga_chapters, inline=True)
        emb.add_field(name="⭐ Score", value=f"{score}", inline=True)
        emb.add_field(name="👥 Members", value=memb, inline=True)
        emb.add_field(name="💳 ID", value=manga_id, inline=True)

        await ctx.send(embed=emb)

    @myanimelist.command(name="character", brief="Find character information", aliases=["chara", "char"])
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist_chara(self, ctx, *, name: str = None):
        """
        Find character information from MyAnimeList!
        """
        if name is None:
            await ctx.send(embed=discord.Embed(description="Please specifiy the character name to find!"))
            return

        if len(name) < 3:
            await ctx.send(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        try:
            parameters = {
                "q": name,
                "limit": 1
            }
            session = self.acquire_session()
            async with session.get(f'https://api.jikan.moe/v3/search/character', params=parameters, timeout=5) as resp:
                data = json.loads(await resp.read(), object_hook=DictObject)

        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status == 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status == 429:
                await ctx.send(embed=discord.Embed(description="⚠ We are being rate limited! calm your horses."))
                return
            if resp.status == 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status == 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access Jikan API, it may be down or inaccessible at the moment."))
                return
            elif resp.status == 503:
                await ctx.send(embed=discord.Embed(description="⚠ MyAnimeList is down at the moment, please try again later."))
                return
            else:
                await ctx.send(embed=discord.Embed(description=f"⚠ An Unknown error occured.)"))
                return
        try:
            char_id = data.results[0].mal_id
            char_url = data.results[0].url
            char_img = data.results[0].image_url
            char_name = data.results[0].name
        except UnboundLocalError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error occured while parsing the data, Please try again later."))
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

        await ctx.send(embed=emb)

    @commands.command(aliases=["uboxgen", "ubox"], name="undertalebox")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unboxgen(self, ctx, *, text):

        parameters = {
            "message": text,
            "character": "sans"
        }

        await ctx.trigger_typing()
        session = self.acquire_session()

        async with session.get(f"https://demirramon.com/utgen.png", params=parameters) as resp:
            image_data = await resp.read()

        img = BytesIO(image_data)
        img.seek(0)
        await ctx.send(file=discord.File(fp=img, filename="image.png"))

    # https://github.com/sks316/mewtwo-bot/blob/master/cogs/fun.py#L220
    @commands.command(aliases=["amb"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def amiibo(self, ctx, *, query: str):
        """
        Looks up information of an Amiibo.
        """
        #--First we connect to the Amiibo API and download the Amiibo information--#
        await ctx.trigger_typing()
        session = self.acquire_session()
        parameters = {
            "name": query
        }
        async with session.get('https://amiiboapi.com/api/amiibo/', params=parameters) as amiibo:
            data = await amiibo.json()

            #--Now we attempt to extract information--#
            try:
                series = data['amiibo'][0]['amiiboSeries']
                character = data['amiibo'][0]['character']
                name = data['amiibo'][0]['name']
                game = data['amiibo'][0]['gameSeries']
                atype = data['amiibo'][0]['type']
                na_release = data['amiibo'][0]['release']['na']
                eu_release = data['amiibo'][0]['release']['eu']
                jp_release = data['amiibo'][0]['release']['jp']
                au_release = data['amiibo'][0]['release']['au']
                image = data['amiibo'][0]['image']
                #--Finally, we format it into a nice little embed--#
                embed = discord.Embed(
                    title=f"Amiibo information for {name} ({series} series)", color=0xd82626)
                embed.add_field(name='Character Represented', value=character)
                embed.add_field(name='Amiibo Series', value=f"{series} series")
                embed.add_field(name='Game of Origin', value=game)
                embed.add_field(name='Type', value=atype)
                embed.add_field(
                    name='Released', value=f":flag_us: {na_release}\n:flag_eu: {eu_release}\n:flag_jp: {jp_release}\n:flag_au: {au_release}")
                embed.set_image(url=image)
                embed.set_thumbnail(
                    url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Amiibo.svg/1024px-Amiibo.svg.png")
                await ctx.send(embed=embed)
            except KeyError:
                return await ctx.send(":x: I couldn't find any Amiibo with that name. Double-check your spelling and try again.")

    # https://github.com/sks316/mewtwo-bot/blob/master/cogs/fun.py#L252
    @commands.command(aliases=["ud"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def urban(self, ctx, *, query: str):
        """
        Look up a definition of a word from Urbban Dictionary!
        """
        msg = await ctx.send("Looking for a definition...")
        try:
            #--First we connect to Urban Dictionary's API and get the results--#
            session = self.acquire_session()
            parameters = {
                "term": query
            }
            async with session.get(f'http://api.urbandictionary.com/v0/define', params=parameters) as r:
                #--Now we decode the JSON and get the variables, truncating definitions and examples if they are longer than 900 characters due to Discord API limitations and replacing example with None if blank--#
                result = await r.json()
                word = result['list'][0]['word']
                url = result['list'][0]['permalink']
                upvotes = result['list'][0]['thumbs_up']
                downvotes = result['list'][0]['thumbs_down']
                author = result['list'][0]['author']
                definition = result['list'][0]['definition']
                definition = definition.replace('[', '')
                definition = definition.replace(']', '')
                if len(definition) > 900:
                    definition = definition[0:901]
                    definition = f"{definition}[...]({url})"
                example = result['list'][0]['example']
                example = example.replace('[', '')
                example = example.replace(']', '')
                if len(example) > 900:
                    example = example[0:901]
                    example = f"{example}[...]({url})"
                if len(example) < 1:
                    example = None
                embed = discord.Embed(
                    title=f":notebook: Urban Dictionary Definition for {word}", description=definition, url=url, color=0x8253c3)
                if example == None:
                    pass
                else:
                    embed.add_field(name="Example:",
                                    value=example, inline=False)
                embed.set_footer(
                    text=f"Author: {author} - 👍️ {str(upvotes)} - 👎️ {str(downvotes)}")
                await msg.edit(content='', embed=embed)

        except:
            await msg.edit(content=":x: Sorry, I couldn't find that word. Check your spelling and try again.")

    # https://github.com/sks316/mewtwo-bot/blob/master/cogs/fun.py#L307
    @commands.command(aliases=["pats", "pet"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pat(self, ctx, *, target=None):
        """
        *pats you*
        """
        if target == None:
            return await ctx.send(":x: You need someone to give headpats to! You can give me a headpat if you want...")
        if target == ctx.author:
            return await ctx.send(":x: You can't give yourself headpats! You can give me a headpat if you want...")
        #--Get image from NekosLife API--#
        session = self.acquire_session()
        async with session.get('https://nekos.life/api/v2/img/pat') as pat:
            data = await pat.json()
            result = data.get('url')
            embed = discord.Embed(
                description=f"{ctx.author.display_name} gives {target} some headpats!",  color=0x8253c3)
            embed.set_image(url=result)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cuddle(self, ctx, *, target=None):
        """
        *cuddles you*
        """
        if target == None:
            return await ctx.send(":x: You need someone to cuddle! You can cuddle me if you want...")
        if target == ctx.author:
            return await ctx.send(":x: You can't cuddle yourself! You can cuddle me if you want...")
        #--Get image from NekosLife API--#
        session = self.acquire_session()
        async with session.get('https://nekos.life/api/v2/img/cuddle') as cuddle:
            data = await cuddle.json()
            result = data.get('url')
            embed = discord.Embed(
                description=f"🤗 {ctx.author.display_name} cuddles {target}!",  color=0x8253c3)
            embed.set_image(url=result)
            await ctx.send(embed=embed)

    @commands.command(aliases=["smooch"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kiss(self, ctx, *, target=None):
        """
        *kisses you*
        """
        if target == None:
            return await ctx.send(":x: You need someone to kiss! You can kiss me if you want...")
        if target == ctx.author:
            return await ctx.send(":x: You can't kiss yourself! You can kiss me if you want...")
        #--Get image from NekosLife API--#
        session = self.acquire_session()
        async with session.get('https://nekos.life/api/v2/img/kiss') as kiss:
            data = await kiss.json()
            result = data.get('url')
            embed = discord.Embed(
                description=f"❤ {ctx.author.display_name} kisses {target}!",  color=0x8253c3)
            embed.set_image(url=result)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def snuggle(self, ctx, *, target=None):
        """
        *snuggles you*
        """
        if target == None:
            return await ctx.send(":x: You need someone to cuddle! You can cuddle me if you want...")
        if target == ctx.author:
            return await ctx.send(":x: You can't cuddle yourself! You can cuddle me if you want...")
        #--Get image from NekosLife API--#
        session = self.acquire_session()
        async with session.get('https://nekos.life/api/v2/img/cuddle') as snuggle:
            data = await snuggle.json()
            result = data.get('url')
            embed = discord.Embed(
                description=f"🤗 {ctx.author.display_name} snuggles {target}!",  color=0x8253c3)
            embed.set_image(url=result)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hug(self, ctx, *, target=None):
        """
        *hugs you*
        """
        if target == None:
            return await ctx.send(":x: You need someone to hug! You can hug me if you want...")
        if target == ctx.author:
            return await ctx.send(":x: You can't hug yourself! You can hug me if you want...")
        #--Get image from NekosLife API--#
        session = self.acquire_session()
        async with session.get('https://nekos.life/api/v2/img/hug') as hug:
            data = await hug.json()
            result = data.get('url')
            embed = discord.Embed(
                description=f"🤗 {ctx.author.display_name} hugs {target}!",  color=0x8253c3)
            embed.set_image(url=result)
            await ctx.send(embed=embed)

    @commands.command(aliases=["memes", "meem"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def meme(self, ctx):
        """
        Send a random meme from Reddit
        """
        await ctx.trigger_typing()
        head = {
            "Authorization": ksoft_key
        }
        session = self.acquire_session()
        async with session.get('https://api.ksoft.si/images/random-meme', headers=head) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            title = data.title
            img_url = data.image_url
            source = data.source
            subreddit = data.subreddit
            upvotes = data.upvotes
            downvotes = data.downvotes
            comments = data.comments
            timestamp = data.created_at
            author = data.author
        except KeyError:
            code = data.code
            msg = data.message
            await ctx.send(embed=discord.Embed(description=f"⚠ An Error Occured! **{msg.capitalize()}** (Code: {code})"))
            return

        emb = discord.Embed(timestamp=datetime.utcnow())
        emb.set_image(url=img_url)
        emb.add_field(name="Title", value=f"[{title}]({source})")
        emb.add_field(name="Author", value=author)
        emb.add_field(name="Subreddit", value=subreddit)
        emb.add_field(
            name="Votes", value=f"⬆ {upvotes} Upvotes\n⬇ {downvotes} Downvotes")
        emb.add_field(name="Comments", value=comments)
        emb.add_field(name="Posted on", value=datetime.fromtimestamp(
            timestamp), inline=False)
        emb.set_footer(icon_url="https://cdn.ksoft.si/images/Logo128.png",
                       text="Data provided by: KSoft.Si")

        await ctx.send(embed=emb)

    @commands.command(aliases=["cute"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def cuteness(self, ctx):
        """
        Send a random cute pictures from Reddit
        """
        await ctx.trigger_typing()
        head = {
            "Authorization": ksoft_key
        }
        session = self.acquire_session()
        async with session.get('https://api.ksoft.si/images/random-aww', headers=head) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            title = data.title
            img_url = data.image_url
            source = data.source
            subreddit = data.subreddit
            upvotes = data.upvotes
            downvotes = data.downvotes
            comments = data.comments
            timestamp = data.created_at
            author = data.author
        except KeyError:
            code = data.code
            msg = data.message
            await ctx.send(embed=discord.Embed(description=f"⚠ An Error Occured! **{msg.capitalize()}** (Code: {code})"))
            return

        emb = discord.Embed(timestamp=datetime.utcnow())
        emb.set_image(url=img_url)
        emb.add_field(name="Title", value=f"[{title}]({source})")
        emb.add_field(name="Author", value=author)
        emb.add_field(name="Subreddit", value=subreddit)
        emb.add_field(
            name="Votes", value=f"⬆ {upvotes} Upvotes\n⬇ {downvotes} Downvotes")
        emb.add_field(name="Comments", value=comments)
        emb.add_field(name="Posted on", value=datetime.fromtimestamp(
            timestamp), inline=False)
        emb.set_footer(icon_url="https://cdn.ksoft.si/images/Logo128.png",
                       text="Data provided by: KSoft.Si")

        await ctx.send(embed=emb)

    @commands.command(aliases=["sub"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def subreddit(self, ctx, *, sub: str = None):
        """
        Send a random post from the specified subreddit
        """
        if sub is None:
            await ctx.send("Please specify the subreddit name!")
            return

        await ctx.trigger_typing()
        head = {
            "Authorization": ksoft_key
        }
        param = {
            "remove_nsfw": "true",
            "span": "all"
        }
        session = self.acquire_session()
        async with session.get(f'https://api.ksoft.si/images/rand-reddit/{sub}', headers=head, params=param) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)

        try:
            title = data.title
            img_url = data.image_url
            source = data.source
            subreddit = data.subreddit
            upvotes = data.upvotes
            downvotes = data.downvotes
            comments = data.comments
            timestamp = data.created_at
            author = data.author
        except KeyError:
            code = data.code
            msg = data.message
            await ctx.send(embed=discord.Embed(description=f"⚠ An Error Occured! **{msg.capitalize()}** (Code: {code})"))
            return

        emb = discord.Embed(timestamp=datetime.utcnow())
        emb.set_image(url=img_url)
        emb.add_field(name="Title", value=f"[{title}]({source})")
        emb.add_field(name="Author", value=author)
        emb.add_field(name="Subreddit", value=subreddit)
        emb.add_field(
            name="Votes", value=f"⬆ {upvotes} Upvotes\n⬇ {downvotes} Downvotes")
        emb.add_field(name="Comments", value=comments)
        emb.add_field(name="Posted on", value=datetime.fromtimestamp(
            timestamp), inline=False)
        emb.set_footer(icon_url="https://cdn.ksoft.si/images/Logo128.png",
                       text="Data provided by: KSoft.Si")

        await ctx.send(embed=emb)

    @commands.command(aliases=["weirdkihow", "wkh", "wikihow"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def wikihowimages(self, ctx):
        """
        Sends a random weird imagery from wikihow
        """
        await ctx.trigger_typing()
        head = {
            "Authorization": ksoft_key
        }
        param = {
            "nsfw": "false"
        }
        session = self.acquire_session()
        async with session.get('https://api.ksoft.si/images/random-wikihow', headers=head, params=param) as resp:
            data = json.loads(await resp.read(), object_hook=DictObject)
        try:
            img_url = data.url
            title = data.title
            article = data.article_url
        except KeyError:
            code = data.code
            msg = data.message
            await ctx.send(embed=discord.Embed(description=f"⚠ An Error Occured! **{msg.capitalize()}** (Code: {code})"))
            return

        emb = discord.Embed(
            description=f"[{title}]({article})", timestamp=datetime.utcnow())
        emb.set_image(url=img_url)
        emb.set_footer(icon_url="https://cdn.ksoft.si/images/Logo128.png",
                       text="Data provided by: KSoft.Si")
        await ctx.send(embed=emb)

    ####
    # https://github.com/DeCoded-Void/Minesweeper_discord.py for the minesweeper command
    ###

    errortxt = ('That is not formatted properly or valid positive integers weren\'t used, ',
                'the proper format is:\n`[Prefix]minesweeper <columns> <rows> <bombs>`\n\n',
                'You can give me nothing for random columns, rows, and bombs.')
    errortxt = ''.join(errortxt)

    @commands.command(aliases=["ms"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
        """
        Play Minesweeper game in Discord!
        Usage: `[p]minesweeper <columns> <rows> <bombs>`
        """
        if columns is None or rows is None and bombs is None:
            if columns is not None or rows is not None or bombs is not None:
                await ctx.send(self.errortxt)
                return
            else:
                # Gives a random range of columns and rows from 4-13 if no arguments are given
                # The amount of bombs depends on a random range from 5 to this formula:
                # ((columns * rows) - 1) / 2.5
                # This is to make sure the percentages of bombs at a given random board isn't too high
                columns = randint(4, 13)
                rows = randint(4, 13)
                bombs = columns * rows - 1
                bombs = bombs / 2.5
                bombs = round(randint(5, round(bombs)))
        try:
            columns = int(columns)
            rows = int(rows)
            bombs = int(bombs)
        except ValueError:
            await ctx.send(self.errortxt)
            return
        except TypeError:
            await ctx.send(self.errortxt)
            return
        if columns > 13 or rows > 13:
            await ctx.send('The limit for the columns and rows are 13 due to discord limits...')
            return
        if columns < 1 or rows < 1 or bombs < 1:
            await ctx.send('The provided numbers cannot be zero or negative...')
            return
        if bombs + 1 > columns * rows:
            await ctx.send(':boom:**BOOM**, you have more bombs than spaces on the grid or you attempted to make all of the spaces bombs!')
            return

        # Creates a list within a list and fills them with 0s, this is our makeshift grid
        grid = [[0 for num in range(columns)] for num in range(rows)]

        # Loops for the amount of bombs there will be
        loop_count = 0
        while loop_count < bombs:
            x = randint(0, columns - 1)
            y = randint(0, rows - 1)
            # We use B as a variable to represent a Bomb (this will be replaced with emotes later)
            if grid[y][x] == 0:
                grid[y][x] = 'B'
                loop_count = loop_count + 1
            # It will loop again if a bomb is already selected at a random point
            if grid[y][x] == 'B':
                pass

        # The while loop will go though every point though our makeshift grid
        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            # We need to predefine this for later
            adj_sum = 0
            # Checks the surrounding points of our "grid"
            for (adj_y, adj_x) in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                # There will be index errors, we can just simply ignore them by using a try and exception block
                try:
                    if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
                        # adj_sum will go up by 1 if a surrounding point has a bomb
                        adj_sum = adj_sum + 1
                except Exception as error:
                    pass
            # Since we don't want to change the Bomb variable into a number,
            # the point that the loop is in will only change if it isn't "B"
            if grid[pos_y][pos_x] != 'B':
                grid[pos_y][pos_x] = adj_sum
            # Increases the X values until it is more than the columns
            # If the while loop does not have "pos_y < rows" will index error
            if pos_x == columns - 1:
                pos_x = 0
                pos_y = pos_y + 1
            else:
                pos_x = pos_x + 1

        # Builds the string to be Discord-ready
        string_builder = []
        for the_rows in grid:
            string_builder.append(''.join(map(str, the_rows)))
        string_builder = '\n'.join(string_builder)
        # Replaces the numbers and B for the respective emotes and spoiler tags
        string_builder = string_builder.replace('0', '||:zero:||')
        string_builder = string_builder.replace('1', '||:one:||')
        string_builder = string_builder.replace('2', '||:two:||')
        string_builder = string_builder.replace('3', '||:three:||')
        string_builder = string_builder.replace('4', '||:four:||')
        string_builder = string_builder.replace('5', '||:five:||')
        string_builder = string_builder.replace('6', '||:six:||')
        string_builder = string_builder.replace('7', '||:seven:||')
        string_builder = string_builder.replace('8', '||:eight:||')
        final = string_builder.replace('B', '||:bomb:||')

        percentage = columns * rows
        percentage = bombs / percentage
        percentage = 100 * percentage
        percentage = round(percentage, 2)

        embed = discord.Embed(
            title='\U0001F642 Minesweeper \U0001F635', color=0xC0C0C0)
        embed.add_field(name='Columns:', value=columns, inline=True)
        embed.add_field(name='Rows:', value=rows, inline=True)
        embed.add_field(name='Total Spaces:',
                        value=columns * rows, inline=True)
        embed.add_field(name='\U0001F4A3 Count:', value=bombs, inline=True)
        embed.add_field(name='\U0001F4A3 Percentage:',
                        value=f'{percentage}%', inline=True)
        embed.add_field(name='Requested by:',
                        value=ctx.author.mention, inline=True)
        await ctx.send(content=f'\U0000FEFF\n{final}', embed=embed)

    @minesweeper.error
    async def minesweeper_error(self, ctx, error):
        await ctx.send(self.errortxt)
        return

    @commands.command(aliases=["owo"])
    async def owoify(self, ctx, *, text: commands.clean_content = "Hello Friend!"):
        """OWO-ify your text!"""
        owoifator = Owoifator()
        fin = owoifator.owoify(text)  # Hewwo fwiend (*^ω^)
        if len(fin) > 2000:
            shorten(fin, width=2000, placeholder="...")
        await ctx.send(embed=discord.Embed(description=fin))

    @commands.command(aliases=["vwi"])
    async def vaporipsum(self, ctx):
        """
        Generate a random text, like Lorem Ipsum, but more nostalgic and aesthetic.
        """
        vapor = vaporize(vaporipsum(2)).upper()
        if len(vapor) > 2000:
            shorten(vapor, width=2000, placeholder="...")
        await ctx.send(embed=discord.Embed(description=vapor))

    @commands.command(aliases=["vwy", "vapor"])
    async def vaporizer(self, ctx, *, text: commands.clean_content = "Hello World"):
        """
        Convert your text from this Hello World to this Ｈｅｌｌｏ Ｗｏｒｌｄ
        """
        if len(text) > 2000:
            await ctx.send(embed=discord.Embed(description="Only 2000 characters or fewer are allowed."))
            return

        vapor = vaporize(text)
        await ctx.send(embed=discord.Embed(description=vapor))

    @commands.command()
    @commands.cooldown(3, 5, commands.BucketType.user)
    @commands.max_concurrency(number=1, per=commands.BucketType.guild, wait=False)
    async def rps(self, ctx, time: int = 3):
        """
        A Simple Rock Paper Scissor countdown
        """
        if time > 10:
            await ctx.send("10 Seconds ought to be enough.")
            time = 10
        msg = await ctx.send(content="Get Ready! countdown starts in a few moments!")
        await asyncio.sleep(2)
        iteration = time
        while iteration:
            await msg.edit(content=f"{iteration}...")
            await asyncio.sleep(1)
            iteration -= 1
        await msg.edit(content="**Shoot!**")

    @commands.group(invoke_without_command=True, aliases=["paste"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def pasta(self, ctx):
        pass

    @pasta.command(name="kecanduan", brief="Astaga ini apa yah??")
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def kecanduan_pasta(self, ctx):

        prms = {
            "pasta": "kecanduan-discord"
        }

        session = self.acquire_session()
        async with session.get('https://pasta.dhikarizky.me/api/use', params=prms) as resp:
            dt = json.loads(await resp.read(), object_hook=DictObject)

        tipe = dt.data.pasta
        out = dt.data.output

        emb = discord.Embed(title=tipe, description=out)
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Fun(bot))
    print("Fun Module has been loaded.")
