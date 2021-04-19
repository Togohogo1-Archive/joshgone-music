import discord
from discord.ext import commands

class Self(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "_self_accept"):
            bot._self_accept = False

    def off(self):
        self.bot.process_commands = self.bot._old_process_commands
        del self.bot._old_process_commands
        self.bot._skip_check = self.bot._old_skip_check

    def on(self):
        self.bot._old_process_commands = self.bot.process_commands
        async def _process_commands(message):  # self is bot
            await self.bot.invoke(await self.bot.get_context(message))
        self.bot.process_commands = _process_commands
        self.bot._old_skip_check = self.bot._skip_check
        self.bot._skip_check = lambda x, y: x != y and self.bot._old_skip_check(x, y)

    @commands.command(name="self", ignore_extra=False, hidden=True)
    @commands.is_owner()
    async def _self(self, ctx, accept_self: bool):
        if accept_self == self.bot._self_accept:
            return
        self.bot._self_accept = accept_self
        if accept_self:
            self.on()
            await ctx.send("Self accept is now on")
        else:
            self.off()
            await ctx.send("Self accept is now off")

def setup(bot):
    bot.add_cog(Self(bot))