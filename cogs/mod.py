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
import json
import os
import discord
from discord.ext import commands


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def format_mod_embed(self, ctx, user, success, method, duration = None):
        """Helper func to format an embed to prevent extra code"""
        emb = discord.Embed(timestamp = ctx.message.created_at)
        emb.set_author(name = method.title(), icon_url = user.avatar_url)
        emb.set_footer(text = f"User ID: {user.id}")
        if success:
            if method == "ban" or method == "hackban":
                emb.description = f"{user} was just {method}ned."
            elif method == "unmute":
                emb.description = f"{user} was just {method}d."
            elif method == "mute":
                emb.description = f"{user} was just {method}d for {duration}."
            elif method == "channel-lockdown" or method == "server-lockdown":
                emb.description = f"`Channel Locked!"
            else:
                emb.description = f"{user} was just {method}ed."
        else:
            if method == "lockdown" or "channel-lockdown":
                emb.description = (
                    f"You do not have the permissions to {method} `{ctx.channel.name}`."
                )
            else:
                emb.description = (
                    f"You do not have the permissions to {method} {user.name}."
                )

        return emb

    @commands.command()
    async def kick(
        self, ctx, member: discord.Member, *, reason = "Please write a reason!"
    ):
        """Kick someone from the server."""
        try:
            await ctx.guild.kick(member, reason = reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, "kick")

        await ctx.send(embed = emb)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(
        self, ctx, member: discord.Member, *, reason = "Please write a reason!"
    ):
        """Ban someone from the server."""
        try:
            await ctx.guild.ban(member, reason = reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, "ban")

        await ctx.send(embed = emb)

    @commands.command()
    async def unban(self, ctx, userid: discord.User, *, reason = None):
        """Unban someone from the server."""
        ban = await ctx.guild.fetch_ban(userid)

        try:
            await ctx.guild.unban(ban.user, reason = reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, ban.user, success, "unban")

        await ctx.send(embed = emb)

    @commands.command(aliases = ["del", "p", "prune"])
    async def purge(self, ctx, limit: int, member: discord.Member = None):
        """Clean a number of messages"""
        if member is None:
            await ctx.channel.purge(limit = limit + 1)
        else:
            async for message in ctx.channel.history(limit = limit + 1):
                if message.author is member:
                    await message.delete()

    @commands.command()
    async def clean(self, ctx, quantity: int):
        """ Clean a number of your own messages
        Usage: {prefix}clean 5 """
        if quantity <= 15:
            total = quantity + 1
            async for message in ctx.channel.history(limit = total):
                if message.author == ctx.author:
                    await message.delete()
                    await asyncio.sleep(3.0)
        else:
            async for message in ctx.channel.history(limit = 6):
                if message.author == ctx.author:
                    await message.delete()
                    await asyncio.sleep(3.0)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def bans(self, ctx):
        """See a list of banned users in the guild"""
        try:
            bans = await ctx.guild.bans()
        except:
            return await ctx.send("You dont have the perms to see bans.")

        em = discord.Embed(title = f"List of Banned Members ({len(bans)}):")
        em.description = ", ".join([str(b.user) for b in bans])

        await ctx.send(embed = em)

    @commands.has_permissions(ban_members=True)
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
    @commands.command()
    async def addrole(self, ctx, member: discord.Member, *, role: discord.Role):
        """Add a role to someone else."""
        if not role:
            return await ctx.send("That role does not exist.")
        try:
            await member.add_roles(role)
            await ctx.send(f"Added: `{role.name}`")
        except:
            await ctx.send("I don't have the perms to add that role.")

    @commands.has_permissions(administrator=True)
    @commands.command(disabled=True, hidden=True)
    async def giveroletoeveryone(self, ctx, *, role: discord.Role):
        """Add a role to everyone else."""
        await ctx.send("Assigning roles to every member...")
        if not role:
            return await ctx.send("That role does not exist.")
        try:
            for users in ctx.guild.members:
                if users.bot is False:
                    await users.add_roles(role)
                    print(f"Added Role: {role.name} to Member: {users}")
        except:
            await ctx.send("I don't have the perms to add that role.")
            pass
        
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def removerole(self, ctx, member: discord.Member, *, rolename: str):
        """Remove a role from someone else."""
        role = discord.utils.find(
            lambda m: rolename.lower() in m.name.lower(), ctx.message.guild.roles
        )
        if not role:
            return await ctx.send("That role does not exist.")
        try:
            await member.remove_roles(role)
            await ctx.send(f"Removed: `{role.name}`")
        except:
            await ctx.send("I don't have the perms to add that role.")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def hackban(self, ctx, userid: discord.User, *, reason = None):
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

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def mute(self, ctx, member: discord.Member, duration, *, reason = None):
        """Denies someone from chatting in all text channels and talking in voice channels for a specified duration"""
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

        progress = await ctx.send("Muting user!")
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
        progress.delete()
        await ctx.send(embed = emb)
        await asyncio.sleep(time)
        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(member, overwrite = None, reason = reason)
        except:
            pass

    @commands.command()
    async def unmute(self, ctx, member: discord.Member, *, reason = None):
        """Removes channel overrides for specified member"""
        progress = await ctx.send("Unmuting user!")
        try:
            for channel in ctx.message.guild.channels:
                await channel.set_permissions(member, overwrite = None, reason = reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, member, success, "unmute")
        progress.delete()
        await ctx.send(embed = emb)

@commands.has_permissions(manage_nicknames=True)
@commands.command(aliases=["selfnick"])
@commands.guild_only()
async def selfnickname(self, ctx, *, newname: str = None):
    """Change my nickname, if omitted, removes it instead."""
    guild = ctx.guild
    if newname == None:
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


def setup(bot):
    bot.add_cog(Mod(bot))
    print("Moderator Module has been loaded.")
