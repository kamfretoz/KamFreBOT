import discord
import asyncio
import aiohttp
import libneko
import json
from datetime import datetime
from discord.ext import commands

class DictObject(dict):
    def __getattr__(self, item):
        return self[item]

class F1MotorSport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def f1(self, ctx):
        mainemb = discord.Embed(description="This command can provide you with information around F1™ Races.\nHere are the available command:")
        mainemb.add_field(name="Race Schedule", value="`[p]f1 schedule [season] [round]`")
        mainemb.add_field(name="Race Result", value="`[p]f1 result [season] [round]`")
        await ctx.send(embed=mainemb)

    @f1.command(name="schedule", aliases=["racesched"], brief="Shows the schedule of F1™ races.")
    async def f1_raceschedule(self, ctx, season: str = "current", round: int = 1):
        """
        Shows the schedule of F1™ races.
        `[p]f1 schedule <season> <round>`
        """

        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ergast.com/api/f1/{season}/{round}.json?limit=1") as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                await session.close()

        try:
            seasoninfo = data.MRData.RaceTable.Races[0].season
            rnd = data.MRData.RaceTable.Races[0].round
            urlrace = data.MRData.RaceTable.Races[0].url
            racename = data.MRData.RaceTable.Races[0].raceName
            circuitname = data.MRData.RaceTable.Races[0].Circuit.circuitName
            urlcircuit = data.MRData.RaceTable.Races[0].Circuit.url
            loc = data.MRData.RaceTable.Races[0].Circuit.Location.locality
            country = data.MRData.RaceTable.Races[0].Circuit.Location.country
            long = data.MRData.RaceTable.Races[0].Circuit.Location.long
            lat = data.MRData.RaceTable.Races[0].Circuit.Location.lat

            time = data.MRData.RaceTable.Races[0].time
            date = data.MRData.RaceTable.Races[0].date

        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error occured! Make sure the season and round number are correct!"))
            return

        emb = discord.Embed(title="F1™ Race Schedule Information", timestamp=datetime.utcnow())
        emb.set_thumbnail(url="https://i.ibb.co/nRfTBPZ/F1.png")
        emb.add_field(name="Season", value=seasoninfo, inline=True)
        emb.add_field(name="Round", value=rnd, inline=True)
        emb.add_field(name="Date", value=date, inline=False)
        emb.add_field(name="Time", value=time, inline=False)
        emb.add_field(name="Race Name",value=f"[{racename}]({urlrace})", inline=False)
        emb.add_field(name="Circuit Name", value=f"[{circuitname}]({urlcircuit})", inline=False)
        emb.add_field(name="Country", value=country, inline=False)
        emb.add_field(name="Location", value=loc, inline=False)
        emb.add_field(name="Longitude", value=long, inline=True)
        emb.add_field(name="Latitude", value=lat, inline=True)

        await ctx.send(embed=emb)

    @f1.command(name="result", aliases=["raceresult"], brief="Shows the result of an F1™ Race.")
    async def f1_raceresult(self, ctx, season: str = "current", round: str = "last"):
        """
        Shows the result of an F1™ Race. (Only 1st place winner will be shown)
        `[p]f1 result <season> <round>`
        """
    
        await ctx.trigger_typing()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ergast.com/api/f1/{season}/{round}/results.json?limit=1") as resp:
                resp.raise_for_status()
                data = json.loads(await resp.read(), object_hook=DictObject)
                await session.close()

        try:
            #CIRCUIT INFO
            seasoninfo = data.MRData.RaceTable.Races[0].season
            rnd = data.MRData.RaceTable.Races[0].round
            urlrace = data.MRData.RaceTable.Races[0].url
            racename = data.MRData.RaceTable.Races[0].raceName
            circuitname = data.MRData.RaceTable.Races[0].Circuit.circuitName
            urlcircuit = data.MRData.RaceTable.Races[0].Circuit.url
            loc = data.MRData.RaceTable.Races[0].Circuit.Location.locality
            country = data.MRData.RaceTable.Races[0].Circuit.Location.country
            long = data.MRData.RaceTable.Races[0].Circuit.Location.long
            lat = data.MRData.RaceTable.Races[0].Circuit.Location.lat
            time = data.MRData.RaceTable.Races[0].time
            date = data.MRData.RaceTable.Races[0].date


            #DRIVER INFO (1st winner only)
            givendrvname = data.MRData.RaceTable.Races[0].Results[0].Driver.givenName
            fmdrvname = data.MRData.RaceTable.Races[0].Results[0].Driver.familyName
            drvdob = data.MRData.RaceTable.Races[0].Results[0].Driver.dateOfBirth
            drvnatio = data.MRData.RaceTable.Races[0].Results[0].Driver.nationality
            drvpos = data.MRData.RaceTable.Races[0].Results[0].position
            drvnum = data.MRData.RaceTable.Races[0].Results[0].number
            drvurl = data.MRData.RaceTable.Races[0].Results[0].Driver.url

            #CONSTRUCTOR INFO 
            consname = data.MRData.RaceTable.Races[0].Results[0].Constructor.name
            consurl = data.MRData.RaceTable.Races[0].Results[0].Constructor.url
            consnatio = data.MRData.RaceTable.Races[0].Results[0].Constructor.nationality

            #RACE STATISTIC
            lap = data.MRData.RaceTable.Races[0].Results[0].laps
            stat = data.MRData.RaceTable.Races[0].Results[0].status
            timestat = data.MRData.RaceTable.Races[0].Results[0].Time.time
            fslap = data.MRData.RaceTable.Races[0].Results[0].FastestLap.lap
            fslaptime = data.MRData.RaceTable.Races[0].Results[0].FastestLap.Time.time
            fslaprank = data.MRData.RaceTable.Races[0].Results[0].FastestLap.rank
            avgspeed = data.MRData.RaceTable.Races[0].Results[0].FastestLap.AverageSpeed.speed
            avgspeedunit = data.MRData.RaceTable.Races[0].Results[0].FastestLap.AverageSpeed.units

        except IndexError:
            await ctx.send(embed=discord.Embed(description="⚠ An Error occured! Make sure the season and round number are correct!"))
            return

        emb = discord.Embed(title="F1™ Race Result Information")
        emb.set_thumbnail(url="https://i.ibb.co/nRfTBPZ/F1.png")
        emb.add_field(name="Season", value=seasoninfo, inline=True)
        emb.add_field(name="Round", value=rnd, inline=True)
        emb.add_field(name="Date", value=date, inline=False)
        emb.add_field(name="Time", value=time, inline=False)
        emb.add_field(name="Race Name",value=f"[{racename}]({urlrace})", inline=False)
        emb.add_field(name="Circuit Name", value=f"[{circuitname}]({urlcircuit})", inline=False)
        emb.add_field(name="Country", value=country, inline=False)
        emb.add_field(name="Location", value=loc, inline=False)
        emb.add_field(name="Longitude", value=long, inline=True)
        emb.add_field(name="Latitude", value=lat, inline=True)

        embdrv = discord.Embed(title="Driver Information")
        embdrv.set_thumbnail(url="https://i.ibb.co/nRfTBPZ/F1.png")
        embdrv.add_field(name="Driver Name", value=f"[{givendrvname} {fmdrvname}]({drvurl})", inline=False)
        embdrv.add_field(name="Date of Birth", value=drvdob, inline=False)
        embdrv.add_field(name="Nationality", value=drvnatio, inline=False)
        embdrv.add_field(name="Number", value=drvnum, inline=True)
        embdrv.add_field(name="Position", value=drvpos, inline=True)

        embcons = discord.Embed(title="Constructor Information")
        embcons.set_thumbnail(url="https://i.ibb.co/nRfTBPZ/F1.png")
        embcons.add_field(name="Name", value=f"[{consname}]({consurl})", inline=False)
        embcons.add_field(name="Nationality", value=consnatio, inline=False)

        embstats = discord.Embed(title="Race Statistic")
        embstats.set_thumbnail(url="https://i.ibb.co/nRfTBPZ/F1.png")
        embstats.add_field(name="Status", value=stat, inline=False)
        embstats.add_field(name="Lap", value=lap, inline=True)
        embstats.add_field(name="Time", value=timestat, inline=True)
        embstats.add_field(name="Fastest Lap", value=fslap, inline=False)
        embstats.add_field(name="Fastest Lap Time", value=fslaptime, inline=False)
        embstats.add_field(name="Fastest Lap Rank", value=fslaprank, inline=False)
        embstats.add_field(name="Average Speed", value=f"{avgspeed} {avgspeedunit.title()}", inline=False)

        allembeds = [emb, embdrv, embcons, embstats]

        navi = libneko.EmbedNavigator(ctx, allembeds)

        await navi.start()

    
def setup(bot):
    print("F1 Module has been Loaded.")
    bot.add_cog(F1MotorSport(bot))