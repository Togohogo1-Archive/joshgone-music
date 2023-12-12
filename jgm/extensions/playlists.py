import os
import typing
import re
import asyncio
import math

import aiosqlite
import discord
from discord.ext import commands
from discord.utils import escape_markdown
from discord.ext.commands import BucketType

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

class Playlists(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["li"], name="playlists", ignore_extra=False, pass_context=True, invoke_without_command=True)
    @commands.cooldown(1, 1, BucketType.user)
    async def _playlists(self, ctx):
        """Configure playlists"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_name FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                names = [row[0] async for row in cursor]
        for i, name in enumerate(names):
            names[i] = f"`{name}`"
        length = len(names)
        if not names:
            names = ["None"]
        for i in range(1, len(names)):
            names[i] = f", {names[i]}"
        names.insert(0, f"Playlists [{length}]: ")
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

    @_playlists.command(name="find", ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def _find(self, ctx, name_pattern: str):
        """Find playlists whose names contain or match the given pattern

        Assume the following playlists exist:
            %playlists add amogus   -
            %playlists add amoguise -
            %playlists add mongus   -
            %playlists add mongue   -

        Usage:
            %playlists find amogus  -> amogus           # exact match
            %playlists find amo%    -> amogus, amoguise # prefix
            %playlists find %gus    -> amogus, mongus   # suffix
            %playlists find mongu?  -> mongus, mongue   # any character
            %playlists find %m?gu%e -> amoguise         # combine them
            %playlists find gui     -> amoguise         # "gui" in amoguise

        The only special characters supported are ? and %, for matching one and
        any number of characters respectively.
        """
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute(
                "SELECT playlist_name FROM playlists WHERE server_id = ?;",
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

    @_playlists.command(name="search", ignore_extra=False)
    async def _search(self, ctx, name_pattern: str, max_amount: typing.Optional[int] = -1):
        """Find playlists whose contents contain or match the given pattern

        Can use substring or glob-ish pattern match
        """
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_name, playlist_text FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                playlists = [row async for row in cursor]
        found = []
        for name, text in playlists:
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

    @_playlists.command(name="regexfind", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _regexfind(self, ctx, max_amount: typing.Optional[int] = -1, *, regex):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_name FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
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

    @_playlists.command(name="regexsearch", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _regexsearch(self, ctx, max_amount: typing.Optional[int] = -1, *, regex):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_name, playlist_text FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                playlists = [row async for row in cursor]
        found = []
        for name, text in playlists:
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

    @_playlists.command(name="regexremove", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _regexremove(self, ctx, max_amount: typing.Optional[int] = -1, *, regex):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_name FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                names = [row[0] async for row in cursor]
        removed = []
        for name in names:
            if len(removed) == max_amount:
                break
            if not re.search(regex, name):
                continue
            removed.append(name)  # Don't wrap around with `` because need to remove from DB
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            for name in removed:
                await db.execute("DELETE FROM playlists WHERE server_id = ? AND playlist_name = ?;", (ctx.guild.id, name))
                name = f"`{name}`"
            await db.commit()
        length = len(removed)
        # Before cuz in `None` would refer to a chant named `None`
        removed = [f"`{i}`" for i in removed]
        if not removed:
            removed = ["None"]
        for i in range(1, len(removed)):
            removed[i] = f", {removed[i]}"
        removed.insert(0, f"Removed {length}: ")
        for message in self.pack(removed):
            await ctx.send(message)

    @_playlists.command(name="update")
    async def _update(self, ctx, name, *, text):
        """Update a playlist

        This will silently overwrite any previous playlist with the same name.
        """
        if len(name) > 35:
            raise ValueError("name too long (length over 35)")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            # Check if user can actually change it
            async with db.execute("SELECT owner_id FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if not (row := await cursor.fetchone()):
                    await ctx.send(f"Playlist `{name}` doesn't exist")
                    return
                else:
                    current = row[0]
            # If there's already an owner, make sure they are allowed to change it
            if current is not None:
                if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                    await ctx.send("You do not have permission to update this playlist.")
                    return
            # Update the playlist
            async with db.execute("SELECT COUNT(*) FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()):
                    raise ValueError("could not get count of playlists")
                if row[0] >= 500:
                    raise ValueError(f"too many playlists stored: {row[0]}")
            await db.execute("INSERT OR REPLACE INTO playlists VALUES (?, ?, ?, ?);", (ctx.guild.id, name, text, current))
            await db.commit()
        await ctx.send(f"Updated playlist `{name}`")

    @_playlists.command(name="rename")
    async def _rename(self, ctx, name, *, new_name):
        """Rename a playlist"""
        if not re.fullmatch(r"[a-zA-Z0-9_]*", new_name):
            raise ValueError("Name does not conform to the regex ^[a-zA-Z0-9_]*$")
        if len(name) > 35:
            raise ValueError("name too long (length over 35)")
        if name == new_name:
            await ctx.send("Playlist unchanged, new name is the same as old name")
            return
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            # Check if user can actually change it
            async with db.execute("SELECT owner_id FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if not (row := await cursor.fetchone()):
                    await ctx.send(f"Playlist `{name}` doesn't exist")
                    return
                else:
                    current = row[0]
            # Check if the new playlist name exists
            async with db.execute("SELECT playlist_text FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, new_name)) as cursor:
                if (row := await cursor.fetchone()):
                    await ctx.send(f"Playlist `{new_name}` exists")
                    return
            # If there's already an owner, make sure they are allowed to update it
            if current is not None:
                if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                    await ctx.send("You do not have permission to rename this playlist.")
                    return
            # Update the name
            await db.execute("UPDATE playlists SET playlist_name = ? WHERE playlist_name = ? AND server_id = ?;", (new_name, name, ctx.guild.id))
            await db.commit()
        await ctx.send(f"Renamed playlist `{name}` to `{new_name}`")

    @_playlists.command(name="add")
    @commands.cooldown(1, 5, BucketType.user)
    async def _add(self, ctx, name, *, text):
        """Add a playlist"""
        if len(name) > 35:
            raise ValueError("Name too long (length over 35)")
        if not re.fullmatch(r"[a-zA-Z0-9_]*", name):
            raise ValueError("Name does not conform to the regex ^[a-zA-Z0-9_]*$")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_text FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if (row := await cursor.fetchone()):
                    await ctx.send(f"Playlist `{name}` exists")
                    return
            async with db.execute("SELECT COUNT(*) FROM playlists WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()):
                    raise ValueError("could not get count of playlists")
                if row[0] >= 500:
                    raise ValueError(f"too many playlists stored: {row[0]}")
            await db.execute("INSERT INTO playlists VALUES (?, ?, ?, ?);", (ctx.guild.id, name, text, ctx.author.id))
            await db.commit()
        await ctx.send(f"Added playlist `{name}`")

    @commands.command(aliases=["h1"], name="check", ignore_extra=False)
    @commands.cooldown(1, 1, BucketType.user)
    async def _check(self, ctx, name: str):
        """Output the text for a single playlist"""
        if not re.fullmatch(r"[a-zA-Z0-9_]*", name):
            raise ValueError("Not a valid playlist name")
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT playlist_text FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if (row := await cursor.fetchone()):
                    await ctx.send(row[0])
                else:
                    await ctx.send(f"Playlist `{name}` doesn't exist")

    @_playlists.command(name="owner", ignore_extra=False)
    async def _owner(self, ctx, name: str, new_owner: typing.Union[discord.Member, Dashes] = None):
        """Check or set the owner of a playlist

        To change a playlist's owner, either the playlist must have no owner, or you
        are the bot owner, guild owner, or the playlist owner.

        To clear the owner, pass "-" as the new owner.

        Usage:
            %playlists owner playlist             ->  gets the playlist's current owner
            %playlists owner playlist GeeTransit  ->  make GeeTransit the playlist owner
            %playlists owner playlist -           ->  removes the playlist's owner
        """
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT owner_id FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await ctx.send(f"Playlist `{name}` doesn't exist")
                    return
                current = row[0]
        # Get owner
        if new_owner is None:
            if current is None:
                await ctx.send(f"Playlist `{name}` has no owner")
            else:
                await ctx.send(f"Playlist `{name}` owner is {ctx.guild.get_member(current).name}")
            return
        # If there's already an owner, make sure they are allowed to change it
        if current is not None:
            if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                await ctx.send("You are not allowed to change this playlist's owner")
                return
        # Store the playlist's new owner
        if new_owner == "-":
            new_owner_value = None
        else:
            new_owner_value = new_owner.id
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("UPDATE playlists SET owner_id = ? WHERE server_id = ? AND playlist_name = ?;", (new_owner_value, ctx.guild.id, name))
            await db.commit()
        # Respond with the new owner
        if new_owner == "-":
            await ctx.send(f"Playlist `{name}` now has no owner")
        else:
            await ctx.send(f"Playlist `{name}` owner now is {new_owner.name}")

    @_playlists.command(name="remove", ignore_extra=False)
    async def _remove(self, ctx, name: str):
        """Remove a playlist"""
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            # Check if user can actually change it
            async with db.execute("SELECT owner_id FROM playlists WHERE server_id = ? AND playlist_name = ? LIMIT 1;", (ctx.guild.id, name)) as cursor:
                if not (row := await cursor.fetchone()):
                    await ctx.send(f"Playlist `{name}` doesn't exist")
                    return
                else:
                    current = row[0]
            # If there's already an owner, make sure they are allowed to change it
            if current is not None:
                if ctx.author.id not in (self.bot.owner_id, ctx.guild.owner_id, current):
                    await ctx.send("You do not have permission to remove this playlist.")
                    return
            # Delete the playlist
            await db.execute("DELETE FROM playlists WHERE server_id = ? AND playlist_name = ?;", (ctx.guild.id, name))
            await db.commit()
        await ctx.send(f"Removed playlist `{name}`")

def setup(bot):
    return bot.add_cog(Playlists(bot))
