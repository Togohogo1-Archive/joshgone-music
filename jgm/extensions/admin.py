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
        await self.bot.wrap_async(self.bot.load_extension(f"jgm.extensions.{module}"))
        await ctx.send("Extension loaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module: str):
        await self.bot.wrap_async(self.bot.unload_extension(f"jgm.extensions.{module}"))
        await ctx.send("Extension unloaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        await self.bot.wrap_async(self.bot.reload_extension(f"jgm.extensions.{module}"))
        await ctx.send("Extension reloaded.")

    @commands.command(name="list", hidden=True)
    @commands.is_owner()
    async def list_(self, ctx):
        extensions = ", ".join(self.bot.extensions)
        await ctx.send(f"Extensions loaded: [{extensions}]")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting bot down.")
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def apply(self, ctx):
        await asyncio.to_thread(self.apply_outstanding)
        await ctx.send("Migrations applied.")

    def apply_outstanding(self):
        backend = yoyo.get_backend(f"sqlite:///{os.environ['JOSHGONE_DB']}")
        migrations = yoyo.read_migrations("./migrations")
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

def setup(bot):
    return bot.add_cog(Admin(bot))
