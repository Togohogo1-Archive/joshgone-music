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
        self.read_count = 0

        # Allow the rewinding of 5 times the maximum rewind time (15 seconds)
        # _MAX_BUF_SZ is the number of 20ms "packets"
        # Assume 20ms has an upper bound of 2**12 = 4096 bytes (actually closer to 3840)
        # deque then takes up approx 4096 * (1/20) * 1000 * 15 * 5 = 15360000 bytes = 15MB upper bound
        self._MAX_BUF_SZ = 5 * 15 * 50

        self.buffer = deque(maxlen=self._MAX_BUF_SZ)
        self.unread_buffer = deque(maxlen=self._MAX_BUF_SZ)
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

    # bug when unloading/reloading (ff doesn't work)
    def read(self) -> bytes:
        # data in unread_buf guaranteed to be valid:
        if self.unread_buffer:  # Evaluates to true if unread_buffer has contents
            ret = self.unread_buffer.popleft()  # First inserted bytestring
        else:
            ret = self._stdout.read(OpusEncoder.FRAME_SIZE)
            if len(ret) != OpusEncoder.FRAME_SIZE:
                return b''

        # Valid data
        self.read_count += 1
        self.buffer.append(ret)
        return ret

    def seek_bw(self, t_sec):
        # Move from buffer to unread_buffer
        for _ in range(t_sec*50):
            if not self.buffer:
                break
            self.unread_buffer.appendleft(self.buffer.pop())
            self.read_count -= 1

    def seek_fw(self, t_sec):
        for _ in range(t_sec*50):  # t_sec*1000 / 20 = t_sec*50 reads
            self.read()