"""Match messages to chants"""

import asyncio
import os
import re
import time

import aiosqlite
from discord.ext import commands

class When(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="when")
    async def when_command(self, ctx, *words):
        """Return all chant names that match the given words

        Based on https://github.com/rjrodger/patrun.

        Assume the following chants exist:
            %chants add when/A  a
            %chants add when/B  b
            %chants add when/C  c
            %chants add when/C2 c
            %chants add when/AB a b
            %chants add when/AD a d
            %chants add when/DA d a

        Usage:
            %when a     -> when/A           # exact match
            %when b     -> when/B           # exact match
            %when c     -> when/C when/C2   # multiple chants can be sent
            %when a b   -> when/AB          # "a b" more words than "a"
            %when a c   -> when/A           # "a" before "b"
            %when b c   -> when/B           # "b" before "c"
            %when a d   -> when/AD when/DA  # chant word order doesn't matter
            %when b a   -> when/AD when/DA  # %when word order doesn't matter

        Chant structure:
            %chants add when/<name> [words...] [-- text]

        Only chants whose names start with "when/" are checked.

        Chants are only sent if all chant words are present in %when words.

        When multiple chants can be sent, more chant words beat less, and
        alphabetically earlier chant words beat later ones.

        The chants names are sent in alphabetical order.

        """
        if ctx.guild is None:
            return
        if not await self._check_running(ctx.guild.id):
            return
        matching_chants = await self.get_matching_when_chants(
            words,
            ctx.guild.id,
        )
        await ctx.reply(
            f"Matches {len(matching_chants)}"
            f" {' '.join(sorted(matching_chants))}",
            mention_author=False,
        )

    @commands.command(name="do")
    async def do_command(self, ctx, *words):
        """Replies with all chants whose name matchs the given words

        Each matching chant is sent in separate messages.

        See %help when for more info.

        """
        if ctx.guild is None:
            return
        if not await self._check_running(ctx.guild.id):
            return
        matching_chants = await self.get_matching_when_chants(
            words,
            ctx.guild.id,
        )
        for name in sorted(matching_chants):
            text = matching_chants[name]["text"]
            await ctx.reply(text, mention_author=False)
            await asyncio.sleep(0.5)
            if not await self._check_running(ctx.guild.id):
                return

    @commands.command(name="_invalidate_when", hidden=True)
    @commands.is_owner()
    async def invalidate_command(self, ctx):
        """Invalidates the %when cache for the current guild"""
        if ctx.guild is None:
            return
        if hasattr(self, "_when_chants"):
            self._when_chants.pop(guild_id, None)
        await ctx.send("Invalidated")

    async def _check_running(self, guild_id):
        # Return whether the server has %running on
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute(
                "SELECT running FROM server WHERE server_id = ? LIMIT 1;",
                [guild_id],
            ) as cursor:
                row = await cursor.fetchone()
                if row is None or not row[0]:
                    return False
        return True

    async def get_matching_when_chants(self, search, guild_id):
        """Return matching %when chants for the given search terms"""
        search = frozenset(search)
        chants = await self.get_when_chants(guild_id)
        # TODO: faster matching of chant words maybe (benchmark needed)
        matching = [
            name
            for name, chant in chants.items()
            if all(word in search for word in chant["words"])
        ]
        if not matching:
            return {}
        best_matches = max(len(chants[name]["words"]) for name in matching)
        best_words = max(
            chant["words"]
            for name, chant in chants.items()
            if len(chants[name]["words"]) == best_matches
        )
        return {
            name: chant
            for name, chant in chants.items()
            if chant["words"] == best_words
        }

    async def get_when_chants(self, guild_id):
        """Return %when chants for the given guild_id

        Do not modify the returned chants as they are cached between calls.

        """
        if not hasattr(self, "_when_chants"):
            when_chants = self._when_chants = {}
        else:
            when_chants = self._when_chants
        # Return cached copy if possible
        timestamp, chants = when_chants.get(guild_id, (0, None))
        if timestamp > time.time():
            return chants
        # Retrieve from database
        chants = {}
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute(
                "SELECT chant_name, chant_text FROM chants"
                " WHERE server_id = ? AND chant_name GLOB 'when/*';",
                [guild_id],
            ) as cursor:
                async for [name, text] in cursor:
                    assert name.startswith("when/")
                    chants[name] = {"raw": text}
        # Extract chant words and response text
        for name, chant in chants.items():
            words = []
            i = 0
            for match in re.finditer(r"\S+", chant["raw"]):
                i = match.end()
                part = match[0]
                if part == "--":
                    break
                elif part.startswith("---"):
                    # This is in case a chant wants to match -- or similar
                    part = part[2:]
                    words.append(part)
                elif part.startswith("-"):
                    pass  # ignore unknown options (no way to error)
                else:
                    words.append(part)
            chant["words"] = sorted(words)
            chant["text"] = chant["raw"][i:]
        # Set timeout to refresh chants
        timeout = 15
        timestamp = time.time() + timeout
        when_chants[guild_id] = timestamp, chants
        task = asyncio.create_task(self._timeout_when_chants(
            guild_id,
            timestamp,
            timeout=timeout,
        ))
        task.add_done_callback(lambda task: task.exception())
        return chants

    async def _timeout_when_chants(self, guild_id, timestamp, *, timeout=15):
        # Remove cached %when chants for the given guild_id after a timeout
        await asyncio.sleep(timeout)
        if not hasattr(self, "_when_chants"):
            return
        when_chants = self._when_chants
        if timestamp == when_chants.get(guild_id, (0, None))[0]:
            del when_chants[guild_id]

def setup(bot):
    bot.add_cog(When(bot))
