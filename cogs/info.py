"""
MIT License
Copyright (c) 2018-2019 Koyagami
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
import random
from collections import Counter
from datetime import datetime

import discord
import libneko
import psutil
import bs4
import lxml
from discord.ext import commands

import config


def format_seconds(time_seconds):
    """Formats some number of seconds into a string of format. d days, x hours, y minutes, z seconds"""
    seconds = time_seconds
    hours = 0
    minutes = 0
    days = 0
    while seconds >= 60:
        if seconds >= 60 * 60 * 24:
            seconds -= 60 * 60 * 24
            days += 1
        elif seconds >= 60 * 60:
            seconds -= 60 * 60
            hours += 1
        elif seconds >= 60:
            seconds -= 60
            minutes += 1

    return f"{days}d {hours}h {minutes}m {seconds}s"


counter = datetime.now()


###############################


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # About command
    @commands.command(brief="Some info about the bot. :)", hidden=True)
    async def about(self, ctx):
        """Information about this bot."""
        about = discord.Embed(
            title=f"{config.botname}", description=f"{config.desc}", color=0xFFFFFF
        )
        about.set_footer(text="Made by KamFretoZ#0080")
        await ctx.send(embed=about)

    @commands.command(aliases=["status"], pass_context=True)
    async def stats(self, ctx):
        """Bot stats."""

        def solveunit(input):
            output = ((input // 1024) // 1024) // 1024
            return int(output)

        try:
            mem_usage = "{:.2f} MiB".format(
                __import__("psutil").Process().memory_full_info().uss / 1024 ** 2
            )
        except AttributeError:
            # OS doesn't support retrieval of USS (probably BSD or Solaris)
            mem_usage = "{:.2f} MiB".format(
                __import__("psutil").Process().memory_full_info().rss / 1024 ** 2
            )

        uptime = datetime.now() - counter
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time = "%s days, %s hours, %s minutes, and %s seconds" % (
                days,
                hours,
                minutes,
                seconds,
            )
        else:
            time = "%s hours, %s minutes, and %s seconds" % (hours, minutes, seconds)
        channel_count = 0
        for guild in self.bot.guilds:
            channel_count += len(guild.channels)
        try:
            em = discord.Embed(title="Bot Stats", color=0x32441C)
            em.add_field(
                name=":desktop: CPU Usage.",
                value=f"{psutil.cpu_percent():.2f}%",
                inline=False,
            )
            em.add_field(
                name=":gear: CPU Frequency.",
                value=f"{psutil.cpu_freq().current} MHz",
                inline=False,
            )
            em.add_field(
                name=":computer: Memory Usage.",
                value=f"System Memory Usage: {psutil.virtual_memory().percent}%",
                inline=False,
            )
            em.add_field(
                name="\U0001F4BE BOT Memory usage:", value=mem_usage, inline=False
            )
            em.add_field(
                name=":minidisc: Disk Usage.",
                value=f"Total Size: {solveunit(psutil.disk_usage('/').total)} GB \nCurrently Used: {solveunit(psutil.disk_usage('/').used)} GB",
                inline=False,
            )
            em.add_field(name="\U0001F553 Uptime", value=time, inline=False)
            em.add_field(
                name="\u2694 Servers", value=str(len(self.bot.guilds)), inline=False
            )
            em.add_field(
                name="\ud83d\udcd1 Channels", value=str(channel_count), inline=False
            )

            await ctx.send(content=None, embed=em)
        except(discord.Forbidden):
            msg = (
                "**Bot Stats:** ```Uptime: %s\nMessages Sent: %s\nMessages Received: %s\nMentions: %s\nguilds: %s\nKeywords logged: %s\nGame: %s```"
                % (time)
            )
            str(len(self.bot.guilds))
            await ctx.send(msg)
            await ctx.message.delete()

    @commands.group(
        invoke_without_command=True,
        brief="Show this server info",
        aliases=["server", "si"],
    )
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """This command will show some informations about this server"""
        guild = ctx.guild
        roles = [role.name.replace("@", "@\u200b") for role in guild.roles]

        booster_amount = None

        if guild.premium_subscription_count is None:
            booster_amount = "This server is not boosted"
        else:
            booster_amount = (
                f"{guild.premium_subscription_count} user(s) has boosted this server!"
            )

        # we're going to duck type our way here
        class Secret:
            pass

        secret_member = Secret()
        secret_member.id = 0
        secret_member.roles = [guild.default_role]

        # figure out what channels are 'secret'
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            text_channels += is_text
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1

        regular_channels = len(guild.channels) - secret_channels
        voice_channels = len(guild.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in guild.members)

        server = discord.Embed(
            color=ctx.message.author.color, timestamp=datetime.utcnow()
        )
        server.title = f"Information about {guild.name}"
        server.add_field(name="》 ID", value=guild.id, inline=False)
        server.add_field(
            name="》 Owner",
            value=f"{guild.owner.mention} ({guild.owner.name})",
            inline=False,
        )
        server.add_field(name="》 Owner ID", value=guild.owner_id, inline=False)
        if guild.icon:
            server.set_thumbnail(url=guild.icon_url_as(format="png", size=1024))

        if guild.splash:
            server.set_image(url=guild.splash_url)

        fmt = f"Text {text_channels} ({secret_channels} secret)\nVoice {voice_channels} ({secret_voice} locked)"
        server.add_field(name="》 Channels", value=fmt)

        fmt = (
            f'Online: {member_by_status["online"]}\n'
            f'Idle: {member_by_status["idle"]}\n'
            f'Do Not Disturb: {member_by_status["dnd"]}\n'
            f'Offline: {member_by_status["offline"]}\n'
            f"Total: {guild.member_count}"
        )
        server.add_field(
            name="》 Created",
            value=guild.created_at.strftime("%d-%m-%Y at %H:%M:%S"),
            inline=False,
        )
        server.add_field(name="》 Is a large guild?", value=guild.large, inline=False)
        server.add_field(name="》 Region", value=f"{guild.region}", inline=False)
        server.add_field(name="》 AFK Channel", value=guild.afk_channel, inline=False)
        server.add_field(
            name="》 AFK Timeout", value=f"{guild.afk_timeout} Seconds", inline=False
        )
        server.add_field(name="》 2FA Level", value=guild.mfa_level, inline=False)
        server.add_field(
            name="》 Verification Level", value=guild.verification_level, inline=False
        )
        server.add_field(
            name="》 Explicit Content Filter",
            value=guild.explicit_content_filter,
            inline=False,
        )
        server.add_field(
            name="》 Default Notification",
            value=guild.default_notifications,
            inline=False,
        )
        server.add_field(name="》 Server Features", value=guild.features, inline=False)
        server.add_field(
            name="》 Nitro Boost Status", value=booster_amount, inline=False
        )
        server.add_field(name="》 Members", value=fmt, inline=False)
        server.add_field(
            name="》 Roles",
            value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
            inline=False,
        )
        server.set_footer(
            text=f"Requested by {ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=f"{ctx.message.author.avatar_url}",
        )
        await ctx.send(embed=server, content=None)

    @serverinfo.command(brief="Show this server icon", name="icon")
    @commands.guild_only()
    async def serverinfo_icon(self, ctx):
        icon = discord.Embed(
            title=f"Server icon for {ctx.guild.name}", color=ctx.message.author.color
        )
        icon.set_image(url=ctx.guild.icon_url_as(format="png", size=2048))
        await ctx.send(embed=icon, content=None)

    @serverinfo.command(
        brief="shows the amount of members on this server",
        name="membercount",
        aliases=["count", "memcount"],
    )
    @commands.guild_only()
    async def serverinfo_membercount(self, ctx):
        bots = 0
        members = 0
        total = 0
        for x in ctx.guild.members:
            if x.bot is True:
                bots += 1
                total += 1
            else:
                members += 1
                total += 1
        count = discord.Embed(
            color=ctx.message.author.color, title=f"{ctx.guild.name} Member Count"
        )
        count.add_field(name="User Count", value=f"{members}", inline=False)
        count.add_field(name="Bot Count", value=f"{bots}", inline=False)
        count.add_field(name="Total", value=f"{total}", inline=False)
        await ctx.send(embed=count, content=None)

    @serverinfo.command(
        no_pm=True, brief="Shows ALL channels, use wisely!", name="channels"
    )
    @commands.guild_only()
    async def serverinfo_channels(self, ctx, serverid: int = None):
        if serverid is None:
            server = ctx.guild
        else:
            server = discord.utils.get(self.bot.guilds, id=serverid)
            if server is None:
                return await ctx.send("Server not found!")

        e = discord.Embed()

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
            await ctx.send(":Warning: Unable to send the embed. Make sure that you have allowed the Embed Permission! (OR the embed itself is maybe too long to be displayed)")

    @serverinfo.command(
        aliases=["ri", "role"],
        no_pm=True,
        name="roleinfo",
        brief="Shows some info about a role",
    )
    @commands.guild_only()
    async def serverinfo_roleinfo(self, ctx, *, role: discord.Role):
        """Shows information about a role"""
        guild = ctx.guild

        since_created = (ctx.message.created_at - role.created_at).days
        role_created = role.created_at.strftime("%d %b %Y %H:%M")
        created_on = "{} ({} days ago!)".format(role_created, since_created)
        members = ""
        i = 0
        for user in role.members:
            members += f"{user.name}, "
            i += 1
            if i > 30:
                break

        if str(role.colour) is "#000000":
            colour = "default"
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            color = int(colour[1:], 16)
        else:
            colour = str(role.colour).upper()
            color = role.colour

        em = discord.Embed(colour=color)
        em.set_author(name=role.name)
        em.add_field(name="Users", value=len(role.members))
        em.add_field(name="Mentionable", value=role.mentionable)
        em.add_field(name="Hoist", value=role.hoist)
        em.add_field(name="Position", value=role.position)
        em.add_field(name="Managed", value=role.managed)
        em.add_field(name="Colour", value=colour)
        em.add_field(name="Creation Date", value=created_on)
        em.add_field(name="Members", value=members[:-2], inline=False)
        em.set_footer(text=f"Role ID: {role.id}")

        await ctx.send(embed=em)

    @commands.guild_only()
    @serverinfo.command(
        name="inrole",
        brief="Show the list of users on a particular role",
    )
    async def serverinfo_inrole(self, ctx, role:discord.Role):
        embed = discord.Embed(
            description=f"List of users on the {role.name} role.", color=0x00FF00
        )
        for x in role.members:
            embed.add_field(
                name=f"{x.name}#{x.discriminator}", value=f"{x.mention}", inline=False
            )

        embed.set_footer(text=f"{len(role.members)} Users in total")
        await ctx.send(embed=embed)

    @serverinfo.command(
        brief="Shows who is the owner of this server", name="owner", aliases=["own"]
    )
    @commands.guild_only()
    async def serverinfo_owner(self, ctx):
        await ctx.send(
            embed=discord.Embed(
                description=f"{ctx.guild.owner} ({ctx.guild.owner.mention}) owns this server!"
            )
        )

    @serverinfo.command(
        brief="Shows when this server was created",
        name="created",
        aliases=["madeon", "born"],
    )
    @commands.guild_only()
    async def serverinfo_created(self, ctx):
        await ctx.send(
            f"**{ctx.guild.name}** was created on `{ctx.guild.created_at.strftime('%B %d, %Y at %I:%M %p')}`"
        )

    @serverinfo.command(
        brief="shows people with administrator permission on the server",
        aliases=["mods", "mod", "admin"],
        name="admins",
    )
    @commands.guild_only()
    async def serverinfo_admins(self, ctx):
        admin = discord.Embed(description=f"Admins on {ctx.guild.name}", color=0x00FF00)
        for x in ctx.guild.members:
            if x.bot is False:
                if x.guild_permissions.administrator:
                    admin.add_field(
                        name=f"{x.name}",
                        value=f"{x.mention}\n===========================",
                        inline=False,
                    )
        await ctx.send(embed=admin)

    @commands.guild_only()
    @serverinfo.command(
        aliases=["booster"],
        name="boost",
        brief="Show the list of Nitro booster on this server",
    )
    async def serverinfo_boost(self, ctx):
        boost = discord.Embed(
            description=f"Nitro Booster on {ctx.guild.name}.", color=0x00FF00
        )
        for x in ctx.guild.premium_subscribers:
            boost.add_field(
                name=f"{x.name}#{x.discriminator}", value=f"{x.mention}", inline=False
            )
        boost.set_footer(text=f"{len(ctx.guild.premium_subscribers)} Users in total")
        await ctx.send(embed=boost)

    @commands.group(
        invoke_without_command=True,
        brief="Show some info about a user",
        aliases=["user", "ui"],
    )
    @commands.guild_only()
    async def userinfo(self, ctx, user: libneko.converters.MemberConverter = None):
        """Show info about the user. If not specified, the command invoker info will be shown instead."""
        if user is None:
            user = ctx.author

        boost_stats = None

        if user.premium_since is None:
            boost_stats = "This user is not boosting this server."
        else:
            boost_stats = user.premium_since.strftime("%d-%m-%Y at %H:%M:%S")

        member = discord.Embed(timestamp=datetime.utcnow())
        roles = [role.name.replace("@", "@\u200b") for role in user.roles]
        shared = sum(1 for m in self.bot.get_all_members() if m.id == user.id)
        voice = user.voice
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = (
                f"{vc.name} with {other_people} others"
                if other_people
                else f"{vc.name} by themselves"
            )
        else:
            voice = "Not connected."

        member.set_author(name=f"Info for {str(user)}")
        member.add_field(name="》 Display Name", value=user.display_name, inline=False)
        member.add_field(
            name="》 Discriminator/Tag", value=f"#{user.discriminator}", inline=False
        )
        member.add_field(
            name="》 Member since",
            value=f'{user.joined_at.strftime("%d-%m-%Y - %H:%M:%S")}',
            inline=False,
        )
        member.add_field(name="》 User ID", value=user.id, inline=False)
        member.add_field(name="》 Mention", value=user.mention, inline=False)
        member.add_field(name="》 Status", value=user.status, inline=False)
        member.add_field(
            name="》 Shared Servers", value=f"{shared} shared", inline=False
        )
        member.add_field(
            name="》 Created at",
            value=user.created_at.strftime("%d-%m-%Y at %H:%M:%S"),
            inline=False,
        )
        member.add_field(name="》 Current Activity", value=user.activity, inline=False)
        member.add_field(
            name="》 is Active on Mobile?", value=user.is_on_mobile(), inline=False
        )
        member.add_field(name="》 Voice", value=voice, inline=False)
        member.add_field(
            name="》 Has Boosted the server since", value=boost_stats, inline=False
        )
        member.add_field(
            name="》 Roles",
            value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
            inline=False,
        )
        member.add_field(name="》 Top Role", value=user.top_role, inline=False)
        member.colour = user.colour
        member.set_footer(
            text=f"Requested by {ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=f"{ctx.message.author.avatar_url}",
        )
        if user.avatar:
            member.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=member)

    @userinfo.command(
        brief="View other user's avatar", name="avatar", aliases=["pfp", "pp"]
    )
    @commands.guild_only()
    async def userinfo_avatar(
        self, ctx, *, user: libneko.converters.MemberConverter = None
    ):
        """Show a user profile picture.\nYou can either use Discord ID or ping them"""
        try:
            if user is None:  # This will be executed when no argument is provided
                pfp = discord.Embed(
                    description=f"{ctx.message.author.name}'s profile picture",
                    title="Avatar Viewer",
                    color=ctx.author.color,
                    timestamp=datetime.utcnow(),
                )
                pfp.set_image(url=ctx.message.author.avatar_url)
                await ctx.send(embed=pfp)
            else:  # This is what normally executed.
                pfp = discord.Embed(
                    description=f"{user.name}'s profile picture",
                    title="Avatar Viewer",
                    timestamp=datetime.utcnow(),
                )
                pfp.set_image(url=user.avatar_url)
                pfp.colour = user.colour
                await ctx.send(embed=pfp)
        except discord.InvalidArgument:
            await ctx.send("Please provide a correct format!")
            await ctx.message.add_reaction("❌")

    @userinfo.command(brief="Return the ID of a user", name="id")
    async def userinfo_id(
        self, ctx, *, user: libneko.converters.MemberConverter = None
    ):
        """Ping the user to get their ID, you can also type their username instead."""
        if user is None:
            user = ctx.message.author
        await ctx.send(
            embed=discord.Embed(
                description=f"The User ID of **{user.mention}** are `{user.id}`"
            )
        )


##    [ WORKS IN PROGRESS ]
#    @userinfo.command(brief="Allows you to check Spotify playback status of other member", name = "spotify")
#    async def userinfo_spotify(self, ctx, *user: libneko.converters.MemberConverter):
#        if user is None:
#            user = ctx.message.author
#        spt = discord.Embed(title="Spotify Playback Viewer",description=f"{user} is listening to...", color=0x1DB954)
#        spt.add_field(name="Title", value=user.Spotify.title)
#
    
def setup(bot):
    bot.add_cog(Information(bot))
    print("Information Module has been loaded.")
