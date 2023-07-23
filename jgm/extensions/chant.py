import os
import typing
import re
import asyncio
import math

import aiosqlite
import discord
from discord.ext import commands
from discord.utils import escape_markdown

class Dashes(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument:
            raise commands.BadArgument("argument does not consist of dashes only")
        if not all(char == "-" for char in argument):
            raise commands.BadArgument("argument does not consist of dashes only")
        return "-"

def match(pattern: str, string: str) -> bool:
    """Return whether pattern matches string in linear time

    - pattern: simple glob-ish pattern
    - string: string to match against

    The only special characters supported are ? and %, for matching one and any
    number of characters respectively.

    Adapted from https://research.swtch.com/glob.

    """
    # Fast paths for specific simple cases
    if "?" not in pattern:
        any_count = pattern.count("%")
        if any_count == 0:  # Simple equality
            return string == pattern
        if any_count == 1:  # Simple prefix + suffix
            prefix, _, suffix = pattern.partition("%")
            return (
                len(prefix) + len(suffix) < len(string)  # Ensure no overlap
                and string.startswith(prefix)
                and string.endswith(suffix)
            )

    # General code
    pi = pj = 0
    i = j = 0
    while pi < len(pattern) or i < len(string):
        if pi < len(pattern):
            char = pattern[pi]
            if char == "?":
                if i < len(string):
                    pi += 1
                    i += 1
                    continue
            elif char == "%":
                pi, pj = pi + 1, pi
                j = i + 1
                continue
            else:
                if i < len(string) and string[i] == char:
                    pi += 1
                    i += 1
                    continue
        if 0 < j <= len(string):
            pi, pj = pj, 0
            i, j = j, 0
            continue
        return False
    return True

class Chant(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="chants", ignore_extra=False, pass_context=True, invoke_without_command=True)
    async def _chants(self, ctx):
        """Configure chants"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_name FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                names = [row[0] async for row in cursor]
        for i, name in enumerate(names):
            names[i] = f"`{name}`"
        length = len(names)
        if not names:
            names = ["None"]
        for i in range(1, len(names)):
            names[i] = f", {names[i]}"
        names.insert(0, f"Chants [{length}]: ")
        for message in self.pack(names):
            await ctx.send(message)

    @staticmethod
    def pack(strings, *, maxlen=2000):
        current = []
        length = 0
        for name in strings:
            if len(name) + length > maxlen:
                yield "".join(current)
                current = []
                length = 0
            length += len(name)
            current.append(name)
        if current:
            yield "".join(current)

    @_chants.command(name="find", ignore_extra=False)
    async def _find(self, ctx, name_pattern: str):
        """Find chants whose names contain or match the given pattern

        Assume the following chants exist:
            %chants add amogus   -
            %chants add amoguise -
            %chants add mongus   -
            %chants add mongue   -

        Usage:
            %chants find amogus  -> amogus           # exact match
            %chants find amo%    -> amogus, amoguise # prefix
            %chants find %gus    -> amogus, mongus   # suffix
            %chants find mongu?  -> mongus, mongue   # any character
            %chants find %m?gu%e -> amoguise         # combine them
            %chants find gui     -> amoguise         # "gui" in amoguise

        The only special characters supported are ? and %, for matching one and
        any number of characters respectively.
        """
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute(
                "SELECT chant_name FROM chants WHERE server_id = ?;",
                [ctx.guild.id],
            ) as cursor:
                names = [
                    f"`{name}`"
                    async for [name] in cursor
                    if match(name_pattern, name) or name_pattern in name
                ]
        length = len(names)
        if not names:
            names = ["None"]
        for i in range(1, len(names)):
            names[i] = f", {names[i]}"
        names.insert(0, f"Found {length}: ")
        for message in self.pack(names):
            await ctx.send(message)

    @_chants.command(name="search", ignore_extra=False)
    async def _search(self, ctx, name_pattern: str, max_amount: typing.Optional[int] = -1):
        """Find chants whose contents contain or match the given pattern

        Can use substring or glob-ish pattern match
        """
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_name, chant_text FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                chants = [row async for row in cursor]
        found = []
        for name, text in chants:
            if len(found) == max_amount:
                break
            if not (match(name_pattern, text) or name_pattern in text):
                continue
            found.append(f"`{name}`")
        length = len(found)
        if not found:
            found = ["None"]
        for i in range(1, len(found)):
            found[i] = f", {found[i]}"
        found.insert(0, f"Found {length}: ")
        for message in self.pack(found):
            await ctx.send(message)

    @_chants.command(name="regexfind", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _regexlist(self, ctx, max_amount: typing.Optional[int] = -1, *, regex):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_name FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                names = [row[0] async for row in cursor]
        found = []
        for name in names:
            if len(found) == max_amount:
                break
            if not re.search(regex, name):
                continue
            found.append(f"`{name}`")
        length = len(found)
        if not found:
            found = ["None"]
        for i in range(1, len(found)):
            found[i] = f", {found[i]}"
        found.insert(0, f"Found {length}: ")
        for message in self.pack(found):
            await ctx.send(message)

    @_chants.command(name="regexsearch", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _regexsearch(self, ctx, max_amount: typing.Optional[int] = -1, *, regex):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_name, chant_text FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                chants = [row async for row in cursor]
        found = []
        for name, text in chants:
            if len(found) == max_amount:
                break
            if not re.search(regex, text):
                continue
            found.append(f"`{name}`")
        length = len(found)
        if not found:
            found = ["None"]
        for i in range(1, len(found)):
            found[i] = f", {found[i]}"
        found.insert(0, f"Found {length}: ")
        for message in self.pack(found):
            await ctx.send(message)

    @_chants.command(name="regexremove", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _regexremove(self, ctx, max_amount: typing.Optional[int] = -1, *, regex):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_name FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                names = [row[0] async for row in cursor]
        removed = []
        for name in names:
            if len(removed) == max_amount:
                break
            if not re.search(regex, name):
                continue
            removed.append(f"`{name}`")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            for name in removed:
                await db.execute("DELETE FROM chants WHERE server_id = ? AND chant_name = ?;", (ctx.guild.id, name))
            await db.commit()
        length = len(removed)
        if not removed:
            removed = ["None"]
        for i in range(1, len(removed)):
            removed[i] = f", {removed[i]}"
        removed.insert(0, f"Removed {length}: ")
        for message in self.pack(removed):
            await ctx.send(message)
        if cron := self.bot.get_cog("Cron"):
            try:
                await cron.notify_chants_updated({"guild_id": ctx.guild.id})
            except Exception as e:
                print(f'Error notifying cron cog: {e!r}')

    @_chants.command(name="update")
    @commands.check_any(
        commands.has_permissions(manage_messages=True),
        commands.has_role("enchanter"),
    )
    async def _update(self, ctx, name, *, text):
        """Update a chant

        This will silently overwrite any previous chant with the same name.
        """
        if len(name) > 35:
            raise ValueError("name too long (length over 35)")
        if not name.isprintable():
            raise ValueError(f"Name not printable: {name!r}")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            # Check if user can actually change it
            async with db.execute("SELECT owner_id FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    current = None
                else:
                    current = row[0]
            # If there's already an owner, make sure they are allowed to change it
            if current is not None:
                if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                    await ctx.send("You are not allowed to change this chant's owner")
                    return
            # Update the chant
            if current is None:
                current = ctx.author.id
            async with db.execute("SELECT COUNT(*) FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()):
                    raise ValueError("could not get count of chants")
                if row[0] >= 500:
                    raise ValueError(f"too many chants stored: {row[0]}")
            await db.execute("INSERT OR REPLACE INTO chants VALUES (?, ?, ?, ?);", (ctx.guild.id, name, text, current))
            await db.commit()
        await ctx.send(f"Updated chant `{name}`")
        if cron := self.bot.get_cog("Cron"):
            try:
                await cron.notify_chants_updated({"guild_id": ctx.guild.id})
            except Exception as e:
                print(f'Error notifying cron cog: {e!r}')

    @_chants.command(name="add")
    @commands.check_any(
        commands.has_permissions(manage_messages=True),
        commands.has_role("enchanter"),
    )
    async def _add(self, ctx, name, *, text):
        """Add a chant

        This will fail if a chant with the same name already exists.
        """
        if len(name) > 35:
            raise ValueError("Name too long (length over 35)")
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
            raise ValueError("Name does not conform to the regex ^[a-zA-Z_][a-zA-Z0-9_]*$")
        if not name.isprintable():
            raise ValueError(f"Name not printable: {name!r}")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_text FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if (row := await cursor.fetchone()):
                    await ctx.send(f"Chant `{name}` exists")
                    return
            async with db.execute("SELECT COUNT(*) FROM chants WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()):
                    raise ValueError("could not get count of chants")
                if row[0] >= 500:
                    raise ValueError(f"too many chants stored: {row[0]}")
            await db.execute("INSERT INTO chants VALUES (?, ?, ?, ?);", (ctx.guild.id, name, text, ctx.author.id))
            await db.commit()
        await ctx.send(f"Added chant `{name}`")
        if cron := self.bot.get_cog("Cron"):
            try:
                await cron.notify_chants_updated({"guild_id": ctx.guild.id})
            except Exception as e:
                print(f'Error notifying cron cog: {e!r}')

    @commands.command(name="h1", ignore_extra=False)
    async def _check(self, ctx, name: str):
        """Output the text for a single chant"""
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
            raise ValueError("Not a valid chant name")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT chant_text FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if (row := await cursor.fetchone()):
                    await ctx.send(row[0])
                else:
                    await ctx.send(f"Chant `{name}` doesn't exist")

    @_chants.command(name="owner", ignore_extra=False)
    async def _owner(self, ctx, name: str, new_owner: typing.Union[discord.Member, Dashes] = None):
        """Check or set the owner of a chant

        To change a chant's owner, either the chant must have no owner, or you
        are the bot owner, guild owner, or the chant owner.

        To clear the owner, pass "-" as the new owner.

        Usage:
            %chants owner chant             ->  gets the chant's current owner
            %chants owner chant GeeTransit  ->  make GeeTransit the chant owner
            %chants owner chant -           ->  removes the chant's owner
        """
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT owner_id FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await ctx.send(f"Chant `{name}` doesn't exist")
                    return
                current = row[0]
        # Get owner
        if new_owner is None:
            if current is None:
                await ctx.send(f"Chant `{name}` has no owner")
            else:
                await ctx.send(f"Chant `{name}` owner is {ctx.guild.get_member(current).name}")
            return
        # If there's already an owner, make sure they are allowed to change it
        if current is not None:
            if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                await ctx.send("You are not allowed to change this chant's owner")
                return
        # Store the chant's new owner
        if new_owner == "-":
            new_owner_value = None
        else:
            new_owner_value = new_owner.id
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("UPDATE chants SET owner_id = ? WHERE server_id = ? AND chant_name = ?;", (new_owner_value, ctx.guild.id, name))
            await db.commit()
        # Respond with the new owner
        if new_owner == "-":
            await ctx.send(f"Chant `{name}` now has no owner")
        else:
            await ctx.send(f"Chant `{name}` owner now is {new_owner.name}")

    @_chants.command(name="remove", ignore_extra=False)
    @commands.check_any(
        commands.has_permissions(manage_messages=True),
        commands.has_role("enchanter"),
    )
    async def _remove(self, ctx, name: str):
        """Remove a chant"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            # Check if user can actually change it
            async with db.execute("SELECT owner_id FROM chants WHERE server_id = ? AND chant_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    current = None
                else:
                    current = row[0]
            # If there's already an owner, make sure they are allowed to change it
            if current is not None:
                if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                    await ctx.send("You are not allowed to change this chant's owner")
                    return
            # Delete the chant
            await db.execute("DELETE FROM chants WHERE server_id = ? AND chant_name = ?;", (ctx.guild.id, name))
            await db.commit()
        await ctx.send(f"Removed chant `{name}`")
        if cron := self.bot.get_cog("Cron"):
            try:
                await cron.notify_chants_updated({"guild_id": ctx.guild.id})
            except Exception as e:
                print(f'Error notifying cron cog: {e!r}')

def setup(bot):
    return bot.add_cog(Chant(bot))
