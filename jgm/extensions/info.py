"""Manages general listeners like on_ready or on_command_error"""

import aiosqlite
import traceback

from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Some debug info
        print(f"JoshGone logged on as {self.bot.user}.")
        print(f"SQLite version is {aiosqlite.sqlite_version}.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Full traceback
        traceback.print_exception(type(error), error, error.__traceback__)

        # Unpack the error for cleaner error messages
        if isinstance(error, commands.CommandInvokeError):
            error = error.__cause__ or error
        try:
            await ctx.send(f"Oops, an error occurred: `{error!r}`")
        except Exception:
            print(f"Error: {error!r}")
            raise

def setup(bot):
    bot.add_cog(Info(bot))
