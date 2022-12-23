import discord
from discord.ext import commands

class Sort(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sort")
    async def _sort(self, ctx, *args):
        r"""Sorts strings and outputs the final order

        Usage:
            %sort c b a     ->  sends a b c
            %sort a b c     ->  sends a b c
            %sort 3 2 1     ->  sends 1 2 3
            %sort 1 2 3     ->  sends 1 2 3
        """
        try:
            # If all arguments can be ints, convert them
            result = sorted(args, key=int)
        except ValueError:
            try:
                # If all arguments can be floats, convert them
                result = sorted(args, key=float)
            except ValueError:
                # Otherwise, just use lexicographical order
                result = sorted(args)
        await ctx.send(" ".join(result))

def setup(bot):
    bot.add_cog(Sort(bot))
