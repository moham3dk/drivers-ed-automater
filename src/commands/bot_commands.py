from discord.ext import commands
import sys


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        await ctx.send("```✅ Bot is online.```")

    @commands.command()
    async def shutdown(self, ctx):
        self.bot.logger.info("Shutting down...")    
        await self.bot.driver.stop()
        await ctx.send("```🚫 Shutting down...```")
        await self.bot.close()
        self.bot.logger.success("Shutdown successful.")
        sys.exit(0)

    @commands.command()
    async def run(self, ctx):
        await self.bot.driver.run()

    @commands.command()
    async def stop(self, ctx):
        await self.bot.driver.stop()


async def setup(bot):
    await bot.add_cog(BotCommands(bot))
