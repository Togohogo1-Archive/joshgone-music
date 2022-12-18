import os

import discord
from discord.ext import commands

# These extensions are loaded automatically on startup
LOAD_ON_STARTUP = (
    "admin", "censor", "chant", "music", "database", "thicc", "gee", "remind",
    "split", "get", "relay", "solver", "sort", "info", "exec", "execbf",
)

# We need intents to resolve a name to a Member object
intents = discord.Intents.default()
intents.members = True

# Our prefix is % or @joshgone
command_prefix = commands.when_mentioned_or("%")

# This function exists so that bot is garbage collected after the function
# ends. The loop's .close method is overridden to do nothing while the bot is
# running. The loop is returned to be closed by the caller.
def _run(token, **bot_kwargs):
    bot = commands.Bot(**bot_kwargs)

    # Get list of extensions to load
    extensions = list(LOAD_ON_STARTUP)
    if int(os.environ.get("JOSHGONE_REPL", "0")):
        extensions.append("repl")

    # Load extensions
    for module in extensions:
        bot.load_extension(f"extensions.{module}")
        print(f"Loaded {module}")
    print(f"All extensions loaded: [{', '.join(extensions)}]")

    # Override the .close method to do nothing
    close = bot.loop.close
    bot.loop.close = lambda: None

    bot.run(token)

    # Restore the .close method.
    bot.loop.close = close
    return bot.loop

def run(token, **bot_kwargs):
    """Runs JoshGone with the provided token and bot options"""
    # The actual bot is run and deleted inside the _run function.
    loop = _run(token, **bot_kwargs)

    # Waits a little bit before closing the loop so objects that use
    # loop.call_soon in their .__del__ methods can be garbage collected without
    # giving an annoying `Exception ignored in <something> RuntimeError: Event
    # loop is closed`.
    try:
        loop.call_later(0.1, loop.stop)
        loop.run_forever()
    finally:
        loop.close()

def main():
    """Entry point to run JoshGone"""
    run(
        os.environ["JOSHGONE_TOKEN"],
        command_prefix=command_prefix,
        intents=intents,
    )

if __name__ == "__main__":
    main()
