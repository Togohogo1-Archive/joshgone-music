"""Provides a better FFmpeg PCM audio source

The builtin class passes creationflags=CREATE_NO_WINDOW to the subprocess. I'm
not entirely sure why this slows down the process's creation. I am sure that,
at least on my computer, that a new window doesn't appear everytime a source
is made.

If, for some reason, each FFmpeg subprocess is actually making a window, you
can pass creationflags=subprocess.CREATE_NO_WINDOW to the constructor to set it
again.

Source code is adapted from discord/player.py.

"""
import sys
import subprocess

import discord

__all__ = ("FFmpegPCMAudio",)

class FFmpegPCMAudio(discord.FFmpegPCMAudio):

    # Default is 0 for no flags (used to be subprocess.CREATE_NO_WINDOW). See
    # the documentation for discord.FFmpegPCMAudio for more info on kwargs.
    def __init__(self, source, *, creationflags=0, **kwargs):
        # The superclass's __init__ calls self._spawn_process, so we need to
        # set creation flags before then, meaning this line can't be after the
        # super().__init__ call.
        self.creationflags = creationflags
        super().__init__(source, **kwargs)

    def _spawn_process(self, args, **subprocess_kwargs):
        # Creation flags only work in Windows
        if sys.platform == "win32":
            subprocess_kwargs["creationflags"] = self.creationflags
        try:
            return subprocess.Popen(args, **subprocess_kwargs)
        except FileNotFoundError:
            if isinstance(args, str):
                executable = args.partition(" ")[0]
            else:
                executable = args[0]
            message = f"{executable} was not found."
            raise discord.ClientException(message) from None
        except subprocess.SubprocessError as exc:
            message = f"Popen failed: {type(exc).__name__}: {exc}"
            raise discord.ClientException(message) from exc
