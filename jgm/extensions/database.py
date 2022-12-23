import os

import aiosqlite
from discord.ext import commands

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("INSERT INTO server (server_id, running) VALUES (?, ?);", (guild.id, True))
            await db.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("DELETE FROM server WHERE server_id = ?;", (guild.id,))
            await db.commit()

    @commands.command(name="reinit", ignore_extra=False)
    async def reinit_command(self, ctx):
        await self.on_guild_remove(ctx.guild)
        await self.on_guild_join(ctx.guild)
        await ctx.send("Reinitialized JoshGone.")

    @commands.command(name="running", aliases=["r"], ignore_extra=False)
    async def running_command(self, ctx, run: bool = None):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            if run is None:
                async with db.execute("SELECT running FROM server WHERE server_id = ? LIMIT 1;", (ctx.guild.id,)) as cursor:
                    row = await cursor.fetchone()
                if row is None:
                    await self.on_guild_join(ctx.guild)
                    async with db.execute("SELECT running FROM server WHERE server_id = ? LIMIT 1;", (ctx.guild.id,)) as cursor:
                        row = await cursor.fetchone()
                running = bool(row[0])
                await ctx.send(f"JoshGone is currently {'running' if running else 'not running'}.")
            else:
                await db.execute("UPDATE server SET running = ? WHERE server_id = ?;", (run, ctx.guild.id))
                await db.commit()
                await ctx.send(f"JoshGone is now {'' if run else 'not '}running.")
        if cron := self.bot.get_cog("Cron"):
            try:
                await cron.notify_running_updated({
                    "guild_id": ctx.guild.id,
                    "running": run,
                })
            except Exception as e:
                print(f'Error notifying cron cog: {e!r}')

def setup(bot):
    bot.add_cog(Database(bot))
