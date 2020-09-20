import asyncio
import aiohttp
import random
import time
import data.config as config
import data.quotes as quotes
import discord
import libneko
import os
import json
import ciso8601
import data.topics as topics
import dateutil
from textwrap import shorten
from collections import deque
from datetime import datetime
from random import randint, sample
from discord.ext import commands
from libneko import embeds

random.seed = (os.urandom(1024))

ZALGO_DEFAULT_AMT = 3
ZALGO_MAX_AMT = 7

ZALGO_PARAMS = {"above": (5, 10), "below": (5, 10), "overlay": (0, 2)}

ZALGO_CHARS = {
    "above": [
        "\u0300",
        "\u0301",
        "\u0302",
        "\u0303",
        "\u0304",
        "\u0305",
        "\u0306",
        "\u0307",
        "\u0308",
        "\u0309",
        "\u030A",
        "\u030B",
        "\u030C",
        "\u030D",
        "\u030E",
        "\u030F",
        "\u0310",
        "\u0311",
        "\u0312",
        "\u0313",
        "\u0314",
        "\u0315",
        "\u031A",
        "\u031B",
        "\u033D",
        "\u033E",
        "\u033F",
        "\u0340",
        "\u0341",
        "\u0342",
        "\u0343",
        "\u0344",
        "\u0346",
        "\u034A",
        "\u034B",
        "\u034C",
        "\u0350",
        "\u0351",
        "\u0352",
        "\u0357",
        "\u0358",
        "\u035B",
        "\u035D",
        "\u035E",
        "\u0360",
        "\u0361",
    ],
    "below": [
        "\u0316",
        "\u0317",
        "\u0318",
        "\u0319",
        "\u031C",
        "\u031D",
        "\u031E",
        "\u031F",
        "\u0320",
        "\u0321",
        "\u0322",
        "\u0323",
        "\u0324",
        "\u0325",
        "\u0326",
        "\u0327",
        "\u0328",
        "\u0329",
        "\u032A",
        "\u032B",
        "\u032C",
        "\u032D",
        "\u032E",
        "\u032F",
        "\u0330",
        "\u0331",
        "\u0332",
        "\u0333",
        "\u0339",
        "\u033A",
        "\u033B",
        "\u033C",
        "\u0345",
        "\u0347",
        "\u0348",
        "\u0349",
        "\u034D",
        "\u034E",
        "\u0353",
        "\u0354",
        "\u0355",
        "\u0356",
        "\u0359",
        "\u035A",
        "\u035C",
        "\u035F",
        "\u0362",
    ],
    "overlay": [
        "\u0334", 
        "\u0335", 
        "\u0336", 
        "\u0337", 
        "\u0338"
    ],
}

# CREDIT TO: Nekoka/Espy Tysm!
class DictObject(dict):
    def __getattr__(self, item):
        return self[item]

def get_filesystem_slash():
    if os.name == "nt":
        return "\\"
    elif os.name == "posix":
        return "/"
    else:
        return "/"

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.jynxed = {}

    @commands.command(aliases=["talk", "speak","sy"])
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
        except discord.Forbidden:
            await ctx.author.send(":no_entry_sign: I'm not allowed to send message here!", delete_after=5)
        except discord.NotFound:
            await ctx.send(discord.Embed(description=":grey_exclamation: ERROR: Original message not found! (404 UNKNOWN MESSAGE)"), delete_after=5)
        except discord.ext.commands.BotMissingPermissions:
            await ctx.send(discord.Embed(description="I don't have permission to delete the original message!"), delete_after=5.0,)    @commands.command(aliases=["talk", "speak","s"])

    @commands.command(aliases=["sghost", "sayg","sg"])
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
        except discord.Forbidden:
            await ctx.author.send(":no_entry_sign: I'm not allowed to send message here!", delete_after=5)

    # Say to all members command
    @commands.command(aliases=["stoall"], hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def saytoall(self, ctx, *, text: commands.clean_content = None):
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
    @commands.command(aliases=["ttstalk", "speaktts","st"], hidden=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def saytts(self, ctx, *, text: commands.clean_content = None):
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
                await ctx.author.send(":no_entry_sign: I'm not allowed to send message here!", delete_after=5)
            except discord.NotFound:
                await ctx.send(discord.Embed(description=":grey_exclamation: ERROR: Original message not found! (404 UNKNOWN MESSAGE)"), delete_after=5)
            except discord.ext.commands.BotMissingPermissions:
                await ctx.send(discord.Embed(description="I don't have permission to delete the original message!"), delete_after=5.0,)

    @commands.command(aliases=["embedsay","syd","emb"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def sayembed(self, ctx, *, message: commands.clean_content = None):
        '''A command to embed messages quickly.'''
        if message is None:
            await ctx.send(discord.Embed(description="❓ What do you want me to say?", delete_after=5))
            await ctx.message.add_reaction("❓")
        else:
            await ctx.message.delete()
            em = discord.Embed(color=random.randint(0, 0xFFFFFF), timestamp=datetime.utcnow())
            em.description = message
            em.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Sent by: {ctx.message.author}")
            await ctx.send(embed=em)

    @commands.command(aliases=["sto"])
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sayto(self, ctx, destination: libneko.converters.GuildChannelConverter=None, *, text: commands.clean_content = None):
        """Send whatever you want to specific channel"""
        if text is None:
            await ctx.send("What do you want me to say?", delete_after=10.0)
            await ctx.message.add_reaction("❓")
        elif destination is None:
            await ctx.send("Where do you want me to send the text?", delete_after=10.0)
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
    async def sendto(self, ctx, target: libneko.converters.InsensitiveUserConverter = None, *, text:commands.clean_content =None):
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
        choices = ["https://i.imgur.com/vzcNPdF.png", "https://i.imgur.com/9YBSnmr.png"]
        flip = discord.Embed(title="Flip The Coin!", color=0xFFFFFF)
        flip.set_image(url=random.choice(choices))
        await ctx.send(embed=flip)


    @commands.command(aliases=["bqt"], hidden=True)
    async def bobertquote(self, ctx):
        """Send a random Bobert Quote!"""
        choice = str(random.choice(quotes.bobert))
        embed_quote = discord.Embed(title="Bobert said...", description=f"{choice}")
        embed_quote.set_thumbnail(url="https://i.imgur.com/zcVN4q1.png")
        await ctx.send(embed=embed_quote)

    @commands.command()
    async def dance(self, ctx):
        """Bobert Dance!"""
        bdance = discord.Embed()
        bdance.set_image(url="https://i.imgur.com/1DEtTrQ.gif")
        await ctx.send(embed=bdance)

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ['❤', '💛', '💚', '💙', '💜','♥']
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

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
              em.set_footer(text="Don't you dare question my names for the textfaces.")
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
        gifemb.set_image(url=random.choice(gifs))
        msg = await ctx.send(embed=gifemb,content=f"Hacking! Target: {user}")
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
              em=discord.Embed(color=color, title="Current List of Awesome Animations:")
              em.description = "wtf (anim wtf), mom (anim mom), gethelp (anim gethelp), sike (anim sike), gitgud (anim gitgud), clock (anim clock), mate (anim mate), oj (anim oj)."
              em.set_footer(text="We will always be adding new animations!")
              await ctx.send(embed=em)
            else:
              await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type [p]anim list')             

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
            "psbad": [
                "Don't count on it",
                "My reply is no",
                "My sources say no",
                "Outlook not so good",
                "Very doubtful",
                "No",
            ],
        }
        choice = random.choice(random.choice(list(ps.values())))

        if choice in ps["psbad"]:
            color = discord.Color(0xFF0000)
        elif choice in ps["psgood"]:
            color = discord.Color(0x26D934)

        eightball = discord.Embed(color=color)
        eightball.add_field(name="Question:", value=question.capitalize(), inline=False)
        eightball.add_field(name="Answer:", value=f"{choice}.")
        eightball.set_author(name="The mighty 8-Ball")
        eightball.set_footer(text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        eightball.set_thumbnail(url="https://i.imgur.com/Q9dxpTz.png")
        await ctx.send(embed=eightball, content=None)

    @commands.command(hidden=True, aliases=["ily"])
    async def iloveyou(self, ctx):
        await ctx.send(f"{ctx.author.mention}, I love you too! :heart::heart::heart:")

    @commands.command(aliases=["rr"], hidden=True)
    async def rickroll(self, ctx):
        """
        Never gonna give you up...
        """
        rick = discord.Embed()
        rick.set_image(url="https://i.kym-cdn.com/photos/images/original/000/041/494/1241026091_youve_been_rickrolled.gif")
        await ctx.send(embed=rick)

    @commands.command(aliases=["bg"])
    async def bigtext(self, ctx, *, text: str):
        """
        Make your text 🇧 🇮 🇬
        """
        s = ""
        for char in text:
            if char.isalpha():
                s += f":regional_indicator_{char.lower()}: "
            elif char.isspace():
                s += "   "
        await ctx.send(s)

    @commands.command(aliases=["kitty", "kitten", "kat","catto"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def cat(self, ctx):
        """
        Send cute cat pics.
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        url = data[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute kitty :D", color=color, timestamp=datetime.utcnow())
        embed.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["doggie","doge","doggo"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def dog(self, ctx):
        """
        Send cute dog pics.
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thedogapi.com/v1/images/search') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        url = data[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute doggo!! :D", color=color, timestamp=datetime.utcnow())
        embed.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["foxes"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def fox(self, ctx):
        """
        Send cute fox pics.
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://randomfox.ca/floof/') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        image = data["image"]
        emb = discord.Embed(description="Here's a cute fox!! :D", color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
        emb.set_image(url=image)
        await ctx.send(embed=emb)

    @commands.command()
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def shibe(self, ctx):
        """
        Send cute shibe pics.
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://shibe.online/api/shibes') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        img = data[0]
        emb = discord.Embed(description="Here's a cute shibe!! :D", color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
        emb.set_image(url=img)
        await ctx.send(embed=emb)

    @commands.command(aliases=["catfact"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def catfacts(self, ctx):
        """
        Get a random cat facts!
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://cat-fact.herokuapp.com/facts/random') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        fact = data["text"]

        emb = discord.Embed(description=fact, color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_image(url="https://i.imgur.com/9RGJ5Ea.png")

        await ctx.send(embed=emb)

    @commands.command(aliases=["adv"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def advice(self, ctx):
        """
        Get a piece of Advice!
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.adviceslip.com/advice') as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                

        adv = data.slip.advice

        emb = discord.Embed(title="Here's some advice for you :)", description=adv,color = ctx.author.color, timestamp=datetime.utcnow())
        await ctx.send(embed=emb)

    @commands.command(aliases=["prgquote","prqt"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def programmingquote(self, ctx):
        """
        Get a random programming quote!
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://programming-quotes-api.herokuapp.com/quotes/random') as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                

        quo = data.en
        aut = data.author

        emb = discord.Embed(description=quo, color = ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(text=f"Quote by: {aut}")
        await ctx.send(embed=emb)

    @commands.command(aliases=["randquote", "inspire","qt"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def quote(self, ctx):
        """
        Get a random quote!
        """
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://quote-garden.herokuapp.com/api/v2/quotes/random') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        quote = data["quote"]["quoteText"]
        author = data["quote"]["quoteAuthor"]

        emb = discord.Embed(description=quote, color=ctx.author.color, timestamp=datetime.utcnow())
        emb.set_footer(text=f"Quote by: {author}")

        await ctx.send(embed=emb)
    
    @commands.command(aliases=["daddyjokes","dadjoke","djoke"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def dadjokes(self, ctx):
        """
        Send Dad Jokes
        """
        await ctx.trigger_typing()
        header = { "Accept": "application/json",
                   "User-Agent": "KamFreBOT(Discord.py) https://github.com/kamfretoz/KamFreBOT"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get('https://icanhazdadjoke.com/', headers=header) as resp:
                session.post
                resp.raise_for_status()
                data = await resp.json()
                

        jokes = data["joke"]

        emb = discord.Embed(title="Dad Joke!", description=jokes, timestamp=datetime.utcnow(), color=ctx.author.color)
        emb.set_thumbnail(url="https://i.ibb.co/6WjYXsP/dad.jpg")

        await ctx.send(embed=emb)

    @commands.command(aliases=["chnorris","chnr","cn","chuck"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def chucknorris(self, ctx):
        """
        You Didn't run this command, Chuck Norris throw this command at your face.
        """

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.chucknorris.io/jokes/random') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        joke = data["value"]
        icon = data["icon_url"]

        emb = discord.Embed(description=joke, timestamp=datetime.utcnow(), color=0x8B0000)
        emb.set_thumbnail(url=icon)

        await ctx.send(embed=emb)

    @commands.command(aliases=["kw","kanye"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def kanyewest(self, ctx):
        """
        Get a random Kanye West quote!
        """

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.kanye.rest/') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        quote = data["quote"]

        emb = discord.Embed(title="Kanye West said:",description=quote, timestamp=datetime.utcnow())
        emb.set_thumbnail(url="https://freepngimg.com/download/kanye_west/7-2-kanye-west-png.png")
        await ctx.send(embed=emb)

    @commands.command(aliases=["ts","taylor"])
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def taylorswift(self, ctx):
        """
        Get a random Taylor Swift quote!
        """

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.taylor.rest/') as resp:
                resp.raise_for_status()
                data = await resp.json()
                

        quote = data["quote"]

        emb = discord.Embed(title="Taylor Swift said:",description=quote, timestamp=datetime.utcnow())
        emb.set_thumbnail(url="https://i.ibb.co/kH35WZX/taylor.png")
        await ctx.send(embed=emb)


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

    @commands.command(hidden=True, aliases=["owo"])
    async def interject(self, ctx):
        """What you’re referring to as Linux, is in fact, GNyU/Linux, or as I’ve recentwy taken to cawwing it, GNyU pwus Linyux."""
        uwu = discord.Embed(description="||[Yes](https://www.youtube.com/watch?v=QXUSvSUsx80)||")
        uwu.set_image(
            url="https://i.ytimg.com/vi/QXUSvSUsx80/maxresdefault.jpg"
        )
        await ctx.send(embed=uwu)

    @commands.command(hidden=True, aliases=["banned"])
    async def banido(self, ctx):
        """Banned!"""
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
            url=random.choice(imgs)
        )
        await ctx.send(embed=rew)

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
    @commands.command(name="curse", aliases=("oppugno", "jynx", "kutuk", "santet"))
    async def emoji_curse(self, ctx, user: libneko.converters.InsensitiveMemberConverter = None, emoji: discord.Emoji = None):
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
        """Post a random xkcd"""
        await ctx.trigger_typing()
        # Creates random number between 0 and 2190 (number of xkcd comics at time of writing) and queries xkcd
        headers = {"content-type": "application/json"}
        url = "https://xkcd.com/info.0.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                xkcd_latest = await response.json()
                xkcd_max = xkcd_latest.get("num") + 1
                

        if entry_number is not None and int(entry_number) > 0 and int(entry_number) < xkcd_max:
            i = int(entry_number)
        else:
            i = randint(0, xkcd_max)
        headers = {"content-type": "application/json"}
        url = "https://xkcd.com/" + str(i) + "/info.0.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                xkcd = await response.json()
                

        # Build Embed
        embed = discord.Embed()
        embed.title = xkcd["title"] + " (" + xkcd["day"] + "/" + xkcd["month"] + "/" + xkcd["year"] + ")"
        embed.url = "https://xkcd.com/" + str(i)
        embed.description = xkcd["alt"]
        embed.set_image(url=xkcd["img"])
        embed.set_footer(text="Powered by xkcd")
        await ctx.send(embed=embed)

    @commands.command(aliases=["love"])
    async def ship(self, ctx, name1: str = None, name2: str = None):
        """Sank or Sail?"""
        if name1 is None or name2 is None:
            await ctx.send(embed=discord.Embed(description="Who are you gonna ship?"))
            return

        shipnumber = random.randint(0,100)

        # A Small Easter Egg for a server        
        if name1 == "Oreo" and name2 == "TaylorSwift":
            shipnumber = 100

        if name1 == "mixtape" and name2 == "calliope":
            shipnumber = 100

        if name1 == "Prisma" and name2 == "Atticus":    
            shipnumber = 100

        if name1 == "qwerty32" and name2 == "Penny":
            shipnumber = 100
            
        if 0 <= shipnumber <= 10:
            status = "Really low! {}".format(random.choice(["Friendzone ;(", 
                                                            'Just "friends"', 
                                                            '"Friends"', 
                                                            "Little to no love ;(", 
                                                            "There's barely any love ;("]))
        elif 10 < shipnumber <= 20:
            status = "Low! {}".format(random.choice(["Still in the friendzone", 
                                                     "Still in that friendzone ;(", 
                                                     "There's not a lot of love there... ;("]))
        elif 20 < shipnumber <= 30:
            status = "Poor! {}".format(random.choice(["But there's a small sense of romance from one person!", 
                                                     "But there's a small bit of love somewhere", 
                                                     "I sense a small bit of love!", 
                                                     "But someone has a bit of love for someone..."]))
        elif 30 < shipnumber <= 40:
            status = "Fair! {}".format(random.choice(["There's a bit of love there!", 
                                                      "There is a bit of love there...", 
                                                      "A small bit of love is in the air..."]))
        elif 40 < shipnumber <= 60:
            status = "Moderate! {}".format(random.choice(["But it's very one-sided OwO", 
                                                          "It appears one sided!", 
                                                          "There's some potential!", 
                                                          "I sense a bit of potential!", 
                                                          "There's a bit of romance going on here!", 
                                                          "I feel like there's some romance progressing!", 
                                                          "The love is getting there..."]))
        elif 60 < shipnumber <= 70:
            status = "Good! {}".format(random.choice(["I feel the romance progressing!", 
                                                      "There's some love in the air!", 
                                                      "I'm starting to feel some love!"]))
        elif 70 < shipnumber <= 80:
            status = "Great! {}".format(random.choice(["There is definitely love somewhere!", 
                                                       "I can see the love is there! Somewhere...", 
                                                       "I definitely can see that love is in the air"]))
        elif 80 < shipnumber <= 90:
            status = "Over average! {}".format(random.choice(["Love is in the air!", 
                                                              "I can definitely feel the love", 
                                                              "I feel the love! There's a sign of a match!", 
                                                              "There's a sign of a match!", 
                                                              "I sense a match!", 
                                                              "A few things can be improved to make this a match made in heaven!"]))
        elif 90 < shipnumber <= 99:
            status = "True love! {}".format(random.choice(["It's a match!", 
                                                           "There's a match made in heaven!", 
                                                           "It's definitely a match!", 
                                                           "Love is truely in the air!", 
                                                           "Love is most definitely in the air!"]))
        elif shipnumber == 100:
            status = "Forever lover! {}".format(random.choice(["Forever together and never be apart."]))

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

        emb = (discord.Embed(color=shipColor, \
                             title="Love test for:", \
                             timestamp=datetime.utcnow(), \
                             description="**{0}** and **{1}** {2}".format(name1, name2, random.choice([
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
        emb.set_author(name="Shipping Machine!", icon_url="http://moziru.com/images/kopel-clipart-heart-6.png")
        emb.add_field(name="Results:", value=f"{shipnumber}%", inline=True)
        emb.add_field(name="Status:", value=(status), inline=False)
        emb.add_field(name="Love Meter:", value=meter, inline=False)
        await ctx.send(embed=emb)

    @commands.command(aliases=['gay-scanner', 'gayscanner', 'gay','homo'])
    async def gay_scanner(self, ctx,* , user: str = None):
        """very mature command yes haha"""
        if not user:
            user = ctx.author.name
            
        gayness = random.randint(0,100)

        if gayness <= 33:
            gayStatus = random.choice(["No homo", 
                                       "Wearing socks", 
                                       '"Only sometimes"', 
                                       "Straight-ish", 
                                       "No homo bro", 
                                       "Girl-kisser", 
                                       "Hella straight",
                                       "Small amount of Homo detected."])
            gayColor = 0xFFC0CB
        elif 33 < gayness < 66:
            gayStatus = random.choice(["Possible homo", 
                                       "My gay-sensor is picking something up", 
                                       "I can't tell if the socks are on or off", 
                                       "Gay-ish", 
                                       "Looking a bit homo", 
                                       "lol half  g a y", 
                                       "safely in between for now",
                                       "50:50"])
            gayColor = 0xFF69B4
        else:
            gayStatus = random.choice(["LOL YOU GAY XDDD FUNNY", 
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

        emb = discord.Embed(description=f"Gayness for **{user}**", color=gayColor)
        emb.add_field(name="Gayness:", value=f"{gayness}% gay", inline=False)
        emb.add_field(name="Comment:", value=f"{gayStatus} :kiss_mm:", inline=False)
        emb.add_field(name="Gay Meter:", value=meter, inline=False)
        emb.set_author(name="Gay-O-Meter™", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/ICA_flag.svg/2000px-ICA_flag.svg.png")
        await ctx.send(embed=emb)

    @commands.command()
    async def zalgo(self, ctx, *, text: str):
        """
        Zalgo-ify your text!
        """
        def zalgoify(self, text, amount=3):
            zalgo_text = ""
            for c in text:
                zalgo_text += c
                if c != " ":
                    for t, range in ZALGO_PARAMS.items():
                        range = (round(x * amount / 5) for x in range)
                        n = min(randint(*range), len(ZALGO_CHARS[t]))
                        zalgo_text += "".join(sample(ZALGO_CHARS[t], n))
            return zalgo_text
        fw = text.split()[0]
        try:
            amount = min(int(fw), ZALGO_MAX_AMT)
            text = text[len(fw) :].strip()
        except ValueError:
            amount = ZALGO_DEFAULT_AMT
        text = zalgoify(text.upper(), amount)
        await ctx.send(text)

    @commands.command()
    async def textmojify(self, ctx, *, msg):
        """Convert text into emojis"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        if msg != None:
            out = msg.lower()
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
    async def topic(self, ctx):
        """Kept running out of topic to talk about? This command might help you!"""
        await ctx.trigger_typing()
        choice = str(random.choice(topics.questions))
        if choice not in topics.usedTopics:
            topics.usedTopics.append(choice)
            embed_quote = discord.Embed(title="Here is a question...", description=f"{choice}",timestamp = datetime.utcnow())
            embed_quote.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
            await ctx.send(embed=embed_quote)
            topics.usedTopics.popleft()

    @commands.command(aliases=["truths","thetruth"])
    async def truth(self, ctx):
        """Spill out TheTruth!"""
        await ctx.trigger_typing()
        choice = str(random.choice(topics.truth))
        if choice not in topics.usedTruth:
            topics.usedTruth.append(choice)
            embed_quote = discord.Embed(title="Let's start a Truth game!", description=f"{choice}",timestamp = datetime.utcnow())
            embed_quote.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
            await ctx.send(embed=embed_quote)
            topics.usedTruth.popleft()

    @commands.command(aliases=["dares"])
    async def dare(self, ctx):
        """Are you up for the Dare?"""
        await ctx.trigger_typing()
        choice = str(random.choice(topics.dare))
        if choice not in topics.usedDare:
            topics.usedDare.append(choice)
            embed_quote = discord.Embed(title="Here is a Dare for you!", description=f"{choice}",timestamp = datetime.utcnow())
            embed_quote.set_footer(icon_url=ctx.message.author.avatar_url, text=f"Requested by: {ctx.message.author}")
            await ctx.send(embed=embed_quote)
            topics.usedDare.popleft()

    @commands.group(aliases=["mal","anime"], invoke_without_command=True)
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist(self, ctx, * , name: str = None):
        """
        Find anime information from MyAnimeList!
        """
        if name is None:
            await ctx.send(embed=discord.Embed(description="Please specifiy the anime title to find!"))
            return

        if len(name) < 3 :
            await ctx.send(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        fname = name.replace(" ", "+")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.jikan.moe/v3/search/anime?q={fname}&limit=1') as resp:
                    resp.raise_for_status()
                    data = json.loads(await resp.read(), object_hook=DictObject)
                    
        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status is 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status is 429:
                await ctx.send(embed=discord.Embed(description="⚠ We are being rate limited! calm your horses."))
                return
            if resp.status is 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status is 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access Jikan API, it may be down or inaccessible at the moment."))
                return
            elif resp.status is 503:
                await ctx.send(embed=discord.Embed(description="⚠ MyAnimeList is down at the moment, please try again later."))
                return
   
        emb = discord.Embed(title="MyAnimeList Anime Information", timestamp=datetime.utcnow())
    
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

        if score is None or score is 0:
            score = "N/A"

        start = data.results[0].start_date
        end = data.results[0].end_date
        mem = data.results[0].members

        # Time zone converter (a few checks will depends on the presence of time_end value)
        time_start = ciso8601.parse_datetime(start)
        formatted_start = time_start.strftime("%B %d, %Y")
        try:
            time_end = ciso8601.parse_datetime(end)
            formatted_end = time_end.strftime("%B %d, %Y")
        except TypeError:
            formatted_end = "Still Ongoing!"
            
        try:
            total_episode = data.results[0].episodes
        except TypeError:
            total_episode = "Not yet determined."

        if anime_status:
            anime_status = "Ongoing"
        elif not anime_status:
            anime_status = "Finished airing"

        if len(anime_synopsis) > 768:
            shorten(anime_synopsis,width=756,placeholder="...")
        
        emb.set_image(url=anime_img)
        emb.set_thumbnail(url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        emb.add_field(name="📝 Title", value=f"[{anime_title}]({anime_url})", inline=False)
        emb.add_field(name="ℹ Synopsis", value=anime_synopsis, inline=False)
        emb.add_field(name="⌛ Status", value=anime_status, inline=False)
        emb.add_field(name="📺 Type", value=anime_type, inline=False)
        emb.add_field(name="📅 First Air Date", value=formatted_start, inline=False)
        emb.add_field(name="📅 Last Air Date", value=formatted_end, inline=False)
        emb.add_field(name="💿 Episodes", value=total_episode, inline=True)
        emb.add_field(name="⭐ Score", value=f"{score}", inline=True)
        
        try:
            rate = data.results[0].rated
            if rate is None:
                rate = "Unknown"
            emb.add_field(name="🔞 Rated", value=rate, inline=True)
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
    async def myanimelist_manga(self, ctx, * , name: str = None):
        """
        Find manga information from MyAnimeList!
        """
        if name is None:
            await ctx.send(embed=discord.Embed(description="Please specifiy the manga title to find!"))
            return

        if len(name) < 3 :
            await ctx.send(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        fname = name.replace(" ", "+")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.jikan.moe/v3/search/manga?q={fname}&limit=1') as resp:
                    resp.raise_for_status()
                    data = json.loads(await resp.read(), object_hook=DictObject)
                    
        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status is 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status is 429:
                await ctx.send(embed=discord.Embed(description="⚠ We are being rate limited! calm your horses."))
                return
            if resp.status is 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status is 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access Jikan API, it may be down or inaccessible at the moment."))
                return
            elif resp.status is 503:
                await ctx.send(embed=discord.Embed(description="⚠ MyAnimeList is down at the moment, please try again later."))
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

        if stat is True:
            stat = "Ongoing"
        elif not stat:
            stat = "Finished"

        if len(manga_synopsis) > 768:
            shorten(manga_synopsis,width=756,placeholder="...")

        emb = discord.Embed(title="MyAnimeList Manga Information", timestamp=datetime.utcnow())
        emb.set_image(url=img_url)
        emb.set_thumbnail(url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        emb.add_field(name="📑 Title", value=f"[{manga_title}]({manga_url})", inline=False)
        emb.add_field(name="ℹ Synopsis", value=manga_synopsis, inline=False)
        emb.add_field(name="⏳ Status", value=stat, inline=False)
        emb.add_field(name="📁 Type", value=manga_type, inline=False)
        emb.add_field(name="📅 Publish Date", value=formatted_start, inline=False)
        emb.add_field(name="📚 Volumes", value=manga_volumes, inline=True)
        emb.add_field(name="📰 Chapters", value=manga_chapters, inline=True)
        emb.add_field(name="⭐ Score", value=f"{score}", inline=True)
        emb.add_field(name="👥 Members", value=memb, inline=True)
        emb.add_field(name="💳 ID", value=manga_id, inline=True)

        await ctx.send(embed=emb)

    @myanimelist.command(name="character", brief="Find character information", aliases=["chara","char"])
    @commands.cooldown(rate=2, per=3.0, type=commands.BucketType.guild)
    async def myanimelist_chara(self, ctx, * , name: str = None):
        """
        Find character information from MyAnimeList!
        """
        if name is None:
            await ctx.send(embed=discord.Embed(description="Please specifiy the character name to find!"))
            return

        if len(name) < 3 :
            await ctx.send(embed=discord.Embed(description="Three or more characters are required for the query!"))
            return

        await ctx.trigger_typing()

        fname = name.replace(" ", "+")

        try:
            async with aiohttp.ClientSession() as session: #im a fucking idiot
                async with session.get(f'https://api.jikan.moe/v3/search/character?q={fname}&limit=1') as resp:
                    resp.raise_for_status()
                    data = json.loads(await resp.read(), object_hook=DictObject)
                    
        except aiohttp.client_exceptions.ClientResponseError:
            if resp.status is 404:
                await ctx.send(embed=discord.Embed(description="⚠ Not Found."))
                return
            if resp.status is 429:
                await ctx.send(embed=discord.Embed(description="⚠ We are being rate limited! calm your horses."))
                return
            if resp.status is 403:
                await ctx.send(embed=discord.Embed(description="⚠ Forbidden."))
                return
            elif resp.status is 500:
                await ctx.send(embed=discord.Embed(description="⚠ Unable to access Jikan API, it may be down or inaccessible at the moment."))
                return
            elif resp.status is 503:
                await ctx.send(embed=discord.Embed(description="⚠ MyAnimeList is down at the moment, please try again later."))
                return

        char_id = data.results[0].mal_id
        char_url = data.results[0].url
        char_img = data.results[0].image_url
        char_name = data.results[0].name

        emb = discord.Embed(title="MyAnimeList Character Information", timestamp=datetime.utcnow())
        emb.set_image(url=char_img)
        emb.set_thumbnail(url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        emb.add_field(name="👤 Name", value=f"[{char_name}]({char_url})", inline=False)

        try:
            alt_name = data.results[0].alternative_names[0]
            emb.add_field(name="👥 Alternative Name", value=f"{alt_name}", inline=False)
        except IndexError:
            pass

        try:
            char_anime_name = data.results[0].anime[0].name
            char_anime_url = data.results[0].anime[0].url
            emb.add_field(name="📺 Animeography", value=f"[{char_anime_name}]({char_anime_url})", inline=False)
        except IndexError:
            pass
            
        try:
            char_manga_name = data.results[0].manga[0].name
            char_manga_url = data.results[0].manga[0].url
            emb.add_field(name="📚 Mangaography", value=f"[{char_manga_name}]({char_manga_url})", inline=False)
        except IndexError:
            pass
        
        emb.add_field(name="💳 ID", value=char_id, inline=True)

        await ctx.send(embed=emb)

    @commands.command() # https://github.com/sks316/mewtwo-bot/blob/master/cogs/fun.py#L220
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def amiibo(self, ctx, *, query: str):
        #--First we connect to the Amiibo API and download the Amiibo information--#
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://amiiboapi.com/api/amiibo/?name={query}') as amiibo:
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
                    embed = discord.Embed(title=f"Amiibo information for {name} ({series} series)", color=0xd82626)
                    embed.add_field(name='Character Represented', value=character)
                    embed.add_field(name='Amiibo Series', value=f"{series} series")
                    embed.add_field(name='Game of Origin', value=game)
                    embed.add_field(name='Type', value=atype)
                    embed.add_field(name='Released', value=f":flag_us: {na_release}\n:flag_eu: {eu_release}\n:flag_jp: {jp_release}\n:flag_au: {au_release}")
                    embed.set_image(url=image)
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Amiibo.svg/1024px-Amiibo.svg.png")
                    await ctx.send(embed=embed)
                except KeyError:
                    return await ctx.send(":x: I couldn't find any Amiibo with that name. Double-check your spelling and try again.")

    @commands.command() # https://github.com/sks316/mewtwo-bot/blob/master/cogs/fun.py#L252
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def urban(self, ctx, *, query: str):
        msg = await ctx.send("Looking for a definition...")
        try:
            #--First we connect to Urban Dictionary's API and get the results--#
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://api.urbandictionary.com/v0/define?term={query}') as r:
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
                    embed = discord.Embed(title=f":notebook: Urban Dictionary Definition for {word}", description=definition, url=url, color=0x8253c3)
                    if example == None:
                        pass
                    else:
                        embed.add_field(name="Example:", value=example, inline=False)
                    embed.set_footer(text=f"Author: {author} - 👍️ {str(upvotes)} - 👎️ {str(downvotes)}")
                    await msg.edit(content='', embed=embed)
                    
        except:
            await msg.edit(content=":x: Sorry, I couldn't find that word. Check your spelling and try again.")

    @commands.command(aliases=["pokemon", "pkmn"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pokedex(self, ctx, *, query: str):
        await ctx.trigger_typing()
        #--Some Pokemon with several forms are named differently on the API, so if one of those Pokemon are specified, we replace the query with the correct name--#
        pkmn = {
            'meloetta': 'Meloetta - Aria Forme',
            'keldeo': 'Keldeo - Ordinary Form',
            'burmy': 'Burmy - Plant Cloak',
            'wormadam': 'Wormadam - Plant Cloak',
            'cherrim': 'Cherrim - Overcast Form',
            'giratina': 'Giratina - Altered Forme',
            'shaymin': 'Shaymin - Land Forme',
            'basculin': 'Basculin - Red-Striped Form',
            'deerling': 'Deerling - Spring Form',
            'tornadus': 'Tornadus - Incarnate Forme',
            'thundurus': 'Thundurus - Incarnate Forme',
            'landorus': 'Landorus - Incarnate Forme',
            'flabebe': 'Flabébé',
            'zygarde': 'Zygarde - Complete Forme',
            'hoopa': 'Hoopa Confined',
            'oricorio': 'Oricorio - Baile Style',
            'lycanroc': 'Lycanroc - Midday Form',
            'wishiwashi': 'Wishiwashi - Solo Form',
            'minior': 'Minior - Meteor Form',
            'mimikyu': 'Mimikyu - Disguised Form',
        }.get(query.lower(), query)

        #--First we connect to the Pokedex API and download the Pokedex entry--#
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.glitch.me/v1/pokemon/{pkmn}') as dex_entry:
                data = await dex_entry.json()
                #--Now we attempt to extract information--#
                try:
                    pkmn_name = data[0]['name']
                    pkmn_no = data[0]['number']
                    pkmn_desc = data[0]['description']
                    pkmn_img = data[0]['sprite']
                    pkmn_height = data[0]['height']
                    pkmn_weight = data[0]['weight']
                    pkmn_species = data[0]['species']
                    pkmn_type1 = data[0]['types'][0]
                    pkmn_gen = str(data[0]['gen'])
                    pkmn_ability1 = data[0]['abilities']['normal'][0]
                    #--Detect if Pokemon has a second ability--#
                    try:
                        pkmn_ability2 = data[0]['abilities']['normal'][1]
                    except IndexError:
                        pkmn_ability2 = None
                    #--Detect if Pokemon has a hidden ability--#
                    try:
                        pkmn_hiddenability = data[0]['abilities']['hidden'][0]
                    except IndexError:
                        pkmn_hiddenability = None
                    #--Detect if Pokemon has a second type--#
                    try:
                        pkmn_type2 = data[0]['types'][1]
                    except IndexError:
                        pkmn_type2 = None
                    #--Finally, we format it into a nice little embed--#
                    embed = discord.Embed(title=f"Pokédex information for {pkmn_name} (#{pkmn_no})", description=pkmn_desc, color=0xd82626)
                    embed.add_field(name='Height', value=pkmn_height)
                    embed.add_field(name='Weight', value=pkmn_weight)
                    embed.add_field(name='Species', value=pkmn_species)
                    #--Detect if type2 is defined--#
                    if pkmn_type2 == None:
                        embed.add_field(name='Type', value=pkmn_type1)
                    else:
                        embed.add_field(name='Types', value=f"{pkmn_type1}, {pkmn_type2}")
                    #--Detect if ability2 and hiddenability defined--#
                    if pkmn_ability2 == None:
                        if pkmn_hiddenability == None:
                            embed.add_field(name='Ability', value=pkmn_ability1)
                        else:
                            embed.add_field(name='Abilities', value=f"{pkmn_ability1};\n**Hidden:** {pkmn_hiddenability}")
                    else:
                        if pkmn_hiddenability == None:
                            embed.add_field(name='Abilities', value=f"{pkmn_ability1}, {pkmn_ability2}")
                        else:
                            embed.add_field(name='Abilities', value=f"{pkmn_ability1}, {pkmn_ability2};\n**Hidden:** {pkmn_hiddenability}")
                    embed.add_field(name='Generation Introduced', value=f"Gen {pkmn_gen}")
                    embed.set_image(url=pkmn_img)
                    embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/7/79/Dream_Pok%C3%A9_Ball_Sprite.png")
                    await ctx.send(embed=embed)
                except KeyError:
                    return await ctx.send(":x: I couldn't find any Pokémon with that name. Double-check your spelling and try again.")

    @commands.command(aliases=["pats", "pet"]) # https://github.com/sks316/mewtwo-bot/blob/master/cogs/fun.py#L307
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pat(self, ctx, *, user: libneko.converters.InsensitiveMemberConverter = None):
        if user == None:
            return await ctx.send(":x: You need someone to give headpats to! You can give me a headpat if you want...")
        if user == ctx.author:
            return await ctx.send(":x: You can't give yourself headpats! You can give me a headpat if you want...")
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/pat') as pat:
                data = await pat.json()
                result = data.get('url')
                embed = discord.Embed(title=f"{ctx.author.display_name} gives {user.display_name} some headpats!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)
                

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cuddle(self, ctx, *, user: libneko.converters.InsensitiveMemberConverter = None):
        if user == None:
            return await ctx.send(":x: You need someone to cuddle! You can cuddle me if you want...")
        if user == ctx.author:
            return await ctx.send(":x: You can't cuddle yourself! You can cuddle me if you want...")
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/cuddle') as cuddle:
                data = await cuddle.json()
                result = data.get('url')
                embed = discord.Embed(title=f"🤗 {ctx.author.display_name} cuddles {user.display_name}!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)
                

    @commands.command(aliases=["smooch"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kiss(self, ctx, *, user: libneko.converters.InsensitiveMemberConverter = None):
        if user == None:
            return await ctx.send(":x: You need someone to kiss! You can kiss me if you want...")
        if user == ctx.author:
            return await ctx.send(":x: You can't kiss yourself! You can kiss me if you want...")
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/kiss') as kiss:
                data = await kiss.json()
                result = data.get('url')
                embed = discord.Embed(title=f"❤ {ctx.author.display_name} kisses {user.display_name}!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)
                

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def snuggle(self, ctx, *, user: libneko.converters.InsensitiveMemberConverter = None):
        if user == None:
            return await ctx.send(":x: You need someone to cuddle! You can cuddle me if you want...")
        if user == ctx.author:
            return await ctx.send(":x: You can't cuddle yourself! You can cuddle me if you want...")
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/cuddle') as snuggle:
                data = await snuggle.json()
                result = data.get('url')
                embed = discord.Embed(title=f"🤗 {ctx.author.display_name} snuggles {user.display_name}!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)
                

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hug(self, ctx, *, user: libneko.converters.InsensitiveMemberConverter = None):
        if user == None:
            return await ctx.send(":x: You need someone to hug! You can hug me if you want...")
        if user == ctx.author:
            return await ctx.send(":x: You can't hug yourself! You can hug me if you want...")
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/hug') as hug:
                data = await hug.json()
                result = data.get('url')
                embed = discord.Embed(title=f"🤗 {ctx.author.display_name} hugs {user.display_name}!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)
                

def setup(bot):
    bot.add_cog(Fun(bot))
    print("Fun Module has been loaded.")
