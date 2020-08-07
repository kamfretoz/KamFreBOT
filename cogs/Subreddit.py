import discord, datetime, time, aiohttp, asyncio, random
from discord.ext import commands
from random import randint
from random import choice
from urllib.parse import quote_plus
from collections import deque

acceptableImageFormats = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]
memeHistory = deque()
memeSubreddits = ["BikiniBottomTwitter", "memes", "2meirl4meirl", "deepfriedmemes", "MemeEconomy"]

async def getSub(self, ctx, query: str):
        """Get stuff from requested sub"""
        sub = query.replace(" ","_")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r{sub}/hot.json?limit=100") as response:
                request = await response.json()
                await session.close()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                #print(f"failed request {attempts}")
                await asyncio.sleep(3)
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=100") as response:
                        request = await response.json()
                        await session.close()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'url' in val['data']:
                        url = val['data']['url']
                        urlLower = url.lower()
                        accepted = False
                        for j, v, in enumerate(acceptableImageFormats): #check if it's an acceptable image
                            if v in urlLower:
                                accepted = True
                        if accepted:
                            if url not in memeHistory:
                                memeHistory.append(url)  #add the url to the history, so it won't be posted again
                                if len(memeHistory) > 64: #limit size
                                    memeHistory.popleft() #remove the oldest
                                break #done with this loop, can send image
                await ctx.send(memeHistory[len(memeHistory) - 1]) #send the last image
                return
        await ctx.send(f"_{str(request['message'])}! ({str(request['error'])})_")

class Subreddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        """Memes from various subreddits (excluding r/me_irl. some don't understand those memes)"""
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r/{random.choice(memeSubreddits)}/hot.json?limit=100") as response:
                request = await response.json()
                await session.close()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                print(f"failed request {attempts}")
                await asyncio.sleep(2)
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://www.reddit.com/r/{(random.choice(memeSubreddits)}/hot.json?limit=100") as response:
                        request = await response.json()
                        await session.close()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'url' in val['data']:
                        url = val['data']['url']
                        urlLower = url.lower()
                        accepted = False
                        for j, v, in enumerate(acceptableImageFormats): 
                            if v in urlLower:
                                accepted = True
                        if accepted:
                            if url not in memeHistory:
                                memeHistory.append(url)  
                                if len(memeHistory) > 64: 
                                    memeHistory.popleft() 

                                break 
                await ctx.send(memeHistory[len(memeHistory) - 1])
                return
        await ctx.send(f"_{str(request['message'])}! ({str(request['error'])})_")
    
    @commands.command()
    async def showerthought(self, ctx):
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.reddit.com/r/showerthoughts/hot.json?limit=100") as response:
                request = await response.json()
                await session.close()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                print(f"failed request {attempts}")
                await asyncio.sleep(2)
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://www.reddit.com/r/showerthoughts/hot.json?limit=100") as response:
                        request = await response.json()
                        await session.close()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'title' in val['data']:
                        url = val['data']['title']
                        urlLower = url.lower()
                        accepted = False
                        if url == "What Is A Showerthought?":
                            accepted = False
                        elif url == "Showerthoughts is looking for new moderators!":
                            accepted = False
                        elif url == "IMPORTANT PSA: No, you did not win a gift card.":
                            accepted = False
                        elif url == "Black lives matter. Registering to vote and how to vote by mail.":
                            accepted = False
                        else:
                            accepted = True
                        if accepted:
                            if url not in memeHistory:
                                memeHistory.append(url)
                                if len(memeHistory) > 63:
                                    memeHistory.popleft()

                                break
                await ctx.send(memeHistory[len(memeHistory) - 1])
                return
        await ctx.send(f"_{str(request['message'])}! ({str(request['error'])})_")

    
    @commands.command(aliases=['dankmeme', 'dank'])
    async def dankmemes(self, ctx):
        await ctx.trigger_typing()
        await getSub(self, ctx, 'dankmemes')
        
    @commands.command()
    async def me_irl(self, ctx):
        await ctx.trigger_typing()
        await getSub(self, ctx, 'me_irl')

    @commands.command()
    async def programmerhumor(self, ctx):
        await ctx.trigger_typing()
        await getSub(self, ctx, 'ProgrammerHumor')

    @commands.command()
    async def sub(self, ctx, subreddit: str = None):
        if subreddit is None:
            await ctx.send(embed=discord.Embed(description="Please specify the subreddit!"))
            return
        try:
            await ctx.trigger_typing()
            await getSub(self, ctx, subreddit)
        except:
            await ctx.send("An Error occured. Make sure the subreddit name were correct!")

def setup(bot):
    print("Subreddit Module has been Loaded.")
    bot.add_cog(Subreddit(bot))
