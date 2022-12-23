"""Run a chant depending on a cron expression"""

import argparse
import asyncio
import os
import re
import dateutil.tz
from shlex import shlex
from heapq import heapify, heapreplace
from datetime import datetime, timezone
from croniter import croniter
from typing import Optional, Tuple, List, Dict

import aiosqlite
import discord
from discord.ext import commands

async def check_running(guild_id: int) -> bool:
    """Return whether the server has %running on"""
    async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
        async with db.execute(
            "SELECT running FROM server WHERE server_id = ? LIMIT 1;",
            [guild_id],
        ) as cursor:
            row = await cursor.fetchone()
            if row is not None and row[0]:
                return True
    return False

async def get_namespaced_chants(
    guild_id: int,
    namespace: str,
) -> Dict[str, str]:
    """Return a dict of chants with a f'{namespace}/' prefix"""
    chants = {}
    async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
        async with db.execute(
            "SELECT chant_name, chant_text FROM chants"
            " WHERE server_id = ? AND chant_name GLOB ?;",
            [guild_id, f'{namespace}/*'],
        ) as cursor:
            async for [name, text] in cursor:
                assert name.startswith(f'{namespace}/')
                chants[name] = text
    return chants

async def get_chant(guild_id: int, name: str) -> Optional[str]:
    async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
        async with db.execute(
            "SELECT chant_text FROM chants"
            " WHERE server_id = ? AND chant_name = ?;",
            [guild_id, name],
        ) as cursor:
            if (row := await cursor.fetchone()) is not None:
                return row[0]
    return None

def _split_chant_text(raw: str) -> Tuple[str, str]:
    # Split by a bare --
    options, text = re.split(r"(?:(?<=\s)|$)--(?:(?=\s)|^)", raw, maxsplit=1)
    return (
        # Replace --- with -- (allows specifying -- in options)
        re.sub(r"(?:(?<=\s)|$)-(-+(?:(?=\s)|^))", r"\1", options),
        # Rest of chant text is unchanged
        text,
    )

def _split_chant_options(options: str) -> List[str]:
    s = shlex(options, posix=True)
    s.whitespace_split = True  # Simulate argument parsing
    return list(s)

_cron_parser = argparse.ArgumentParser(add_help=False)
_cron_parser.add_argument("cron", nargs="*")
_cron_parser.add_argument("-c", "--channel")
_cron_parser.add_argument(
    "-z", "--timezone",
    dest="tz",
    default="America/Toronto",
)

def _info_from_options(name: str, text: str, argv: List[str]) -> dict:
    args, _ = _cron_parser.parse_known_args(argv)
    return {"name": name, "text": text, **vars(args)}

def _next_from_info(now, info: dict) -> datetime:
    cron_expr = " ".join(info["cron"])
    tz = dateutil.tz.gettz(info["tz"])
    return croniter(
        cron_expr,
        now.astimezone(tz),
        datetime,
        hash_id=info.get("name", ""),
        day_or=False,
    ).get_next()

def _get_chant_channel(info: dict, text_channels: list):
    for channel in text_channels:
        if (
            str(channel.id) == info["channel"]
            or channel.name == info["channel"]
        ):
            return channel
    raise LookupError(f'no matching channel for {info["channel"]}')

def _info_from_raw(now, name: str, raw: str):
    options, text = _split_chant_text(raw)
    argv = _split_chant_options(options)
    return _info_from_options(name, text, argv)

class Cron(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cron_runners = {}
        self._cron_next = {}
        for guild in self.bot.guilds:
            self.start_runner(guild.id)

    def cog_unload(self):
        for task in self._cron_runners.values():
            task.cancel()

    async def notify_chants_updated(self, info):
        if "guild_id" not in info:
            return
        self.restart_runner(info["guild_id"])

    async def notify_running_updated(self, info):
        if "guild_id" not in info:
            return
        if info.get("running", True):  # default to starting the runner
            self.start_runner(info["guild_id"])
        else:
            self.stop_runner(info["guild_id"])

    def start_runner(self, guild_id):
        if guild_id not in self._cron_runners:
            runner = self.guild_cron_runner(guild_id)
            self._cron_runners[guild_id] = task = asyncio.create_task(runner)
            self._cron_next[guild_id] = None
            # Log uncaught errors
            def _on_runner_done(task):
                if task.cancelled():
                    return
                if not (e := task.exception()):
                    return
                print(f'Cron fatal error in {guild_id}: {e!r}')
            task.add_done_callback(_on_runner_done)

    def stop_runner(self, guild_id):
        if task := self._cron_runners.get(guild_id):
            task.cancel()
            del self._cron_runners[guild_id]
            del self._cron_next[guild_id]

    def restart_runner(self, guild_id):
        self.stop_runner(guild_id)
        self.start_runner(guild_id)

    async def guild_cron_runner(self, guild_id: int):
        # Create heap of chants sorted by UTC time and chant name
        chants = await get_namespaced_chants(guild_id, "cron")
        now = datetime.now(tz=timezone.utc)
        def _heap_key(info):
            try:
                return (
                    _next_from_info(now, info),
                    info["name"],
                    info,
                )
            except BaseException as e:
                print(f'Cron error on {info["name"]}: {e!r}')
                return None
        croniter_heap = []
        for name, raw in chants.items():
            try:
                info = _info_from_raw(now, name, raw)
            except BaseException as e:
                print(f'Cron error on {name}: {e!r}')
            if item := _heap_key(info):
                croniter_heap.append(item)
        heapify(croniter_heap)
        while croniter_heap:
            # wait until next cron
            now = datetime.now(tz=timezone.utc)
            self._cron_next[guild_id] = croniter_heap[0][1]
            next_seconds = (croniter_heap[0][0] - now).total_seconds()
            await asyncio.sleep(next_seconds)
            # Send newest message if it's scheduled to run
            now = datetime.now(tz=timezone.utc)
            if croniter_heap[0][0] <= now:
                info = croniter_heap[0][-1]
                # push cron's next time
                if item := _heap_key(info):
                    heapreplace(croniter_heap, item)
                # send chant
                try:
                    guild = discord.utils.get(
                        self.bot.guilds,
                        id=guild_id,
                    )
                    if guild is None:
                        raise LookupError(
                            f'guild not found: id={guild_id}'
                        )
                    channel = _get_chant_channel(
                        info,
                        guild.text_channels,
                    )
                    await channel.send(info["text"])
                except Exception as e:
                    print(f'Cron send error on {info["name"]}: {e!r}')

    @commands.command(name="next")
    async def next_command(self, ctx, *, name: Optional[str] = None):
        """Return the next time the specified cron chant will run

        If name isn't specified, the next cron chant for the server will be
        shown.

        """
        if name is None:
            name = self._cron_next.get(ctx.guild.id)
            if name is None:
                await ctx.send("No crons running")
                return
            raw = await get_chant(ctx.guild.id, name)
            assert raw is not None
            now = datetime.now(tz=timezone.utc)
            info = _info_from_raw(now, name, raw)
            next_ = _next_from_info(now, info)
            await ctx.send(f'{next_} [<t:{int(next_.timestamp())}:F>, {name}]')
            return
        raw = await get_chant(ctx.guild.id, name)
        if raw is None:
            await ctx.send("Chant not found :/")
            return
        now = datetime.now(tz=timezone.utc)
        info = _info_from_raw(now, name, raw)
        next_ = _next_from_info(now, info)
        await ctx.send(f'{next_} [<t:{int(next_.timestamp())}:F>]')

    @commands.command(name="_restart_cron", hidden=True)
    @commands.is_owner()
    async def restart_command(self, ctx):
        """Restart the %cron runner for the current guild"""
        self.restart_runner(ctx.guild.id)
        await ctx.send("Restarted")

def setup(bot):
    bot.add_cog(Cron(bot))
