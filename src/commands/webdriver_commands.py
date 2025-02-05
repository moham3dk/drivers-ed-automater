import discord
from discord.ext import commands
from selenium.webdriver.common.by import By
import os


class WebDriverCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_dom(self, ctx):
        await ctx.send("```⚙️ Getting DOM...```")

        dom = await self.bot.driver.get_dom()

        with open("index.html", "w") as f:
            f.write(dom)

        await ctx.send(file=discord.File("index.html"))

        os.remove("index.html")

        await ctx.send("```✅ DOM fetched successfully.```")

    @commands.command()
    async def click_element(self, ctx, by: str, value: str):
        await ctx.send(f"```⚙️ Clicking element: {value}...```")

        by_mapping = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }

        if by.lower() in by_mapping:
            by = by_mapping[by.lower()]
            clicked = self.bot.driver.click_element(by, value)

            if not clicked:
                await ctx.send("```❌ Element not found.```")
            else:
                await ctx.send("```✅ Element clicked successfully.```")
        else:
            await ctx.send("```❌ Invalid 'by' value.```")

    @commands.command()
    async def screenshot(self, ctx):
        try:
            await ctx.send("```⚙️ Taking a screenshot...```")

            if hasattr(self.bot, "driver") and self.bot.driver:
                screenshot_path = os.path.join(os.getcwd(), "screenshot.png")
                await self.bot.driver.save_screenshot(screenshot_path)

                await ctx.send(file=discord.File(screenshot_path))

                os.remove(screenshot_path)

                await ctx.send("```✅ Screenshot taken successfully.```")
            else:
                await ctx.send(
                    "```❌ No active browser driver found to take a screenshot.```"
                )

        except Exception as e:
            await ctx.send(f"```An error occurred: {str(e)}```")


async def setup(bot):
    await bot.add_cog(WebDriverCommands(bot))
