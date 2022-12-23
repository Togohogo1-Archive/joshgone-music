import asyncio
import re

import discord
from discord.ext import commands
from discord.utils import get

class Relay(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.user = None

    @staticmethod
    def split(string):
        i = string.index(" ") if " " in string else 9999
        j = string.index("\n") if "\n" in string else 9999
        x = min(i, j)
        return string[:x], string[x+1:]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is not None:
            return
        if message.author == self.bot.user:
            return
        gee = get(self.bot.users, name="GeeTransit")
        if message.author != gee:
            # inbound
            await gee.send(f"{message.author}: {message.content}")
        else:
            # outbound
            command, content = self.split(message.content)
            if command == "ss":
                name, content = self.split(content)
                self.user = get(self.bot.users, name=name.replace("~", " "))
            elif command == "rr":
                if self.user is None:
                    raise ValueError("last user is still None")
            else:
                raise ValueError(f"unknown command {command}")
            if self.user.dm_channel is None:
                await self.user.create_dm()
            if not content:
                return
            await self.user.dm_channel.send(content)

    @commands.Cog.listener("on_message")
    async def handle_gee_dm(self, message):
        if message.guild:
            return
        if message.author == self.bot.user:
            return
        if not message.reference:
            return
        gee = get(self.bot.users, name="GeeTransit")
        if message.author != gee:
            return
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        try:
            # Explicitly replying to a message
            reference = message.reference
            if reference.cached_message:
                reply = reference.cached_message
            else:

                # Fetch message if possible
                cid = reference.channel_id
                mid = reference.message_id
                channel = self.bot.get_channel(cid)
                if not channel:
                    channel = await self.bot.fetch_channel(cid)
                reply = await channel.fetch_message(mid)

            # Get original message sender
            match = re.match(r"^([^#\n]+)#([0-9]{4}): ", reply.content)
            if not match:
                raise ValueError("replier not found")
            self.user = get(
                self.bot.users,
                name=match[1].strip(),
                discriminator=match[2],
            )

        except Exception as e:
            await message.channel.send(f'Reply error: {e!r}')

        if self.user.dm_channel is None:
            await self.user.create_dm()
        await self.user.dm_channel.send(message.content)

def setup(bot):
    bot.add_cog(Relay(bot))
