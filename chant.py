import os
import asyncio
import math

import aiosqlite
from discord.ext import commands

class Chant(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="chants", ignore_extra=False, pass_context=True, invoke_without_command=True)
    async def _chants(self, ctx):
        """Configure chants"""
        await self._list(ctx)

    @_chants.command(name="list", ignore_extra=False)
    async def _list(self, ctx, debug: bool = False):
        """List available chants"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_name FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                names = [row[0] async for row in cursor]
        if debug:
            names = [f"`{name}`" for name in names]
        length = len(names)
        if not names:
            names = (None,)
        await ctx.send(f"Chants [{length}]: {', '.join(names)}")

    @_chants.command(name="add", aliases=["update"])
    @commands.check_any(
        commands.has_permissions(manage_messages=True),
        commands.has_role("enchanter"),
    )
    async def _add(self, ctx, name: str, *, text: str):
        """Add / update a chant"""
        if not name.isprintable():
            raise ValueError(f"Name not printable: {name!r}")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT COUNT(*) FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()):
                    raise ValueError("could not get count of chants")
                if row[0] > 100:
                    raise ValueError(f"too many chants stored: {row[0]}")
            await db.execute("INSERT OR REPLACE INTO chants VALUES (?, ?, ?);", (ctx.guild.id, name, text))
            await db.commit()
        await ctx.send(f"Added chant {name}")

    @_chants.command(name="check", ignore_extra=False)
    async def _check(self, ctx, name: str):
        """Output the text for a single chant"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_text FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if (row := await cursor.fetchone()):
                    await ctx.send(f"Chant {name} {{`{name!r}`}}: {row[0]}")
                else:
                    await ctx.send(f"Chant {name} {{`{name!r}`}} doesn't exist")

    @_chants.command(name="remove", ignore_extra=False)
    @commands.check_any(
        commands.has_permissions(manage_messages=True),
        commands.has_role("enchanter"),
    )
    async def _remove(self, ctx, name: str):
        """Remove a chant"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("DELETE FROM chants WHERE server_id = ? AND chant_name = ?;", (ctx.guild.id, name))
            await db.commit()
        await ctx.send(f"Removed chant {name}")

    @commands.command(name="chant", aliases=["h"], ignore_extra=False)
    async def _chant(self, ctx, name: str, repeats: int = 5, delay: float = 2):
        """Repeat a chant multiple times

        `repeat` specifies the number of times to repeat the chant
        `delay` specifies the number of seconds to wait between chants
        """
        if not math.isfinite(delay):
            raise ValueError(f"{delay!r} is not finite")
        for _ in range(repeats):
            async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
                async with db.execute("SELECT running FROM server WHERE server_id = ? LIMIT 1;", (ctx.guild.id,)) as cursor:
                    if not (row := await cursor.fetchone()) or not row[0]:
                        break
                async with db.execute("SELECT chant_text FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        break
                    text = row[0]
                    if not text:
                        break
            await ctx.send(text)
            await asyncio.sleep(delay)

def setup(bot):
    bot.add_cog(Chant(bot))
