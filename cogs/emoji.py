"""
MIT License

Copyright (c) 2017 XLR

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

import io
import re

import discord
import requests
from discord.ext import commands
from libneko import pag

"""Tools relating to custom emoji manipulation and viewing."""
static_re = re.compile(r"<:([^:]+):(\d+)>")
animated_re = re.compile(r"<a:([^:]+):(\d+)>")


class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def find_emoji(self, msg):
        msg = re.sub("<a?:(.+):([0-9]+)>", "\\2", msg)
        color_modifiers = [
            "1f3fb",
            "1f3fc",
            "1f3fd",
            "1f44c",
            "1f3fe",
            "1f3ff",
        ]  # These color modifiers aren't in Twemoji

        name = None

        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in emoji.name.lower():
                    name = emoji.name + (".gif" if emoji.animated else ".png")
                    url = emoji.url
                    id = emoji.id
                    guild_name = guild.name
                if msg.strip() in (str(emoji.id), emoji.name):
                    name = emoji.name + (".gif" if emoji.animated else ".png")
                    url = emoji.url
                    return name, url, emoji.id, guild.name
        if name:
            return name, url, id, guild_name

        # Here we check for a stock emoji before returning a failure
        codepoint_regex = re.compile("([\d#])?\\\\[xuU]0*([a-f\d]*)")
        unicode_raw = msg.encode("unicode-escape").decode("ascii")
        codepoints = codepoint_regex.findall(unicode_raw)
        if codepoints == []:
            return "", "", "", ""

        if len(codepoints) > 1 and codepoints[1][1] in color_modifiers:
            codepoints.pop(1)

        if codepoints[0][0] == "#":
            emoji_code = "23-20e3"
        elif codepoints[0][0] == "":
            codepoints = [x[1] for x in codepoints]
            emoji_code = "-".join(codepoints)
        else:
            emoji_code = "3{}-{}".format(codepoints[0][0], codepoints[0][1])
        url = "https://raw.githubusercontent.com/astronautlevel2/twemoji/gh-pages/128x128/{}.png".format(
            emoji_code
        )
        name = "emoji.png"
        return name, url, "N/A", "Official"

    @commands.group(pass_context=True, aliases=["emote"], invoke_without_command=True)
    async def emoji(self, ctx, *, msg):
        """
        View, copy, add or remove emoji.
        Usage:
        1) [p]emoji <emoji> - View a large image of a given emoji. Use [p]emoji s for additional info.
        2) [p]emoji copy <emoji> - Copy a custom emoji on another server and add it to the current server if you have the permissions.
        3) [p]emoji add <url> - Add a new emoji to the current server if you have the permissions.
        4) [p]emoji remove <emoji> - Remove an emoji from the current server if you have the permissions
        """
        await ctx.message.delete()
        emojis = msg.split()
        if msg.startswith("s "):
            emojis = emojis[1:]
            get_guild = True
        else:
            get_guild = False

        if len(emojis) > 5:
            return await ctx.send("Maximum of 5 emojis at a time.")

        images = []
        for emoji in emojis:
            name, url, id, guild = self.find_emoji(emoji)
            if url == "":
                await ctx.send("Could not find {}. Skipping.".format(emoji))
                continue
            response = requests.get(url, stream=True)
            if response.status_code == 404:
                await ctx.send(
                    "Emoji {} not available. Open an issue on <https://github.com/astronautlevel2/twemoji> with the name of the missing emoji".format(
                        emoji
                    )
                )
                continue

            img = io.BytesIO()
            for block in response.iter_content(1024):
                if not block:
                    break
                img.write(block)
            img.seek(0)
            images.append((guild, str(id), url, discord.File(img, name)))

        for (guild, id, url, file) in images:
            if ctx.channel.permissions_for(ctx.author).attach_files:
                if get_guild:
                    await ctx.send(
                        content="**ID:** {}\n**Server:** {}".format(id, guild),
                        file=file,
                    )
                else:
                    await ctx.send(file=file)
            else:
                if get_guild:
                    await ctx.send(
                        "**ID:** {}\n**Server:** {}\n**URL: {}**".format(id, guild, url)
                    )
                else:
                    await ctx.send(url)
            file.close()

    @emoji.command()
    @commands.has_permissions(manage_emojis=True)
    async def copy(self, ctx, *, msg):
        await ctx.message.delete()
        msg = re.sub("<:(.+):([0-9]+)>", "\\2", msg)

        match = None
        exact_match = False
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in str(emoji):
                    match = emoji
                if msg.strip() in (str(emoji.id), emoji.name):
                    match = emoji
                    exact_match = True
                    break
            if exact_match:
                break

        if not match:
            return await ctx.send("Could not find emoji.")

        response = requests.get(match.url)
        emoji = await ctx.guild.create_custom_emoji(
            name=match.name, image=response.content
        )
        await ctx.send(
            "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!".format(
                emoji, "a" if emoji.animated else ""
            )
        )

    @emoji.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, name, url):
        await ctx.message.delete()
        try:
            response = requests.get(url)
        except (
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidURL,
            requests.exceptions.InvalidSchema,
            requests.exceptions.ConnectionError,
        ):
            return await ctx.send("The URL you have provided is invalid.")
        if response.status_code == 404:
            return await ctx.send("The URL you have provided leads to a 404.")
        try:
            emoji = await ctx.guild.create_custom_emoji(
                name=name, image=response.content
            )
        except discord.InvalidArgument:
            return await ctx.send(
                "Invalid image type. Only PNG, JPEG and GIF are supported."
            )
        await ctx.send(
            "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!".format(
                emoji, "a" if emoji.animated else ""
            )
        )

    @emoji.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove(self, ctx, name):
        await ctx.message.delete()
        emotes = [x for x in ctx.guild.emojis if x.name == name]
        emote_length = len(emotes)
        if not emotes:
            return await ctx.send(
                "No emotes with that name could be found on this server."
            )
        for emote in emotes:
            await emote.delete()
        if emote_length == 1:
            await ctx.send("Successfully removed the {} emoji!".format(name))
        else:
            await ctx.send(
                "Successfully removed {} emoji with the name {}.".format(
                    emote_length, name
                )
            )

    @staticmethod
    async def find_emojis(channel, limit):
        animated, static, message = [], [], None
        async for message in channel.history(limit=limit):
            animated.extend(animated_re.findall(message.content))
            static.extend(static_re.findall(message.content))
            if animated or static:
                break
        return animated, static, message

    @commands.command(aliases=["loot", "swag", "pinch", "begal"], hidden=False)
    async def steal(self, ctx, *, message=None):
        """
        Takes a message ID for the current channel, or if not, a string message containing
        the emojis you want to steal. If you don't specify anything, I look through the
        past 200 messages. Using `^` will have the same effect, and mostly exists for legacy
        and/or muscle memory with other commands.

        I get all custom emojis in the message and send them to your inbox with links; this
        way, you can download them or add them to your stamp collection or whatever the hell
        you do for fun.

        Teach those Nitro users no more big government. Break their hearts out. FINISH THEM.
        VIVA LA REVOLUTION!
        """
        if not message or message == "^":
            animated, static, message = await self.find_emojis(ctx.channel, 200)
        else:
            try:
                message = int(message)
                message = await ctx.channel.get_message(message)
            except ValueError:
                message = ctx.message
            finally:
                animated = animated_re.findall(message.content)
                static = static_re.findall(message.content)
        if not static and not animated or not message:
            return await ctx.send("No custom emojis could be found...", delete_after=10)
        paginator = pag.Paginator(enable_truncation=False)
        paginator.add_line(f"Emoji loot from {message.jump_url}")
        paginator.add_line()
        for name, id in static:
            paginator.add_line(f" ⚝ {name}: https://cdn.discordapp.com/emojis/{id}.png")
        for name, id in animated:
            paginator.add_line(
                f" ⚝ {name}: https://cdn.discordapp.com/emojis/{id}.gif <animated>"
            )
        async with ctx.typing():
            for page in paginator.pages:
                await ctx.author.send(page)
        tot = len(animated) + len(static)
        await ctx.send(
            f'Check your DMs. You looted {tot} emoji{"s" if tot - 1 else ""}!',
            delete_after=7.5,
        )
        try:
            await ctx.message.delete()
        except:
            pass

    @staticmethod
    def transform_mute(emojis):
        return [str(emoji) + " " for emoji in emojis]

    @staticmethod
    def transform_verbose(emojis):
        return [
            f"{emoji} = {emoji.name}\n"
            for emoji in sorted(emojis, key=lambda e: e.name.lower())
        ]

    @commands.command(aliases=["emojis", "emojilist"], hidden=False)
    async def emojilibrary(self, ctx, arg=None):
        """Shows all emojis I can see ever. Pass the --verbose/-v flag to see names."""
        if arg:
            transform = self.transform_verbose
        else:
            transform = self.transform_mute
        emojis = transform(ctx.bot.emojis)
        p = pag.StringNavigatorFactory()
        for emoji in emojis:
            p += emoji
        p.start(ctx)


def setup(bot):
    bot.add_cog(Emoji(bot))
    print("Emoji Module has been loaded.")
