import asyncio
import os
from discord.ext import commands

class JSE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["%%"])
    async def jse(self, ctx, *, code):
        if code.startswith("```ts\n") and code.endswith("\n```"):
            code = code[6:-4]
        elif code.startswith("```js\n") and code.endswith("\n```"):
            code = code[6:-4]
        process = await asyncio.create_subprocess_exec(
            "deno", "run", "--allow-net", "--allow-hrtime", "-",
            env=os.environ | {"NO_COLOR": "1"},
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(code.encode()), 5)
        except BaseException as e:
            if process.returncode is None:
                process.terminate()
            await ctx.send(f"*Executor terminated:* `{e!r}`")
            return
        if stderr:
            await ctx.send(f"*Executor errored:* ```js\n{stderr.decode()}\n```")
            return
        if stdout:
            content = stdout.decode()
            if len(content) > 30000:
                raise ValueError("Result too long for output")
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
    bot.add_cog(JSE(bot))
