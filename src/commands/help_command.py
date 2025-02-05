import discord
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 TooCoolTrafficSchool Bot - Help",
            description="Here's a list of commands you can use:",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🚀 **Run WebDriver**",
            value="```!run```Runs the WebDriver.",
            inline=False
        )

        embed.add_field(
            name="🛑 **Stop WebDriver**",
            value="```!stop```Stops the WebDriver.",
            inline=False
        )

        embed.add_field(
            name="📸 **Take Screenshot**",
            value="```!screenshot```Captures a screenshot of the current website.",
            inline=False
        )

        embed.add_field(
            name="📄 **Get DOM**",
            value="```!get_dom```Sends an HTML file containing the current DOM.",
            inline=False
        )

        embed.add_field(
            name="🖱️ **Click Element**",
            value=(
                "```!click_element <by> <value>```"
                "Clicks an element on the page.\n"
                "**Parameters:**\n"
                "- `by`: The Selenium 'By' method (e.g., `id`, `name`, `xpath`)\n"
                "- `value`: The value corresponding to the 'By' method"
            ),
            inline=False
        )

        embed.add_field(
            name="⚡ **Shutdown Bot**",
            value="```!shutdown```Safely shuts down the bot.",
            inline=False
        )

        embed.add_field(
            name="📊 **Bot Status**",
            value="```!status```Displays the current status of the bot.",
            inline=False
        )

        embed.set_footer(text="Use the commands exactly as shown above.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
