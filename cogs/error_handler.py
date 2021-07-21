import traceback
import discord
import random
import math
from datetime import datetime
import data.config as config
import data.quotes as quotes
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Main Exception
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            nocommand = discord.Embed(
                description=":warning: **Invalid Command!**")
            nocommand.set_image(url="https://http.cat/404.jpg")
            await ctx.send(content=None, embed=nocommand, delete_after=10)

        elif isinstance(error, commands.errors.MissingPermissions):
            perms = []
            for x in error.missing_perms:
                perms.append(x)
            nopermission = discord.Embed(
                description=f"**:warning: You dont have permissiont to run that command!**")
            nopermission.add_field(
                name="Required Permission(s):", value=f'```{", ".join(perms)}```')
            nopermission.set_image(url="https://http.cat/403.jpg")
            await ctx.send(content=None, embed=nopermission, delete_after=15)

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            missingargs = discord.Embed(
                description="**:warning: You are missing required arguments, Please refer to the help menu with `[p]help <command>` for more information.**")
            missingargs.set_image(url="https://http.cat/410.jpg")
            await ctx.send(content=None, embed=missingargs, delete_after=10)

        elif isinstance(error, commands.errors.BadArgument):
            badargument = discord.Embed(
                description="**:warning: You have given an invalid value. Please refer to the help menu with `[p]help <command>` for more information.**")
            badargument.set_image(url="https://http.cat/400.jpg")
            await ctx.send(content=None, embed=badargument, delete_after=10)

        elif isinstance(error, commands.CommandOnCooldown):
            cooldownerr = discord.Embed(
                description=f"**:warning: That command is on cooldown. Please try again after {math.ceil(error.retry_after) + 1} second(s).**")
            cooldownerr.set_image(url="https://http.cat/429.jpg")
            await ctx.send(embed=cooldownerr, content=None, delete_after=10)

        elif isinstance(error, commands.errors.BotMissingPermissions):
            perms = []
            for x in error.missing_perms:
                perms.append(x)
            missperm = discord.Embed(
                description=f"**:warning: I don't have required permission to complete that command.**")
            missperm.add_field(name="Required Permission(s):",
                               value=f'```{", ".join(perms)}```')
            missperm.set_image(url="https://http.cat/423.jpg")
            await ctx.send(embed=missperm, content=None, delete_after=15)

        elif isinstance(error, commands.errors.TooManyArguments):
            toomanyargs = discord.Embed(
                description=f"**:warning: You have inputted too many arguments!**")
            toomanyargs.set_image(url="https://http.cat/413.jpg")
            await ctx.send(embed=toomanyargs, content=None, delete_after=10)

        elif isinstance(error, commands.errors.DisabledCommand):
            ded = discord.Embed(
                description=f"**:warning: This command are disabled.**")
            ded.set_image(url="https://http.cat/503.jpg")
            await ctx.send(embed=ded, content=None, delete_after=10)

        elif isinstance(error, discord.Forbidden):
            missaccess = discord.Embed(
                description=f"**:no_entry_sign: I'm not allowed to do that!**")
            missaccess.set_image(url="https://http.cat/403.jpg")
            await ctx.send(embed=missaccess, content=None, delete_after=10)

        elif isinstance(error, commands.errors.NotOwner):
            notowner = discord.Embed(
                description=f"**:warning: You are not my owner!**")
            notowner.set_image(url="https://http.cat/401.jpg")
            await ctx.send(embed=notowner, content=None, delete_after=10)

        elif isinstance(error, discord.NotFound):
            notfound = discord.Embed(
                description=f"**:warning: Can't find the target message!**")
            notfound.set_image(url="https://http.cat/404.jpg")
            await ctx.send(embed=notfound, content=None, delete_after=10)

        elif isinstance(error, commands.errors.ConversionError):
            conv = discord.Embed(
                description=f"**:warning: Lookup error, target not found! (is the syntax correct?)**")
            conv.set_image(url="https://http.cat/404.jpg")
            await ctx.send(embed=conv, content=None, delete_after=10)

        elif isinstance(error, commands.errors.ArgumentParsingError):
            arg_err = discord.Embed(
                description=f"**:warning: An Error occured during parsing of user's argument! (is the input correct?)**")
            arg_err.set_image(url="https://http.cat/417.jpg")
            await ctx.send(embed=arg_err, content=None, delete_after=10)

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            conc = discord.Embed(
                description=f"**:warning: This command is currently rate-limited! You can use it only {error.number} time(s) at once until it is completed.**")
            conc.set_image(url="https://http.cat/429.jpg")
            await ctx.send(embed=conc, content=None, delete_after=10)

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(f'**:no_entry: `{ctx.command}` can not be used in Private Messages.**')

        elif isinstance(error, commands.errors.NSFWChannelRequired):
            conc = discord.Embed(
                description=f"**:warning: You can only use this command on channels that are marked as NSFW.**")
            conc.set_image(url="https://http.cat/423.jpg")
            await ctx.send(embed=conc, content=None, delete_after=10)

        elif isinstance(error, commands.errors.CheckFailure):
            conv = discord.Embed(
                description=f"**:warning: Command Check Failure, You are not authorized to use this command!**")
            conv.set_image(url="https://http.cat/401.jpg")
            await ctx.send(embed=conv, content=None, delete_after=10)

        else:
            try:
                now = datetime.now()
                print(f"Ignoring exception in command {ctx.command.name}")
                trace = traceback.format_exception(
                    type(error), error, error.__traceback__)
                print("".join(trace))
                errormsg = discord.Embed(
                    title=f"🛑 An error occurred with the `{ctx.command.name}` command.", description=f"ℹ More Information")
                errormsg.add_field(name="🖥 Server", value=ctx.guild.name)
                errormsg.add_field(name="📑 Channel", value=f"#{ctx.channel}")
                errormsg.add_field(name="👥 User", value=ctx.message.author)
                errormsg.add_field(
                    name="🕓 Time", value=f"<t:{int(datetime.utcnow().timestamp())}:f>")
                #errormsg.add_field(name="📜 Log", value=trace)
                errormsg.set_image(url="https://http.cat/500.jpg")
                await self.bot.get_channel(config.home).send(content=f"{random.choice(quotes.errors)}", embed=errormsg)
                await ctx.send(content=f"{random.choice(quotes.errors)}", embed=errormsg)
                await self.bot.get_channel(config.home).send("📜 **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```")
                await ctx.send("📜 **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```")
            except discord.HTTPException:
                fuckeduperr = discord.Embed(
                    title="💥 An error occurred while displaying the previous error.")
                fuckeduperr.set_image(url="https://http.cat/500.jpg")
                trace = traceback.format_exception(
                    type(error), error, error.__traceback__)
                print("".join(trace))
                await ctx.send(embed=fuckeduperr, delete_after=5)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
    print("Errrror Handler Module has been loaded.")
