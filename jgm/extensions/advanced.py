import discord
from discord.ext import commands
from discord.ext import tasks

class Advanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mus = bot.cogs["Music"]  # Getting active music object

    @commands.command()
    async def skip10(self, ctx):
        self.mus.current_audio_stream.original.seekfw10()
        await ctx.send("forward10")

    @commands.command()
    async def rev10(self, ctx):
        self.mus.current_audio_stream.original.seekbw10()
        await ctx.send("backward10")

    @commands.command()
    async def loc(self, ctx):
        await ctx.send(str(self.mus.current_audio_stream.original.read_count*0.02) + " seconds in")

    @commands.command()
    @commands.is_owner()
    async def tim(self, ctx, *, _time):
        _FFMPEG_3 = {
            'options': f'-vn',
            # Source: https://stackoverflow.com/questions/66070749/
            "before_options": f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {_time}",
        }
        self.mus.ffmpeg_opts = _FFMPEG_3
        await ctx.send("skip to time")

def setup(bot):
    bot.add_cog(Advanced(bot))
