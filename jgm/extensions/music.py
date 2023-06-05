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
from collections import deque

import discord
from discord.ext import commands
from discord.ext import tasks

import yt_dlp as youtube_dl

import jgm.patched_player as patched_player
import soundit as s

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
    # Options passed to FFmpeg
    _DEFAULT_FFMPEG_OPTS = {
        'options': '-vn',
        # Source: https://stackoverflow.com/questions/66070749/
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    }

    def __init__(
        self,
        bot,
        *,
        ytdl_opts=_DEFAULT_YTDL_OPTS,
        ffmpeg_opts=_DEFAULT_FFMPEG_OPTS,
    ):
        self.bot = bot
        # Options are stores on the instance in case they need to be changed
        self.ytdl_opts = ytdl_opts
        self.ffmpeg_opts = ffmpeg_opts
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
    async def _play_local(self, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        return source, query

    # Searches various sites using url. Title is data["title"] or url
    async def _play_stream(self, url):
        original_url = url
        if url[0] == "<" and url[-1] == ">":
            url = url[1:-1]
        player, data = await self.player_from_url(url, stream=True)
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
            info["current"] = None
            if queue:
                # Get the next song
                current = queue.popleft()
                info["current"] = current
                # Get an audio source and play it
                after = lambda error, ctx=ctx: self.schedule(ctx, error)
                async with channel.typing():
                    source, title = await getattr(self, f"_play_{current['ty']}")(current['query'])
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
            wrapped["current"] = None
            wrapped["waiting"] = False
            wrapped["loop"] = False
            wrapped["processing"] = False
            wrapped["autoshuffle_task"] = None
            wrapped["sleep_timer_task"] = None
            wrapped["version"] = 3
        else:
            wrapped = self.data[guild_id]
        if wrapped["version"] == 3:
            wrapped["channel_id"] = ctx.channel.id
            wrapped["version"] = 4
        return wrapped

    # Helper function to remove the info for a guild
    def pop_info(self, ctx):
        return self.data.pop(ctx.guild.id, None)

    # Creates an audio source from a url
    async def player_from_url(self, url, *, loop=None, stream=False):
        ytdl = youtube_dl.YoutubeDL(self.ytdl_opts)
        loop = loop or asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        audio = patched_player.FFmpegPCMAudio(filename, **self.ffmpeg_opts)
        player = discord.PCMVolumeTransformer(audio)
        return player, data

    @commands.command()
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
        queue.append({"ty": "local", "query": query})
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Appended to queue: local {query}")

    @commands.command()
    @commands.is_owner()
    async def local_prepend(self, ctx, *, query):
        # """Plays a file from the local filesystem"""
        info = self.get_info(ctx)
        queue = info["queue"]
        queue.appendleft({"ty": "local", "query": query})
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Prepended to queue: local {query}")

    @commands.command(aliases=["yt", "play", "p"])
    async def stream(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""
        if len(url) > 100:
            raise ValueError("url too long (length over 100)")
        if not url.isprintable():
            raise ValueError(f"url not printable: {url!r}")
        print(ctx.message.author.name, "queued", repr(url))
        info = self.get_info(ctx)
        queue = info["queue"]
        queue.append({"ty": "stream", "query": url})
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Appended to queue: stream {url}")

    @commands.command(aliases=["prepend", "pplay", "pp"])
    async def stream_prepend(self, ctx, *, url):
        # """Plays from a url (almost anything youtube_dl supports)"""
        if len(url) > 100:
            raise ValueError("url too long (length over 100)")
        if not url.isprintable():
            raise ValueError(f"url not printable: {url!r}")
        print(ctx.message.author.name, "queued", repr(url))
        info = self.get_info(ctx)
        queue = info["queue"]
        queue.appendleft({"ty": "stream", "query": url})
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Prepended to queue: stream {url}")

    async def add_to_queue(self, ctx, source):
        """Plays the specified source"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                raise RuntimeError("Author not connected to a voice channel")
        info = self.get_info(ctx)
        queue = info["queue"]
        queue.append({"ty": "raw", "query": source})
        if info["current"] is None:
            self.schedule(ctx)

    @commands.command()
    async def _add_playlist(self, ctx, *, url):
        """Adds all songs in a playlist to the queue"""
        if len(url) > 100:
            raise ValueError("url too long (length over 100)")
        if not url.isprintable():
            raise ValueError(f"url not printable: {url!r}")
        print(ctx.message.author.name, "queued playlist", repr(url))
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
            url = f"https://www.youtube.com/watch?v={entry['url']}"
            if bracketed:
                url = f"<{url}>"
            queue.append({"ty": "stream", "query": url})
        if info["current"] is None:
            self.schedule(ctx)
        await ctx.send(f"Added playlist to queue: {url}")

    @commands.command(name="batch_add")
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
        except (OverflowError, ValueError):
            pass
        if not await self.bot.is_owner(ctx.author):
            # prevent insane ppl from doing this
            volume = min(100, volume)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(aliases=["stop"])
    async def pause(self, ctx):
        """Pauses playing"""
        ctx.voice_client.pause()

    @commands.command(aliases=["start"])
    async def resume(self, ctx):
        """Resumes playing"""
        ctx.voice_client.resume()

    @commands.command()
    async def leave(self, ctx):
        """Disconnects the bot from voice and clears the queue"""
        self.pop_info(ctx)
        if ctx.voice_client is None:
            return
        await ctx.voice_client.disconnect()

    @commands.command(aliases=["c"])
    async def current(self, ctx):
        """Shows the current song"""
        query = None
        if ctx.voice_client is not None:
            info = self.get_info(ctx)
            current = info["current"]
            if current is not None and not info["waiting"]:
                query = current["query"]
        await ctx.send(f"Current: {query}")

    @commands.command(aliases=["q"])
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
                paginator.add_line(f"{i}: {song['query']}")
        for page in paginator.pages:
            await ctx.send(page)

    def normalize_index(self, ctx, position, length):
        index = position
        if index > 0:
            index -= 1
        if index < 0:
            index += length
        if not 0 <= index < length:
            raise ValueError(position)
        return index

    @commands.command()
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
        await ctx.send(f"Removed song [{position}]: {song['query']}")

    @commands.command()
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
        await ctx.send(f"Moved song [{origin} -> {target}]: {song['query']}")

    @commands.command()
    async def clear(self, ctx):
        """Clears all songs on queue"""
        info = self.get_info(ctx)
        queue = info["queue"]
        queue.clear()
        await ctx.send("Cleared queue")

    @commands.command(aliases=["s"])
    async def skip(self, ctx):
        """Skips current song"""
        info = self.get_info(ctx)
        current = info["current"]
        ctx.voice_client.stop()
        if current is not None and not info["waiting"]:
            await ctx.send(f"Skipped: {current['query']}")

    @commands.command()
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

    def match_hhmmss_type(self, pos):
        # Based off simplified version of https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
        # Match [[HH:]MM:]SS or integer seconds, brackets optional
        # First check regex match
        # Regex pattern slightly modified from: https://stackoverflow.com/a/8318367
        return re.match(r"^(?:(?:(\d?\d):)?([0-5]?\d):)?([0-5]?\d)$", pos)

    def match_any_seconds(self, pos):
        # Returns false for negative numbers too
        # Sufficient to check if `pos` is a positive integer in string form
        return pos.isdigit()

    def hhmmss_to_seconds(self, hhmmss):
        """
        Assumes already in valid [[HH]:MM:]SS regex format
        if len 1 -> ss
        if len 2 -> mm:ss
        if len 3 -> hh:mm:ss

        never hh:ss
        """
        hhmmss_list = hhmmss.split(":")
        hour_s = int(hhmmss_list[-3])*3600 if len(hhmmss_list) >= 3 else 0
        min_s = int(hhmmss_list[-2])*60 if len(hhmmss_list) >= 2 else 0
        return hour_s + min_s + int(hhmmss_list[-1])

    async def sleep_task(self, ctx, dur):
        await asyncio.sleep(dur)
        info = self.get_info(ctx)
        info["sleep_timer_task"] = None  # Easier to ju do it in here rather than have some other function needing to detect when the task is done

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
        if not self.match_hhmmss_type(dur) and not self.match_any_seconds(dur):
            raise commands.CommandError(f"Position [{dur}] not in the form of [[HH:]MM:]SS or a positive integer number of seconds.")

        # If the form is <int> seconds, check for > 99:59:59 exceed
        if self.match_any_seconds(dur) and int(dur) > self.hhmmss_to_seconds("99:59:59"):
            raise commands.CommandError(f"Time in seconds greater than 99:59:59.")

        # Now we have a valid form
        dur_seconds = self.hhmmss_to_seconds(dur)

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

    @commands.command()
    @commands.is_owner()
    async def reschedule(self, ctx):
        """Reschedules the current guild onto the advancer task"""
        self.schedule(ctx, force=True)
        await ctx.send("Rescheduled")

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
    async def check_playing(self, ctx):
        await self.check_connected(ctx)
        if ctx.voice_client.source is None:
            raise commands.CommandError("Not playing anything right now")

    @remove.before_invoke
    @reschedule.before_invoke
    @skip.before_invoke
    @clear.before_invoke
    @volume.before_invoke
    @sleep_in.before_invoke
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
