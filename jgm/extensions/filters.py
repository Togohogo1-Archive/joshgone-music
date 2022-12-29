import discord
from discord.ext import commands
from discord.ext import tasks

class Filters(commands.Cog):
    # 'options': '-vn -filter:a "atempo=1.5"',
    _OTHER_FFMPEG_OPTS = {
        'options': '-vn -filter:a asetrate=44800*1.2,aresample=44800,atempo=1.1',
        # Source: https://stackoverflow.com/questions/66070749/
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    }

    _OTHER_FFMPEG_OPTS2 = {
        'options': '-vn -filter:a asetrate=44800*0.8,aresample=44800,atempo=1.1',
        # Source: https://stackoverflow.com/questions/66070749/
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    }

    _FFMPEG_3 = {
        'options': '-vn -af bass=g=20',
        # Source: https://stackoverflow.com/questions/66070749/
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    }

    def __init__(self, bot):
        self.bot = bot
        self.mus = bot.cogs["Music"]  # Getting active music object
        print(dir(self.mus))

    @commands.command()
    async def dc(self, ctx):
        self.mus.ffmpeg_opts = self._OTHER_FFMPEG_OPTS2
        await ctx.send("daycore options set, will activate on the next song if current one is playing")

    @commands.command()
    async def norm(self, ctx):
        self.mus.ffmpeg_opts = self.mus._DEFAULT_FFMPEG_OPTS
        await ctx.send("normal ffmpeg options set")

    @commands.command()
    async def nc(self, ctx):
        self.mus.ffmpeg_opts = self._OTHER_FFMPEG_OPTS
        await ctx.send("nightcore options set, will activate on the next song if current one is playing")

    @commands.command()
    async def bb(self, ctx):
        self.mus.ffmpeg_opts = self._FFMPEG_3
        await ctx.send("maximum bass boost set, will activate on the next song if current one is playing")



def setup(bot):
    bot.add_cog(Filters(bot))