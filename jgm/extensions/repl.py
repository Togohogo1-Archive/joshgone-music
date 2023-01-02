import asyncio
import asyncio.__main__ as asyncio_main

# Imported so the REPL can use them
import discord
from discord.ext import commands

# Subclass of AsyncIOInteractiveConsole that doesn't use globals
import types
import inspect
import concurrent.futures
import asyncio.futures

# Pig repl
import sys
sys.ps1 = "🐷🐷🐷 ┃"
sys.ps2 = "🐽🐽🐽 ┆"


class AsyncIOInteractiveConsole(asyncio_main.AsyncIOInteractiveConsole):

    def __init__(self, locals, loop):
        super().__init__(locals, loop)
        self.future = None
        self.interrupted = False

    def runcode(self, code):
        future = concurrent.futures.Future()

        def callback():
            self.future = None
            self.interrupted = False

            func = types.FunctionType(code, self.locals)
            try:
                coro = func()
            except SystemExit:
                raise
            except KeyboardInterrupt as ex:
                self.interrupted = True
                future.set_exception(ex)
                return
            except BaseException as ex:
                future.set_exception(ex)
                return

            if not inspect.iscoroutine(coro):
                future.set_result(coro)
                return

            try:
                self.future = self.loop.create_task(coro)
                asyncio.futures._chain_future(self.future, future)
            except BaseException as exc:
                future.set_exception(exc)

        self.loop.call_soon_threadsafe(callback)

        try:
            return future.result()
        except SystemExit:
            raise
        except BaseException:
            if self.interrupted:
                self.write("\nKeyboardInterrupt\n")
            else:
                self.showtraceback()

# Subclass of REPLThread that doesn't stop the loop (joshgone.py handles that)
# Adapted from: Python39/Lib/asyncio/__main__.py
import sys
import warnings

class REPLNoStopThread(asyncio_main.REPLThread):

    def __init__(self, console):
        super().__init__()
        self.console = console

    def run(self):
        try:
            banner = (
                f'asyncio REPL {sys.version} on {sys.platform}\n'
                f'Use "await" directly instead of "asyncio.run()".\n'
                f'Type "help", "copyright", "credits" or "license" '
                f'for more information.\n'
                f'{getattr(sys, "ps1", ">>> ")}import asyncio'
            )

            self.console.interact(
                banner=banner,
                exitmsg='exiting asyncio REPL...')
        finally:
            warnings.filterwarnings(
                'ignore',
                message=r'^coroutine .* was never awaited$',
                category=RuntimeWarning)

            # The main thread will stop it. Otherwise, this chokes the cleanup
            # code in discord.py.
            # loop.call_soon_threadsafe(loop.stop)


class Repl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thread = None

    @commands.Cog.listener()
    async def on_ready(self):
        # Make sure the REPL isn't initialized twice
        if self.thread is not None:
            return
        # Starts the REPL using asyncio's code
        variables = globals()
        loop = asyncio_main.loop = asyncio.get_running_loop()
        console = AsyncIOInteractiveConsole(variables, loop)
        self.thread = REPLNoStopThread(console)
        self.thread.daemon = True
        self.thread.start()

# Utility method to send a message that will be processed using `process`
async def self_process(text_channel, content):
    message = await text_channel.send(content)
    return await process(message)

# Utility method to temporarily disable the bot check and to process the message
async def process(message):
    old_skip_check = bot._skip_check
    bot._skip_check = lambda x, y: False if x == y else old_skip_check(x, y)
    try:
        ctx = await bot.get_context(message)
        return await bot.invoke(ctx)
    finally:
        bot._skip_check = old_skip_check

def setup(_bot):
    global bot
    bot = _bot
    bot.add_cog(Repl(bot))
