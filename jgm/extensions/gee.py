import random
import re

import discord
from discord.ext import commands

class Gee(commands.Cog):
    replies = [reply.replace("-", " ") for reply in '''
        dang-lol  lmao  fax  bruh-lol  lol  o-ezpz  bruh-tru  damn
        dang  tru  lmaoo  big-fax  o-really  ebic  o-dang  wut-lol  damn-boi
        tooez  pog  lol-aight  o-bruh  sus  ree  yeebruh  xD  bruh
        pong  lol-pong  ezpz  bruh-moment  ez  monke  toocool
    '''.split()]
    replies_question = [reply.replace("-", " ") for reply in '''
        ye-lol  lol-idk  na-lol  ye-ik  na  ye  bruh-na  orz-ye  sus-na
    '''.split()]
    replies_question_weights = [
        3/7/4, 1/7, 3/7/4, 3/7/4, 3/7/4, 3/7/4, 3/7/4, 3/7/4, 3/7/4,
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["g"])
    async def gee(self, ctx, *, arg=None):
        """Reply with something GeeTransit would say

        Usage:
            %gee                ->  random response
            %gee ...            ->  yes / no
            %gee ... (or ...)+  ->  random choice
            %gee X ...          ->  random number in [0, X]
            %gee X Y ...        ->  random number in [X, Y]
        """
        if arg is None:
            arg = ""
        splitted = arg.split()

        if "or" in splitted:
            # Reply with one of the choices
            await ctx.send(random.choice(re.split(r"\bor\b", arg)))
            return

        try:
            a = int(splitted[0])
        except IndexError:
            # Reply with a response if empty
            await ctx.send(random.choice(self.replies))
            return
        except ValueError:
            # Reply with yes or no to a question
            await ctx.send(random.choices(
                self.replies_question,
                weights=self.replies_question_weights,
                k=1,
            )[0])
            return

        try:
            b = int(splitted[1])
        except (ValueError, IndexError):
            # Pick random number given a bound (0 to a)
            x = random.randint(*sorted((0, a)))
            await ctx.send(f"{x}")
            return

        if (a, b) == (69, 420):
            # Special numbers
            x = random.choice((69, 420))
        else:
            # Pick random number given two bounds (a to b)
            x = random.randint(*sorted((a, b)))
        await ctx.send(f"{x}")

def setup(bot):
    bot.add_cog(Gee(bot))
