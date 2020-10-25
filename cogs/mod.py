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
import discord
import libneko
from libneko import pag
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def format_mod_embed(self, ctx, user, success, method, duration = None):
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
                    emb.description = f"**{user}** was just {method}d for {duration}."
                else:
                    emb.description = f"**{user}** was just {method}ed."
            else:
                emb.description = (
                    f"Unable to {method} **{user}**. \nMake sure that i have the required permission or the target are correct! **(UNKNOWN ERROR)**"
                )
        except AttributeError:
            emb.description = "❌ An Error Occured, The User cannot be found!"

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
            except:
                success = False
            else:
                success = True

            emb = await self.format_mod_embed(ctx, member, success, "kick")

            await ctx.send(embed = emb)

    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def ban(self, ctx, member: libneko.converters.InsensitiveMemberConverter, message_deletion: int = 0, *, reason: str = "No reason provided."):
        """
        Ban someone from the server.
        Usage: `[p]ban <member> [message_deletion] [reason]`
        Where you specify `message_deletion` with the amount of days where the old messages of the banned member will be deleted.
        Default value is 0 (which is None)
        Max value is 7 days
        """
        try:
            if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
                    if member == ctx.author:
                        return await ctx.send("***:no_entry: You can't ban yourself...***")
                    try:
                        await ctx.guild.ban(member, reason = reason, delete_message_days = message_deletion)
                    except:
                        success = False
                    else:
                        success = True

                    emb = await self.format_mod_embed(ctx, member, success, "ban")
    
                    await ctx.send(embed = emb)
        except AttributeError as e:
            return await ctx.send(f"***:x: An Error Occured.*** {e}")

    # This one is meant to be used as a joke
    @commands.guild_only()
    @commands.command(aliases=["fban"])
    async def fakeban(self, ctx, member: libneko.converters.InsensitiveMemberConverter,  *, reason: str = "No reason provided."):
        """
        Ban someone from the server. Or is it...?
        """
        success = True
        emb = await self.format_mod_embed(ctx, member, success, "ban") 
        emb.add_field(name="Reason", value=reason)
        await ctx.send(embed = emb)

    @ban.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid usage!\nUsage: `[p]ban <member> [message_deletion] [reason]`')

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(aliases=['sb'])
    async def softban(self, ctx, user : libneko.converters.InsensitiveMemberConverter, *, reason=None):
        """
        Bans and unbans the user, so their messages are deleted
        """
        if ctx.author.top_role > user.top_role or ctx.author == ctx.guild.owner:
            if user == ctx.author:
                return await ctx.send("***:no_entry: You can't softban yourself...***")
            await user.ban(reason=reason)
            await user.unban(reason=reason)
            if not reason:
                await ctx.send(f"**{user} was softbanned :wave:**")                
            else:
                await ctx.send(f"**{user} was softbanned** :wave: **Reason: {reason}")


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
    @commands.command(aliases = ["del", "p", "prune"])
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
                    async for message in ctx.channel.history(limit = amount + 1):
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
        try:
            bans = await ctx.guild.bans()
        except:
            return await ctx.send("You dont have the perms to see bans.")

        banned = ""

        @pag.embed_generator(max_chars=2048)
        def det_embed(paginator, page, page_index):
            em = discord.Embed(title = f"List of Banned Members:", description=page)
            em.set_footer(text=f"{len(bans)} Members in Total.")
            return em

        page = pag.EmbedNavigatorFactory(factory=det_embed)

        for users in bans:
            banned += f"{users.user}\n"

        page += banned
        page.start(ctx)

    @commands.has_permissions(ban_members=True, view_audit_log=True)
    @commands.bot_has_permissions(ban_members=True, view_audit_log=True)
    @commands.guild_only()
    @commands.command()
    async def baninfo(self, ctx, *, userid: discord.User):
        """Check the reason of a ban from the audit logs."""
        ban = await ctx.guild.fetch_ban(userid)
        em = discord.Embed()
        em.set_author(name=str(ban.user), icon_url=ban.user.avatar_url)
        em.add_field(name="Reason", value=ban.reason or "None")
        em.set_thumbnail(url=ban.user.avatar_url)
        em.set_footer(text=f"User ID: {ban.user.id}")

        await ctx.send(embed=em)

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
    async def createrole(self, ctx, colour: str, * , role_name: str = None):
        """
        Creates a new role!
        Color field only accept RGB Hex value. (Ex: 36393e)
        """
        try:
            await ctx.guild.create_role(
                name=(colour if not role_name else role_name),
                colour=discord.Colour(eval("0x0{}".format(colour.lstrip("#").lstrip("0x")))),
            )
            await ctx.send(embed=discord.Embed(description=f"Created New Role **{role_name}**!", colour=discord.Colour(eval("0x0{}".format(colour.lstrip("#").lstrip("0x"))))))
        except discord.Forbidden:
            await ctx.send("Can't do that!")
        except SyntaxError:
            await ctx.send("Invalid color format!! Only Hex codes are allowed")

    @commands.has_permissions(administrator=True)
    @commands.command(disabled=True, hidden=True)
    @commands.guild_only()
    async def giveroletoeveryone(self, ctx, *, role: discord.Role):
        """
        Give a role to everyone else.
        Can only be used by server owner.
        Can be unreliable.
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
        """Ban someone not in the server"""
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
        else:
            emb = await self.format_mod_embed(ctx, userid, success, "hackban")
        await ctx.send(embed = emb)

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def mute(self, ctx, member: libneko.converters.InsensitiveMemberConverter, duration, *, reason: str = None):
        """Denies someone from chatting in all text channels and talking in voice channels for a specified duration"""
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
                await ctx.send("Invalid Unit! Use `s`, `m`, or `h`.")
                return

            progress = await ctx.send(embed=discord.Embed(description=f"Muting {member}!"))
            try:
                for channel in ctx.guild.text_channels:
                    await channel.set_permissions(
                        member,
                        overwrite = discord.PermissionOverwrite(send_messages = False),
                        reason = reason,
                    )

                for channel in ctx.guild.voice_channels:
                    await channel.set_permissions(
                        member,
                        overwrite = discord.PermissionOverwrite(speak = False),
                        reason = reason,
                    )
            except:
                success = False
            else:
                success = True

            emb = await self.format_mod_embed(
                ctx, member, success, "mute", f"{str(duration[:-1])} {longunit}"
            )
            await progress.delete()
            await ctx.send(embed = emb)
            await asyncio.sleep(time)
            try:
                for channel in ctx.guild.channels:
                    await channel.set_permissions(member, overwrite = None, reason = reason)
            except:
                pass

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def unmute(self, ctx, member: libneko.converters.InsensitiveMemberConverter, *, reason: str = None):
        """Removes channel overrides for specified member"""
        if ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner:
            progress = await ctx.send(embed=discord.Embed(description=f"Unmuting {member}!"))
            try:
                for channel in ctx.message.guild.channels:
                    await channel.set_permissions(member, overwrite = None, reason = reason)
            except:
                success = False
            else:
                success = True

            emb = await self.format_mod_embed(ctx, member, success, "unmute")
            await progress.delete()
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

        if len(duration) > 4:
            await ctx.send("Invalid Input!")
            return

        if time > 21600:
            await ctx.send(embed=discord.Embed(description="⛔ Duration can't be over than 6 hours!"))
            return

        if duration == "0s":
            await ctx.channel.edit(slowmode_delay=time)
            a = await ctx.send(embed=discord.Embed(description="ℹ **Slowmode is off for this channel**"))
            await a.add_reaction("⏱")
            return
        else:
            await ctx.channel.edit(slowmode_delay=time)
            confirm = await ctx.send(embed=discord.Embed(description=f"**Set the channel slow mode delay to `{str(duration[:-1])} {longunit}` \nTo turn this off, run the command without any value**"))
            await confirm.add_reaction("⏱")


def setup(bot):
    bot.add_cog(Mod(bot))
    print("Moderator Module has been loaded.")
