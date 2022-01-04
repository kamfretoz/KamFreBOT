import random
from collections import Counter
from datetime import datetime, timezone

import discord
import libneko
import psutil
import platform
from libneko import pag
from discord.ext import commands
class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = datetime.now()

    @commands.command(aliases=["status"])
    async def stats(self, ctx):
        """Bot stats."""

        def solveunit(input):
            output = ((input // 1024) // 1024) // 1024
            return int(output)

        try:
            mem_usage = "{:.2f} MiB".format(
                __import__("psutil").Process(
                ).memory_full_info().uss / 1024 ** 2
            )
        except AttributeError:
            # OS doesn't support retrieval of USS (probably BSD or Solaris)
            mem_usage = "{:.2f} MiB".format(
                __import__("psutil").Process(
                ).memory_full_info().rss / 1024 ** 2
            )

        sysboot = datetime.fromtimestamp(
            psutil.boot_time()).strftime("%B %d, %Y at %I:%M:%S %p")

        uptime = datetime.now() - self.counter
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
            time = "%s hours, %s minutes, and %s seconds" % (
                hours, minutes, seconds)

        channel_count = 0
        for guild in self.bot.guilds:
            channel_count += len(guild.channels)
        try:
            em = discord.Embed(title="System Status", color=0x32441C)

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
                name=":dna: Kernel Version",
                value=f"{platform.platform()} {platform.version()}",
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
                name="\u2694 Servers (Guilds)",
                value=str(len(self.bot.guilds)),
                inline=False
            )
            em.add_field(
                name="\ud83d\udcd1 Channels",
                value=str(channel_count),
                inline=False
            )
            em.add_field(
                name="👥 Users",
                value=str(len(self.bot.users)),
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
    async def serverinfo(self, ctx, serverid: int = None):
        """This command will show some informations about this server"""
        await ctx.trigger_typing()

        if serverid is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(serverid)
            if guild is None:
                await ctx.send(embed=discord.Embed(description="Server not found!"))
                return

        if guild.unavailable:
            await ctx.send(embed=discord.Embed(description="That server is currently unavailable"))
            return

        if guild.premium_tier == 0 or guild.premium_tier is None:
            level = "No Level"
        else:
            level = f"Level {str(guild.premium_tier)}"

        region = str(guild.region)
        roles = [role.mention for role in guild.roles]

        booster_amount = None

        if not guild.premium_subscription_count:
            booster_amount = "This server is not boosted"
        else:
            booster_amount = (
                f"This server has {guild.premium_subscription_count} boost(s)!"
            )

        sregion = {
            'brazil': ':flag_br: Brazil',
            'europe': ':flag_eu: Europe',
            'hongkong': ':flag_hk: Hong Kong',
            'india': ':flag_in: India',
            'japan': ':flag_jp: Japan',
            'russia': ':flag_ru: Russia',
            'singapore': ':flag_sg: Singapore',
            'southafrica': ':flag_za: South Africa',
            'sydney': ':flag_au: Sydney',
            'us-central': ':flag_us: US Central',
            'us-east': ':flag_us: US East',
            'us-south': ':flag_us: US South',
            'us-west': ':flag_us: US West',
        }.get(region)

        member_by_status = Counter(str(m.status) for m in guild.members)
        fmt = (
            f'🟢 Online: {member_by_status["online"]}\n'
            f'🟡 Idle: {member_by_status["idle"]}\n'
            f'🔴 Do Not Disturb: {member_by_status["dnd"]}\n'
            f'⚫ Offline: {member_by_status["offline"]}\n'
            f"➕ Total: {guild.member_count}"
        )
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

        server = discord.Embed(
            color=ctx.message.author.color, timestamp=datetime.utcnow()
        )
        server.title = f"Information about {guild.name}"
        if guild.description:
            server.add_field(
                name="》 Description",
                value=guild.description,
                inline=False
            )
        server.add_field(name="》 ID", value=guild.id, inline=False)
        server.add_field(
            name="》 Owner",
            value=f"{guild.owner.mention} ({guild.owner})",
            inline=False,
        )
        server.add_field(name="》 Owner ID", value=guild.owner_id, inline=False)

        if guild.icon:
            if guild.is_icon_animated() is True:
                server.set_thumbnail(
                    url=guild.icon_url_as(format="gif", size=4096))
            else:
                server.set_thumbnail(
                    url=guild.icon_url_as(format="png", size=4096))
        if guild.splash:
            server.set_image(url=guild.splash_url_as(format="png", size=4096))

        def sec2min(seconds):  # https://stackoverflow.com/a/775075
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            return f'{h} Hour, {m} Minutes'

        since_created = (ctx.message.created_at - guild.created_at).days
        timestamp = guild.created_at.replace(tzinfo=timezone.utc).timestamp()

        server.add_field(
            name="》 Channel Count",
            value=f"{len(guild.channels)} channels",
            inline=False
        )
        server.add_field(
            name="》 Roles",
            value=", ".join(roles) if len(
                roles) < 10 else f"{len(roles)} roles",
            inline=False,
        )
        server.add_field(
            name="》 Created",
            value=f"<t:{int(timestamp)}:F> ({since_created} days ago!)",
            inline=False,
        )
        server.add_field(
            name="》 Region",
            value=sregion,
            inline=False
        )
        server.add_field(
            name="》 Server Boost Status",
            value=booster_amount,
            inline=False
        )
        server.add_field(
            name="》 Server Level",
            value=level,
            inline=False
        )
        server.add_field(
            name="》 Server size",
            value=f"{'Large server' if guild.large else 'Small server'}",
            inline=False
        )
        server.add_field(
            name="》 AFK Channel",
            value=guild.afk_channel,
            inline=False
        )
        server.add_field(
            name="》 AFK Timeout",
            value=sec2min(guild.afk_timeout),
            inline=False
        )
        server.add_field(
            name=f"》 Members",
            value=f"```{fmt}```",
            inline=False
        )
        server.set_footer(
            text=f"Requested by {ctx.message.author}",
            icon_url=f"{ctx.message.author.avatar_url}",
        )
        await ctx.send(embed=server, content=None)

    @serverinfo.command(name="icon", brief="Show the icon of this server.", aliases=["pfp", "pp"])
    @commands.guild_only()
    async def serverinfo_icon(self, ctx, serverid: int = None):
        """
        Show the icon of this server.
        """
        if serverid is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(serverid)
            if guild is None:
                await ctx.send(embed=discord.Embed(description="Server not found!"))
                return

        link_frmt = ""
        icon = discord.Embed(
            title=f"Server icon for {guild.name}", color=ctx.message.author.color)
        if guild.is_icon_animated() is True:
            icon.set_image(url=guild.icon_url_as(format="gif", size=4096))
            link_frmt = f"[png]({guild.icon_url_as(format='png',size=4096)}) | [gif]({guild.icon_url_as(format='gif',size=4096)}) | [jpg]({guild.icon_url_as(format='jpg',size=4096)}) | [webp]({guild.icon_url_as(format='webp',size=4096)})"
        else:
            icon.set_image(url=guild.icon_url_as(format="png", size=4096))
            link_frmt = f"[png]({guild.icon_url_as(format='png',size=4096)}) | [jpg]({guild.icon_url_as(format='jpg',size=4096)}) | [webp]({guild.icon_url_as(format='webp',size=4096)})"
        icon.add_field(name="Full server icon link", value=link_frmt)
        await ctx.send(embed=icon, content=None)

    @serverinfo.command(name="banner", brief="Show this server's banner, if any")
    @commands.guild_only()
    async def serverinfo_banner(self, ctx):
        """
        Show this server's banner, if any
        """
        link_frmt = f"[png]({ctx.guild.banner_url_as(format='png',size=4096)}) | [jpg]({ctx.guild.banner_url_as(format='jpg',size=4096)}) | [webp]({ctx.guild.banner_url_as(format='webp',size=4096)})"

        if "BANNER" in ctx.guild.features and ctx.guild.banner_url is not None:
            bannerembed = discord.Embed(
                title=f"Server Banner for **{ctx.guild.name}**")
            bannerembed.add_field(name="Full image link", value=link_frmt)
            bannerembed.set_image(
                url=ctx.guild.banner_url_as(format="png", size=4096))
            await ctx.send(embed=bannerembed, content=None)

        else:
            nobanner = discord.Embed(
                description="This server either doesn't have the Boost level Required to set a banner or no splash image have been set.")
            await ctx.send(embed=nobanner)

    @serverinfo.command(name="membercount", aliases=["count", "memcount", "members", "member", "mem"], brief="shows the amount of members on this server.")
    @commands.guild_only()
    async def serverinfo_membercount(self, ctx):
        """
        shows the amount of members on this server.
        """
        guild = ctx.guild
        member_by_status = Counter(str(m.status) for m in guild.members)
        fmt = (
            f'🟢 Online: {member_by_status["online"]}\n'
            f'🟡 Idle: {member_by_status["idle"]}\n'
            f'🔴 Do Not Disturb: {member_by_status["dnd"]}\n'
            f'⚫ Offline: {member_by_status["offline"]}\n'
        )
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
        count.add_field(name="Status", value=f"```{fmt}```", inline=False)
        await ctx.send(embed=count, content=None)

    @serverinfo.command(aliases=["rl", "role"], no_pm=True, name="roleinfo", brief="Shows information about a role")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def serverinfo_roleinfo(self, ctx, *, role: libneko.converters.RoleConverter):
        """Shows information about a role"""
        since_created = (ctx.message.created_at - role.created_at).days
        role_created = f"<t:{int(datetime.utcnow().timestamp())}:F>"
        created_on = f"{role_created} ({since_created} days ago!)"

        if str(role.colour) == "#000000":
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

        em = discord.Embed(
            title=f"`{role.name}` Role Information", colour=color, timestamp=datetime.utcnow())
        em.add_field(name="Users", value=len(role.members))
        em.add_field(name="Mentionable", value=role.mentionable)
        em.add_field(name="Hoisted", value=role.hoist)
        em.add_field(name="Position from Bottom", value=role.position)
        em.add_field(name="Managed", value=role.managed)
        em.add_field(name="Color", value=colour)
        em.add_field(name="Creation Date", value=created_on)
        em.add_field(name='Permissions', value=perms, inline=False)
        em.set_footer(text=f"Role ID: {role.id}")

        await ctx.send(embed=em)

    @serverinfo_roleinfo.error
    async def roleinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Cannot find that role. Make sure the spelling and the case-sensitivity is correct!')

    @serverinfo.command(name="inrole", aliases=["inrl"], brief="Show the list of users on a particular role.")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def serverinfo_inrole(self, ctx, *, role: libneko.converters.RoleConverter = None):
        """
        Show the list of users on a particular role.
        """
        if str(role.colour) == "#000000":
            color = discord.Color(0x99AAB5)
        else:
            color = role.colour

        if role is None:
            await ctx.send(discord.Embed(description="⚠ Please specify the role."))
        else:
            @pag.embed_generator(max_chars=2048)
            def det_embed(paginator, page, page_index):
                embed = discord.Embed(
                    description=page, title=f"Members on `{role.name}` role:", color=color, timestamp=datetime.utcnow())
                embed.set_footer(
                    text=f"{str(len(role.members))} Members in Total.")
                return embed
            lst = pag.EmbedNavigatorFactory(factory=det_embed)
            members = []

            try:
                for user in role.members:
                    members.append(f"{user.name}#{user.discriminator}")
            except discord.Forbidden:
                await ctx.send(embed=discord.Embed(description="⚠ Role cannot be found or i dont have permission!"))
                return

            lst += "\n".join(members)
            lst.start(ctx)

    @serverinfo_inrole.error
    async def inrole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Cannot find that role. Make sure the spelling and the case-sensitivity is correct!')

    @serverinfo.command(aliases=["lsrole", "listrole"], brief="Shows the list of all roles in this server")
    @commands.has_permissions(manage_roles=True)
    async def rolelist(self, ctx):
        """
        Shows the list of all roles in this server
        """
        roles = [role.mention for role in ctx.guild.roles]
        emb = discord.Embed(title=f"{ctx.guild.name}'s Role list", description=", ".join(
            roles), timestamp=datetime.utcnow())
        emb.set_footer(
            text=f"Requested by {ctx.message.author} | {len(roles)} roles in total.",
            icon_url=f"{ctx.message.author.avatar_url}",
        )
        await ctx.send(embed=emb)
        
    @serverinfo.command(name="oldestacc", aliases=["oldacc"] ,brief="Shows the oldest account in the server")
    async def oldestaccount(self, ctx, page = 1, sort_type = "oldest"):
        """
        Shows the oldest account in the server
        """
        page = abs(int(page))
        if page > 99: page = 99

        every_member = []
        for x in ctx.guild.members:
            userinfo = (f"{x} - {x.created_at.strftime('%d/%m/%Y')}", x.created_at)
            every_member.append(userinfo)
        every_member.sort(key=lambda x:x[1])

        if sort_type == "oldest": every_member_sliced = every_member[((page-1)*10):(page*10)]
        if sort_type == "newest": every_member_sliced = every_member[(len(every_member)-(((page-1)*10)+1)):((-10*page)-1):-1]

        output_string = ""
        cycle_int = 0
        for x, z in every_member_sliced:
            cycle_int = cycle_int + 1
            output_string += f"**{cycle_int+((page-1)*10)}** - {x}\n"

        if output_string != "":
            em = discord.Embed(color=ctx.author.color)
            em.add_field(name=f"{sort_type.capitalize()} accounts in **{ctx.guild.name}**", value=output_string, inline=False)

            em.set_footer(text=f"Page: {page}")
            em.timestamp = datetime.utcnow()

            await ctx.send(embed=em)
        else: await ctx.send("Nothing here.")

    @serverinfo.command(name="owner", aliases=["own"], brief="Shows the owner of this server")
    @commands.guild_only()
    async def serverinfo_owner(self, ctx):
        """
        Shows the owner of this server
        """
        own = discord.Embed(color=ctx.guild.owner.colour)
        if ctx.guild.owner.is_avatar_animated() is True:
            pic_frmt = "gif"
        else:
            pic_frmt = "png"
        own.add_field(name=f"Who own {ctx.guild.name}?",
                    value=f"{ctx.guild.owner} ({ctx.guild.owner.mention}) owns the server!")
        own.set_thumbnail(url=ctx.guild.owner.avatar_url_as(
            format=pic_frmt, size=4096))
        await ctx.send(embed=own)

    @serverinfo.command(name="created", aliases=["madeon", "born"], brief="Shows when this server was created")
    @commands.guild_only()
    async def serverinfo_created(self, ctx):
        """
        Shows when this server was created.
        """
        since_created = (ctx.message.created_at - ctx.guild.created_at).days
        timestamp = ctx.guild.created_at.replace(tzinfo=timezone.utc).timestamp()
        create = discord.Embed(
            description=f"**{ctx.guild.name}** was created on <t:{int(timestamp)}:F> ({since_created} days ago!)")

        if ctx.guild.icon:
            if ctx.guild.is_icon_animated() is True:
                create.set_thumbnail(
                    url=ctx.guild.icon_url_as(format="gif", size=4096))
            else:
                create.set_thumbnail(
                    url=ctx.guild.icon_url_as(format="png", size=4096))

        await ctx.send(embed=create)

    @serverinfo.command(name="administrators", aliases=["admin", "admins", "adm"], brief="Check which admins are online on current server")
    @commands.guild_only()
    async def serverinfo_administrators(self, ctx):
        """ Check which admins are online on current guild """
        admins = ""
        online, idle, dnd, offline = [], [], [], []
        await ctx.trigger_typing()

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

        emb = discord.Embed(
            title=f"Admins in `{ctx.guild.name}`", description=f"```{admins}```")
        await ctx.send(embed=emb)

    @serverinfo.command(name="moderators", aliases=["moderator", "mod", "mods"], brief="Check which mods are online on current server")
    @commands.guild_only()
    async def serverinfo_moderators(self, ctx):
        """ Check which mods are online on current guild """
        mods = ""
        online, idle, dnd, offline = [], [], [], []
        await ctx.trigger_typing()

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

        emb = discord.Embed(
            title=f"Moderators in `{ctx.guild.name}`", description=f"```{mods}```")
        await ctx.send(embed=emb)

    @commands.guild_only()
    @serverinfo.command(aliases=["booster"], name="boost", brief="Show the list of Nitro booster on this server.")
    async def serverinfo_boost(self, ctx):
        """
        Show the list of Nitro booster on this server.
        """
        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            boost = discord.Embed(
                title=f"Nitro Booster on **{ctx.guild.name}**.", description=page, color=0x00FF00)
            boost.set_footer(
                text=f"{len(ctx.guild.premium_subscribers)} Users in total ({ctx.guild.premium_subscription_count} Boost(s))")
            return boost

        navi = pag.EmbedNavigatorFactory(factory=main_embed)

        boosters = []
        for x in ctx.guild.premium_subscribers:
            boosters.append(f"{x} ({x.mention})")

        navi += "\n".join(boosters)
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
    @serverinfo.command(name="emoji", aliases=["emojis", "emote"], brief="Shows all emojis I can see in this server.")
    async def serverinfo_emojilibrary(self, ctx, serverid: int = None, arg=None):
        """
        Shows all emojis I can see in this server. Pass the --verbose/-v flag to see names.
        You can also supply the server ID to see their emojis, This bot needs to be on that server as well.
        """
        if serverid is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(serverid)
            if guild is None:
                await ctx.send(embed=discord.Embed(description="Server not found!"))
                return
        if arg:
            transform = self.transform_verbose
        else:
            transform = self.transform_mute
        emojis = transform(guild.emojis)
        p = pag.StringNavigatorFactory()
        for emoji in emojis:
            p += emoji
        p.start(ctx)

    @commands.guild_only()
    @serverinfo.command(name="splash", aliases=["splashes", "images"], brief="Show the splash image of this server, if any")
    async def serverinfo_splash(self, ctx):
        """Show the splash image of this server, if any"""
        link_frmt = f"[png]({ctx.guild.splash_url_as(format='png',size=4096)}) | [jpg]({ctx.guild.splash_url_as(format='jpg',size=4096)}) | [webp]({ctx.guild.splash_url_as(format='webp',size=4096)})"

        if "INVITE_SPLASH" in ctx.guild.features and ctx.guild.splash is not None:
            splashembed = discord.Embed(
                title=f"{ctx.guild.name}'s Splash Image.")
            splashembed.add_field(name="Full image link", value=link_frmt)
            splashembed.set_image(
                url=ctx.guild.splash_url_as(format="png", size=4096))
            await ctx.send(embed=splashembed, content=None)
        else:
            nosplash = discord.Embed(
                description="This server doesn't have the required boost lever or has no splash image configured.")
            await ctx.send(embed=nosplash)

    @commands.group(invoke_without_command=True, aliases=["user", "ui", "profile", "uinf"])
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: libneko.converters.InsensitiveMemberConverter = None):
        """Show info about the user. If not specified, the command caller info will be shown instead."""
        await ctx.trigger_typing()

        if user is None:
            user = ctx.author

        boost_stats = None

        try:
            if not user.premium_since:
                boost_stats = "The user are not boosting this server."
            else:
                premium = user.premium_since.replace(tzinfo=timezone.utc).timestamp()
                boost_stats = f"Boosting the server since <t:{int(premium)}:F>"
        except AttributeError:
            boost_stats = "Information Unavailable"

        member = discord.Embed(timestamp=datetime.utcnow())

        try:
            status = {
                'online': '🟢 Online',
                'idle': '🟡 Idle',
                'dnd': '🔴 Do Not Disturb',
                'offline': '⚫ Offline'
            }.get(str(user.status))

            roles = [role.mention for role in user.roles]
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
        except AttributeError:
            pass

        shared = sum(1 for m in self.bot.get_all_members() if m.id == user.id)

        member.set_author(name=f"Information of {str(user)}")

        try:
            member.add_field(
                name="》 Display Name",
                value=user.display_name,
                inline=False
            )
        except AttributeError:
            pass
        member.add_field(
            name="》 Discriminator/Tag",
            value=f"#{user.discriminator}",
            inline=False
        )
        try:
            created = user.created_at.replace(tzinfo=timezone.utc).timestamp()
            joined = user.joined_at.replace(tzinfo=timezone.utc).timestamp()
            member.add_field(
                name="》 Created",
                value=f"<t:{int(created)}:F>",
                inline=False,
            )
            member.add_field(
                name="》 Joined",
                value=f"<t:{int(joined)}:F>",
                inline=False,
            )
        except AttributeError:
            pass
        member.add_field(
            name="》 User ID",
            value=user.id,
            inline=False
        )
        member.add_field(
            name="Account Type",
            value=f"{'BOT' if user.bot else 'Human'}",
            inline=False
        )
        try:
            if not user.bot and user.status is not discord.Status.offline:
                member.add_field(
                    name="Platform",
                    value=f"{'Mobile' if user.is_on_mobile() else 'Desktop'}",
                    inline=False
                )
            member.add_field(
                name="》 Status",
                value=status,
                inline=False
            )
        except:
            pass
        member.add_field(
            name="》 Mention",
            value=user.mention,
            inline=False
        )
        member.add_field(
            name="》 Shared Servers",
            value=f"{shared} shared",
            inline=False
        )
        try:
            member.add_field(
                name="》 Voice",
                value=voice,
                inline=False
            )
            member.add_field(
                name="》 Nitro Stats",
                value=boost_stats,
                inline=False
            )
            member.add_field(
                name=f"》 Roles [{len(roles)}]",
                value=", ".join(roles) if len(
                    roles) < 10 else f"{len(roles)} roles",
                inline=False,
            )
            member.add_field(
                name="》 Top Role",
                value=user.top_role.mention,
                inline=False
            )

            member.colour = user.colour
        except:
            pass

        member.set_footer(
            text=f"Requested by {ctx.message.author}",
            icon_url=f"{ctx.message.author.avatar_url}",
        )

        if user.avatar:
            member.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=member)

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Cannot find that user.')
            
    @commands.guild_only()
    @userinfo.command(name="banner", brief="Show the banner of a user, if any")
    async def userinfo_banner(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """Show the banner of a user, if any"""
        if user is None:
            user = ctx.author
        
        req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
        banner_id = req["banner"]
        # If statement because the user may not have a banner
        if banner_id:
            if banner_id.startswith("a_"):
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=4096"
            else:
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=4096"
            bnr = discord.Embed(
                    description=f"**{user.mention}**'s Banner",
                    title="Banner Viewer",
                    color=user.colour,
                    timestamp=datetime.utcnow(),
                )
            bnr.set_image(url=banner_url)
            bnr.set_footer(text=f"User: {user} ({user.id})")
            await ctx.send(embed=bnr)
        else:
            await ctx.send(embed=discord.Embed(description="This User has no banner set.", color=user.colour))

    @userinfo.command(name="created", aliases=["create", "made"], brief="Shows when an account was made")
    @commands.guild_only()
    async def userinfo_created(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """
        Shows when this account was created.
        """
        if user is None:
            user = ctx.message.author
        timestamp = user.created_at.replace(tzinfo=timezone.utc).timestamp()
        since_created = (ctx.message.created_at - user.created_at).days
        create = discord.Embed(
            description=f"The account of {user} was created on <t:{int(timestamp)}:F> ({since_created} days ago!)")

        if user.avatar:
            if user.is_avatar_animated() is True:
                create.set_thumbnail(
                    url=user.avatar_url_as(format="gif", size=4096))
            else:
                create.set_thumbnail(
                    url=user.avatar_url_as(format="png", size=4096))

        create.set_footer(text=f"User: {user} ({user.id})")
        await ctx.send(embed=create)

    @userinfo.command(name="joined", aliases=["join"], brief="Shows when a user joined the server")
    @commands.guild_only()
    async def userinfo_joined(self, ctx, user: libneko.converters.InsensitiveMemberConverter = None):
        """
        Shows when this user joined the server.
        """
        if user is None:
            user = ctx.message.author
            
        try:
            timestamp = user.joined_at.replace(tzinfo=timezone.utc).timestamp()
        except AttributeError:
            return await ctx.send("Cannot find that user or they are not in this server!")
        since_joined = (ctx.message.created_at - user.joined_at).days
        joined = discord.Embed(
            description=f"{user.mention} joined the server on <t:{int(timestamp)}:F> ({since_joined} days ago!)")

        if user.avatar:
            if user.is_avatar_animated() is True:
                joined.set_thumbnail(
                    url=user.avatar_url_as(format="gif", size=4096))
            else:
                joined.set_thumbnail(
                    url=user.avatar_url_as(format="png", size=4096))

        joined.set_footer(text=f"User: {user} ({user.id})")
        await ctx.send(embed=joined)

    @userinfo.command(name="avatar", aliases=["pfp", "pp", "icon", "ava"], brief="View the avatar of a member.")
    @commands.guild_only()
    async def userinfo_avatar(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """View the avatar of a member.\nYou can either use Discord ID or ping them instead"""
        await ctx.trigger_typing()

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
                pfp = discord.Embed(
                    description=f"**{ctx.message.author.mention}**'s profile picture",
                    title="Avatar Viewer",
                    color=ctx.author.color,
                    timestamp=datetime.utcnow(),
                )
                pfp.add_field(
                    name="User", value=f"{ctx.message.author} ({ctx.message.author.id})")
                pfp.add_field(name="Full avatar link", value=link_frmt)
                pfp.set_image(url=ctx.message.author.avatar_url_as(
                    format=pic_frmt, size=4096))
                await ctx.send(embed=pfp)
            else:  # This is what normally executed.
                pfp = discord.Embed(
                    description=f"{user.mention}'s profile picture",
                    title="Avatar Viewer",
                    color=user.colour,
                    timestamp=datetime.utcnow(),
                )
                pfp.add_field(name="Full avatar link", value=link_frmt)
                pfp.set_image(url=user.avatar_url_as(
                    format=pic_frmt, size=4096))
                pfp.set_footer(text=f"User: {user} ({user.id})")
                pfp.colour = user.colour
                await ctx.send(embed=pfp)
        except discord.InvalidArgument:
            await ctx.send("Please provide a correct format!")
            await ctx.message.add_reaction("❌")

    @userinfo_avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Cannot find that user.')

    @userinfo.command(name="id", brief="Mention the user to get their ID")
    async def userinfo_id(self, ctx, user: libneko.converters.InsensitiveUserConverter = None):
        """Ping the user to get their ID, you can also type their username instead."""
        if user is None:
            user = ctx.message.author
        await ctx.send(
            embed=discord.Embed(
                description=f"The User ID of **{user.mention}** are `{user.id}`",
                color=user.colour
            )
        )

    @userinfo_id.error
    async def id_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Cannot find that user.')

    @userinfo.command(name="roles", brief="Show all roles that the member has.")
    async def userinfo_roles(self, ctx, member: libneko.converters.InsensitiveMemberConverter = None):
        """Show all roles that the member has."""
        if member is None:
            member = ctx.message.author

        roles = [role.mention for role in member.roles]
        memrole = discord.Embed(title=f"Role Viewer.", color=member.colour)
        memrole.add_field(name=f"{member}'s Roles", value=", ".join(roles))
        memrole.set_footer(
            text=f"{len(roles)} roles in total!", icon_url=member.avatar_url)
        await ctx.send(embed=memrole)

    @userinfo_roles.error
    async def roles_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Cannot find that user.')

    @userinfo.command(name="mention", brief="Mention a user.", aliases=["tag"])
    async def userinfo_mention(self, ctx, target: libneko.converters.InsensitiveUserConverter = None):
        """
        Mention a user.
        """
        if target is None:
            return await ctx.send(f"Mention who?")
        elif target == ctx.message.author:
            return await ctx.send(f"{ctx.message.author.mention} Mentioned themselves.")
        await ctx.send(f"{target.mention} has been mentioned by {ctx.message.author.mention}!")

    @userinfo.command(name="shared", aliases=["share"], brief="See all the servers that you shared with the someone")
    async def userinfo_shared(self, ctx, user: libneko.converters.InsensitiveUserConverter, user2: libneko.converters.InsensitiveUserConverter):
        """
        See all the servers that you shared with the someone else
        """

        @pag.embed_generator(max_chars=2048)
        def main_embed(paginator, page, page_index):
            embed = discord.Embed(
                title=f'Servers that {user} and {user2} shared with', description=page, color=ctx.message.author.color)
            return embed

        pagi = pag.EmbedNavigatorFactory(factory=main_embed)

        shared = []
        for guild in self.bot.guilds:
            if user in guild.members:
                if user2 in guild.members:
                    shared.append(guild.name)

        pagi += "\n".join(shared)
        pagi.start(ctx)


def setup(bot):
    bot.add_cog(Information(bot))
    print("Information Module has been loaded.")
