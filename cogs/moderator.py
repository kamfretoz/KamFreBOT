import discord
import asyncio
import config
from discord.ext import commands

bot = commands.Bot(command_prefix=config.prefix)


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Assign a role to someone
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    @commands.command(aliases=["assignrole", "giverole"])
    @commands.guild_only()
    async def promote(self, ctx, member: discord.Member, *, xrole: discord.Role):
        """Assign a role to a member."""
        await member.add_roles(xrole)
        await ctx.send(
            embed=discord.Embed(
                description=f":white_check_mark: Successfully added the role **{xrole.name}** to Member **{member.mention}**"
            )
        )

    # Remove a role from someone
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    @commands.command(
        aliases=["deassignrole", "revokerole"]
    )
    @commands.guild_only()
    async def demote(self, ctx, member: discord.Member, *, xrole: discord.Role):
        """Remove a role from a member"""
        await member.remove_roles(xrole)
        await ctx.send(
            embed=discord.Embed(
                description=f":white_check_mark: Successfully removed the role **{xrole.name}** from Member **{member.mention}**"
            )
        )

    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.command(
        aliases=["changenick", "nick"]
    )
    @commands.guild_only()
    async def nickname(self, ctx, member: discord.Member, *, newname: str = None):
        """Change other user's nickname, if omitted, removes it instead."""
        if newname is None:
            await member.edit(nick=None)
            await ctx.send(
                embed=discord.Embed(
                    description=f"Successfully reset the nickname of **{member.mention}**"
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

# DON'T USE IT'S UNSTABLE
#    @commands.has_permissions(manage_roles=True)
#    @commands.bot_has_permissions(manage_roles=True)
#    @commands.command(brief="Move the position of a role", aliases=["moverole"])
#    @commands.guild_only()
#    async def move(self, ctx, xrole: discord.Role, posx: int):
#        """Move the order of a role (Descending from 0 (bottom most))"""
#        await xrole.edit(position=posx)
#        await ctx.send(
#            embed=discord.Embed(
#                description=f":white_check_mark: Successfully moved the role **{xrole.name}** to position **{posx}**"
#            )
#        )

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member):
        """Kick a member"""
        if member == ctx.message.author:
            await ctx.send(
            embed=discord.Embed(description=f":x: You cannot kick yourself!")
            )
        else:
            await ctx.guild.kick(member)
            await ctx.send(
                embed=discord.Embed(
                    description=f":white_check_mark: **{member.name}** has been kicked from the server"
                )
            )

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command()
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member):
        """Ban a member"""
        if user == ctx.message.author:
            await ctx.send(
                embed=discord.Embed(description=f":x: You cannot ban yourself!")
            )
        else:
            await ctx.guild.ban(user)
            await ctx.send(
                embed=discord.Embed(
                    description=f":white_check_mark: **{user.name}** has been banned from the server"
                )
            )

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command()
    @commands.guild_only()
    async def unban(self, ctx, user: discord.Member):
        """Unban a member"""
        userid = discord.Object(user)
        await ctx.guild.unban(user=userid)
        await ctx.send(
            embed=discord.Embed(
                description=f":white_check_mark: **{user.name}** has been unbanned from the server"
            )
        )

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command(aliases=["prune"])
    @commands.guild_only()
    async def purge(self, ctx, number: int = None):
        """
        Clean numbers of messages on the channel.
        Maximum allowed amount are 500 at given times.
        """
        if number is None:
            await ctx.send("Please define the amount of messages you want to purge!")
        elif number > 500:
            await ctx.send("Maximum allowed amount are 500 at given times.")
        elif number is 1:
            await ctx.channel.purge(limit=number + 1)
            await ctx.send(f"Deleted {number} message", delete_after=5)
        else:
            await ctx.channel.purge(limit=number + 1)
            await ctx.send(f"Deleted {number} message(s)", delete_after=5)

    @commands.is_owner()
    @commands.guild_only()
    @commands.command(brief="Leave a server (Can only be used by bot owner)", hidden=True)
    async def leaveserver(self, ctx, serverid: int  = None):
        await ctx.send("Affirmative, Your Majesty.")
        await asyncio.sleep(3)
        await ctx.guild.leave()

def setup(bot):
    bot.add_cog(Moderator(bot))
