import asyncio
import random
import time
import config
import quotes
import discord
import libneko
import requests
import os
from discord.ext import commands
from libneko import embeds


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

    @commands.command(aliases=["talk", "speak","s"])
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
    @commands.command(aliases=["stoall"], hidden=True)
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
    @commands.command(aliases=["ttstalk", "speaktts","st"], hidden=True)
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
    async def sayto(self, ctx, destination: libneko.converters.GuildChannelConverter=None, *, text=None):
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
    async def sendto(self, ctx, target: libneko.converters.MemberConverter = None, *, text=None):
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
        random.seed()
        choices = ["https://i.imgur.com/vzcNPdF.png", "https://i.imgur.com/9YBSnmr.png"]
        flip = discord.Embed(title="Flip The Coin!", color=0xFFFFFF)
        flip.set_image(url=random.choice(choices))
        await ctx.send(embed=flip)


    @commands.group(invoke_without_command=True, aliases=["qt"])
    async def quote(self, ctx):
        """Send a random Bobert Quote!"""
        random.seed()
        choice = str(random.choice(quotes.bobert))
        embed_quote = discord.Embed(title="Bobert said...", description=f"{choice}")
        embed_quote.set_thumbnail(url="https://i.imgur.com/zcVN4q1.png")
        await ctx.send(embed=embed_quote)

    @quote.command(aliases=["qtchk"])
    async def quote_check(self,ctx):
        """checks the amount of quotes available."""
        amount = discord.Embed(title="Bobert's Quote Checker", description=f"There are {str(quotes.bobert)} available quotes that are randomly chosen!")
        await ctx.send(embed=amount)

    @commands.command()
    async def dance(self, ctx):
        """Bobert Dance!"""
        bdance = discord.Embed()
        bdance.set_image(url="https://i.imgur.com/1DEtTrQ.gif")
        await ctx.send(embed=bdance)

    @commands.group(invoke_without_command=True, aliases=["meme"])
    async def memes(self, ctx):
        """send memes!"""
        random.seed()
        upload = await ctx.send("Uploading, Please Wait!")
        str(upload)
        await asyncio.sleep(1)
        await ctx.trigger_typing()
        if os.path.isdir(config.dir):
            folder = config.dir + get_filesystem_slash() + random.choice(os.listdir(config.dir))
            await ctx.send(file=discord.File(folder))
        await ctx.send("Finished!")
        await upload.delete()

    @commands.cooldown(rate=2,per=900.0, type=commands.BucketType.user)
    @memes.command(name='overload')
    async def memes_overload(self, ctx, count: int = 5):
        """MOAR MEMES!"""
        random.seed()
        selected_images = []
        uploading = await ctx.send(f"Uploading {count} images... This may take a while.")
        str(uploading)
        await asyncio.sleep(3)
        if count <= 50:
            for i in range(0, int(count)):
                await ctx.trigger_typing()
                stop = False
                while not stop:
                    path = config.dir + get_filesystem_slash() + random.choice(os.listdir(config.dir))
                    if path not in selected_images:
                        selected_images.append(path)
                        await ctx.send(file=discord.File(path))
                        stop = True
        else:
           await ctx.send("Please select the amount between 2 and 50")
        await ctx.send("Finished!", delete_after=3.0)
        await uploading.delete()

    @commands.command(aliases=['tf'])
    async def textface(self, ctx, Type):
        """Get those dank/cool faces here. Type *textface list for a list."""
        if Type is None:
            await ctx.send('That is NOT one of the dank textfaces in here yet. Use: *textface [lenny/tableflip/shrug]')
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
              await ctx.send('That is NOT one of the dank textfaces in here yet. Use *textface list to see a list of the textfaces.')

    @commands.command()
    async def hack(self, ctx, user: discord.Member):
        """Hack someone's account! Try it!"""
        msg = await ctx.send(f"Hacking! Target: {user}")
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
    async def anim(self, ctx, Type):
        """Animations! Usage: *anim [type]. For a list, use *anim list."""
        if Type is None:
            await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type *anim list')
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
              await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type *anim list')             

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
        random.seed()
        choice = random.choice(random.choice(list(ps.values())))

        if choice in ps["psbad"]:
            color = discord.Color(0xFF0000)
        elif choice in ps["psmed"]:
            color = discord.Color(0xFFFF00)
        elif choice in ps["psgood"]:
            color = discord.Color(0x26D934)

        eightball = discord.Embed(color=color)
        eightball.add_field(name="Question:", value=question.capitalize(), inline=False)
        eightball.add_field(name="Answer:", value=f"{choice}.")
        eightball.set_author(
            name="The mighty 8-Ball", icon_url="https://i.imgur.com/Q9dxpTz.png"
        )
        await ctx.send(embed=eightball, content=None)

    @commands.command(hidden=True, aliases=["ily"])
    async def iloveyou(self, ctx):
        await ctx.send(f"{ctx.author.mention}, I love you too! :heart::heart::heart:")

    @commands.command(aliases=["rr"])
    async def rickroll(self, ctx):
        """
        Never gonna give you up...
        """
        rick = discord.Embed()
        rick.set_image(url="https://i.kym-cdn.com/photos/images/original/000/041/494/1241026091_youve_been_rickrolled.gif")
        await ctx.send(embed=rick)

    @commands.command(
        aliases=["bg"], disabled=True
    )
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

    @commands.command(aliases=["kitty", "kitten", "kat"])
    async def cat(self, ctx):
        """
        Send cute cat pics.
        """
        r = requests.get("https://api.thecatapi.com/v1/images/search").json()
        url = r[0]["url"]
        color = ctx.author.color
        embed = discord.Embed(description="Here's a cute kitty :D", color=color)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["doggie","doge"])
    async def dog(self, ctx):
        """
        Send cute cat pics.
        """
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
    @commands.command(name="curse", aliases=("oppugno", "jynx", "kutuk", "santet"), hidden=True)
    async def emoji_curse(self, ctx, user: discord.Member, emoji: discord.Emoji, *, text=None):
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

def setup(bot):
    bot.add_cog(Fun(bot))
    print("Fun Module has been loaded.")
