"""
MIT License

Copyright (c) 2017 Grok

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
FITNESS FOR A PARTICULAR PURPOSE AND NONINFINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
from datetime import datetime
import discord
import libneko
from libneko import pag
from discord.ext import commands
from io import BytesIO
from collections import namedtuple

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted = {}

    async def format_mod_embed(self, ctx, user, success, method, logs = None):
        """Helper func to format an embed to prevent extra code"""
        emb = discord.Embed(timestamp = ctx.message.created_at)
        try:
            emb.set_author(name = method.title())
            emb.set_footer(text = f"User ID: {user.id}")
            emb.set_thumbnail(url = user.avatar_url)
            if success:
                if method == "ban" or method == "hackban":
                    emb.description = f"**{user}** was just {method}ned."
                elif method == "unmute":
                    emb.description = f"**{user}** was just {method}d."
                elif method == "mute":
                    emb.description = f"**{user}** was just {method}d."
                elif method == "softban":
                    emb.description = f"**{user} was softbanned**"
                else:
                    emb.description = f"**{user}** was just {method}ed."
            else:
                if logs:
                    emb.description = (f"{logs}")
        except AttributeError as e:
            emb.description = (f"❌ An Error Occured, `{e}`")

        return emb

    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command()
    async def kick(self, ctx, member: libneko.converters.InsensitiveMemberConverter, *, reason: str = "No reason provided."):
        """Kick someone from the server."""
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            try:
                await ctx.guild.kick(member, reason = reason)
            except Exception as e:
                success = False
                return await ctx.send(embed=await self.format_mod_embed(ctx, member, success, "kick", e))
            else:
                success = True
            emb = await self.format_mod_embed(ctx, member, success, "kick")

            await ctx.send(embed = emb)

    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def ban(self, ctx, members:str, *, reason="Not Specified."):
        """Bans the member(s) from the guild."""

        members_list = members.split()

        l_bar = "█"
        l_empty = "░"

        async with ctx.typing():
            m_amount = len(members_list)
            m = 0

            banned = []
            alr_banned = []
            not_found = []
            forbidden = []
            failed = []

            embed = discord.Embed(
                title="Banning Members...",
                description=f"0% **(0/{m_amount})**",
                color=discord.Color.blurple()
            )
            message : discord.Message = await ctx.reply(embed=embed)
            dot = 0

            for member_id in members_list:

                await asyncio.sleep(0.5)
                try:
                    member = await commands.MemberConverter().convert(ctx, member_id)
                    await member.ban(reason=f'"{reason}" by {ctx.author}')
                    banned.append(f"{member.mention} {member}")
                except commands.MemberNotFound or discord.UserNotFound:
                    try:
                        user_ = await commands.UserConverter().convert(ctx, member_id)
                        await ctx.message.guild.fetch_ban(user_)
                        alr_banned.append(f"{user_.mention} {user_}")
                    except:
                        not_found.append(f"<@{member_id}>")
                except discord.Forbidden:
                    memb = await commands.MemberConverter().convert(ctx, member_id)
                    forbidden.append(f"{memb.mention} {memb}")
                except:
                    failed.append(f"<@{member_id}>")

                m += 1
                if m < m_amount:
                    dot += 1
                    if dot > 3:
                        dot = 1
                    embed.title = "Banning members" + dot*"."
                    progress = m/m_amount
                    bars = int(progress * 10)
                    embed.description = l_bar*bars + l_empty*(10-bars) + f" {int(progress*100)}% **({m}/{m_amount})**"
                    await message.edit(embed=embed)

            Results = namedtuple("Results", ["banned", "already_banned", "not_found", "forbidden", "failed"])

            def add_ban_fields(embed:discord.Embed, fields):
                field_names = Results(
                    banned=":white_check_mark: Banned: `{}`",
                    already_banned=":ballot_box_with_check: Already Banned: `{}`",
                    not_found=":warning: Not Found: `{}`",
                    forbidden=":no_entry_sign: Missing Permissions: `{}`",
                    failed=":x: Failed: `{}`",
                )
                field_names_txt = Results(
                    banned="Banned: {}",
                    already_banned="Already Banned: {}",
                    not_found="Not Found: {}",
                    forbidden="Missing Permissions: {}",
                    failed="Failed: {}",
                )
                results = []
                inline = False
                use_txt = False

                for m_list in fields:
                    j = "\n".join(m_list)
                    results.append(j)
                    if len(j) > 1024:
                        use_txt = True

                f_list = ["BAN REPORT\n"]

                for i in range(len(results)):
                    if results[i]:
                        if not use_txt:
                            embed.add_field(name=field_names[i].format(len(fields[i])), value=results[i], inline=inline)
                        else:
                            f_list.append(f"{field_names_txt[i].format(len(fields[i]))}\n{results[i]}\n")

                if use_txt:
                    everything = "\n".join(f_list)
                    return [True, BytesIO(everything.encode("utf-8"))]
                else:
                    return [False, None]

            embed.title = ":hammer: Finished! :hammer:"
            embed.description = f"**{len(banned)}** members banned for: ``{reason}``\n⠀"
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/758301208082513920/824494391942316072/tenor_2.gif")
            embed.color = discord.Color.red()
            use_text, data = add_ban_fields(embed, Results(banned, alr_banned, not_found, forbidden, failed))
            embed.set_footer(text=f"Ran by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.utcnow()
            await message.delete()
            if use_text:
                await ctx.send(embed=embed, file=discord.File(data, filename="ban_summary.txt"))
            else:
                await ctx.send(embed=embed)


    # This one is meant to be used as a joke
    @commands.guild_only()
    @commands.command(aliases=["fban", "fmute", "fakemute"], hidden=True)
    async def fakeban(self, ctx, member: libneko.converters.InsensitiveMemberConverter,  *, reason: str = "No reason provided."):
        """
        Ban (or mute) someone from the server. Or is it...?
        """
        if member.id == ctx.bot.user.id:
            return await ctx.send("For real?")
        success = True
        if "mute" in ctx.invoked_with:
            emb = await self.format_mod_embed(ctx, member, success, "mute")
        else:
            emb = await self.format_mod_embed(ctx, member, success, "ban")
        emb.add_field(name="Reason", value=reason)
        await ctx.send(embed=emb)

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(aliases=['sb'])
    async def softban(self, ctx, user : libneko.converters.InsensitiveMemberConverter, *, reason=None):
        """
        Bans and unbans the user, so their messages are deleted
        """
        if ctx.author.top_role > user.top_role or ctx.author == ctx.guild.owner:
            try:
                if user == ctx.author:
                    return await ctx.send("***:no_entry: You can't softban yourself...***")
                await user.ban(reason=reason)
                await user.unban(reason=reason)
                if not reason:
                    success = True
                    emb = await self.format_mod_embed(ctx, user, success, "softban",)
                else:
                    success = True
                    emb = await self.format_mod_embed(ctx, user, success, "softban", reason)
            except Exception as e:
                success = False
                return await ctx.send(embed=await self.format_mod_embed(ctx, user, success, "softban", e))
            
            await ctx.send(embed = emb)



    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command()
    @commands.guild_only()
    async def unban(self, ctx, userid: discord.User, *, reasons: str = None):
        """Unban someone from the server."""
        ban = await ctx.guild.fetch_ban(userid)

        if reasons is None:
            try:
                await ctx.guild.unban(ban.user, reason = "No Reason Specified!")
            except:
                success = False
            else:
                success = True
        
        else:
            try:
                await ctx.guild.unban(ban.user, reason = reasons)
            except:
                success = False
            else:
                success = True

        emb = await self.format_mod_embed(ctx, ban.user, success, "unban")

        await ctx.send(embed = emb)

    @commands.cooldown(rate=1, per=5.0)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(aliases = ["del", "pr", "prune"])
    async def purge(self, ctx, amount: int, member: libneko.converters.InsensitiveMemberConverter = None):
        """
        Clean a number of messages from a channel.
        You can also clean messages of a specific member.
        """
        try:
            if amount <= 500:
                if member is None:
                    await ctx.channel.purge(limit = amount + 1)
                else:
                    async for message in ctx.channel.history(limit = amount + 2):
                        if message.author is member:
                            await message.delete()
            elif amount == 0:
                await ctx.send(discord.Embed(description="⚠ Please Specify the amount of messages to be deleted!"))
            else:
                await ctx.send(discord.Embed(description="❌ Maximum amount of purging reached. You can only purge 500 messages at a time"))
        except:
            await ctx.send(embed=discord.Embed(description="⚠ An error has occured! Please make sure that i have the correct permission!"))

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(aliases=["banlist"])
    async def bans(self, ctx):
        """See a list of banned users in the guild"""
        bans = await ctx.guild.bans()

        banned = []

        @pag.embed_generator(max_chars=2048)
        def det_embed(paginator, page, page_index):
            em = discord.Embed(title = f"List of Banned Members:", description=page)
            em.set_footer(text=f"{len(bans)} Members in Total.")
            return em

        page = pag.EmbedNavigatorFactory(factory=det_embed)

        for users in bans:
            banned.append(str(users.user))

        page += "\n".join(banned)
        page.start(ctx)

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, view_audit_log=True)
    @commands.guild_only()
    @commands.command()
    async def baninfo(self, ctx, *, userid: discord.User):
        """Check the reason of a ban from the audit logs."""
        ban = await ctx.guild.fetch_ban(userid)
        em = discord.Embed()
        em.set_author(name=str(ban.user), icon_url=ban.user.avatar_url)
        em.add_field(name="Ban Reason", value=ban.reason or "None")
        em.set_thumbnail(url=ban.user.avatar_url)
        em.set_footer(text=f"User ID: {ban.user.id}")

        await ctx.send(embed=em)

    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def banfinder(self, ctx, *, string: str = None):
        """Count the amount of bans in the guild that contain the search in their reasons."""
        if string is None:
            await ctx.send("Type something to search!", delete_after=5)
        
        n = 0
        async with ctx.typing():
            bans = await ctx.guild.bans()
            for ban in bans:
                if not ban.reason:
                    continue
                if string.lower() in ban.reason.lower():
                    n += 1
        
        await ctx.send(
            embed = discord.Embed(
                title="Done!",
                description=f"``{n}`` Bans corresponding to ``{string}``.",
                color=discord.Color.green()
            )
        )

    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(aliases=["assignrole","giverole"])
    async def addrole(self, ctx, member: libneko.converters.InsensitiveMemberConverter, *, role: libneko.converters.RoleConverter = None):
        """Add a role to someone else."""
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            try:
                if not role:
                    return await ctx.send("That role does not exist.")
                await member.add_roles(role)
                await ctx.send(embed=discord.Embed(description=f"Added: `{role.name}` to `{member}`"))
            except discord.Forbidden:
                    await ctx.send(embed=discord.Embed(description="⚠ I don't have permission to manage roles!"))

    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(aliases=["makerole","mkrole"])
    async def createrole(self, ctx, colour: libneko.converters.ColourConverter, * , role_name: str):
        """
        Creates a new role!
        Color field only accept RGB Hex value. (Ex: #36393e)
        """
        try:
            await ctx.guild.create_role(
                name=role_name,
                colour=colour,
            )
            await ctx.send(embed=discord.Embed(description=f"Successfully created New Role **{role_name}**!", colour=colour))
        except discord.Forbidden:
            await ctx.send("Can't do that!")

    @commands.has_permissions(administrator=True)
    @commands.command(disabled=True, hidden=True)
    @commands.guild_only()
    async def giveroletoeveryone(self, ctx, *, role: discord.Role):
        """
        Give a role to everyone else.
        Can only be used by server owner.
        Can be unreliable.
        Please don't use unless absolutely necessary
        //TODO: Find a more reliable method
        """
        if ctx.author == ctx.guild.owner:
            if not role:
                return await ctx.send("That role does not exist.")
            curr = 0
            total = len(ctx.guild.members)
            progress = f"{curr}/{total}"
            await ctx.send(progress)
            await ctx.send("Assigning roles to every member... (THIS WILL TAKE A WHILE)")
            for users in ctx.guild.members:
                if users.bot is False:
                    if users not in role.members:
                        await users.add_roles(role)
                        curr += 1
                        await progress.edit(content=f"({curr}/{total})")
                        print(f"Added Role: {role.name} to Member: {users}")
                        await asyncio.sleep(5)
                await ctx.send("Completed!")
                print("Completed!")
        
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command(aliases=["unassignrole"])
    async def removerole(self, ctx, member: libneko.converters.InsensitiveMemberConverter, *, rolename: libneko.converters.RoleConverter):
        """Remove a role from someone else."""
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            if not rolename:
                return await ctx.send("That role does not exist.")
            await member.remove_roles(rolename)
            await ctx.send(embed=discord.Embed(description=f"Removed: `{rolename}` from `{member}`"))

    @commands.bot_has_permissions(ban_members=True, view_audit_log=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(aliases=["hban"])
    async def hackban(self, ctx, userid: int, *, reason = None):
        """Ban someone that are not in the server"""
        try:
            await ctx.guild.ban(discord.Object(userid), reason = reason)
        except:
            success = False
        else:
            success = True

        if success:
            async for entry in ctx.guild.audit_logs(
                limit = 1, user = ctx.guild.me, action = discord.AuditLogAction.ban
            ):
                emb = await self.format_mod_embed(ctx, entry.target, success, "hackban")
                emb.add_field(name="Reason", value=reason)
        else:
            emb = await self.format_mod_embed(ctx, userid, success, "hackban")
            emb.add_field(name="Reason", value=reason)
        await ctx.send(embed = emb)

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def mute(self, ctx, member: libneko.converters.InsensitiveMemberConverter, duration: str, *, reason: str = None):
        """
        Denies someone from chatting in all text channels and talking in voice channels for a specified duration    
        """
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            unit = duration[-1]
            if unit == "s":
                time = int(duration[:-1])
                longunit = "seconds"
            elif unit == "m":
                time = int(duration[:-1]) * 60
                longunit = "minutes"
            elif unit == "h":
                time = int(duration[:-1]) * 60 * 60
                longunit = "hours"
            else:
                return await ctx.send("Invalid Unit! Use `s`, `m`, or `h`.")
            
            muted = self.muted.get(f"{member.id}@{ctx.guild.id}")
            if muted is not None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"{member.mention} is already muted!",
                        color=discord.Colour.red(),
                    )
                )
            else:
                async def mute_task(self):
                    role = discord.utils.get(ctx.guild.roles, name="Muted") # retrieves muted role returns none if there isn't 
                    if not role: # checks if there is muted role
                        try: # creates muted role 
                            muted = await ctx.guild.create_role(name="Muted", reason="To be used for muting")
                            for channel in ctx.guild.channels: # removes permission to view and send in the channels 
                                await channel.set_permissions(muted, send_messages=False,
                                                              read_message_history=False,
                                                              read_messages=False)
                                await member.add_roles(muted, reason=reason) # add newly created role
                        except discord.Forbidden:
                            return await ctx.send("I have no permissions to make a muted role") # self-explainatory
                    else:
                        await member.add_roles(role) # gives the member the muted role
                    
                    success = True
                    emb = await self.format_mod_embed(ctx, member, success, "mute", f"{str(duration[:-1])} {longunit}")
                    emb.add_field(name="Reason", value=reason)
                    await ctx.send(embed = emb, content="💀 You're gonna have a bad time")
                    
                    await asyncio.sleep(time)
                    
                    try:
                        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted")) # removes muted role
                    except:
                        pass
                    
                    del self.muted[f"{member.id}@{ctx.guild.id}"]
                
                mute = self.bot.loop.create_task(mute_task(self))
                self.muted.update({f"{member.id}@{ctx.guild.id}": mute})
                    

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def unmute(self, ctx, member: libneko.converters.InsensitiveMemberConverter, *, reason: str = None):
        """Unmute someone so they can talk again"""
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            try:
                muted = self.muted.get(f"{member.id}@{ctx.guild.id}")
                if muted is None:
                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"{member.mention} is not muted!",
                            color=discord.Colour.red(),
                        )
                    )
                del self.muted[f"{member.id}@{ctx.guild.id}"]
                await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted")) # removes muted role
            except:
                success = False
            else:
                success = True

            emb = await self.format_mod_embed(ctx, member, success, "unmute")
            await ctx.send(embed = emb)

    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.command(aliases=["selfnick"])
    @commands.guild_only()
    async def selfnickname(self, ctx, *, newname: str = None):
        """Change my nickname, if omitted, removes it instead."""
        guild = ctx.guild
        if newname is None:
            await guild.me.edit(nick=None)
            await ctx.send(
                embed=discord.Embed(description=f"Successfully reset my nickname.")
            )
        elif len(newname) > 32:
            await ctx.send(
                embed=discord.Embed(
                    description=f":warning: The new nickname must be 32 or fewer in length."
                )
            )
        else:
            await guild.me.edit(nick=newname)
            await ctx.send(
                embed=discord.Embed(
                    description=f"Successfully changed my nickname to **{newname}**!"
                )
            )
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.command(aliases=["changenick", "nick"])
    @commands.guild_only()
    async def nickname(self, ctx, member: libneko.converters.InsensitiveMemberConverter, *, newname: str = None):
        """Change other user's nickname, if omitted, removes it instead."""
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            try:
                if newname is None:
                    await member.edit(nick=None)
                    await ctx.send(
                        embed=discord.Embed(
                            description=f"Successfully reset the nickname of **{member.name}**"
                        )
                    )
                elif len(newname) > 32:
                    await ctx.send(
                        embed=discord.Embed(
                            description=f":warning: The new nickname must be 32 or fewer in length."
                        )
                    )
                else:
                    await member.edit(nick=newname)
                    await ctx.send(
                        embed=discord.Embed(
                            description=f"Successfully changed the nickname of **{member.name}** to **{newname}**"
                        )
                    )
            except discord.Forbidden:
                    await ctx.send(embed=discord.Embed(description="⚠ I don't have permission to change their nickname!"))

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.command(aliases=['slowmo','slow'])
    async def slowmode(self, ctx, duration: str = "0s"):
        """Set the slowmode for this"""
        try:
            unit = duration[-1]
            if unit == "s":
                time = int(duration[:-1])
                longunit = "seconds"
            elif unit == "m":
                time = int(duration[:-1]) * 60
                longunit = "minutes"
            elif unit == "h":
                time = int(duration[:-1]) * 60 * 60
                longunit = "hours"
            else:
                await ctx.send("Invalid Unit! Use `s`, `m`, or `h`.")
                return
        except ValueError:
            await ctx.send("Invalid Value! Example: `30s`, `5m`, or `1h`.")
            return

        if len(duration) > 4:
            await ctx.send("Invalid Input!")
            return

        if time > 21600:
            await ctx.send(embed=discord.Embed(description="⛔ Duration can't be over than 6 hours!"))
            return

        if duration == "0s":
            await ctx.channel.edit(slowmode_delay=time)
            a = await ctx.send(embed=discord.Embed(description="ℹ **Slowmode is turned off for this channel**"))
            await a.add_reaction("⏱")
            return
        else:
            await ctx.channel.edit(slowmode_delay=time)
            confirm = await ctx.send(embed=discord.Embed(description=f"**Set the channel slow mode delay to `{str(duration[:-1])} {longunit}` \nTo turn this off, run the command without any value**"))
            await confirm.add_reaction("⏱")

    @commands.command(aliases=["send", "dm"])
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def sendto(self, ctx, target: libneko.converters.InsensitiveMemberConverter = None, *, text:commands.clean_content = None):
        """
        Send a message to a user's DM
        Can only be used by moderators
        """
        msg = await ctx.send("Preparing...")
        if text is None:
            err = discord.Embed(description="What do you want me to say?")
            await msg.edit(embed=err, content=None)
            await ctx.message.add_reaction("❓")
            return
        if target is None:
            err = discord.Embed(description="Who do you want me to send the message to?")
            await msg.edit(embed=err, content=None)
            await ctx.message.add_reaction("❓")
            return
        try:
            snd = discord.Embed(description="Sending Message!")
            await msg.edit(embed=snd, content=None)
            recv = discord.Embed(description=text, timestamp=datetime.utcnow())
            recv.set_author(name=f"Message from {ctx.guild.name}", icon_url=ctx.guild.icon_url)
            #recv.set_footer(text=f"Sent by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
            await target.send(embed=recv)
            snd = discord.Embed(description="Message Sent!")
            await msg.edit(embed=snd)
        except discord.Forbidden:
            err = discord.Embed(description=f"⛔ {target} has their DM disabled.")
            await msg.edit(embed=err, content=None)
            await ctx.message.add_reaction("❌")
            return


def setup(bot):
    bot.add_cog(Mod(bot))
    print("Moderator Module has been loaded.")
