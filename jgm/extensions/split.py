import asyncio
import math
import typing

import discord
from discord.ext import commands

class Split(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lines", aliases=["split"])
    async def _lines(self, ctx, delay: typing.Optional[float] = 0.5, *, lines):
        r"""Splits and sends the argument's lines as separate messages

        `delay` specifies the number of seconds between messages

        Usage:
            %lines a \n b           ->  sends a, b
            %lines \n a \n \n b     ->  sends a, b
        """
        if not math.isfinite(delay):
            raise ValueError(f"{delay!r} is not finite")
        for line in lines.splitlines():
            if not line or line.isspace():
                continue
            await ctx.send(line)
            await asyncio.sleep(delay)

    @commands.command(name="words")
    async def _words(self, ctx, delay: typing.Optional[float] = 0.5, *words):
        r"""Splits and sends the argument's words as separate messages

        `delay` specifies the number of seconds between messages

        Usage:
            %words a b  ->  sends a, b
        """
        if not math.isfinite(delay):
            raise ValueError(f"{delay!r} is not finite")
        for word in words:
            if not word or word.isspace():
                continue
            await ctx.send(word)
            await asyncio.sleep(delay)

def setup(bot):
    bot.add_cog(Split(bot))
