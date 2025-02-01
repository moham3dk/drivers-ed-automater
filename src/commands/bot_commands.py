import discord
from discord.ext import commands
import os


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        await ctx.send("```✅ Bot is online.```")

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("```🚫 Shutting down...```")
        await self.bot.close()

    @commands.command()
    async def run_driver(self, ctx):
        try:
            await self.bot.driver.run()
        except Exception as e:
            await ctx.send(f"```{str(e)}```")

    @commands.command()
    async def stop_driver(self, ctx):
        await self.bot.driver.stop()


async def setup(bot):
    await bot.add_cog(BotCommands(bot))
