import re

import discord
from discord.ext import commands

class Thicc(commands.Cog):

    ignore_regex = r"(?:<a?:\w+:\d+>|:[a-z_]+:)"

    mapping = {}
    for original, target in zip(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿",
    ):
        mapping[original.upper()] = f"{target}\u180E"
        mapping[original.lower()] = f"{target}\u180E"
    for original, target in zip(
        "!?+-",
        "❗❓➕➖",
    ):
        mapping[original] = target
    for original, target in zip(
        "$*#",
        ["️💲", "*️⃣", "#️⃣"],
    ):
        mapping[original] = target
    for original, target in zip(
        "0123456789",
        "zero one two three four five six seven eight nine ten".split(),
    ):
        mapping[original] = f":{target}:"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def thicc(self, ctx, *, message):
        """Convert letters to emojis"""
        result = []
        end = 0
        for match in re.finditer(self.ignore_regex, message):
            if unmatched := message[end : match.start()]:
                result.append("".join(self.mapping.get(char, char) for char in unmatched))
            result.append(match[0])
            end = match.end()
        if unmatched := message[end:]:
            result.append("".join(self.mapping.get(char, char) for char in unmatched))
        await ctx.send("".join(result))

def setup(bot):
    bot.add_cog(Thicc(bot))
