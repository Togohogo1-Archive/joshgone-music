import asyncio
import random
import re

import discord
from discord.ext import commands

class Remind(commands.Cog):

    # Ordered by length so that "7minutes" gets parsed as ("7", "minutes") and
    # not ("7minute", "s").
    suffixes = {
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "s": 1,
        "m": 60,
        "h": 3600,
    }

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "_remind_tasks"):
            bot._remind_tasks = {}
        self.tasks = bot._remind_tasks

    async def _send_after(self, ctx, seconds, name, arg):
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            self.tasks.pop(name, None)
            await ctx.send(f"Cancelled {name!r}")
        else:
            self.tasks.pop(name, None)
            await ctx.send(arg)

    @commands.command()
    async def remind(self, ctx, name: str, time, *, arg):
        """Sends the message after the specified amount of time

        Set name to - or -- to get a randomized reminder name.

        The default unit is minutes, but there are other suffixes to specify
        the unit:
            -s / -seconds
            -m / -minutes
            -h / -hours

        Usage:
            %remind - 15 breaktime      ->  sends "breaktime" in 15 minutes
            %remind - 69s haha nice     ->  sends "haha nice" in 69 seconds
            %remind - 24h tomorrow      ->  sends "tomorrow" in 24 hours
        """
        if name == "-" or name == "--":
            name = f"Reminder-{random.randint(100, 999)}"
        if name in self.tasks:
            raise ValueError(f"{name!r} already in tasks")
        for suffix, multiplier in self.suffixes.items():
            if time.endswith(suffix):
                time = int(time.removesuffix(suffix))
                break
        else:
            multiplier = 60
            time = int(time)
        seconds = time * multiplier
        task = asyncio.create_task(self._send_after(ctx, seconds, name, arg))
        self.tasks[name] = task
        await ctx.send(f"Added reminder with name {name!r}")

    @commands.command(name="in")
    async def in_(self, ctx, time, *, message):
        """Sends the message after the specified amount of time

        Equivalent to %remind - <time> <message>. If message doesn't contain a
        ping however, a ping to the author will be prepended. See %remind for
        more info.

        """
        if not re.match(r"<@\d+>", message):
            message = f'{ctx.author.mention} {message}'
        await self.remind(ctx, "-", time, arg=message)

    @commands.command()
    async def cancel(self, ctx, *, name):
        """Cancels a previous reminder"""
        if name not in self.tasks:
            return
        self.tasks.pop(name).cancel()

    @commands.command()
    async def reminders(self, ctx):
        """Lists out the names of all reminders"""
        names = list(self.tasks)
        if not names:
            names = (None,)
        await ctx.send(f"Reminders: {', '.join(map(str, names))}")

def setup(bot):
    bot.add_cog(Remind(bot))
