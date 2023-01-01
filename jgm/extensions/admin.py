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
        self.bot.load_extension(f"jgm.extensions.{module}")
        await ctx.send("Extension loaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module: str):
        self.bot.unload_extension(f"jgm.extensions.{module}")
        await ctx.send("Extension unloaded.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        self.bot.reload_extension(module)
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
    async def execold(self, ctx, *, text):
        """Executes some code

        The code needs to be approved by the bot owner to be run.
        """
        lines = text.splitlines()
        if len(lines) == 1:
            line = lines[0]
            if len(line) >= 2 and line[0] == "`" and line[-1] == "`":
                line = line[1:-1]
            if len(line) >= 2 and line[0] == "`" and line[-1] == "`":
                line = line[1:-1]
            if "return" not in line:
                line = f"return {line}"
            lines[0] = line
        elif len(lines) >= 2:
            if lines[0] != "```py":
                await ctx.send(f"First line has to be \\`\\`\\`py")
                return
            if lines[-1] != "```":
                await ctx.send(f"Last line has to be \\`\\`\\`")
                return
            del lines[0]
            del lines[-1]
        if ctx.author.id != self.bot.owner_id:
            message = await ctx.reply(f"Awaiting approval...", mention_author=False)
            try:
                await message.add_reaction("✅")
                await message.add_reaction("❌")
                def check(reaction, user):
                    return (
                        reaction.message.id == message.id
                        and reaction.emoji in {"✅", "❌"}
                        and user.id == self.bot.owner_id
                    )
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                except asyncio.TimeoutError:
                    await message.edit(content=f"{message.content}\nApproval timed out")
                    return
                if reaction.emoji == "❌":
                    await message.edit(content=f"{message.content}\nCode denied :(")
                    return
                await message.edit(content=f"{message.content}\nCode approved :D")
            except discord.NotFound:
                return
        for i, line in enumerate(lines):
            lines[i] = f"    {line}"
        lines.insert(0, "async def ____thingy(bot, ctx):\n    pass")
        code = "\n".join(lines)
        scope = globals().copy()
        exec(code, scope)
        result = await scope["____thingy"](self.bot, ctx)
        if result is not None:
            await ctx.send(result)

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
    bot.add_cog(Admin(bot))
