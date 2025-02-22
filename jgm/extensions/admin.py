import asyncio
import os
import pydoc
import functools

import yoyo
import discord
from discord.ext import commands

@functools.wraps(pydoc.render_doc)
def helps(*args, **kwargs):
    stack = []
    for char in pydoc.render_doc(*args, **kwargs):
        if char == "\b":
            if stack:
                stack.pop()
            continue
        stack.append(char)
    return "".join(stack)

async def pages(ctx, obj):
    """Paginates obj and sends them to the current context"""
    obj = str(obj)
    paginator = commands.Paginator()
    for line in obj.splitlines():
        paginator.add_line(line)
    for page in paginator.pages:
        await ctx.send(page)

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module: str):
        # `wrap_async` because ..._extension used to be sync in v1.x
        await self.bot.wrap_async(self.bot.load_extension(f"jgm.extensions.{module}"))
        await ctx.send("Extension loaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module: str):
        # `wrap_async` because ..._extension used to be sync in v1.x
        await self.bot.wrap_async(self.bot.unload_extension(f"jgm.extensions.{module}"))
        await ctx.send("Extension unloaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        # `wrap_async` because ..._extension used to be sync in v1.x
        await self.bot.wrap_async(self.bot.reload_extension(f"jgm.extensions.{module}"))
        await ctx.send("Extension reloaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def extensions(self, ctx):
        extensions = ", ".join(self.bot.extensions)
        await ctx.send(f"Extensions loaded: [{extensions}]")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting bot down.")
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def ctx_(self, ctx):
        if not hasattr(self.bot, "ctx_"):
            self.bot.ctx_ = ctx
            await ctx.send("[DEBUG PURPOSES] Added a `ctx` instance to the bot.")

def setup(bot):
    return bot.add_cog(Admin(bot))
