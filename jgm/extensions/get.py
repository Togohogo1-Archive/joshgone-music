import re
import asyncio

import discord
from discord.ext import commands

class Get(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="get", require_var_positional=True)
    async def _get(self, ctx, *indices):
        r"""Gets a message from the channel's history

        Used to create a single command from multiple parts when self
        accept is on.

        Usage:
            %get 1      ->  sends last message
            %get 1 2    ->  sends last message \n second last message
            %get 1 1    ->  sends last message \n last message
            %get 1.0    ->  sends last message
            %get 1.1    ->  sends last message's first word
            %get 1.-1   ->  sends last message's last word
        """
        # \d means [0-9], \s means whitespace
        pattern = r"\s*(\d+)(?:\s*\.\s*(?:([+-]?)\s*|())(\d+)|()())\s*"
        wanted = []
        for index in indices:
            match = re.fullmatch(pattern, index)
            if not match:
                raise ValueError(f"couldn't parse index: {index!r}")
            message, sign, word = filter(lambda x: x is not None, match.groups())
            i, j = map(int, (message, f"{sign}{word}" or 0))
            wanted.append((i, j))
        if any(i <= 0 for i, _ in wanted):
            raise ValueError("all message indices must be positive")
        if any(i > 100 for i, _ in wanted):
            raise ValueError("all message indices must be less than or equal to 100")
        limit = max(i for i, _ in wanted)
        messages = {i: None for i, _ in wanted}
        i = 0
        async for message in ctx.channel.history(limit=limit+1):
            if i in messages:
                messages[i] = message
            i += 1
        result = []
        for i, j in wanted:
            if j == 0:
                result.append(messages[i].content)
                continue
            if j > 0:
                j -= 1
            words = messages[i].content.split()
            try:
                result.append(words[j])
            except IndexError:
                result.append("")
        await ctx.send("\n".join(result))

def setup(bot):
    bot.add_cog(Get(bot))
