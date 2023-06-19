import discord
import typing
from discord.ext import commands
from discord.ext import tasks

import jgm.patched_player as pp

class More(commands.Cog):
    # TODO make these filters go to the next song
    def __init__(self, bot):
        self.bot = bot
        self.mus = bot.cogs["Music"]  # Getting active music object

    @commands.command(aliases=["ff"])
    async def fast_forward(self, ctx, sec: int = 5):
        # TODO shouldn't be albe to fast forward when paused
        await self.mus._fast_forward(ctx, sec)

    @commands.command(aliases=["rr"])
    async def rewind(self, ctx, sec: int = 5):
        await self.mus._rewind(ctx, sec)

    @commands.command(aliases=["goto", "j"])
    async def jump(self, ctx, pos):
        await self.mus._jump(ctx, pos)

    @fast_forward.before_invoke
    async def disable_if_live(self, ctx):
        if self.mus.current_metadata["is_live"]:
            raise commands.CommandError("this command doesn't work with the source is live")

def setup(bot):
    return bot.add_cog(More(bot))
