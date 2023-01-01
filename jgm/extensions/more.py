import discord
from discord.ext import commands
from discord.ext import tasks

class More(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mus = bot.cogs["Music"]  # Getting active music object
        print(dir(self.mus))

    @commands.command(aliases=["bb"])
    async def bassboost(self, ctx):
        self.mus._set_audio_filter("bassboost")
        await self.mus._apply_filter(ctx)

    @commands.command()
    async def deepfry(self, ctx):
        self.mus._set_audio_filter("deepfry")
        await self.mus._apply_filter(ctx, complx=True)

    @commands.command(aliases=["nc"])
    async def nightcore(self, ctx):
        self.mus._set_audio_filter("nightcore")
        await self.mus._apply_filter(ctx)

    @commands.command(aliases=["dc"])
    async def daycore(self, ctx):
        self.mus._set_audio_filter("daycore")
        await self.mus._apply_filter(ctx)

    @commands.command(aliases=["no"])
    async def normal(self, ctx):
        self.mus._set_audio_filter("normal")
        await self.mus._apply_filter(ctx)

    @commands.command(aliases=["df"])
    async def defaults(self, ctx):
        self.mus._set_audio_filter("normal")
        self.mus._apply_speed_filter(1)
        await self.mus._apply_filter(ctx)

    @commands.command(aliases=["sp"])
    async def speed(self, ctx, factor: float):
        self.mus._apply_speed_filter(factor)
        await self.mus._apply_filter(ctx)


def setup(bot):
    bot.add_cog(More(bot))