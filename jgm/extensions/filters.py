import discord
from discord.ext import commands
from discord.ext import tasks

class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mus = bot.cogs["Music"]  # Getting active music object
        print(dir(self.mus))

    @commands.command(aliases=["bb"])
    async def bassboost(self, ctx):
        await self.mus._set_audio_filter(ctx, "bassboost")

    @commands.command()
    async def deepfry(self, ctx):
        await self.mus._set_audio_filter(ctx, "deepfry")

    @commands.command(aliases=["nc"])
    async def nightcore(self, ctx):
        await self.mus._set_audio_filter(ctx, "nightcore")

    @commands.command(aliases=["dc"])
    async def daycore(self, ctx):
        await self.mus._set_audio_filter(ctx, "daycore")

    @commands.command(aliases=["no"])
    # rename this to flat?
    async def normal(self, ctx):
        await self.mus._set_audio_filter(ctx, "normal")

    @commands.command(aliases=["df"])
    async def defaults(self, ctx):
        await ctx.send("TBA, for now run 2 commands")

    @commands.command(aliases=["sp"])
    async def speed(self, ctx, factor: float):
        await self.mus._set_speed_filter(ctx, factor)


def setup(bot):
    bot.add_cog(Filters(bot))
