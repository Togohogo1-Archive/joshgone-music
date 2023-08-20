# Source: https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py

import asyncio
import random
import typing
import traceback
import json
import queue
import threading
import os
import sys
import shlex
import re
import time
import datetime
import textwrap
import mutagen  # Alphabetize later
from collections import deque
from urllib.parse import urlparse

import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import BucketType

import yt_dlp as youtube_dl

import jgm.patched_player as patched_player
import soundit as s


class FilterData:
    def __init__(self):
        self.tempo = 1
        self.pitch = 1
        self.filter_name = "default"

    def to_ffmpeg_opts(self, filter_dict, local=False):
        # Passing in _FFMPEG_FILTER_DICT

        # Non-tempo filter
        ffmpeg_other_filters = filter_dict[self.filter_name]

        # Pitch and tempo
        ffmpeg_pitch = "" if self.pitch == 1 else f"pitch={self.pitch}"
        ffmpeg_tempo = "" if self.tempo == 1 else f"tempo={self.tempo}"
        ffmpeg_rubberband = "" \
            if ffmpeg_pitch == ffmpeg_tempo == "" \
            else f"rubberband={':'.join(filter(None, [ffmpeg_pitch, ffmpeg_tempo]))}" # Deal with empty string to avoid a ",e" case

        # Combining the 2
        ffmpeg_filter_opt = "" \
            if ffmpeg_other_filters == ffmpeg_rubberband == "" \
            else f"-filter_complex {','.join(filter(None, [ffmpeg_rubberband, ffmpeg_other_filters]))}" # Deal with empty string to avoid a ",e" case

        ret = {
            'options': '-vn',
            # Source: https://stackoverflow.com/questions/66070749/
            "before_options": f"{ffmpeg_filter_opt} {'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5' if not local else ''}",
        }
        return ret

    def copy_from(self, other):
        self.__dict__.update(other.__dict__)


class Audio:
    def __init__(self, ty, query):
        self.ty = ty
        self.query = query
        self.metadata_fields_stream = [
            "id",
            "title",
            "uploader",
            "duration",
            "url",  # The URL queried from the API (for seeking)
            "webpage_url",  # For display purposes (e.g. soundcloud generating an api audio link)
            "live_status",
            "webpage_url_domain",
            "duration_string"
        ]
        self.metadata_funcs_local = {
            "duration": lambda mut: mut.info.length,
            "contents": lambda mut: mut.info.pprint(),
            "url": lambda mut: mut.filename  # For consistency with stream ["url"] query for seeking
        }
        self.metadata = {}
        self.filter_data = FilterData()

        # TODO seek head things ...
        # Scaled frames (we don't know how long a frame is, just the number of frames)
        self.sframes = 0

    def filter_metadata(self, data):
        if self.ty == "stream":
            self.metadata = {field:data.get(field) for field in self.metadata_fields_stream}
        else:
            self.metadata = {k:v(data) for k, v in self.metadata_funcs_local.items()}

    # More readable in the code following
    def reset_playhead(self):
        self.sframes = 0


    def playhead_hashtags(self):
        duration = self.metadata.get("duration")

        if duration is None:
            return ""

        # We round down to be safe (no exceed 20 #s)
        duration = int(duration)
        secs_passed = scaled_frames_to_seconds(self.sframes, self.filter_data.tempo)
        duration_ratio = secs_passed/duration
        hashtags = int(20*duration_ratio)

        return "#"*min(20, hashtags)

    def generate_time_sig(self):
        duration = self.metadata.get("duration")
        secs_passed = scaled_frames_to_seconds(self.sframes, self.filter_data.tempo)
        timestamp = seconds_to_hhmmss(secs_passed)

        if duration is None:
            duration = 0

        return f"{timestamp}/{seconds_to_hhmmss(int(duration))}"


def match_hhmmss_type(pos):
    # Based off simplified version of https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
    # Match [[HH:]MM:]SS or integer seconds, brackets optional
    # First check regex match
    # Regex pattern slightly modified from: https://stackoverflow.com/a/8318367
    return re.match(r"^(?:(?:(\d?\d):)?([0-5]?\d):)?([0-5]?\d)$", pos)


def match_any_seconds(pos):
    # Returns false for negative numbers too
    # Sufficient to check if `pos` is a positive integer in string form
    return pos.isdigit()


def hhmmss_to_seconds(hhmmss):
    """
    Assumes already in valid [[HH:]MM:]SS regex format
    if len 1 -> ss
    if len 2 -> mm:ss
    if len 3 -> hh:mm:ss

    never hh:ss
    """
    hhmmss_list = hhmmss.split(":")
    hour_s = int(hhmmss_list[-3])*3600 if len(hhmmss_list) >= 3 else 0
    min_s = int(hhmmss_list[-2])*60 if len(hhmmss_list) >= 2 else 0
    return hour_s + min_s + int(hhmmss_list[-1])


def seconds_to_hhmmss(seconds):
    """
    returns to [[HH:]MM:]SS
    """
    min, sec = divmod(seconds, 60)
    hr, min = divmod(min, 60)  # Moves the bulk to hours
    return f"{int(hr):0>2}:{int(min):0>2}:{round(sec):0>2}"


def seconds_to_scaled_frames(seconds, tempo):
    # Doesn't allow integer values
    sframes = ((1000/20)*seconds) / tempo
    return round(sframes)


def scaled_frames_to_seconds(frames, tempo):
    # Allows non integer values
    return (frames*tempo) / (1000/20)


class Music(commands.Cog):
    # Options that are passed to youtube-dl
    _DEFAULT_YTDL_OPTS = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'playlistend': 1,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

    _FFMPEG_FILTER_DICT = {
        "bassboost": "bass=g=15",
        "default": "",
        "deepfry": "acrusher=level_in=8:level_out=18:bits=8:mode=log:aa=1",
    }

    def __init__(
        self,
        bot,
        *,
        ytdl_opts=_DEFAULT_YTDL_OPTS,
        filter_dict=_FFMPEG_FILTER_DICT
    ):
        self.bot = bot
        # Options are stores on the instance in case they need to be changed
        self.ytdl_opts = ytdl_opts
        self.filter_dict = filter_dict
        # Data is persistent between extension reloads
        if not hasattr(bot, "_music_data"):
            bot._music_data = {}
        if not hasattr(bot, "_music_advance_queue"):
            bot._music_advance_queue = asyncio.Queue()
        self.data = bot._music_data
        self.advance_queue = bot._music_advance_queue
        # Start the advancer's auto-restart task
        self.advance_task = None
        self.advancer.start()

    # Cancel just the advancer and the auto-restart tasks
    def cog_unload(self):
        self.advancer.cancel()

    # - Song players
    # Returns a source object and the title of the song

    # Finds a file using query. Title is query
    async def _play_local(self, ctx, query):
        # Move from before info["current"] line to here bc need to access the global filter and speed info
        info = self.get_info(ctx)
        current = info["current"]
        filter_data = info["filter_data"]
        # Cleaning up before playing (to prevent persistent history instance vars)
        current.reset_playhead()
        current.filter_data.copy_from(filter_data)  # Before playing current, override its filterdata
        mutagen_query = mutagen.File(query)
        current.filter_metadata(mutagen_query)
        source = discord.PCMVolumeTransformer(patched_player.FFmpegPCMAudio(current, **filter_data.to_ffmpeg_opts(self.filter_dict, local=True)))
        return source, query

    def uri_validator(self, x):
        # Validates a URL
        # https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False

    # Searches various sites using url. Title is data["title"] or url
    async def _play_stream(self, ctx, url):
        original_url = url

        if url[0] == "<" and url[-1] == ">":
            if self.uri_validator(url[1:-1]):
                url = url[1:-1]
        player, data = await self.player_from_url(ctx, url, stream=True)
        self.bot._datuh = data
        self.bot._datuh2 = data
        return player, data.get("title", original_url)

    # Returns the raw source (calling the function if possible)
    async def _play_raw(self, source):
        if callable(source):
            source = source()
        if not isinstance(source, discord.AudioSource):
            source = s.wrap_discord_source(s.chunked(source))
        return source, repr(source)

    # Auto-restart task for the advancer task
    @tasks.loop(seconds=15)
    async def advancer(self):
        if self.advance_task is not None and self.advance_task.done():
            try:
                exc = self.advance_task.exception()
            except asyncio.CancelledError:
                pass
            else:
                print("Exception occured in advancer task:")
                traceback.print_exception(None, exc, exc.__traceback__)
            self.advance_task = None
        if self.advance_task is None:
            self.advance_task = asyncio.create_task(self.handle_advances(), name="music_advancer")

    # Cancel the advancer task if the monitoring task is getting cancelled
    # (such as when the cog is getting unloaded)
    @advancer.after_loop
    async def on_advancer_cancel(self):
        if self.advancer.is_being_cancelled():
            if self.advance_task is not None:
                self.advance_task.cancel()
                self.advance_task = None

    # The advancer task loop
    async def handle_advances(self):
        while True:
            item = await self.advance_queue.get()
            asyncio.create_task(self.handle_advance(item))

    # The actual music advancing logic
    async def handle_advance(self, item):
        ctx, error = item
        info = self.get_info(ctx)
        channel = ctx.guild.get_channel(info["channel_id"])
        try:
            # If we are processing it right now...
            if info["processing"]:
                # Wait a bit and reschedule it again
                await asyncio.sleep(1)
                self.advance_queue.put_nowait(item)
                return
            info["processing"] = True
            # If there's an error, send it to the channel
            if error is not None:
                await channel.send(f"Player error: {error!r}")
            # If we aren't connected anymore, notify and leave
            if ctx.voice_client is None:
                await channel.send("Not connected to a voice channel anymore")
                await self.leave(ctx)
                return
            queue = info["queue"]
            # If we're looping, put the current song at the end of the queue
            if info["loop"] > 0 and info["current"] is not None:
                queue.append(info["current"])
            # Previous will not intefere cuz number can't be >0 and <0 at the same time
            if info["loop"] < 0 and info["current"] is not None:
                queue.appendleft(info["current"])

            # Before setting it to none, we add it to the history, provided it is not None itself
            if info["current"] is not None:
                info["history"].append(info["current"])
                info["songs_played"] += 1

            info["current"] = None

            if queue:
                # Get the next song
                current = queue.popleft()
                info["current"] = current
                # Get an audio source and play it
                after = lambda error, ctx=ctx: self.schedule(ctx, error)
                async with channel.typing():
                    source, title = await getattr(self, f"_play_{current.ty}")(ctx, current.query)
                    # Pausing just in case ctx.voice_client is still playing audio
                    # Moved this line after the await ... because that was a blocking operation
                    # Was there previously and that somehow allowed ;reschedule to sneak its way through
                    # Raising the Internal Error: ClientException('Already playing audio.')
                    ctx.voice_client.pause()
                    ctx.voice_client.play(source, after=after)
                await channel.send(f"Now playing: {title}")
            else:
                await channel.send(f"Queue empty")
        except Exception as e:
            await channel.send(f"Internal Error: {e!r}")
            info["waiting"] = False
            await self.skip(ctx)
            self.schedule(ctx)
        finally:
            info["waiting"] = False
            info["processing"] = False

    # Schedules advancement of the queue
    def schedule(self, ctx, error=None, *, force=False):
        info = self.get_info(ctx)
        if force or not info["waiting"]:
            self.advance_queue.put_nowait((ctx, error))
            info["waiting"] = True

    # Helper function to create the info for a guild
    def get_info(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in self.data:
            wrapped = self.data[guild_id] = {}
            wrapped["queue"] = deque()
            wrapped["history"] = deque(maxlen=100)
            wrapped["filter_data"] = FilterData()
            wrapped["songs_played"] = 0
            wrapped["current"] = None
            wrapped["waiting"] = False
            wrapped["loop"] = 0
            wrapped["processing"] = False
            wrapped["autoshuffle_task"] = None
            wrapped["sleep_timer_task"] = None
            wrapped["version"] = 3
        else:
            wrapped = self.data[guild_id]
        # Smth about for reloading
        if wrapped["version"] == 3:
            wrapped["channel_id"] = ctx.channel.id
            wrapped["version"] = 4
        return wrapped

    # Helper function to remove the info for a guild
    def pop_info(self, ctx):
        # Do some cleanup first, cancel any tasks in the thin wrapper
        data = self.get_info(ctx)

        if data["autoshuffle_task"] is not None:
            data["autoshuffle_task"].cancel()
        if data["sleep_timer_task"] is not None:
            _, _, task = data["sleep_timer_task"]  # More formal way than [-1]
            task.cancel()

        return self.data.pop(ctx.guild.id, None)

    # Creates an audio source from a url
    async def player_from_url(self, ctx, url, *, loop=None, stream=False):
        ytdl = youtube_dl.YoutubeDL(self.ytdl_opts)
        loop = loop or asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        # Generate ffmpeg_opts from the function
        info = self.get_info(ctx)
        current = info["current"]  # Also need to get current
        filter_data = info["filter_data"]
        # Cleaning up before playing (to prevent persistent history instance vars)
        current.reset_playhead()
        current.filter_data.copy_from(filter_data)  # Before playing current, override its filterdata
        current.filter_metadata(data)
        audio = patched_player.FFmpegPCMAudio(current, **filter_data.to_ffmpeg_opts(self.filter_dict))
        player = discord.PCMVolumeTransformer(audio)
        return player, data

    @commands.command(aliases=["nc"])
    async def nightcore(self, ctx):
        info = self.get_info(ctx)
        filter_data = info["filter_data"]
        filter_data.tempo = 1.2
        filter_data.pitch = 1.2
        await ctx.send("Applying nightcore (1.2x tempo and pitch) effect for next song")

    @commands.command(aliases=["dc"])
    async def daycore(self, ctx):
        info = self.get_info(ctx)
        filter_data = info["filter_data"]
        # A little bit less than 0.8333 (1/1.2) because I like more daycore
        filter_data.tempo = 0.8
        filter_data.pitch = 0.8
        await ctx.send("Applying daycore (0.8x tempo and pitch) effect for next song")

    @commands.command(aliases=["no"])
    async def normal(self, ctx):
        info = self.get_info(ctx)
        filter_data = info["filter_data"]
        filter_data.tempo = 1
        filter_data.pitch = 1
        filter_data.filter_name = "default"
        await ctx.send("Restoring default tempo, pitch, and filter for next song.")

    @commands.command(aliases=["f"])
    @commands.cooldown(1, 1, BucketType.user)
    async def apply_filter(self, ctx, filter_name):
        """Applies a filter to the next song
        """
        if filter_name not in self.filter_dict.keys():
            raise commands.CommandError(f"Filter '{filter_name}' not in list of available filters.")
        else:
            info = self.get_info(ctx)
            filter_data = info["filter_data"]
            filter_data.filter_name = filter_name
            await ctx.send(f"Applying filter '{filter_name}' to the next song.")

    @commands.command(aliases=["sp"])
    async def speed(self, ctx, factor: float = None):
        if not (0.25 <= factor <= 4):
            raise commands.CommandError(f"Speed factor = {factor}x outside of range from 0.25 to 4 inclusive.")

        info = self.get_info(ctx)
        filter_data = info["filter_data"]
        filter_data.tempo = factor
        await ctx.send(f"Setting speed factor = x{factor} for next song.")

    @commands.command(aliases=["pi"])
    async def pitch(self, ctx, factor: float = None):
        if not (0.25 <= factor <= 4):
            raise commands.CommandError(f"Pitch factor = {factor}x outside of range from 0.25 to 4 inclusive.")

        info = self.get_info(ctx)
        filter_data = info["filter_data"]
        filter_data.pitch = factor
        await ctx.send(f"Setting pitch factor = x{factor} for next song.")

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel

        Text output will be sent from the channel this command was run in. This
        command can be run multiple times safely.

        """
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        info = self.get_info(ctx)
        if info["channel_id"] != ctx.channel.id:
            info["channel_id"] = ctx.channel.id
            await ctx.send("Switching music output to this channel")

    @commands.command()
    @commands.is_owner()
    async def local(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        info = self.get_info(ctx)
        queue = info["queue"]
        history = info["history"]
        # Handling prev song
        if query == "prev":
            if not history:
                # Raise error no need for another case
                raise commands.CommandError("No previous song.")
            # History exists now
            previous = history[-1]
            if previous.ty != "local":
                raise commands.CommandError("Previous song not added locally. Use ;stream prev.")
            # Else
            query = previous.query
        elif query == "cur":
            current = info["current"]
            if current is None:
                raise commands.CommandError("No current song.")
            # current exists now
            if current.ty != "local":
                raise commands.CommandError("Current song was not added locally. Use ;stream cur.")
            # Else
            query = current.query
        audio = Audio(ty="local", query=query)
        queue.append(audio)
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Appended to queue: local {audio.query}")

    @commands.command()
    @commands.is_owner()
    async def local_prepend(self, ctx, *, query):
        # """Plays a file from the local filesystem"""
        info = self.get_info(ctx)
        queue = info["queue"]
        history = info["history"]
        # Handling prev song
        if query == "prev":
            if not history:
                # Raise error no need for another case
                raise commands.CommandError("No previous song.")
            # History exists now
            previous = history[-1]
            if previous.ty != "local":
                raise commands.CommandError("Previous song not added locally. Use ;stream_prepend prev.")
            # Else
            query = previous.query
        elif query == "cur":
            current = info["current"]
            if current is None:
                raise commands.CommandError("No current song.")
            # current exists now
            if current.ty != "local":
                raise commands.CommandError("Current song was not added locally. Use ;stream_prepend cur.")
            # Else
            query = current.query
        audio = Audio(ty="local", query=query)
        queue.appendleft(audio)
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Prepended to queue: local {audio.query}")

    @commands.command(aliases=["yt", "play", "p"])
    async def stream(self, ctx, *, url):
        """Plays from a url (almost anything yt-dlp supports)"""
        if len(url) > 100:
            raise ValueError("url too long (length over 100)")
        if not url.isprintable():
            raise ValueError(f"url not printable: {url!r}")
        info = self.get_info(ctx)
        queue = info["queue"]
        history = info["history"]
        # Handling prev song
        if url == "prev":
            if not history:
                # Raise error no need for another case
                raise commands.CommandError("No previous song.")
            # History exists now
            previous = history[-1]
            if previous.ty != "stream":
                raise commands.CommandError("Previous song added locally. Use ;local prev.")
            # Else
            url = previous.query
        elif url == "cur":
            current = info["current"]
            if current is None:
                raise commands.CommandError("No current song.")
            # current exists now
            if current.ty != "stream":
                raise commands.CommandError("Current song was added locally. Use ;local cur.")
            # Else
            url = current.query
        audio = Audio(ty="stream", query=url)
        queue.append(audio)
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Appended to queue: stream {audio.query}")

    @commands.command(aliases=["prepend", "pplay", "pp"])
    async def stream_prepend(self, ctx, *, url):
        # """Plays from a url (almost anything youtube_dl supports)"""
        if len(url) > 100:
            raise ValueError("url too long (length over 100)")
        if not url.isprintable():
            raise ValueError(f"url not printable: {url!r}")
        info = self.get_info(ctx)
        queue = info["queue"]
        history = info["history"]
        # Handling prev song
        if url == "prev":
            if not history:
                # Raise error no need for another case
                raise commands.CommandError("No previous song.")
            # History exists now
            previous = history[-1]
            if previous.ty != "stream":
                raise commands.CommandError("Previous song added locally. Use ;local_prepend prev.")
            # Else
            url = previous.query
        elif url == "cur":
            current = info["current"]
            if current is None:
                raise commands.CommandError("No current song.")
            # current exists now
            if current.ty != "stream":
                raise commands.CommandError("Current song was added locally. Use ;local cur.")
            # Else
            url = current.query
        audio = Audio(ty="stream", query=url)
        queue.appendleft(audio)
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Prepended to queue: stream {audio.query}")

    @commands.command()
    async def playlist_link(self, ctx, *, url):
        """Adds all songs in a playlist to the queue"""
        if len(url) > 100:
            raise ValueError("url too long (length over 100)")
        if not url.isprintable():
            raise ValueError(f"url not printable: {url!r}")
        bracketed = False
        if url[0] == "<" and url[-1] == ">":
            bracketed = True
            url = url[1:-1]
        info = self.get_info(ctx)
        queue = info["queue"]
        ytdl = youtube_dl.YoutubeDL(self.ytdl_opts | {
            'noplaylist': None,
            'playlistend': None,
            "extract_flat": True,
        })
        data = await asyncio.to_thread(ytdl.extract_info, url, download=False)
        if 'entries' not in data:
            raise ValueError("cannot find entries of playlist")
        entries = data['entries']
        for entry in entries:
            playlist_url = entry['url']
            if bracketed:
                playlist_url = f"<{playlist_url}>"
            audio = Audio(ty="stream", query=playlist_url)
            queue.append(audio)
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Added playlist to queue: {url}")

    @commands.command(name="batch_add")
    @commands.cooldown(rate=1, per=2, type=BucketType.user)
    async def _batch_add(self, ctx, *, urls):
        """Plays from multiple urls split by lines"""
        for url in urls.splitlines():
            await self.stream(ctx, url=url)
            await asyncio.sleep(0.1)

    def shuffle_helper(self, queue_ref):
        temp = []
        while queue_ref:
            temp.append(queue_ref.popleft())
        random.shuffle(temp)
        while temp:
            queue_ref.appendleft(temp.pop())

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def shuffle(self, ctx):
        """Shuffles the queue"""
        info = self.get_info(ctx)
        self.shuffle_helper(info["queue"])
        await ctx.send("Queue shuffled")

    async def autoshuffler(self, queue_ref):
        while True:
            self.shuffle_helper(queue_ref)
            await asyncio.sleep(5)

    @commands.command(aliases=["ashuffle"])
    @commands.cooldown(1, 1, BucketType.user)
    async def autoshuffle(self, ctx, to_ashuffle: typing.Optional[bool] = None):
        info = self.get_info(ctx)
        queue = info["queue"]

        if to_ashuffle is None:
            # None if no task, the acutal task if exists task
            await ctx.send(f"Autoshuffler is {'off' if info['autoshuffle_task'] is None else 'on'}.")
            return

        if to_ashuffle:
            # Overwriting if task already exist
            # Create a new one if task doesn't exist
            await ctx.send("Enabling queue autoshuffle.")
            task = asyncio.create_task(self.autoshuffler(queue))
            info["autoshuffle_task"] = task
            await task
        else:
            await ctx.send("Disabling queue autoshuffle.")
            # For safe measure, turn info["autoshuffle"] to None first
            task = info["autoshuffle_task"]

            # So doesn't raise AttributeError for NoneType
            if task is None:
                return

            info["autoshuffle_task"] = None
            task.cancel()

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def volume(self, ctx, volume: float = None):
        """Gets or changes the player's volume"""
        if volume is None:
            volume = ctx.voice_client.source.volume * 100
            if int(volume) == volume:
                volume = int(volume)
            await ctx.send(f"Volume set to {volume}%")
            return
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel")
        try:
            if int(volume) == volume:
                volume = int(volume)
        except (OverflowError, ValueError) as e:
            raise commands.CommandError(e)
        if not 0 <= volume <= 200:
            raise commands.CommandError("Volume must be in the range [0, 200].")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(aliases=["stop"])
    @commands.cooldown(1, 0.5, BucketType.user)
    async def pause(self, ctx):
        """Pauses playing"""
        ctx.voice_client.pause()

    @commands.command(aliases=["start"])
    @commands.cooldown(1, 0.5, BucketType.user)
    async def resume(self, ctx):
        """Resumes playing"""
        ctx.voice_client.resume()

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def leave(self, ctx):
        """Disconnects the bot from voice and clears the queue"""
        self.pop_info(ctx)
        if ctx.voice_client is None:
            return
        await ctx.voice_client.disconnect()

    @commands.command(aliases=["c"])
    @commands.cooldown(1, 0.5, BucketType.user)
    async def current(self, ctx):
        """Shows the current song"""
        query = None
        if ctx.voice_client is not None:
            info = self.get_info(ctx)
            current = info["current"]
            if current is not None and not info["waiting"]:
                query = current.query
        await ctx.send(f"Current: {query}")

    @commands.command(aliases=["q"])
    @commands.cooldown(1, 1, BucketType.user)
    async def queue(self, ctx):
        """Shows the songs on queue"""
        queue = ()
        length = 0
        loop_messages = {1: "loop all", 0: "no loop", -1: "loop one"}
        looping = None
        if ctx.voice_client is not None:
            info = self.get_info(ctx)
            queue = info["queue"]
            length = len(queue)
            looping = loop_messages[info["loop"]]
        if not queue:
            queue = (None,)
        paginator = commands.Paginator()
        # Looping default None, if it is then dont print the status to make it look nicer when the bot isn't joined in a VC
        paginator.add_line(f"Queue [{length}]{f' ({looping})' if looping is not None else ''}:")
        for i, song in enumerate(queue, start=1):
            if song is None:
                paginator.add_line("None")
            else:
                paginator.add_line(f"{i}: {song.query}")
        for page in paginator.pages:
            await ctx.send(page)

    @commands.command(aliases=["history", "hist"])
    async def playback_history(self, ctx, display_last: int = 5):
        info = self.get_info(ctx)
        history = info["history"]
        played = info["songs_played"]

        if not history:
            await ctx.send("No playback history")
            return

        paginator = commands.Paginator()

        # Cap it at the limit
        if display_last <= 0:
            raise commands.CommandError(f"Cannot display last {display_last} songs")

        paginator.add_line(f"Playback history{'' if min(display_last, history.maxlen) >= played else f' (showing last {min(display_last, history.maxlen)}/{played} played)'}:") #({ 15/{played} played total) (showing last {len(history)} played):")
        for i, song in enumerate(reversed(history), start=1):
            if i > display_last:
                break
            paginator.add_line(f"{i}: {song.query} {f'({song.ty})' if song.ty == 'local' else ''}")

        if display_last > history.maxlen:
            paginator.add_line(f"\n[WARNING] History size capped at {history.maxlen} items")

        for page in paginator.pages:
            await ctx.send(page)

    @commands.command(aliases=["hclear"])
    async def playback_history_clear(self, ctx):
        info = self.get_info(ctx)
        info["history"].clear()
        info["songs_played"] = 0

        await ctx.send("Successfully cleared payback history.")

    def normalize_index(self, ctx, position, length):
        index = position
        if index > 0:
            index -= 1
        if index < 0:
            index += length
        if not 0 <= index < length or position == 0:
            raise ValueError(position)
        return index

    @commands.command(aliases=["rm"])
    @commands.cooldown(1, 1, BucketType.user)
    async def remove(self, ctx, position: int):
        """Removes a song on queue"""
        info = self.get_info(ctx)
        queue = info["queue"]
        try:
            index = self.normalize_index(ctx, position, len(queue))
        except ValueError:
            raise commands.CommandError(f"Index out of range [{position}]")
        queue.rotate(-index)
        song = queue.popleft()
        queue.rotate(index)
        await ctx.send(f"Removed song [{position}]: {song.query}")

    @commands.command(aliases=["mv"])
    @commands.cooldown(1, 1, BucketType.user)
    async def move(self, ctx, origin: int, target: int):
        """Moves a song on queue"""
        info = self.get_info(ctx)
        queue = info["queue"]
        try:
            origin_index = self.normalize_index(ctx, origin, len(queue))
        except ValueError:
            raise commands.CommandError(f"Origin index out of range [{origin}]")
        try:
            target_index = self.normalize_index(ctx, target, len(queue))
        except ValueError:
            raise commands.CommandError(f"Target index out of range [{target}]")
        queue.rotate(-origin_index)
        song = queue.popleft()
        queue.rotate(origin_index - target_index)
        queue.appendleft(song)
        queue.rotate(target_index)
        await ctx.send(f"Moved song [{origin} -> {target}]: {song.query}")

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def clear(self, ctx):
        """Clears all songs in queue"""
        info = self.get_info(ctx)
        queue = info["queue"]
        if not queue:
            await ctx.send("Queue is empty.")
            return
        queue.clear()
        await ctx.send("Cleared queue.")

    @commands.command(aliases=["s"])
    @commands.cooldown(1, 1, BucketType.user)
    async def skip(self, ctx):
        """Skips current song"""
        info = self.get_info(ctx)
        current = info["current"]
        ctx.voice_client.stop()
        if current is not None and not info["waiting"]:
            await ctx.send(f"Skipped: {current.query}")

    @commands.command(aliases=["fs"])
    async def forceskip(self, ctx):
        info = self.get_info(ctx)
        current = info["current"]
        # The only exception to history command (because it was)
        history = info["history"]
        if info["waiting"] or current is None:
            raise commands.CommandError("Inappropriate time to use this command. Likely nonexistent AudioSource or handling queue advance.")
        ctx.voice_client.pause()
        info["current"] = None
        history.append(current)
        info["songs_played"] += 1
        self.schedule(ctx, force=True)
        await ctx.send(f"Forceskipped: {current.query}")

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def loop(self, ctx, loop: typing.Optional[int] = None):
        """Gets or sets queue looping"""
        sign = loop//abs(loop) if loop else 0
        loop_messages = {1: "loop all", 0: "no loop", -1: "loop one"}
        info = self.get_info(ctx)
        if loop is None:
            await ctx.send(f"Queue status: {info['loop']} ({loop_messages[info['loop']]})")
            return
        info["loop"] = sign
        await ctx.send(f"Set queue status to {info['loop']} ({loop_messages[info['loop']]})")

    async def sleep_task(self, ctx, dur):
        await asyncio.sleep(dur)
        info = self.get_info(ctx)
        info["sleep_timer_task"] = None  # Easier to just do it in here rather than have some other function needing to detect when the task is done

        # Doesn't seem to throw any exception when not in voice channel
        await self.leave(ctx)

    @commands.command(aliases=["leavein", "sleepin"])
    async def sleep_in(self, ctx, dur: typing.Optional[str] = None):
        info = self.get_info(ctx)
        task_tuple = info["sleep_timer_task"]

        if dur is None:
            if task_tuple is None:
                await ctx.send("No sleep timer set.")
            else:
                task_start, task_duration, _ = task_tuple
                elapsed = int(time.time()-task_start)
                hhmmss = datetime.timedelta(seconds=task_duration-elapsed)
                await ctx.send(f"Disconnecting in approximately {hhmmss}")
            return

        # After this is in the form of <int> seconds or [[HH:]MM:]SS
        if not match_hhmmss_type(dur) and not match_any_seconds(dur):
            raise commands.CommandError(f"Position [{dur}] not in the form of [[HH:]MM:]SS or a positive integer number of seconds.")

        # If the form is <int> seconds, check for > 99:59:59 exceed
        if match_any_seconds(dur) and int(dur) > hhmmss_to_seconds("99:59:59"):
            raise commands.CommandError(f"Time in seconds greater than 99:59:59.")

        # Now we have a valid form
        dur_seconds = hhmmss_to_seconds(dur)

        if task_tuple is None:
            await ctx.send(f"Sleep timer created, bot will disconnect in {datetime.timedelta(seconds=dur_seconds)}")
            task = asyncio.create_task(self.sleep_task(ctx, dur_seconds))
            info["sleep_timer_task"] = (time.time(), dur_seconds, task)
            await task
        else:
            await ctx.send("Please cancel the currently running sleep timer first.")

    @commands.command()
    async def cancel(self, ctx):
        info = self.get_info(ctx)
        task_tuple = info["sleep_timer_task"]

        if task_tuple is None:
            raise commands.CommandError(f"No sleep timer task to be cancelled.")
        # Before to prevent the case where the timing is just right where
        # info["sleep_timer_task"] is not none yet the task is cancelled
        # which could be the case if the statement below was put after the tuple unpacking
        info["sleep_timer_task"] = None
        _, _, task = task_tuple
        task.cancel()
        await ctx.send("Cancelled the current sleep timer.")

    @commands.command(aliases=["i"])
    async def info(self, ctx):
        info = self.get_info(ctx)
        a = info["current"]  # A for audio

        if a is None or info["waiting"]:
            await ctx.send("Nothing currently playing.")
            return

        local_metadata_formatted = f"""
        METADATA {a.metadata.get("contents")}
        """.strip()
        stream_metadata_formatted = f"""
        DOMAIN   {a.metadata.get("webpage_url_domain")}
        ID       {a.metadata.get("id")}
        LINK     {a.metadata.get("webpage_url")}
        TITLE    {a.metadata.get("title")}
        UPLOADER {a.metadata.get("uploader")}
        """.strip()

        await ctx.send(textwrap.dedent(f"""
        ```
        ;{a.ty} {a.query}

        {stream_metadata_formatted if a.ty == "stream" else local_metadata_formatted}

        EFFECTS  x{a.filter_data.tempo} speed, x{a.filter_data.pitch} pitch
        FILTER   {a.filter_data.filter_name}
        VOLUME   {ctx.voice_client.source.volume*100}%

        {'(paused) ' if ctx.voice_client.is_paused() else ''}[{a.playhead_hashtags():.<20}] {a.generate_time_sig()}{" (live)" if a.metadata.get("live_status") == "is_live" else ''}
        ```"""))

    # async def status
    @commands.command(aliases=["ig"])
    async def info_global(self, ctx):
        info = self.get_info(ctx)
        await ctx.send(textwrap.dedent(f"""
        ```
        AUTOSHUFFLE_TASK {"running" if info["autoshuffle_task"] else None}
        GLOBAL_EFFECTS   x{info["filter_data"].tempo} speed, x{info["filter_data"].pitch} pitch
        GLOBAL_FILTER    {info["filter_data"].filter_name}
        HISTORY_SIZE     {len(info["history"])}
        LOOP_TYPE        {dict([(1, "loop all"), (0, "no loop"), (-1, "loop one")])[info["loop"]]}
        PAUSED           {False if ctx.voice_client is None else ctx.voice_client.is_paused()}
        PLAYING          {False if ctx.voice_client is None else ctx.voice_client.is_playing()}
        PROCESSING       {info["processing"]}
        QUEUE_LENGTH     {len(info["queue"])}
        SLEEP_TIMER_TASK {"running" if info["sleep_timer_task"] else None}
        SONGS_PLAYED     {info["songs_played"]}
        WAITING          {info["waiting"]}
        ```
        """))

    @commands.command(aliases=["j"])
    async def jump(self, ctx, pos):
        info = self.get_info(ctx)

        # After this is in the form of <int> seconds or [[HH:]MM:]SS
        # This if statement
        if not match_hhmmss_type(pos) and not match_any_seconds(pos):
            raise commands.CommandError(f"Position [{pos}] not in the form of [[HH:]MM:]SS nor a positive integer number of seconds.")

        # If in [[HH:]MM:]SS here, we're good, otherwise we do a length check
        if match_any_seconds(pos) and int(pos) > hhmmss_to_seconds("99:59:59"):
            raise commands.CommandError(f"Time in seconds greater than 99:59:59.")

        current = info["current"]
        is_cur_local = current.ty=="local"  # More intuitive to put this outside function call below
        ffmpeg_opts = current.filter_data.to_ffmpeg_opts(self.filter_dict, is_cur_local)

        # Create a copy so "-ss" doesn't stack at the end
        ffmpeg_opts_after_jump = ffmpeg_opts.copy()
        ffmpeg_opts_after_jump["before_options"] += f" -ss {pos}"
        # Updating the seek playhead
        # hhmmss_to_seconds(<seconds>) will return seconds
        current.sframes = seconds_to_scaled_frames(hhmmss_to_seconds(pos), current.filter_data.tempo)
        # Metadata generated before this line
        seek_stream = discord.PCMVolumeTransformer(patched_player.FFmpegPCMAudio(current, **ffmpeg_opts_after_jump))  # "url" is the same when querying
        # `current` doesn't get overridden, a copy of the same `ffmpeg_opts` is just used with a seek flag
        ctx.voice_client._player.source = seek_stream
        await ctx.send(f"Jumped to {f'{pos} seconds' if match_any_seconds(pos) else f'timestamp {pos}'}.")

    @commands.command(aliases=["ff"])
    async def fast_forward(self, ctx, sec: int = 5):
        if not (1 <= sec <= 15):
            raise commands.CommandError(f"Seek time [{sec}] not a positive integer number of seconds ranging from 1 to 15 seconds inclusive.")

        info = self.get_info(ctx)
        current = info["current"]
        tempo = current.filter_data.tempo

        # Scaled seeking: a frame may not correspond to 20ms for different tempos
        # We do an adjustment so that the relative seek time is the same
        # For faster tempo a frame will contain > 20ms => seek less
        # For slower tempo a frame will contain < 20ms => seek more
        actual_frames = (1000/20) * sec
        scaled_frames = round(actual_frames/tempo)
        read_frames = 0

        # We round to average out the "one off errors"
        for _ in range(scaled_frames):
            frame = ctx.voice_client._player.source.original.read()
            if frame == b'':
                break
            # Means a full size frame was read and the program didn't break
            read_frames += 1

        if read_frames == scaled_frames:
            await ctx.send(f"Seeking {sec}s forward.")
        elif read_frames == 0:
            await ctx.send("Nothing to seek.")
        else:
            partial_sec = read_frames*tempo / (1000/20)
            await ctx.send(f"[WARNING] Unable to seek {sec}s forward. Seeking {partial_sec}s instead.")

    @commands.command(aliases=["rr"])
    async def rewind(self, ctx, sec: int = 5):
        if not (1 <= sec <= 15):
            raise commands.CommandError(f"Seek time [{sec}] not a positive integer number of seconds ranging from 1 to 15 seconds inclusive.")

        info = self.get_info(ctx)
        current = info["current"]
        tempo = current.filter_data.tempo

        # Scaled seeking: a frame may not correspond to 20ms for different tempos
        # We do an adjustment so that the relative seek time is the same
        # For faster tempo a frame will contain > 20ms => seek less
        # For slower tempo a frame will contain < 20ms => seek more
        actual_frames = (1000/20) * sec
        scaled_frames = round(actual_frames/tempo)
        read_frames = 0

        # We round to average out the "one off errors"
        for _ in range(scaled_frames):
            frame = ctx.voice_client._player.source.original.unread()
            if frame == b'':
                break
            # Means a full size frame was read and the program didn't break
            read_frames += 1

        if read_frames == scaled_frames:
            await ctx.send(f"Rewinding {sec}s backward.")
        elif read_frames == 0:
            await ctx.send("Nothing to rewind.")
        else:
            partial_sec = read_frames*tempo / (1000/20)
            await ctx.send(f"[WARNING] Unable to rewind {sec}s backward. Rewinding {partial_sec}s instead.")

    @commands.command()
    @commands.is_owner()
    async def reschedule(self, ctx):
        """Reschedules the current guild onto the advancer task"""
        self.schedule(ctx, force=True)
        await ctx.send("Rescheduling...")

    @local.before_invoke
    @local_prepend.before_invoke
    @stream.before_invoke
    @stream_prepend.before_invoke
    async def ensure_connected(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                raise commands.CommandError("Author not connected to a voice channel")

    @pause.before_invoke
    @resume.before_invoke
    @jump.before_invoke
    @fast_forward.before_invoke
    @rewind.before_invoke
    async def check_playing(self, ctx):
        # Can't have forceskip before_invoke here because smth like ;local <nonexistent file>
        # Returns None, so we will have this error and not be able to forceskip
        await self.check_connected(ctx)
        if ctx.voice_client.source is None:
            raise commands.CommandError("Not playing anything right now")

    @_batch_add.before_invoke
    @clear.before_invoke
    @current.before_invoke
    @remove.before_invoke
    @reschedule.before_invoke
    @skip.before_invoke
    @volume.before_invoke
    @sleep_in.before_invoke
    @forceskip.before_invoke
    @info.before_invoke
    @loop.before_invoke
    @queue.before_invoke
    @shuffle.before_invoke
    @apply_filter.before_invoke
    @autoshuffle.before_invoke
    async def check_connected(self, ctx):
        if ctx.voice_client is None:
            raise commands.CommandError("Not connected to a voice channel")

def setup(bot):
    # Suppress noise about console usage from errors
    bot._music_old_ytdl_bug_report_message = youtube_dl.utils.bug_reports_message
    youtube_dl.utils.bug_reports_message = lambda: ''

    return bot.add_cog(Music(bot))

def teardown(bot):
    youtube_dl.utils.bug_reports_message = bot._music_old_ytdl_bug_report_message
    return bot.wrap_async(None)
