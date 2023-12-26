import os
import asyncio
import inspect

import discord
from discord.ext import commands

# These extensions are loaded automatically on startup
LOAD_ON_STARTUP = (
    "admin", "playlists", "music", "database", "info"
)

# We need intents to resolve a name to a Member object
intents = discord.Intents.all()

# Our prefix is % or @joshgone
command_prefix = commands.when_mentioned_or(";")

# Use v1.x help command
help_command = commands.DefaultHelpCommand(
    show_parameter_descriptions=False
)
# try:
#     help_command = commands.DefaultHelpCommand(
#         show_parameter_descriptions=False
#     )
# except TypeError:
#     help_command = None

# Wrap a non-awaitable value with an awaitable
def _wrap_async(value):
    if inspect.isawaitable(value):
        return value
    future = asyncio.Future()  # This is awaitable
    future.set_result(value)
    return future

# This function exists so that bot is garbage collected after the function
# ends.
async def _run(token, **bot_kwargs):
    bot = commands.Bot(**bot_kwargs)

    # Helper for improving compatibility between discord.py v1.x and v2.x
    bot.wrap_async = _wrap_async

    # Get list of extensions to load
    extensions = list(LOAD_ON_STARTUP)
    if int(os.environ.get("JOSHGONE_REPL", "0")):
        extensions.append("repl")

    # Load extensions
    for module in extensions:
        await bot.load_extension(f"jgm.extensions.{module}")
        print(f"Loaded {module}")
    print(f"All extensions loaded: [{', '.join(extensions)}]")

    try:
        await bot.start(token)
    finally:
        # Force the GC to run before closing the loop so objects that use
        # loop.call_soon in their .__del__ methods can be garbage collected
        # without giving an annoying `Exception ignored in <something>
        # RuntimeError: Event loop is closed`.
        del bot
        import gc
        gc.collect()

def run(token, **bot_kwargs):
    """Runs JoshGone with the provided token and bot options"""
    # The actual bot is run and deleted inside the _run function.
    try:
        asyncio.run(_run(token, **bot_kwargs))
    except KeyboardInterrupt:
        pass

def main():
    """Entry point to run JoshGone"""
    run(
        os.environ["JOSHGONE_TOKEN"],
        command_prefix=command_prefix,
        intents=intents,
        help_command=help_command
    )
