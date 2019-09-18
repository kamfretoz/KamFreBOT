import discord
import config
import random
import asyncio
import aiohttp
import aiofiles
import quotes
import aiofiles
import os
import requests
import datetime
import time
from random import randint, choice, sample
import re
import collections
import libneko
from libneko import commands, pag, converters, embeds, logging
from discord.ext import commands

ZALGO_DEFAULT_AMT = 3
ZALGO_MAX_AMT = 7

ZALGO_PARAMS = {
    'above': (5, 10),
    'below': (5, 10),
    'overlay': (0, 2)
}

ZALGO_CHARS = {
    'above': ['\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305', '\u0306', '\u0307', '\u0308', '\u0309', '\u030A', '\u030B', '\u030C', '\u030D', '\u030E', '\u030F', '\u0310', '\u0311', '\u0312', '\u0313', '\u0314', '\u0315', '\u031A', '\u031B', '\u033D', '\u033E', '\u033F', '\u0340', '\u0341', '\u0342', '\u0343', '\u0344', '\u0346', '\u034A', '\u034B', '\u034C', '\u0350', '\u0351', '\u0352', '\u0357', '\u0358', '\u035B', '\u035D', '\u035E', '\u0360', '\u0361'],
    'below': ['\u0316', '\u0317', '\u0318', '\u0319', '\u031C', '\u031D', '\u031E', '\u031F', '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327', '\u0328', '\u0329', '\u032A', '\u032B', '\u032C', '\u032D', '\u032E', '\u032F', '\u0330', '\u0331', '\u0332', '\u0333', '\u0339', '\u033A', '\u033B', '\u033C', '\u0345', '\u0347', '\u0348', '\u0349', '\u034D', '\u034E', '\u0353', '\u0354', '\u0355', '\u0356', '\u0359', '\u035A', '\u035C', '\u035F', '\u0362'],
    'overlay': ['\u0334', '\u0335', '\u0336', '\u0337', '\u0338']
}

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    # Say Command
    @commands.command(aliases=["talk", "speak"])
    #@commands.bot_has_permissions(manage_messages=True)
    async def say(self, ctx, *, text = None):
        """Say whatever you typed in"""
        try:
            if text == None:
                await ctx.send("❓ What do you want me to say?", delete_after=5.0)
                await ctx.message.add_reaction("❓")
            else:
                await ctx.trigger_typing()
                await ctx.send(text)
                await ctx.message.delete()
        except:
            pass

    # Say Command with TTS
    @commands.command(aliases=["ttstalk", "speaktts"], hidden=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def saytts(self, ctx, *, text = None):
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


    @commands.command(aliases=["sto"])
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sayto(self, ctx, destination: discord.TextChannel, *, text = None):
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

    @commands.command(aliases=["send","dm"])
    @commands.guild_only()
    async def sendto(self, ctx, target: discord.Member = None, *, text = None):
        """Send whatever you want to a user's DM"""
        if text == None:
            await ctx.send("What do you want me to say?", delete_after=10.0)
            await ctx.message.add_reaction("❓")
        elif target == None:
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
        #flip = discord.Embed(title="Flip The Coin!", color=0xFFFFFF)
        #flip.set_image(url=random.choice(choices))
        await ctx.send(random.choice(choices))

    @commands.command(name="8ball", aliases=["ball"])
    async def ball(self, ctx, *, question: str):
        """Ask a question to the 8Ball!"""
        ps = {
            "psgood": [
                "Yes",
                "It is certain",
                "It is decidedly so",
                "Without a doubt",
                "Yes - definitly",
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
        
        eightball = discord.Embed(color = color)
        eightball.add_field(name='Question:', value=question.capitalize())
        eightball.add_field(name='Answer:', value=f'{choice}.')
        eightball.set_author(name='The mighty 8-Ball', icon_url='https://i.imgur.com/Q9dxpTz.png')
        await ctx.send(embed=eightball, content=None)

    @commands.command(hidden=True, aliases=["ily"])
    async def iloveyou(self, ctx):
        await ctx.send(f"{ctx.author.mention}, I love you too! :heart::heart::heart:")

    @commands.command(
        aliases=["rr"]
    )
    async def rickroll(self, ctx):
        rick = discord.Embed()
        rick.set_image(url="https://media.giphy.com/media/kFgzrTt798d2w/giphy.gif")
        await ctx.send(embed=rick)

    @commands.command(
        aliases=["bg"],
        disabled=True,
    )
    async def bigtext(self, ctx, *, text: str):
        s = ""
        for char in text:
            if char.isalpha():
                s += f":regional_indicator_{char.lower()}: "
            elif char.isspace():
                s += "   "
        await ctx.send(s)

    @commands.command(aliases = ['kitty', 'kitten', "kat"])
    async def cat(self,ctx):
        r = requests.get('https://api.thecatapi.com/v1/images/search').json()
        url = r[0]['url']
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute kitty :D", color=color)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases= ['doggie'])
    async def dog(self,ctx):
        r = requests.get('https://api.thedogapi.com/v1/images/search').json()
        url = r[0]['url']
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute doggo!! :D", color=color)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["googleit","searchit"])
    async def lmgtfy(self, ctx, *, query:str):
        """Search Google the fun way ;)"""
        result = f"http://lmgtfy.com/?q={query}"
        final = result.replace(" ","+")
        gugel = discord.Embed(title=f"Searching for: **{query}**", description=f"[Click Here]({final})")
        gugel.set_image(url="https://lmgtfy.com/assets/logo-color-small-70dbef413f591a3fdfcfac7b273791039c8fd2a5329e97c4bfd8188f69f0da34.png")
        await ctx.send(embed=gugel, content=None)
        
    @commands.command(aliases=["zucc"])
    async def succ(self, ctx):
        """Gives you the zucc"""
        zuccy = discord.Embed()
        zuccy.set_image(url="https://pics.me.me/he-protec-he-attac-but-most-importantly-he-zucc-28716903.png")
        await ctx.send(embed=zuccy, content="<:zucc:451945809144184862>")
    
    
    def zalgoify(self, text, amount=3):
        zalgo_text = ''
        for c in text:
            zalgo_text += c
            if c != ' ':
                for t, range in ZALGO_PARAMS.items():
                    range = (round(x*amount/5) for x in range)
                    n = min(randint(*range), len(ZALGO_CHARS[t]))
                    zalgo_text += ''.join(sample(ZALGO_CHARS[t], n))
        return zalgo_text

    @commands.command()
    async def zalgo(self, ctx, *, text: str):
        fw = text.split()[0]
        try:
            amount = min(int(fw), ZALGO_MAX_AMT)
            text = text[len(fw):].strip()
        except ValueError:
            amount = ZALGO_DEFAULT_AMT
        text = self.zalgoify(text.upper(), amount)
        await ctx.send(text)
        
def setup(bot):
    bot.add_cog(Fun(bot))