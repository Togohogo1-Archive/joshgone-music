import discord
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

    @commands.command()
    async def loc(self, ctx):
        # rename this to smth better later
        await self.mus._loc(ctx)
    '''
    @commands.command()
    @commands.is_owner()
    async def tim(self, ctx, *, _time):
        _FFMPEG_3 = {
            'options': '-vn',
            # Source: https://stackoverflow.com/questions/66070749/
            "before_options": f"-ss {_time} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }
        import time
        a = time.time()
        new_audio = pp.FFmpegPCMAudio(self.mus.current_audio_link, **_FFMPEG_3)
        await self.mus.skip(ctx)

        after = lambda error, ctx=ctx: self.mus.schedule(ctx, error)
        # ctx.voice_client.stop()
        ctx.voice_client.play(new_audio, after=after)
        # self.mus.ffmpeg_opts = _FFMPEG_3
        b = time.time() - a
        await ctx.send(b)
    '''

def setup(bot):
    bot.add_cog(More(bot))
