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
        await self.bot.driver.stop()
        await self.bot.close()

    @commands.command()
    async def run(self, ctx):
        try:
            await self.bot.driver.run()
            await ctx.send("```✅ Bot is running.```")
        except Exception as e:
            await ctx.send(f"```{str(e)}```")

    @commands.command()
    async def stop(self, ctx):
        await self.bot.driver.stop()
        await ctx.send("```🛑 Bot stopped.```")


async def setup(bot):
    await bot.add_cog(BotCommands(bot))
