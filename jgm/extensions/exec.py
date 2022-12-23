"""Provides an exec command

Adapted from ULHack Bot's cogs/exec.py

"""
import asyncio
import ast
import functools
import pydoc

import discord
from discord.ext import commands

class Exec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def ensure_scope(self):
        # Ensures that the bot has an execution scope
        if not hasattr(self.bot, "scope"):
            # Initialize the scope with some modules and the bot
            self.bot.scope = {
                "bot": self.bot,
                "asyncio": asyncio,
                "discord": discord,
                "commands": commands,
            }

    @staticmethod
    @functools.wraps(pydoc.render_doc)
    def helps(*args, **kwargs):
        stack = []
        for char in pydoc.render_doc(*args, **kwargs):
            if char == "\b":
                if stack:
                    stack.pop()
                continue
            stack.append(char)
        return "".join(stack)

    @staticmethod
    def raws(obj: object, lang: str = "py") -> str:
        if not isinstance(obj, str):
            obj = ascii(obj)
        else:
            obj = ascii(obj)
            obj = obj.replace("\\"+obj[0], obj[0])[1:-1].replace("\\n", "\n")
        return f"```{lang}\n" + obj.replace("`", "`\u200b") + "\n```"

    @staticmethod
    def reload(name):
        """Helper function to reload the specified module"""
        import importlib
        importlib.invalidate_caches()
        module = importlib.import_module(name)
        return importlib.reload(module)

    @staticmethod
    def clean_code(text):
        """Remove backticks from a Discord message's content

        Examples:
            clean_code("`69420`") == "69420"
            clean_code("``69420``") == "69420"
            clean_code("```py\n69420\n```") == "69420"

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
        if lines[0].strip() != "```py":
            raise ValueError(r"First line has to be \`\`\`py")
        if lines[-1].strip() != "```":
            raise ValueError(r"Last line has to be \`\`\`")
        del lines[0]
        del lines[-1]
        text = "".join(lines)
        return text

    @staticmethod
    def return_last(body):
        """Returns a new body that tries to returns the last statement"""
        if body and isinstance(body[-1], ast.Expr):
            expr = body[-1].value
            return_ = ast.parse("return None").body[0]
            return_.value = expr
            return [*body[:-1], return_]
        return body

    @staticmethod
    def wrap_ast(
        body,
        *,
        scope=None,
        header="def ____thingy(): pass",
        returnlast=False,
        filename="<wrappedfunc>",
    ):
        """Returns a function by merging the header and body

        The filename is passed to the compile function. The scope is passed to
        the exec function.

        """
        if scope is None:
            scope = {}
        # Wrap the statements in a function definition (possibly async)
        module = ast.parse(header)
        function = module.body[0]
        function.body = body
        module.body = [function]
        # Compile and execute it in the provided scope
        code = compile(ast.fix_missing_locations(module), filename, "exec")
        exec(code, scope)
        # Return the defined function
        return scope[function.name]

    async def wait_approval(self, message):
        """Sends a reply to the original message waiting for approval

        Only the bot owners will be able to approve it.

        """
        message = await message.reply(
            content="Awaiting approval...",
            mention_author=False,
        )
        try:
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60,
                    check=lambda reaction, user: (
                        reaction.message == message
                        and user.id in (self.bot.owner_id, *self.bot.owner_ids)
                        and reaction.emoji in ("✅", "❌")
                    ),
                )
            except asyncio.TimeoutError:
                await message.edit(content=f"{message.content}\nTimed out")
                return False
            if reaction.emoji == "❌":
                await message.edit(content=f"{message.content}\nDenied :(")
                return False
            else:
                await message.edit(content=f"{message.content}\nApproved :D")
                return True
        except discord.NotFound:
            return False

    @commands.command(aliases=["%"], hidden=True)
    async def exec(self, ctx, *, text=""):
        """Executes some code"""
        self.ensure_scope()
        # Remove backticks
        try:
            text = self.clean_code(text)
        except ValueError as e:
            await ctx.send(f"Error cleaning code: {e!s}")
            return
        # Check for approval if not owner
        if not await self.bot.is_owner(ctx.author):
            if not await self.wait_approval(ctx.message):
                return
        # Dictionary of locals for the script
        variables = {
            "ctx": ctx,
            "cog": self,
            "help": self.helps,
            "raw": self.raws,
            "reload": self.reload,
            "message": ctx.message,
            "author": ctx.author,
            "channel": ctx.channel,
        }
        if ctx.guild is not None:
            # A guild doesn't exist when in a DM
            variables["guild"] = ctx.guild
        if ctx.message.reference is not None:
            reference = ctx.message.reference
            if reference.cached_message is not None:
                variables["reply"] = reference.cached_message
            else:
                # Fetch message if possible
                cid = reference.channel_id
                mid = reference.message_id
                try:
                    channel = self.bot.get_channel(cid)
                    if channel is None:
                        channel = await self.bot.fetch_channel(cid)
                    variables["reply"] = await channel.fetch_message(mid)
                except:
                    pass
        if hasattr(self, "result"):
            variables["_"] = self.result
        try:
            # Compile and get a list of statements
            body = ast.parse(text).body
            # Ensure there's at least one statement
            if not body:
                body.append(ast.Pass())
            # Try to return the last expression
            body = self.return_last(body)
            # Wrap in an async function
            func = self.wrap_ast(
                body,
                scope=self.bot.scope,
                header=f"async def ____thingy({', '.join(variables)}): pass",
                filename="<discordexec>",
            )
        except Exception as e:
            raise RuntimeError(f"Error preparing code: {e!r}") from e
        try:
            # Await and send its result
            result = await func(**variables)
        except BaseException as e:
            import traceback
            traceback.print_exc()
            await ctx.send(f"*Traceback printed:* `{e!r}`")
        else:
            if result is not None:
                self.result = result
                if isinstance(result, str):
                    content = result
                else:
                    content = repr(result)
                if len(content) > 30000:
                    raise ValueError("Result too long for output")
                if content.startswith("```") and content.endswith("\n```"):
                    prefix, _, content = content.partition("\n")
                    if len(prefix) > 50:
                        content = prefix[50:] + content
                        prefix = prefix[:50]
                    content, _, suffix = content.rpartition("\n")
                    paginator = commands.Paginator(prefix=prefix+"\n", suffix="\n"+suffix)
                else:
                    paginator = commands.Paginator(prefix="", suffix="")
                for line in content.splitlines():
                    for start in range(0, len(line), 1950):
                        paginator.add_line(line[start : start+1950])
                if len(paginator.pages) > 20:
                    raise ValueError("Result too long for output")
                nonempty = 0
                for page in paginator.pages:
                    nonempty += 1
                    await ctx.send(page.strip())
                if nonempty == 0:
                    await ctx.send("*Empty string*")
            else:
                await ctx.send("*Finished*")

def setup(bot):
    bot.add_cog(Exec(bot))
