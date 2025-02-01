import discord
from discord.ext import commands
import os
import sys

from services.webdriver_service import WebDriverService
from utils.logger import Logger
from config.config import Config

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

bot.driver = WebDriverService(bot)
bot.logger = Logger()


class TooCoolTrafficSchoolBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

        self.driver = WebDriverService(self)
        self.logger = Logger()

    async def setup_hook(self):
        self.logger.info("Loading cogs...")

        for filename in os.listdir("src/commands"):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await self.load_extension(f"commands.{filename[:-3]}")
                    self.logger.success(f"Loaded cog: {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to load cog {filename}: {e}")

        self.logger.success("Cogs loaded successfully.")

    async def on_ready(self):
        self.logger.success(f"Logged in as {self.user.name}")

        # Find the first available text channel
        for guild in self.guilds:
            for channel in guild.text_channels:
                self.log_channel = channel
                break
            if hasattr(self, "log_channel"):
                break

        if hasattr(self, "log_channel"):
            await self.log_channel.send("```✅ TooCoolTrafficSchool Bot is online```")
            await self.log_channel.send("```🚗 Starting the driver...```")
        else:
            self.logger.error(
                "No available text channel found for logging. Make sure the bot is in a server with at least one text channel."
            )
            sys.exit(1)

        await self.driver.run()


bot = TooCoolTrafficSchoolBot()
bot.run(Config.bot_token)
