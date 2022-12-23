import aiohttp
from discord.ext import commands

class YesNo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def yesno(self, ctx):
        """Reply with a GIF of yes or no

        Uses https://www.yesno.wtf/api to get a GIF.

        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://yesno.wtf/api") as response:
                data = await response.json()
                await ctx.send(f"{data['answer']} lol: {data['image']}")

def setup(bot):
    bot.add_cog(YesNo(bot))
