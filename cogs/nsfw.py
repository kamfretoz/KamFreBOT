"""
MIT License

Copyright (c) 2019 sks316

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
import aiohttp
import random
from discord.ext import commands

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["r34"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def rule34(self, ctx, *, search: str):
        """
        Browse the Rule34
        """
        await ctx.trigger_typing()
        loading = await ctx.send('Looking for an image on Rule34...')
        #--Connect to Rule34 JSON API and download search data--#
        param = {
            "tags": search,
            "limit": 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://r34-json.herokuapp.com/posts', params = param) as r34:
                data = await r34.json()
                #--Now we attempt to extract information--#
                try:
                    posts = data['posts']
                    post = random.choice(posts)
                    score = post['score']
                    post_id = post['id']
                    image = post['file_url']
                    image = image.replace("https://r34-json.herokuapp.com/images?url=", "")
                    if image.endswith(".webm") or image.endswith(".mp4"):
                        await loading.edit(content=f":underage: Rule34 image for **{search}** \n\n:arrow_up: **Score:** {score}\n\n:link: **Post URL:** <https://rule34.xxx/index.php?page=post&s=view&id={post_id}>\n\n:link: **Video URL:** {image}")
                    else:
                        embed = discord.Embed(title=f":underage: Rule34 image for **{search}**", description=f"_ _ \n:arrow_up: **Score:** {score}\n\n:link: **[Post URL](https://rule34.xxx/index.php?page=post&s=view&id={post_id})**", color=0x8253c3)
                        embed.set_image(url=image)
                        await loading.edit(content='', embed=embed)
                except IndexError:
                    return await loading.edit(content=":x: No results found for your query. Check your spelling and try again.")

    @commands.command(aliases=["gbooru"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def gelbooru(self, ctx, *, search: str):
        """
        Browse the Gelbooru
        """
        await ctx.trigger_typing()
        loading = await ctx.send('Looking for an image on Gelbooru...')
        param = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "tags": search
        }
        #--Connect to Gelbooru JSON API and download search data--#
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://gelbooru.com/index.php', params = param) as gel:
                data = await gel.json()
                #--Now we attempt to extract information--#
                try:
                    post = random.choice(data)
                    score = str(post['score'])
                    post_id = str(post['id'])
                    image = post['file_url']
                    if image.endswith(".webm") or image.endswith(".mp4"):
                        await loading.edit(content=f":underage: Gelbooru image for **{search}** \n\n:arrow_up: **Score:** {score}\n\n:link: **Post URL:** <https://gelbooru.com/index.php?page=post&s=view&id={post_id}>\n\n:link: **Video URL:** {image}")
                    else:
                        embed = discord.Embed(title=f":underage: Gelbooru image for **{search}**", description=f"_ _ \n:arrow_up: **Score:** {score}\n\n:link: **[Post URL](https://gelbooru.com/index.php?page=post&s=view&id={post_id})**", color=0x8253c3)
                        embed.set_image(url=image)
                        await loading.edit(content='', embed=embed)
                except IndexError:
                    return await loading.edit(content=":x: No results found for your query. Check your spelling and try again.")
                except TypeError:
                    return await loading.edit(content=":x: No results found for your query. Check your spelling and try again.")

    @commands.command(aliases=["booby", "tiddy", "tits"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def boobs(self, ctx):
        """
        Boobs!!
        """
        boobs =[
            'https://nekos.life/api/v2/img/boobs',
            'https://nekos.life/api/v2/img/tits',
        ]
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get(random.choice(boobs)) as tiddy:
                data = await tiddy.json()
                result = data.get('url')
                embed = discord.Embed(title="🔞 Boobies!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def fuck(self, ctx, *, user: discord.Member = None):
        """
        FUCC
        """
        if user == None:
            return await ctx.send(":x: You need someone to fuck! Make sure they consent to it first...")
        if user == ctx.author:
            return await ctx.send(":x: You can't fuck yourself! You can masturbate, but you can't self-fuck.")
        #--Get image from NekosLife API--#
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/classic') as fuck:
                data = await fuck.json()
                result = data.get('url')
                embed = discord.Embed(title=f"🔞 {ctx.author.display_name} fucks {user.display_name}!",  color=0x8253c3)
                embed.set_image(url=result)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def yandere(self, ctx, *, search: str):
        """
        Browse the yandere.re
        """
        loading = await ctx.send('Looking for an image on yande.re...')
        #--Connect to yande.re and get first 100 results--#
        yande_agent = {'User-Agent': 'Bobert BOT: https://github.com/kamfretoz/KamFreBOT'}
        param = {
            "tags": search,
            "limit": 100
        }
        async with aiohttp.ClientSession(headers=yande_agent) as session:
            async with session.get(f'https://yande.re/post/index.json', params = param) as yande:
                data = await yande.json()
                #--Now we attempt to extract information--#
                try:
                    post = random.choice(data)
                    score = str(post['score'])
                    post_id = str(post['id'])
                    image = post['file_url']
                    if image.endswith(".webm") or image.endswith(".mp4"):
                        await loading.edit(content=f":underage: yande.re image for **{search}** \n\n:arrow_up: **Score:** {score}\n\n:link: **Post URL:** <https://yande.re/post/show/{post_id}>\n\n:link: **Video URL:** {image}")
                    else:
                        embed = discord.Embed(title=f":underage: yande.re image for **{search}**", description=f"_ _ \n:arrow_up: **Score:** {score}\n\n:link: **[Post URL](https://yande.re/post/show/{post_id})**", color=0x8253c3)
                        embed.set_image(url=image)
                        await loading.edit(content='', embed=embed)
                except IndexError:
                    return await loading.edit(content=":x: No results found for your query. Check your spelling and try again.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def e621(self, ctx, *, search: str):
        """
        Browse e621
        """
        loading = await ctx.send('Looking for an image on e621...')
        #--Connect to e621 and get first 100 results--#
        e621_agent = {'User-Agent': 'Bobert BOT: https://github.com/kamfretoz/KamFreBOT'}
        param = {
            "tags": search,
            "limit": 100
        }
        async with aiohttp.ClientSession(headers=e621_agent) as session:
            async with session.get(f'https://e621.net/posts.json?', params = param) as esix:
                data = await esix.json()
                #--Now we attempt to extract information--#
                try:
                    data = data['posts']
                    post = random.choice(data)
                    score = str(post['score']['total'])
                    post_id = str(post['id'])
                    image = post['file']['url']
                    if image.endswith(".webm") or image.endswith(".mp4"):
                        await loading.edit(content=f":underage: e621 image for **{search}**\n\n:arrow_up: **Score:** {score}\n\n:link: **Post URL:** <https://e621.net/posts/{post_id}>\n\n:link: **Video URL:** {image}")
                    else:
                        embed = discord.Embed(title=f":underage: e621 image for **{search}**", description=f"_ _ \n:arrow_up: **Score:** {score}\n\n:link: **[Post URL](https://e621.net/posts/{post_id})**", color=0x8253c3)
                        embed.set_image(url=image)
                        await loading.edit(content='', embed=embed)
                except IndexError:
                    return await loading.edit(content=":x: No results found for your query. Check your spelling and try again.")
        
def setup(bot):
    bot.add_cog(NSFW(bot))
    print("NSFW Module has been loaded.")
