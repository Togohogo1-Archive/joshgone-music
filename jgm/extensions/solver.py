import math
import re

import simpleeval
from discord.ext import commands

# To prevent my computer from dying
simpleeval.MAX_POWER = 40000

# Add extra functions
evaluator = simpleeval.SimpleEval()
evaluator.functions["round"] = round

def factorial(num):
    if num > 25:
        raise ValueError("yeebruh u tryna 🅱️reak 🅱ot")
    return math.factorial(num)
evaluator.functions["factorial"] = factorial
evaluator.functions["fax"] = factorial

class Solver(commands.Cog):
    NUM = r"\d+(?:\.\d*)?"
    VAR = r"(?!\d)\w"
    SIGN = r"[+-]"
    EXPR = fr"((?:{SIGN} )*)(?:(?:({NUM}) |())({VAR})|({NUM})())"  # sign, num, var

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def solve(self, ctx, *, eq=""):
        """Solves a very simple linear equation (only + and -)"""
        infos = []  # Holds constant and coefficient of variable
        name = None  # Name of the variable

        # Loop through each expression and add them into `info`
        for expr in eq.split("="):
            info = [0, 0]  # [0] = coefficient, [1] = constant
            match = None  # Last match (for the empty expression checker)
            first = True  # Whether the term is the first term (can omit +/-)
            last = 0  # End index of the last match

            if re.match(r"^\s*9\s*\+\s*10\s*$", expr):
                infos.append([0, 21])
                continue

            # Loop over each term. Raise an error when the substring between
            # matches contains something that's not a space.
            for match in re.finditer(self.EXPR.replace(" ", r"\s*"), expr):
                # Connecting substring must be whitespace only
                if expr[last:match.start()] and not expr[last:match.start()].isspace():
                    raise ValueError(f"couldn't parse: {expr[last:match.start()]}")

                # Get the match's groups
                signs, num, var = filter(lambda i: i is not None, match.groups())
                signs = signs.split()
                # Only the first term can omit the +/-
                if not signs and not first:
                    raise ValueError(f"missing sign for {num}{var}")
                # Default to 1 (such as when a variable is passed: 7+a)
                if not num:
                    num = "1"

                # Turn the value into a Python int / float
                value = float(num) if "." in num else int(num)
                for sign in signs:
                    if sign == "-":
                        value *= -1

                # Update expression info
                if var:
                    # Only allow one variable is allowed for now
                    if name is not None:
                        if name != var:
                            raise ValueError(f"more than one variable found: {name}, {var}")
                    else:
                        name = var
                    info[0] += value  # Add to coefficient
                else:
                    info[1] += value  # Add to constant

                # Update first and last variables
                if first:
                    first = False
                last = match.end()

            # Trailing substring must be whitespace only
            if expr[last:] and not expr[last:].isspace():
                raise ValueError(f"couldn't parse: {expr[last:]}")
            # The expression cannot be empty (at least one term needed)
            if match is None:
                raise ValueError(f"empty expression: {expr}")
            infos.append(info)  # Add to infos list

        if len(infos) == 1:
            # Single expression (no equals sign)
            var, const = infos[0]
            if var != 0:
                # Solve for the variable
                value = const / var
                if int(value) == value:
                    value = int(value)
                await ctx.send(f"{name} = {value}")
            else:
                # Return the expression result
                await ctx.send(f"{const}")
            return

        # Multiple expressions
        first_var, first_const = infos[0]
        check = None
        for info in infos[1:]:
            var, const = info
            if not math.isclose(first_var, var):
                # Solve for the variable
                value = (const - first_const) / (first_var - var)
                # Check that the solved value equals previous values
                if check is not None:
                    if not math.isclose(check, value):
                        raise ValueError(f"more than one possible value: {check}, {value}")
                else:
                    check = value
            else:
                # Check that the constants equal eachother
                if not math.isclose(const, first_const):
                    raise ValueError(f"more than one value: {first_const}, {const}")
        # Return solved value (variable or constant)
        if check is not None:
            if int(check) == check:
                check = int(check)
            await ctx.send(f"{name} = {check}")
        else:
            await ctx.send(f"{first_const}")

    @commands.command()
    async def calc(self, ctx, *, expr):
        """Calculates an expression"""
        # First strip any potential backticks
        for _ in range(3):
            if expr[0] == "`" == expr[-1] and len(expr) > 1:
                expr = expr[1:-1]
            else:
                break
        await ctx.send(evaluator.eval(expr))

def setup(bot):
    bot.add_cog(Solver(bot))
