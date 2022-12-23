"""Provides an exec command for running Brainf*** code

Adapted from extensions/exec.py

"""
import asyncio
import collections

import discord
from discord.ext import commands

class BFExecutor:

    def __init__(self, program, channel, author_id, executor_id):
        self.program = program
        self.channel = channel
        self.author_id = author_id
        self.executor_id = executor_id
        # Task stuff
        self._task = None
        self._runner = self._run()
        self._steps = 0
        # State needed for running
        self._data = bytearray(30000)
        self._paired_brackets = {}
        self._unpaired_brackets = []
        self._data_ptr = 0
        self._program_ptr = 0
        self._out = collections.deque()
        self._inp = collections.deque()
        # Set when finished
        self.stopped_event = asyncio.Event()

    def start(self):
        self.task = asyncio.Task(self._wrap(self._runner.asend(None)))

    def stop(self):
        if self.task is not None:
            self.task.cancel()
        else:
            self.task = asyncio.Task(self._wrap(
                self._runner.athrow(asyncio.CancelledError))
            )

    async def _wrap(self, coroutine):
        try:
            await coroutine
        except StopAsyncIteration:
            pass

    async def _run(self):
        try:
            # Run until the program ends
            while self._program_ptr < len(self.program):

                # Return control to asyncio loop every now and then
                self._steps += 1
                if self._steps % 10000 == 0:
                    await asyncio.sleep(0.1)

                # Get operation and act on it
                char = self.program[self._program_ptr]

                if char == "+":
                    value = self._data[self._data_ptr]
                    self._data[self._data_ptr] = (value + 1) % 256

                elif char == "-":
                    value = self._data[self._data_ptr]
                    self._data[self._data_ptr] = (value - 1) % 256

                elif char == "<":
                    # Don't allow the pointer to go left of zero
                    self._data_ptr = max(self._data_ptr - 1, 0)

                elif char == ">":
                    # Don't allow the pointer to go right of memory
                    self._data_ptr = min(
                        self._data_ptr + 1,
                        len(self._data) - 1,
                    )

                elif char == ",":
                    if not self._inp:
                        if self._out:
                            await self.channel.send(bytes(self._out).decode())
                            self._out.clear()
                        self.task = None
                        await self.channel.send(
                            f"*ID={self.executor_id} Awaiting input*"
                        )
                        yield "input"
                    inp = self._inp.popleft()
                    if inp is not None:
                        self._data[self._data_ptr] = inp

                elif char == ".":
                    value = self._data[self._data_ptr]
                    self._out.append(value)
                    # Flush buffer if value was a newline or if buffer full
                    if value == ord("\n") or len(self._out) >= 2000:
                        await self.channel.send(bytes(self._out).decode())
                        self._out.clear()

                elif char == "[":
                    if self._program_ptr not in self._paired_brackets:
                        # add to stack of unpaired brackets
                        self._unpaired_brackets.append(self._program_ptr)
                    if self._data[self._data_ptr] == 0:
                        if self._program_ptr in self._paired_brackets:
                            self._program_ptr = self._paired_brackets[
                                self._program_ptr
                            ]
                        else:
                            # skip to matching ]
                            count = 1
                            self._program_ptr += 1
                            while self._program_ptr < len(self.program):
                                if self.program[self._program_ptr] == "[":
                                    self._unpaired_brackets.append(
                                        self._program_ptr
                                    )
                                    count += 1
                                if self.program[self._program_ptr] == "]":
                                    other_ptr = self._unpaired_brackets.pop()
                                    self._paired_brackets[
                                        self._program_ptr
                                    ] = other_ptr
                                    self._paired_brackets[
                                        other_ptr
                                    ] = self._program_ptr
                                    count -= 1
                                    if count == 0:
                                        break
                                self._program_ptr += 1
                            if self._program_ptr == len(self.program):
                                self._program_ptr -= 1

                elif char == "]":
                    if self._program_ptr not in self._paired_brackets:
                        if self._unpaired_brackets:
                            other_ptr = self._unpaired_brackets.pop()
                            self._paired_brackets[
                                self._program_ptr
                            ] = other_ptr
                            self._paired_brackets[
                                other_ptr
                            ] = self._program_ptr
                        else:
                            # Loop to start on unmatched ending brackets
                            self._paired_brackets[self._program_ptr] = -1
                    if self._data[self._data_ptr] != 0:
                        self._program_ptr = self._paired_brackets[
                            self._program_ptr
                        ]

                self._program_ptr += 1

            if self._out:
                await self.channel.send(bytes(self._out).decode())

        except asyncio.CancelledError:
            await self.channel.send(f"*ID={self.executor_id} Cancelled*")

        except BaseException as e:
            await self.channel.send(
                f"*ID={self.executor_id} Error while executing BF:* `{e!r}`"
            )

        else:
            await self.channel.send(f"*ID={self.executor_id} Finished*")

        finally:
            self.stopped_event.set()

class ExecBF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.executors = {}
        self._next_executor_id = 0

    def cog_unload(self):
        for executor in self.executors.values():
            executor.stop()

    @staticmethod
    def clean_code(text):
        """Remove backticks from a Discord message's content

        Examples:
            clean_code("`69420`") == "69420"
            clean_code("``69420``") == "69420"
            clean_code("```bf\n69420\n```") == "69420"

        """
        # Check if the text is multiline or not
        if "\n" not in text.strip().replace("\r", "\n"):
            # It's a single line - remove wrapping backticks (up to 2)
            for _ in range(2):
                if len(text) >= 2 and text[0] == text[-1] == "`":
                    text = text[1:-1]
                else:
                    break
            return text
        # It's on multiple lines - remove wrapping code fences
        lines = text.splitlines(keepends=True)
        if lines[0].strip() != "```bf":
            raise ValueError(r"First line has to be \`\`\`bf")
        if lines[-1].strip() != "```":
            raise ValueError(r"Last line has to be \`\`\`")
        del lines[0]
        del lines[-1]
        text = "".join(lines)
        return text

    @commands.group(hidden=True, invoke_without_command=True)
    async def bf(self, ctx):
        """Command group for executing and managing Brainf*** code"""
        raise commands.CommandNotFound("Please use a valid subcommand")

    @bf.command()
    async def exec(self, ctx, *, text=""):
        """Executes some code"""
        # Remove backticks
        try:
            text = self.clean_code(text)
        except ValueError as e:
            await ctx.send(f"Error cleaning code: {e!s}")
            return
        # Check if user can make another executor
        if sum(
            executor.author_id == ctx.author.id
            for executor in self.executors.values()
        ) >= 5:
            raise RuntimeError("Cannot create another executor")
        # Get next executor id
        executor_id = self._next_executor_id
        self._next_executor_id += 1
        # Create the executor instance and start it
        executor = BFExecutor(text, ctx.channel, ctx.author.id, executor_id)
        self.executors[executor_id] = executor
        try:
            executor.start()
            # Tell user the executor ID
            await ctx.send(f"*Running under ID={executor_id}*")
            # Wait until the executor has stopped
            await executor.stopped_event.wait()
        finally:
            # Remove the executor
            self.executors.pop(executor_id)

    @bf.command(ignore_extra=False)
    async def list(self, ctx):
        """Lists all executor IDs"""
        await ctx.send(", ".join(map(str, self.executors.keys())))

    @bf.command(ignore_extra=False)
    async def listmine(self, ctx):
        """Lists author's executor IDs"""
        await ctx.send(", ".join(map(str, (
            executor_id
            for executor_id, executor in self.executors.items()
            if executor.author_id == ctx.author.id
        ))))

    @bf.command(ignore_extra=False)
    async def cancel(self, ctx, id_: int):
        """Cancels the executor with the given ID"""
        if id_ not in self.executors:
            return
        executor = self.executors[id_]
        if ctx.author.id not in [executor.author_id, self.bot.owner_id]:
            raise RuntimeError("Executor is not author's")
        executor.stop()

    @bf.command(ignore_extra=False)
    async def cancelmine(self, ctx):
        """Cancels author's executors"""
        for executor in self.executors.values():
            if executor.author_id != ctx.author.id:
                continue
            executor.stop()

    @bf.command(ignore_extra=False)
    @commands.is_owner()
    async def cancelall(self, ctx):
        """Cancels all executors"""
        for executor in self.executors.values():
            executor.stop()

    @bf.command(ignore_extra=False)
    async def input(self, ctx, id_: int, *, text=""):
        """Feeds the rest of the message into the executor with the given ID"""
        if id_ not in self.executors:
            return
        executor = self.executors[id_]
        if executor.task is not None:
            await ctx.send("Executor is still running")
            return
        if text == "\\":
            inp = [None]
        elif text.endswith("\\"):
            inp = text[-1:].encode()
        else:
            inp = f"{text}\n".encode()
        executor._inp.extend(inp)
        executor.start()

def setup(bot):
    bot.add_cog(ExecBF(bot))
