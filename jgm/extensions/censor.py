import os
import re
import typing

import aiosqlite
import discord
from discord.ext import commands

class Censor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="emojis", aliases=["e"], ignore_extra=False, pass_context=True, invoke_without_command=True)
    async def emojis(self, ctx):
        await self.emojis_list(ctx)

    @emojis.command(name="list", aliases=["l"], ignore_extra=False)
    async def emojis_list(self, ctx):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            removed_emojis = []
            guild_emojis = {emoji.id: emoji for emoji in ctx.guild.emojis}
            async with db.execute("SELECT emoji_id FROM removed_emoji WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                async for row in cursor:
                    emoji_id = row[0]
                    if isinstance(emoji_id, str):
                        removed_emojis.append(emoji_id)
                    if emoji_id in guild_emojis:
                        removed_emojis.append(guild_emojis[emoji_id])
            await ctx.send(f"JoshGone is currently removing {', '.join(sorted(map(str, removed_emojis)))}.")

    @emojis.command(name="add", aliases=["a"])
    async def emojis_add(self, ctx, *emojis: typing.Union[discord.Emoji, str]):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            values = []
            for emoji in emojis:
                if isinstance(emoji, str):
                    if len(emoji) == 1:
                        values.append((ctx.guild.id, emoji))
                    else:
                        print(repr(emoji))
                        print(*map(ord, emoji))
                elif emoji.id is not None:
                    values.append((ctx.guild.id, emoji.id))
            await db.executemany("INSERT INTO removed_emoji VALUES (?, ?) ON CONFLICT DO NOTHING;", values)
            await db.commit()
            await ctx.send(f"Added {', '.join(map(str, emojis))} to removal list.")

    @emojis.command(name="remove", aliases=["r"])
    async def emojis_remove(self, ctx, *emojis: typing.Union[discord.Emoji, str]):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            values = []
            for emoji in emojis:
                if isinstance(emoji, str):
                    values.append((ctx.guild.id, emoji))
                elif emoji.id is not None:
                    values.append((ctx.guild.id, emoji.id))
            await db.executemany("DELETE FROM removed_emoji WHERE server_id = ? AND emoji_id = ?;", values)
            await db.commit()
            await ctx.send(f"Removed {', '.join(map(str, emojis))} from removal list.")

    @emojis.command(name="clear", aliases=["c"], ignore_extra=False)
    async def emojis_clear(self, ctx):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("DELETE FROM removed_emoji WHERE server_id = ?;", (ctx.guild.id,))
            await db.commit()
            await ctx.send("Cleared removal list.")

    @commands.group(name="allow", aliases=["a"], ignore_extra=False, pass_context=True, invoke_without_command=True)
    async def allow(self, ctx):
        await self.allow_list(ctx)

    @allow.command(name="list", aliases=["l"], ignore_extra=False)
    async def allow_list(self, ctx):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT user_id FROM allowed_user WHERE server_id = ?;", (ctx.guild.id,)) as cursor:
                users = [ctx.guild.get_member(row[0]) async for row in cursor]
            await ctx.send(f"JoshGone is currently ignoring {', '.join(user.name for user in users)}.")

    @allow.command(name="add", aliases=["a"])
    async def allow_add(self, ctx, *users: discord.Member):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            values = [(ctx.guild.id, user.id) for user in users]
            await db.executemany("INSERT INTO allowed_user VALUES (?, ?) ON CONFLICT DO NOTHING;", values)
            await db.commit()
            await ctx.send(f"Added {', '.join(user.name for user in users)} to allow list.")

    @allow.command(name="remove", aliases=["r"])
    async def allow_remove(self, ctx, *users: discord.Member):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            values = [(user.id, ctx.guild.id) for user in users]
            await db.executemany("DELETE FROM allowed_user WHERE user_id = ? AND server_id = ?;", values)
            await db.commit()
            await ctx.send(f"Removed {', '.join(user.name for user in users)} from allow list.")

    @allow.command(name="clear", aliases=["c"], ignore_extra=False)
    async def allow_clear(self, ctx):
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            await db.execute("DELETE FROM allowed_user WHERE server_id = ?;", (ctx.guild.id,))
            await db.commit()
            await ctx.send("Cleared allow list.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT running FROM server WHERE server_id = ? LIMIT 1;", (reaction.message.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()) or not row[0]:
                    return
            async with db.execute("SELECT * FROM removed_emoji WHERE server_id = ? AND emoji_id = ? LIMIT 1;", (reaction.message.guild.id, reaction.emoji if isinstance(reaction.emoji, str) else reaction.emoji.id)) as cursor:
                if not await cursor.fetchone():
                    return
            async with db.execute("SELECT * FROM allowed_user WHERE server_id = ? AND user_id = ? LIMIT 1;", (reaction.message.guild.id, user.id)) as cursor:
                if await cursor.fetchone():
                    return
            await reaction.remove(user)

    async def process_message(self, message):
        author = message.author
        if author == self.bot.user:
            return
        async with aiosqlite.connect(os.environ["JOSHGONE_DB"]) as db:
            async with db.execute("SELECT running FROM server WHERE server_id = ? LIMIT 1;", (message.guild.id,)) as cursor:
                if not (row := await cursor.fetchone()) or not row[0]:
                    return
            async with db.execute("SELECT * FROM allowed_user WHERE server_id = ? AND user_id = ? LIMIT 1;", (message.guild.id, author.id)) as cursor:
                if await cursor.fetchone():
                    return
            for match in re.finditer(r"(?<!\\)<(a|):(\w+):(\d+)>", message.content):
                animated, name, id = match.groups()
                async with db.execute("SELECT * FROM removed_emoji WHERE server_id = ? AND emoji_id = ? LIMIT 1;", (message.guild.id, id)) as cursor:
                    if await cursor.fetchone():
                        break
            else:
                for char in message.content:
                    async with db.execute("SELECT * FROM removed_emoji WHERE server_id = ? AND emoji_id = ? LIMIT 1;", (message.guild.id, char)) as cursor:
                        if await cursor.fetchone():
                            break
                else:
                    return
            await author.send(f"Message deleted:\n```\n{message.content}\n```")
            await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        await self.process_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.guild is None:
            return
        await self.process_message(after)

def setup(bot):
    bot.add_cog(Censor(bot))
