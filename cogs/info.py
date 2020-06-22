import random
from collections import Counter
from datetime import datetime

import discord
import libneko
import psutil
import bs4
import lxml
import time
import libneko
from libneko import pag
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

        sysboot = datetime.fromtimestamp(psutil.boot_time()).strftime("%B %d, %Y at %I:%M %p")

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
            em = libneko.embeds.Embed(title="System Status", color=0x32441C)
            
            em.add_field(
                name=":desktop: CPU Usage",
                value=f"{psutil.cpu_percent():.2f}% ({psutil.cpu_count(logical=False)} Cores) \nload avg: {psutil.getloadavg()}",
                inline=False,
            )
            em.add_field(
                name=":gear: CPU Frequency",
                value=f"{psutil.cpu_freq().current} MHz",
                inline=False,
            )
            em.add_field(
                name=":computer: System Memory Usage",
                value=f"**{psutil.virtual_memory().percent}%** Used",
                inline=False,
            )
            em.add_field(
                name="\U0001F4BE BOT Memory usage", 
                value=mem_usage, 
                inline=False
            )
            em.add_field(
                name=":minidisc: Disk Usage",
                value=f"Total Size: {solveunit(psutil.disk_usage('/').total)} GB \nCurrently Used: {solveunit(psutil.disk_usage('/').used)} GB",
                inline=False,
            )
            em.add_field(
                name="\U0001F553 BOT Uptime",
                value=time, 
                inline=False
            )
            em.add_field(
                name="⏲️ Last System Boot Time", 
                value=sysboot, 
                inline=False
            )
            em.add_field(
                name="\u2694 Servers", 
                value=str(len(self.bot.guilds)), 
                inline=False
            )
            em.add_field(
                name="\ud83d\udcd1 Channels", 
                value=str(channel_count), 
                inline=False
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

    @commands.group(invoke_without_command=True, aliases=["server", "si"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """This command will show some informations about this server"""
        guild = ctx.guild
        roles = [role.name.replace("@", "@\u200b") for role in guild.roles]

        booster_amount = None

        if guild.premium_subscription_count == 0 or None:
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

        server = libneko.embeds.Embed(
            color=ctx.message.author.color, timestamp=datetime.utcnow()
        )
        server.title = f"Information about {guild.name}"
        server.add_field(name="》 ID", value=guild.id, inline=False)
        server.add_field(
            name="》 Owner",
            value=f"{guild.owner.mention} ({guild.owner})",
            inline=False,
        )
        server.add_field(name="》 Owner ID", value=guild.owner_id, inline=False)
        if guild.icon:
            if guild.is_icon_animated() is True:
                server.set_thumbnail(url=guild.icon_url_as(format="gif", size=4096))
            else:
                server.set_thumbnail(url=guild.icon_url_as(format="png", size=4096))
        if guild.splash:
            server.set_image(url=guild.splash_url_as(format="png",size=4096))

        fmt = f"Text {text_channels} ({secret_channels} secret)\nVoice {voice_channels} ({secret_voice} locked)"
        server.add_field(
            name="》 Channels",
            value=fmt, 
            inline=False
        )
        server.add_field(
            name="》 Roles",
            value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
            inline=False,
        )
        fmt = (
            f'🟢 Online: {member_by_status["online"]}\n'
            f'🟡 Idle: {member_by_status["idle"]}\n'
            f'🔴 Do Not Disturb: {member_by_status["dnd"]}\n'
            f'⚫ Offline: {member_by_status["offline"]}\n'
            f"➕ Total: {guild.member_count}"
        )
        server.add_field(
            name="》 Created",
            value=guild.created_at.strftime("%B %d, %Y at %I:%M %p"),
            inline=False,
        )
        server.add_field(
            name="》 Is a large guild?", 
            value=guild.large, 
            inline=False
        )
        server.add_field(
            name="》 Region", 
            value=f"{guild.region}", 
            inline=False
        )
        server.add_field(
            name="》 AFK Channel", 
            value=guild.afk_channel, 
            inline=False
        )
        server.add_field(
            name="》 AFK Timeout", 
            value=f"{guild.afk_timeout} Seconds", 
            inline=False
        )
        server.add_field(
            name="》 2FA Level", 
            value=guild.mfa_level, 
            inline=False)
        server.add_field(
            name="》 Verification Level", 
            value=guild.verification_level, 
            inline=False
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
        server.add_field(
            name="》 Server Features", 
            value=guild.features, 
            inline=False
        )
        server.add_field(
            name="》 Nitro Boost Status", 
            value=booster_amount, 
            inline=False
        )
        server.add_field(
            name="》 Members", 
            value=f"```{fmt}```",
            inline=False
        )
        server.set_footer(
            text=f"Requested by {ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=f"{ctx.message.author.avatar_url}",
        )
        await ctx.send(embed=server, content=None)

    @serverinfo.command(name="icon", brief="Show the icon of this server.")
    @commands.guild_only()
    async def serverinfo_icon(self, ctx):
        """
        Show the icon of this server.
        """
        link_frmt = ""
        icon = libneko.embeds.Embed(title=f"Server icon for {ctx.guild.name}", color=ctx.message.author.color)

        if ctx.guild.is_icon_animated() is True:
            icon.set_image(url=ctx.guild.icon_url_as(format="gif", size=4096))
            link_frmt = f"[png]({ctx.guild.icon_url_as(format='png',size=4096)}) | [gif]({ctx.guild.icon_url_as(format='gif',size=4096)}) | [jpg]({ctx.guild.icon_url_as(format='jpg',size=4096)}) | [webp]({ctx.guild.icon_url_as(format='webp',size=4096)})"
        else:
            icon.set_image(url=ctx.guild.icon_url_as(format="png", size=4096))
            link_frmt = f"[png]({ctx.guild.icon_url_as(format='png',size=4096)}) | [jpg]({ctx.guild.icon_url_as(format='jpg',size=4096)}) | [webp]({ctx.guild.icon_url_as(format='webp',size=4096)})"
        icon.add_field(name="Full server icon link", value=link_frmt)
        await ctx.send(embed=icon, content=None)
    
    @serverinfo.command(name="banner", brief="Show this server's banner, if any")
    @commands.guild_only()
    async def serverinfo_banner(self, ctx):
        """
        Show this server's banner, if any
        """
        link_frmt = f"[png]({ctx.guild.banner_url_as(format='png',size=4096)}) | [jpg]({ctx.guild.banner_url_as(format='jpg',size=4096)}) | [webp]({ctx.guild.banner_url_as(format='webp',size=4096)})"

        if "BANNER" in ctx.guild.features:
            bannerembed = libneko.embeds.Embed(title=f"Server Banner for **{ctx.guild.name}**")
            bannerembed.add_field(name="Full image link", value=link_frmt)
            bannerembed.set_image(url=ctx.guild.banner_url_as(format="png", size=4096))
            await ctx.send(embed=bannerembed, content=None)
            
        else:
            nobanner = libneko.embeds.Embed(description="This server doesn't have the Boost level Required to set a banner.")
            await ctx.send(embed=nobanner)


    @serverinfo.command(name="membercount", aliases=["count", "memcount"], brief="shows the amount of members on this server.")
    @commands.guild_only()
    async def serverinfo_membercount(self, ctx):
        """
        shows the amount of members on this server.
        """
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
        count = libneko.embeds.Embed(
            color=ctx.message.author.color, title=f"{ctx.guild.name} Member Count"
        )
        count.add_field(name="User Count", value=f"{members}", inline=False)
        count.add_field(name="Bot Count", value=f"{bots}", inline=False)
        count.add_field(name="Total", value=f"{total}", inline=False)
        await ctx.send(embed=count, content=None)

    @serverinfo.command(aliases=["rl", "role"], no_pm=True, name="roleinfo", brief="Shows information about a role")
    @commands.guild_only()
    async def serverinfo_roleinfo(self, ctx, *, role: libneko.converters.RoleConverter):
        """Shows information about a role"""
        guild = ctx.guild

        since_created = (ctx.message.created_at - role.created_at).days
        role_created = role.created_at.strftime("%d %b %Y %H:%M")
        created_on = "{} ({} days ago!)".format(role_created, since_created)

        if str(role.colour) is "#000000":
            colour = "default"
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            color = int(colour[1:], 16)
        else:
            colour = str(role.colour).upper()
            color = role.colour

        perms = ""
        if role.permissions.administrator:
            perms += "Administrator, "
        if role.permissions.create_instant_invite:
            perms += "Create Instant Invite, "
        if role.permissions.kick_members:
            perms += "Kick Members, "
        if role.permissions.ban_members:
            perms += "Ban Members, "
        if role.permissions.manage_channels:
            perms += "Manage Channels, "
        if role.permissions.manage_guild:
            perms += "Manage Guild, "
        if role.permissions.add_reactions:
            perms += "Add Reactions, "
        if role.permissions.view_audit_log:
            perms += "View Audit Log, "
        if role.permissions.read_messages:
            perms += "Read Messages, "
        if role.permissions.send_messages:
            perms += "Send Messages, "
        if role.permissions.send_tts_messages:
            perms += "Send TTS Messages, "
        if role.permissions.manage_messages:
            perms += "Manage Messages, "
        if role.permissions.embed_links:
            perms += "Embed Links, "
        if role.permissions.attach_files:
            perms += "Attach Files, "
        if role.permissions.read_message_history:
            perms += "Read Message History, "
        if role.permissions.mention_everyone:
            perms += "Mention Everyone, "
        if role.permissions.external_emojis:
            perms += "Use External Emojis, "
        if role.permissions.connect:
            perms += "Connect to Voice, "
        if role.permissions.speak:
            perms += "Speak, "
        if role.permissions.mute_members:
            perms += "Mute Members, "
        if role.permissions.deafen_members:
            perms += "Deafen Members, "
        if role.permissions.move_members:
            perms += "Move Members, "
        if role.permissions.use_voice_activation:
            perms += "Use Voice Activation, "
        if role.permissions.change_nickname:
            perms += "Change Nickname, "
        if role.permissions.manage_nicknames:
            perms += "Manage Nicknames, "
        if role.permissions.manage_roles:
            perms += "Manage Roles, "
        if role.permissions.manage_webhooks:
            perms += "Manage Webhooks, "
        if role.permissions.manage_emojis:
            perms += "Manage Emojis, "

        if perms is None:
            perms = "None"
        else:
            perms = perms.strip(", ")

        em = libneko.embeds.Embed(colour=color)
        em.set_author(name=role.name)
        em.add_field(name="Users", value=len(role.members))
        em.add_field(name="Mentionable", value=role.mentionable)
        em.add_field(name="Hoist", value=role.hoist)
        em.add_field(name="Position from Bottom", value=role.position)
        em.add_field(name="Managed", value=role.managed)
        em.add_field(name="Colour", value=colour)
        em.add_field(name="Creation Date", value=created_on)
        em.add_field(name='Permissions', value=perms, inline=False)
        em.set_footer(text=f"Role ID: {role.id}")

        await ctx.send(embed=em)

    @commands.guild_only()
    @serverinfo.command(name="inrole", aliases=["inrl"], brief="Show the list of users on a particular role.")
    async def serverinfo_inrole(self, ctx, role:libneko.converters.RoleConverter = None):
        """
        Show the list of users on a particular role.
        """
        if role is None:
            await ctx.send(libneko.embeds.Embed(description="⚠ Please specify the role."))
        else:
            @pag.embed_generator(max_chars=2048)
            def det_embed(paginator, page, page_index):
                embed = libneko.embeds.Embed(description=page, title=f"Members on {role.name} role ({str(len(role.members))}):")
                return embed


            lst = pag.EmbedNavigatorFactory(factory=det_embed, max_lines=10)
            
            members = ""
            for user in role.members:
                members += f"{user.mention}:({user.name})\n "

            lst += members
            lst.start(ctx)


    @serverinfo.command(name="owner", aliases=["own"], brief="Shows the owner of this server")
    @commands.guild_only()
    async def serverinfo_owner(self, ctx):
        """
        Shows the owner of this server
        """
        await ctx.send(
            embed=libneko.embeds.Embed(
                description=f"{ctx.guild.owner} ({ctx.guild.owner.mention}) owns this server!"
            )
        )

    @serverinfo.command(name="created", aliases=["madeon", "born"], brief="Shows when this server was created")
    @commands.guild_only()
    async def serverinfo_created(self, ctx):
        """
        Shows when this server was created.
        """
        create = libneko.embeds.Embed(description=f"**{ctx.guild.name}** was created on `{ctx.guild.created_at.strftime('%B %d, %Y at %I:%M %p')}`")
        await ctx.send(embed = create)

    @serverinfo.command(name="administrators", aliases=["admin", "admins"], brief="Check which admins are online on current server")
    @commands.guild_only()
    async def serverinfo_administrators(self, ctx):
        """ Check which admins are online on current guild """
        admins = ""
        online, idle, dnd, offline = [], [], [], []
        ctx.trigger_typing()

        for user in ctx.guild.members:
            if ctx.channel.permissions_for(user).administrator:
                if not user.bot and user.status is discord.Status.online:
                    online.append(f"{user}")
                if not user.bot and user.status is discord.Status.idle:
                    idle.append(f"{user}")
                if not user.bot and user.status is discord.Status.dnd:
                    dnd.append(f"{user}")
                if not user.bot and user.status is discord.Status.offline:
                    offline.append(f"{user}")

        if online:
            admins += f"🟢 {', '.join(online)}\n"
        if idle:
            admins += f"🟡 {', '.join(idle)}\n"
        if dnd:
            admins += f"🔴 {', '.join(dnd)}\n"
        if offline:
            admins += f"⚫ {', '.join(offline)}\n"

        emb = libneko.embeds.Embed(title=f"Admins in `{ctx.guild.name}`", description=f"```{admins}```")
        await ctx.send(embed=emb)

    @serverinfo.command(name="moderators", aliases=["moderator", "mod","mods"], brief="Check which mods are online on current server")
    @commands.guild_only()
    async def serverinfo_moderators(self, ctx):
        """ Check which mods are online on current guild """
        mods = ""
        online, idle, dnd, offline = [], [], [], []
        ctx.trigger_typing()

        for user in ctx.guild.members:
            if ctx.channel.permissions_for(user).kick_members or \
               ctx.channel.permissions_for(user).ban_members:
                if not user.bot and user.status is discord.Status.online:
                    online.append(f"{user}")
                if not user.bot and user.status is discord.Status.idle:
                    idle.append(f"{user}")
                if not user.bot and user.status is discord.Status.dnd:
                    dnd.append(f"{user}")
                if not user.bot and user.status is discord.Status.offline:
                    offline.append(f"{user}")

        if online:
            mods += f"🟢 {', '.join(online)}\n"
        if idle:
            mods += f"🟡 {', '.join(idle)}\n"
        if dnd:
            mods += f"🔴 {', '.join(dnd)}\n"
        if offline:
            mods += f"⚫ {', '.join(offline)}\n"

        emb = libneko.embeds.Embed(title=f"Moderators in `{ctx.guild.name}`", description=f"```{mods}```")
        await ctx.send(embed=emb)

    @commands.guild_only()
    @serverinfo.command(aliases=["booster"], name="boost", brief="Show the list of Nitro booster on this server.")
    async def serverinfo_boost(self, ctx):
        """
        Show the list of Nitro booster on this server.
        """
        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            boost = libneko.embeds.Embed(title=f"Nitro Booster on **{ctx.guild.name}**.",description = page, color=0x00FF00)
            boost.set_footer(text=f"{len(ctx.guild.premium_subscribers)} Users in total")
            return boost

        navi = pag.EmbedNavigatorFactory(factory=main_embed, max_lines=10)

        boosters = ""
        for x in ctx.guild.premium_subscribers:
                boosters += f"{x.name}#{x.discriminator} ({x.mention})\n"

        navi += boosters
        navi.start(ctx)
        

    @staticmethod
    def transform_mute(emojis):
        return [str(emoji) + " " for emoji in emojis]

    @staticmethod
    def transform_verbose(emojis):
        return [
            f"{emoji} = {emoji.name}\n"
            for emoji in sorted(emojis, key=lambda e: e.name.lower())
        ]

    @commands.guild_only()
    @serverinfo.command(name="emoji",aliases=["emojis","emote"], brief="Shows all emojis I can see in this server.")
    async def serverinfo_emojilibrary(self, ctx, arg=None):
        """Shows all emojis I can see in this server. Pass the --verbose/-v flag to see names."""
        if arg:
            transform = self.transform_verbose
        else:
            transform = self.transform_mute
        emojis = transform(ctx.guild.emojis)
        p = pag.StringNavigatorFactory()
        for emoji in emojis:
            p += emoji
        p.start(ctx)

    
    @commands.guild_only()
    @serverinfo.command(name="splash", aliases=["splashes","images"], brief="Show the splash image of this server, if any")
    async def serverinfo_splash(self, ctx):
        """Show the splash image of this server, if any"""
        link_frmt = f"[png]({ctx.guild.splash_url_as(format='png',size=4096)}) | [jpg]({ctx.guild.splash_url_as(format='jpg',size=4096)}) | [webp]({ctx.guild.splash_url_as(format='webp',size=4096)})"

        if "INVITE_SPLASH" in ctx.guild.features and ctx.guild.splash is not None:
            splashembed = libneko.embeds.Embed(title=f"{ctx.guild.name}'s Splash Image.")
            splashembed.add_field(name="Full image link", value=link_frmt)
            splashembed.set_image(url=ctx.guild.splash_url_as(format="png", size=4096))
            await ctx.send(embed=splashembed, content=None)
        else:
            nosplash = libneko.embeds.Embed(description="This server doesn't have the required boost lever or has no splash image configured.")
            await ctx.send(embed=nosplash)


    @commands.group(invoke_without_command=True,aliases=["user", "ui"])
    @commands.guild_only()
    async def userinfo(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """Show info about the user. If not specified, the command caller info will be shown instead."""
        if user is None:
            user = ctx.author

        boost_stats = None
        nitro_stats = None

        if user.premium_since is None:
            boost_stats = "This user is not boosting this server."
        else:
            boost_stats = user.premium_since.strftime("%d-%m-%Y at %H:%M:%S")

        member = libneko.embeds.Embed(timestamp=datetime.utcnow())
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

        member.add_field(
            name="》 Display Name", 
            value=user.display_name, 
            inline=False)
        member.add_field(
            name="》 Discriminator/Tag", 
            value=f"#{user.discriminator}", 
            inline=False
        )
        member.add_field(
            name="》 Member since",
            value=f'{user.joined_at.strftime("%B %d, %Y at %I:%M %p")}',
            inline=False,
        )
        member.add_field(
            name="》 User ID", 
            value=user.id, 
            inline=False
        )
        member.add_field(
            name="》 Mention", 
            value=user.mention, 
            inline=False
        )
        member.add_field(
            name="》 Status", 
            value=user.status, 
            inline=False
        )
        member.add_field(
            name="》 Shared Servers", 
            value=f"{shared} shared", 
            inline=False
        )
        member.add_field(
            name="》 Created",
            value=user.created_at.strftime("%B %d, %Y at %I:%M %p"),
            inline=False,
        )
        member.add_field(
            name="》 Current Activity/Status", 
            value=user.activity, 
            inline=False)
        member.add_field(
            name="》 is Active on Mobile?", 
            value=user.is_on_mobile(), 
            inline=False
        )
        member.add_field(
            name="》 Voice", 
            value=voice, 
            inline=False)
        member.add_field(
            name="》 Has Boosted the server since", 
            value=boost_stats, 
            inline=False
        )   
        member.add_field(
            name="》 Roles",
            value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
            inline=False,
        )
        member.add_field(
            name="》 Top Role", 
            value=user.top_role, 
            inline=False)
        member.colour = user.colour

        member.set_footer(
            text=f"Requested by {ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=f"{ctx.message.author.avatar_url}",
        )
        if user.avatar:
            member.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=member)

    @userinfo.command(name="avatar", aliases=["pfp", "pp"], brief="View the avatar of a member.")
    @commands.guild_only()
    async def userinfo_avatar(self, ctx, *, user: libneko.converters.InsensitiveUserConverter = None):
        """View the avatar of a member.\nYou can either use Discord ID or ping them instead"""
        pic_frmt = None
        link_frmt = None

        if user is None:
            user = ctx.message.author

        if user.is_avatar_animated() is True:
            pic_frmt = "gif"
            link_frmt = f"[png]({user.avatar_url_as(format='png',size=4096)}) | [gif]({user.avatar_url_as(format='gif',size=4096)}) | [jpg]({user.avatar_url_as(format='jpg',size=4096)}) | [webp]({user.avatar_url_as(format='webp',size=4096)})"
        else:
            pic_frmt = "png"
            link_frmt = f"[png]({user.avatar_url_as(format='png',size=4096)}) | [jpg]({user.avatar_url_as(format='jpg',size=4096)}) | [webp]({user.avatar_url_as(format='webp',size=4096)})"

        try:
            if user is None:  # This will be executed when no argument is provided
                pfp = libneko.embeds.Embed(
                    description=f"{ctx.message.author.name}'s profile picture",
                    title="Avatar Viewer",
                    color=ctx.author.color,
                    timestamp=datetime.utcnow(),
                )
                pfp.add_field(name="Full avatar link", value=link_frmt)
                pfp.set_image(url=ctx.message.author.avatar_url_as(format=pic_frmt, size=4096))
                await ctx.send(embed=pfp)
            else:  # This is what normally executed.
                pfp = libneko.embeds.Embed(
                    description=f"{user.name}'s profile picture",
                    title="Avatar Viewer",
                    timestamp=datetime.utcnow(),
                )
                pfp.add_field(name="Full avatar link", value=link_frmt)
                pfp.set_image(url=user.avatar_url_as(format=pic_frmt, size=4096))
                pfp.colour = user.colour
                await ctx.send(embed=pfp)
        except discord.InvalidArgument:
            await ctx.send("Please provide a correct format!")
            await ctx.message.add_reaction("❌")

    @userinfo.command(name="id", brief="Mention the user to get their ID")
    async def userinfo_id(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """Ping the user to get their ID, you can also type their username instead."""
        if user is None:
            user = ctx.message.author
        await ctx.send(
            embed=libneko.embeds.Embed(
                description=f"The User ID of **{user.mention}** are `{user.id}`"
            )
        )

    @userinfo.command(name="roles", brief="Show all roles that the member has.")
    async def userinfo_roles(self, ctx, member: libneko.converters.InsensitiveMemberConverter = None):
        """Show all roles that the member has."""
        if member is None:
            member = ctx.message.author

        roles = [role.name.replace("@", "@\u200b") for role in member.roles]
        memrole = libneko.embeds.Embed(title=f"Role Viewer.")
        memrole.add_field(
            name=f"{member}'s Roles", value=", ".join(roles))
        memrole.set_footer(text=f"{len(roles)} roles in total!", icon_url=member.avatar_url)
        await ctx.send(embed=memrole)


    @userinfo.command(name="mention", brief="Mention a user.")
    async def userinfo_mention(self, ctx, target: libneko.converters.InsensitiveMemberConverter = None):
        """
        Mention a user.
        """
        if target is None:
            await ctx.send(f"Mention who? {ctx.message.author}")

        await ctx.send(f"{target.mention} has been mentioned by {ctx.message.author.mention}!")

def setup(bot):
    bot.add_cog(Information(bot))
    print("Information Module has been loaded.")
