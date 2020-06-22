import logging

logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
import asyncio
import youtube_dl
import discord
import libneko
from discord.ext import commands
from .core.ytpy.ytpy.youtube import YoutubeService
from random import shuffle, random

# if not discord.opus.is_loaded():
#    discord.opus.load_opus('libopus.so')

ys = YoutubeService()

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -nostats -loglevel 0",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5, player=None, requester=None, video=None):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")
        self.duration = self.parse_duration(int(data.get("duration")))
        self.thumbnail = data.get("thumbnail")

        """Attributes.

        player: downloaded instance data to play the song.
        requester: user that requested the song.
        video: youtube video details.
        """

        self.player = player
        self.requester = requester
        self.video = video

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        # gonna change this later
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f"{days}d")
        if hours > 0:
            duration.append(f"{hours}h")
        if minutes > 0:
            duration.append(f"{minutes}m")
        if seconds > 0:
            duration.append(f"{seconds}s")

        return " : ".join(duration)

        self.player = player
        self.requester = requester
        self.video = video

    def create_embed(self):
        """Embed for now_playing command."""

        embed = libneko.embeds.Embed(
            title=":musical_note: Now Playing :musical_note:",
            colour=discord.Colour(value=11735575).orange(),
        )
        embed.add_field(
            name="Song", value="**{}**".format(self.title), inline=False
        )
        embed.add_field(name="Requester", value=str(self.requester.name), inline=True)
        embed.add_field(name="Duration", value=str(self.player.duration), inline=True)
        if not self.video is None:
            embed.set_thumbnail(url=self.video.thumbnails["high"]["url"])
        else:
            embed.set_thumbnail(url=self.player.thumbnail)
        return embed


class GuildVoiceState:
    """Guild voice channel state."""

    def __init__(self, client):
        """Represents every guild state.

        Every guild have their own: client, now_playing song, voice client,
        song queue, volume, search result, channel, skip votes, repeat status.
        """

        self.client = client
        self.current = None  # current voice_entry
        self.voice_client = None
        self.queue = []  # voice entries
        self.volume = 0.05
        self.search_result = None
        self.channel = None
        self.skip_votes = set()
        self.repeat = False
        self.waiting = None

    def get_embedded_np(self):
        """Get embbeded 'now playing song'"""

        embed = self.current.create_embed()
        embed.add_field(name="Volume", value=str(self.volume * 100), inline=True)
        return embed

    def get_embedded_queue(self):
        """Get embedded current queue state"""

        if self.channel is None:
            embed = libneko.embeds.Embed(
                title=":x: | Queue is empty.".format(),
                description="Prefix: do. | max_search_limit: 7",
                colour=discord.Colour(value=11735575).orange(),
            )
            return embed

        embed = libneko.embeds.Embed(
            title="{}'s voice state".format(self.channel.guild.name),
            description="Prefix: do. | max_search_limit: 7",
            colour=discord.Colour(value=11735575).orange(),
        )

        # Queue state info field
        if self.queue == []:
            fmt_queue = "empty"
        else:
            fmt_queue = "".join(
                [
                    "**{}. {} [{}]**\nRequested by **{}**\n".format(
                        i + 1, entry.video.title, entry.video.duration, entry.requester
                    )
                    for i, entry in enumerate(self.queue)
                ]
            )
        embed.add_field(name=":notes: | Queue", value=fmt_queue, inline=False)

        ## Repeat status info field
        if self.repeat:
            val_repeat = "On"
        else:
            val_repeat = "Off"
        embed.add_field(
            name=":repeat: | Repeat", value="**{}**".format(val_repeat), inline=True
        )

        ## Volumes info field
        if self.volume > 0.5:
            fmt_volume = ":loud_sound: | Volume"
        elif self.volume == 0.0 or self.volume == 0:
            fmt_volume = ":speaker: | Volume"
        else:
            fmt_volume = ":sound: | Volume"
        embed.add_field(
            name=fmt_volume, value="**{}** %".format(self.volume * 100), inline=True
        )

        # Now playing info field
        if self.current != None:
            fmt_np = "**{}**\nRequested by **{}**".format(
                self.current.video.title, self.current.requester
            )
        else:
            fmt_np = "None"
        embed.add_field(name=":musical_note: | Now playing", value=fmt_np, inline=False)

        embed.set_thumbnail(url=self.current.player.thumbnail)
        embed.set_footer(
            text="{} can skip current song | {}/3 skip votes.".format(
                self.current.requester, str(len(self.skip_votes))
            )
            # icon_url=self.client.get_user(self.client.id).avatar_url
        )
        return embed

    def next(self):
        """Trigger after client done playing current song.
        Client get next song to play or if there is no song on queue, client left voice channel.

        State1:
        if theres no any other user (not bot) in voice channel, client leave voice channel.

        State2:
        if queue is empty or theres no next song to play, client leave voice channel.

        State3:
        else, play next song.
        """

        if self.channel is None:
            return

        # check if theres any hooman in voice channel.
        found = False
        for member in self.voice_client.channel.members:
            # found hooman.
            if not member.bot:
                found = True
                break
        # if hooman not found.
        if not found:
            self.skip_votes.clear()
            self.client.loop.create_task(self.done_playing())
            return

        if self.repeat:
            self.queue.append(self.current)

        self.skip_votes.clear()

        if self.queue != []:
            next_entry = self.queue.pop(0)
            future = asyncio.run_coroutine_threadsafe(
                self.get_player(url=next_entry.video.url), self.client.loop
            )
            next_entry.player = future.result()
            self.voice_client.play(
                next_entry.player,
                after=lambda e: print("Player error: %s" % e) if e else self.next(),
            )
            self.voice_client.source.volume = self.volume
            self.current = next_entry
            self.client.loop.create_task(self.notify_np())
        else:  # when theres no song to play.. disconnect from voice channel
            self.client.loop.create_task(self.done_playing())

    async def get_player(self, url):
        """Get player from given url."""

        player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
        return player

    async def notify_np(self):
        """Notify channel about next song"""

        embed = self.get_embedded_np()
        await self.channel.send(embed=embed)

    async def done_playing(self):
        """Trigger when done playing.
        Client immediately left voice channel after done playing song.
        """

        await self.voice_client.disconnect()
        embed = libneko.embeds.Embed(
            title="Done playing music.", colour=discord.Colour(value=11735575).orange()
        )
        await self.channel.send(embed=embed, delete_after=15)

        self.current = None
        self.queue = []

    async def await_for_member(self):
        """Awaiting for any member to join voice channel."""

        await asyncio.sleep(10)  # 300
        # if theres no member joins after 5 minutes awaiting
        await self.channel.send(
            ":x: | Left voice channel after 5 minutes afk.", delete_after=15
        )
        self.channel = None
        self.current = None
        self.queue = []
        await self.voice_client.disconnect()

    def shuffle_queue(self):
        """Shuffles current queue."""

        if self.queue != []:
            shuffle(self.queue)

    def create_embed(self):
        """Embed for now_playing command."""

        embed = libneko.embeds.Embed(
            title=":musical_note: Now Playing :musical_note:",
            colour=discord.Colour(value=11735575).orange(),
        )
        embed.add_field(
            name="Song", value="**{}**".format(self.player.title), inline=False
        )
        embed.add_field(name="Requester", value=str(self.requester.name), inline=True)
        embed.add_field(name="Duration", value=str(self.player.duration), inline=True)
        if not self.video is None:
            embed.set_thumbnail(url=self.video.thumbnails["high"]["url"])
        else:
            embed.set_thumbnail(url=self.player.thumbnail)
        return embed


class VoiceEntry(GuildVoiceState):
    """Entities represents a requested song."""

    def __init__(self, player=None, requester=None, video=None):
        """Attributes.

        player: downloaded instance data to play the song.
        requester: user that requested the song.
        video: youtube video details.
        """

        self.player = player
        self.requester = requester
        self.video = video

    def create_embed(self):
        """Embed for now_playing command."""

        embed = libneko.embeds.Embed(
            title=":musical_note: Now Playing :musical_note:",
            colour=discord.Colour(value=11735575).orange(),
        )
        embed.add_field(
            name="Song", value="**{}**".format(self.player.title), inline=False
        )
        embed.add_field(name="Requester", value=str(self.requester.name), inline=True)
        embed.add_field(name="Duration", value=str(self.player.duration), inline=True)
        if not self.video is None:
            embed.set_thumbnail(url=self.video.thumbnails["high"]["url"])
        else:
            embed.set_thumbnail(url=self.player.thumbnail)
        return embed


class AsyncVoiceState:
    """Guild voice channel state that implements asynchronous loop for the audio player task."""

    def __init__(self, client):
        self.client = client
        self.voice_client = None
        self.volume = 0.75
        self.songs = AsyncSongQueue()
        self.asyncio_event = asyncio.Event()
        self.audio_player = client.loop.create_task(self.audio_player_task())

    async def audio_player_task(self):
        while True:
            self.asyncio_event.clear()
            video = await self.songs.get()
            player = await YTDLSource.from_url(video.url, stream=True)
            player.source.volume = self.volume
            self.voice_client.play(
                player, loop=self.client.loop, after=self.play_next_song
            )
            await self.asyncio_event.wait()

    def play_next_song(self, error=None):
        fut = asyncio.run_coroutine_threadsafe(
            self.asyncio_event.set(), self.client.loop
        )
        try:
            fut.result()
        except:
            print(error + " error")
            pass


class AsyncSongQueue(asyncio.Queue):
    def shuffle(self):
        random.shuffle(self._queue)


class Music(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.guild_states = {}

    def get_guild_state(self, guild_id):
        """Gets Guild's Voice State"""

        if not guild_id in self.guild_states:
            self.guild_states[guild_id] = GuildVoiceState(client=self.client)
        return self.guild_states[guild_id]

    async def on_voice_state_update(self, member, before, after):
         """Listener for when guild member updates their voice state.
         For memory efficiency.
         State 1:
         If member leave voice channel and then client is the only 1 at voice channel
         Then pause, countdown to leave voice channel if theres no one comin to the voice channel.

         State 2:
         Else if someone join before countdown finished
         Then resumes.
         """

         if member.bot:
             return

         state = self.get_guild_state(member.guild.id)
         if state.current is None or state.channel is None:
             return

         # theres no one else except client in voice channel.
         if len(state.voice_client.channel.members) <= 1:
             if state.voice_client.is_playing():
                 state.voice_client.pause()
                 await state.channel.send(':pause_button: | Awaiting for any member to join.')
                 state.waiting = asyncio.ensure_future(state.await_for_member())
         else:
             # if someone joins and client at awaiting state.
             if not state.voice_client.is_playing():
                 state.voice_client.resume()
                 await state.channel.send(':arrow_forward: | Continue playing song.')
                 state.waiting.cancel()
                 state.waiting = None

    async def play(self, ctx, video=None):
        """Plays song from given video"""

        if ctx.voice_client is None:
            ctx.voice_client.connect()

        state = self.get_guild_state(ctx.guild.id)
        if ctx.voice_client.is_playing() or state.current is not None:
            entry = VoiceEntry(player=None, requester=ctx.message.author, video=video)
            state.queue.append(entry)
            await ctx.send("Enqueued " + video.title)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(
                video.url, loop=self.client.loop, stream=True
            )
            ctx.voice_client.play(
                player,
                after=lambda e: print("Player error: %s" % e) if e else state.next(),
            )
            ctx.voice_client.source.volume = state.volume

        entry = VoiceEntry(player=player, requester=ctx.message.author, video=video)
        state.current = entry
        state.voice_client = ctx.voice_client
        state.channel = ctx.message.channel

        await ctx.send(embed=state.get_embedded_np())

    async def handle_url(self, ctx, url):
        """Handle input url, play from given url"""

        search_result = await self.client.loop.run_in_executor(
            None, lambda: ys.search(url)
        )
        try:
            search_result[0]
        except:
            await ctx.send(
                ":x: | Cannot extract data from given url, make sure it is a valid url."
            )
            return
        entry = VoiceEntry(
            player=None, requester=ctx.message.author, video=search_result[0]
        )

        state = self.get_guild_state(ctx.guild.id)
        if ctx.voice_client.is_playing() or state.current is not None:
            state.queue.append(entry)
            await ctx.send("Enqueued " + entry.video.title)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            ctx.voice_client.play(
                player,
                after=lambda e: print("Player error: %s" % e) if e else state.next(),
            )
            ctx.voice_client.source.volume = state.volume
            entry.player = player

        state.voice_client = ctx.voice_client
        state.current = entry
        state.channel = ctx.message.channel

        await ctx.send(embed=state.get_embedded_np())
        return

    @commands.command(name="search", aliases=["srch", "play"])
    async def search_(self, ctx, *args):
        """Search song by keyword and do start song selection"""

        # get keyword from args
        keyword = "".join([word + " " for word in args])

        # check if inpuy keyword is url
        if "www" in keyword or "youtu" in keyword or "http" in keyword:
            # handle url
            await self.handle_url(ctx, keyword)
            return

        # search video by keyword
        search_result = await self.client.loop.run_in_executor(
            None, lambda: ys.search(keyword)
        )
        # build embed
        embed = libneko.embeds.Embed(
            title="Song Selection | Reply the song number to continue",
            description="prefix: n> | search_limit: 7",
            color=discord.Colour(value=11735575).orange(),
        )

        # Converts search_result into a string
        song_list = "".join(
            [
                "{}. **[{}]({})**\n".format(i + 1, video.title, video.url)
                for i, video in enumerate(search_result)
            ]
        )

        # fill embed
        embed.add_field(
            name="search result for " + keyword, value=song_list, inline=False
        )
        embed.set_thumbnail(url=search_result[0].thumbnails["high"]["url"])
        embed.set_footer(text="Song selection | Type the entry number to continue")
        embedded_list = await ctx.send(embed=embed)

        # wait for author response
        request_channel = ctx.message.channel
        request_author = ctx.author

        def check(m):
            try:  # '/^*[0-9][0-9 ]*$/'
                picked_entry_number = int(m.content)
                return m.channel == request_channel and m.author == request_author
            except:
                return False

        try:
            msg = await self.client.wait_for("message", check=check, timeout=10.0)
        except:
            # TIMEOUT ERROR EXCEPTION
            await embedded_list.delete()
            return
        # await request_channel.send('picked_entry_number: {}'.format(msg.content))
        await self.play(ctx=ctx, video=search_result[int(msg.content) - 1])

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        # if already connected to voice channel, then move
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        # if not connected yet, then connect
        await channel.connect()

    @commands.command(name="localplay",aliases=["lp"])
    async def play_(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        sfile = f"audio/{query}"

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(sfile))
        ctx.voice_client.play(
            source, after=lambda e: print("Player error: %s" % e) if e else None
        )

    @commands.command(name="playlist", aliases=["pl", "play_list"])
    async def play_list(self, ctx, *, url):
        """Handles playlist input"""
        return

    @commands.command()
    async def ytplay(self, ctx, *, url):
        """(almost anything youtube_dl supports)"""
        state = self.get_guild_state(ctx.guild.id)
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop)
            ctx.voice_client.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )
        state.voice_client = ctx.voice_client
        state.current = player
        await ctx.send("Now playing: {}".format(player.title))

    @commands.command(aliases=["str"])
    async def stream(self, ctx, *, url):
        """Streams from a url (doesn't predownload)"""

        state = self.get_guild_state(ctx.guild.id)
        if ctx.voice_client.is_playing():
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            video = ys.search(url)[0]
            entry = VoiceEntry(player=player, requester=ctx.message.author, video=video)
            state.queue.append(entry)
            await ctx.send("Enqueued " + player.title)
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )

        state.voice_client = ctx.voice_client
        state.current = player
        await ctx.send("Now playing: {}".format(player.title))

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        # set certains guild volume
        state = self.get_guild_state(ctx.guild.id)
        state.volume = float(volume / 100.0)

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = state.volume
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        self.guild_states[ctx.guild.id].channel = None
        await ctx.voice_client.disconnect()
        del self.guild_states[ctx.guild.id]

    @commands.command()
    async def summon(self, ctx):
        """Force the bot to join author's voice channel
        Ensured voice before invoke summon.
        """

        return

    @commands.command(name="np", aliases=["now_play", "nowplay", "now_playing"])
    async def now_playing_(self, ctx):
        """Gets current playing song information"""

        state = self.get_guild_state(ctx.guild.id)
        if state.current is None:
            await ctx.send(":x: | Not playing anything.")
            return
        embed = state.get_embedded_np()
        np = "Now Playing {}".format(state.current.title)
        await ctx.send(embed=embed)

    @commands.command(name="skip")
    async def skip_(self, ctx):
        """Vote to skip a song.
        Requester can automatically skip.
        3 skip votes are needed to skip the song.
        """

        # if not connected to voice channel or voice client is not playing any song
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("Not playing any music.")
            return

        state = self.get_guild_state(ctx.guild.id)
        if state.current.requester == ctx.message.author:
            # do skip song
            state.voice_client.stop()
            await ctx.message.add_reaction("⏭")
            return
        elif ctx.author.id not in state.skip_votes:
            # increment voters
            state.skip_votes.add(ctx.author.id)
            total_votes = len(state.skip_votes)
            # check voters
            if total_votes >= 3:
                await ctx.message.add_reaction("⏭")
                state.voice_client.stop()
            else:
                await ctx.send("⏭ | Current skip votes **{}/3**".format(total_votes))

    @commands.command(name="pause")
    async def pause_(self, ctx):
        """Pause current playing song"""

        state = self.get_guild_state(ctx.guild.id)
        if state.voice_client is None or not state.voice_client.is_playing():
            await ctx.send(":x: | Not playing any song.")
            return
        await ctx.message.add_reaction("\U000023F8")
        state.voice_client.pause()

    @commands.command(name="resume")
    async def resume_(self, ctx):
        """Resumes paused song"""

        state = self.get_guild_state(ctx.guild.id)
        # check if theres any paused song.
        if state.voice_client is None or state.voice_client.is_playing():
            await ctx.send(":x: | Nothing to resume.")
        # check if theres any song to resume.
        if not state.current is None:
            await ctx.message.add_reaction("\U000025B6")
            state.voice_client.resume()

    @commands.command(name="queue", aliases=["q"])
    async def queue_(self, ctx):
        """Shows current queue state"""

        state = self.get_guild_state(ctx.guild.id)
        await ctx.send(embed=state.get_embedded_queue())

    @commands.command(name="repeat", aliases=["loop"])
    async def repeat_(self, ctx):
        """Repeats song after done playing or add to queue"""

        state = self.get_guild_state(ctx.guild.id)
        if state.repeat:
            state.repeat = False
        else:
            state.repeat = True
        await ctx.message.add_reaction("🔁")

    @commands.command(name="shuffle", aliases=["randq", "random_queue"])
    async def shuffle_(self, ctx):
        """Shuffles guild states song queue"""

        state = self.get_guild_state(ctx.guild.id)
        await self.client.loop.run_in_executor(None, lambda: state.shuffle_queue())
        await ctx.send(embed=state.get_embedded_queue())

    @play_.before_invoke
    @ytplay.before_invoke
    @stream.before_invoke
    @search_.before_invoke
    @repeat_.before_invoke
    @resume_.before_invoke
    @pause_.before_invoke
    @queue_.before_invoke
    @stop.before_invoke
    @skip_.before_invoke
    @summon.before_invoke
    @shuffle_.before_invoke
    async def ensure_voice(self, ctx):
        """Do this before invoke commands"""

        self.get_guild_state(ctx.guild.id)
        # check author voice state
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")


def setup(bot):
    bot.add_cog(Music(bot))
    print("Music Module has been loaded.")