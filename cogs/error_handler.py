import traceback
import discord
import random
from datetime import datetime
import data.quotes as quotes
import data.config as config
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_message = {
            "CommandNotFound": "Invalid Command!",
            "MissingPermissions": "You dont have `{}` permission to run that command!",
            "MissingRequiredArgument": "You are missing required arguments: `{}`, Please refer to the help menu for more information.",
            "BadArgument": "You have given an invalid value, please refer to the help menu for more information.",
            "CommandOnCooldown": "That command is on cooldown. Please try again after `{}` seconds.",
            "BotMissingPermissions": "I don't have required permission `{}` to complete that command.",
            "NotOwner": "You are not my owner!",
            "DisabledCommand": "This command are disabled.",
            "Forbidden": "I'm not allowed to do that!",
            "NotFound": "Can't find the target!.",
            "ConversionError": "Lookup error, target `{}` not found!",
            "ArgumentParsingError": "An Error occured during the parsing of user's argument!",
            "MaxConcurrencyReached": "This command is currently rate-limited! You can use it only `{}` time(s) at once",
            "NoPrivateMessage": "The command `{}` cannot be used in DMs!",
            "NSFWChannelRequired": "You can only use this command on channels that are marked as NSFW.",
            "CheckFailure": "Command Check Failure, You are not authorized to use this command!"
        }

    # Main Exception
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        async def send_embed(name, code, *args):
            message = self.error_message[name]
            if args:
                message = message.format(*args)
            err = discord.Embed(description=f"**:warning: {message}**", timestamp=datetime.utcnow(), color=0xFF0000)
            if code:
                err.set_image(url=f"https://http.cat/{code}.jpg")
            await ctx.send(content=f"{random.choice(quotes.errors)}", embed=err, delete_after=15)
            
        
        if isinstance(error, commands.errors.CommandNotFound):
            await send_embed("CommandNotFound", 404)

        elif isinstance(error, commands.errors.MissingPermissions):
            await send_embed("MissingPermissions", 403, error.missing_perms)

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await send_embed("MissingRequiredArgument", 410 ,error.param)

        elif isinstance(error, commands.errors.BadArgument):
            await send_embed("BadArgument", 400)

        elif isinstance(error, commands.CommandOnCooldown):
            await send_embed("CommandOnCooldown", 429, int(error.retry_after))

        elif isinstance(error, commands.errors.BotMissingPermissions):
            await send_embed("BotMissingPermissions", 423, error.missing_perms)

        elif isinstance(error, commands.errors.TooManyArguments):
            await send_embed("TooManyArguments", 413)

        elif isinstance(error, commands.errors.DisabledCommand):
            await send_embed("DisabledCommand", 503)

        elif isinstance(error, discord.Forbidden):
            await send_embed("Forbidden", 403)

        elif isinstance(error, commands.errors.NotOwner):
            await send_embed("NotOwner", 401)

        elif isinstance(error, discord.NotFound):
            await send_embed("NotFound", 404)

        elif isinstance(error, commands.errors.ConversionError):
            await send_embed("ConversionError", 404, error.converter)

        elif isinstance(error, commands.errors.ArgumentParsingError):
            await send_embed("ArgumentParsingError", 417)

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            await send_embed("MaxConcurrencyReached", 420, error.number)

        elif isinstance(error, commands.NoPrivateMessage):
            await send_embed("NoPrivateMessage", 423, ctx.command.name)

        elif isinstance(error, commands.errors.NSFWChannelRequired):
            await send_embed("NSFWChannelRequired", 423)

        elif isinstance(error, commands.errors.CheckFailure):
            await send_embed("CheckFailure", 401)

        else:
            try:
                print(f"Ignoring exception in command {ctx.command.name}")
                trace = traceback.format_exception(type(error), error, error.__traceback__)
                full_traceback = "".join(trace)
                print(full_traceback)
                
                errormsg = discord.Embed(title=f"🛑 An error occurred with the `{ctx.command.name}` command.", description=f"ℹ More Information", color=0xFF0000)
                errormsg.add_field(name="🖥 Server", value=ctx.guild.name)
                errormsg.add_field(name="📑 Channel", value=f"#{ctx.channel}")
                errormsg.add_field(name="👥 User", value=ctx.message.author)
                errormsg.add_field(name="🕓 Time", value=f"<t:{int(datetime.utcnow().timestamp())}:F>")
                errormsg.set_image(url="https://http.cat/500.jpg")
                await ctx.send(content=f"{random.choice(quotes.errors)}", embed=errormsg)
                await ctx.send("📜 **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```")
                
                # This is for personal logging of the error message for further debugging
                await self.bot.get_channel(config.home).send(content=f"{random.choice(quotes.errors)}", embed=errormsg) 
                await self.bot.get_channel(config.home).send("📜 **__Full Traceback__**:\n```py\n" + "".join(trace) + "\n```")
                
            except discord.HTTPException:
                trace = traceback.format_exception(type(error), error, error.__traceback__)
                full = "".join(trace)
                print(full)
                
                fuckeduperr = discord.Embed(title="💥 An error occurred while displaying the previous error.")
                fuckeduperr.set_image(url="https://assets.hongkiat.com/uploads/funny_error_messages/operation-completed-succesfully-error-funny-error-messages.jpg")
                await ctx.send(embed=fuckeduperr, delete_after=5)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
    print("Errrror Handler Module has been loaded.")
