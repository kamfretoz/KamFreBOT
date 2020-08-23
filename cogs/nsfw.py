import discord
import asyncio
import aiohttp
import libneko
import json
import ciso8601
from datetime import datetime
from discord.ext import commands

class DictObject(dict):
    def __getattr__(self, item):
        return self[item]

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["r34"])
    @commands.is_nsfw()
    async def rule34(self, ctx, query: str):
        """
        Allows you to search for R34 Tags
        """
        await ctx.trigger_typing()

        tags = query.replace(" ","_")

        async with aiohttp.ClientSession() as session: #https://github.com/kurozenzen/r34-json-api
            async with session.get(f"https://r34-json.herokuapp.com/posts?limit=1&tags={tags}") as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                await session.close()

        try:
            image = data.posts[0].file_url
            score = data.posts[0].score
            rating = data.posts[0].rating
            post_date = data.posts[0].created_at
        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ No result was found."))
            return

        #converted_time = ciso8601.parse_datetime(post_date)
        #formatted_time = converted_time.strftime("%B %d, %Y")

        emb = discord.Embed(title="Rule34 Image Viewer", timestamp=datetime.utcnow())
        emb.add_field(name="Score", value=score, inline=True)
        emb.add_field(name="Rating", value=rating, inline=True)
        emb.add_field(name="Posted On", value=post_date, inline=False)
        emb.set_image(url=image)
        emb.set_footer(text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=emb)
        
def setup(bot):
    bot.add_cog(NSFW(bot))
    print("NSFW Module has been loaded.")
