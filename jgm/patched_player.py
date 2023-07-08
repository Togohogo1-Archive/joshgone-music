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
from collections import deque

import discord
from discord.opus import Encoder as OpusEncoder

__all__ = ("FFmpegPCMAudio",)

class FFmpegPCMAudio(discord.FFmpegPCMAudio):
    # Default is 0 for no flags (used to be subprocess.CREATE_NO_WINDOW). See
    # the documentation for discord.FFmpegPCMAudio for more info on kwargs.
    def __init__(self, source, *, creationflags=0, **kwargs):
        # The superclass's __init__ calls self._spawn_process, so we need to
        # set creation flags before then, meaning this line can't be after the
        # super().__init__ call.
        self.creationflags = creationflags

        # MAX_BUF_SZ is the number of frames, frames can range from 10ms to 40ms
        # Assume 20ms (normal frame size) upper bound of 2**12 = 4096 bytes (actually closer to 3840)
        # deque then takes up approx 4096 * (1/20) * 1000 * 15 * 5 = 15360000 bytes = 15MB upper bound
        # Seek forward maximum of 15 seconds, in worse case (0.25 speed), that equiv to 60 seconds of frames
        # MAX_BUF_SZ can hold a maximum of 75 seconds of frames (extra padding)
        self.MAX_BUF_SZ = 5 * 15 * 50
        self.buffer = deque(maxlen=self.MAX_BUF_SZ)
        self.unread_buffer = deque(maxlen=self.MAX_BUF_SZ)

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

    def read(self):
        if self.unread_buffer:
            ret = self.unread_buffer.popleft()
        else:
            ret = self._stdout.read(OpusEncoder.FRAME_SIZE)
            if len(ret) != OpusEncoder.FRAME_SIZE:
                return b''
        # No empty binary strings in the buffer (otherwise will overflow)
        # All frames appended in the buffer guaranteed to be size of `OpusEncoder.FRAME_SIZE`
        self.buffer.append(ret)
        return ret

    # Equivalent of `read` but does the opposite
    def unread(self):
        if self.buffer:
            ret = self.buffer.pop()
            self.unread_buffer.appendleft(ret)
            return ret
        # Nothing to unread
        return b''
