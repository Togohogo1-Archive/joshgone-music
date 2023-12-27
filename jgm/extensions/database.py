import os

import aiosqlite
from discord.ext import commands

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Ensure that guilds the bot was previous in have been initialized
        for guild in self.bot.guilds:
            await self.on_guild_join(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("INSERT OR IGNORE INTO server (server_id) VALUES (?);", (guild.id,))
            await db.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("DELETE FROM server WHERE server_id = ?;", (guild.id,))
            await db.commit()

    @commands.command(name="reinit", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def reinit_command(self, ctx):
        await self.on_guild_remove(ctx.guild)
        await self.on_guild_join(ctx.guild)
        await ctx.send("Reinitialized Just Good Music.")

def setup(bot):
    return bot.add_cog(Database(bot))
