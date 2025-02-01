# TODO fix the failed checks logic or remove it all together and add a different way of checking the status
import sys
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from config.config import Config


class WebDriverService:
    def __init__(self, bot):
        self.bot = bot
        self.driver = None
        self.running = False

    # BASE FUNCTIONS FOR THE DRIVER
    # ex. click_element, get_dom, etc.
    async def click_element(self, by, value):
        self.bot.logger.debug(f"Clicking element: {value}...")
        try:
            element = self.driver.find_element(by, value)
            element.click()
            return True
        except Exception as e:
            return False

    async def get_dom(self):
        self.bot.logger.debug("Getting DOM...")
        return self.driver.page_source

    async def save_screenshot(self, path):
        self.bot.logger.debug("Taking a screenshot...")
        self.driver.save_screenshot(path)

    # BASE FUNCTIONS FOR AUTOMATION
    # ex. login, start_course, checking buttons/alerts/other things, etc.
    async def login(self, username, password):
        self.bot.logger.debug("Logging in...")
        self.driver.get("https://school.toocooltrafficschool.com/login")
        await asyncio.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "_submit").click()

    async def start_course(self):
        self.bot.logger.debug("Starting the course.")
        self.driver.get(Config.course_url)
        await asyncio.sleep(1)
        await self.check_resume_chapter_button()

    async def check_resume_chapter_button(self):
        return await self.click_element(
            By.XPATH, "//a[span[contains(text(),'Resume Chapter')]]"
        )

    async def check_still_here_button(self):
        return await self.click_element(
            By.XPATH, '//button[contains(text(), "I\'m Still Here")]'
        )

    async def check_alert(self):
        self.bot.logger.debug("Checking for alerts...")
        try:
            alert = self.driver.find_element(By.CLASS_NAME, "alert")
            if alert:
                await self.handle_alert()
            return True
        except Exception:
            return False

    async def handle_alert(self):
        self.bot.logger.info("Alert found. Stopping the driver.")
        await self.bot.log_channel.send("@everyone")
        await self.bot.log_channel.send("```🚨 Alert found.```")
        await self.bot.log_channel.send(
            "```⚙️ The bot has been stopped. Please clear the alert then use !run to resume.```"
        )
        await self.stop()

    async def check_quiz(self):
        self.bot.logger.debug("Checking for quizzes...")
        try:
            quiz = self.driver.find_element(By.ID, "quiz-answer-group")
            if not quiz.get_attribute("style") == "display: none;":
                clicked = await self.click_element(
                    By.XPATH, "//label[@data-correct='yes']"
                )
                if clicked:
                    self.bot.logger.info("Answered quiz successfully.")
                    await self.bot.log_channel.send(
                        "```✅ Answered quiz successfully.```"
                    )
                else:
                    self.bot.logger.warning("Failed to answer quiz.")
                    await self.bot.log_channel.send("@everyone")
                    await self.bot.log_channel.send(
                        "```❌ Failed to answer quiz. Use !screenshot to see the current state.```"
                    )
        except Exception:
            pass

    async def check_next_button(self):
        return await self.click_element(By.ID, "next-button")

    # BASE FUNCTIONS FOR THE BOT
    # ex. automate, run, stop
    async def automate(self):
        checks = [
            self.check_alert(),
            self.check_still_here_button(),
            self.check_quiz(),
            self.check_next_button(),
            self.check_resume_chapter_button(),
        ]

        failed_checks = 0
        for check in checks:
            if not await check:
                self.bot.logger.debug(f"Check failed: {check.__name__}")
                failed_checks += 1

        if failed_checks == len(checks):
            self.bot.logger.warning("All checks failed. Stopping the driver.")
            await self.bot.log_channel.send("@everyone")
            await self.bot.log_channel.send(
                "```❌ All checks failed. Stopping the driver.```"
            )
            await self.bot.log_channel.send(
                "```⚙️ Please resolve the issue then use !run_driver to resume.```"
            )
            await self.stop()

        await asyncio.sleep(1)

    async def create_driver(self):
        options = Options()
        options.add_argument("--mute-audio")
        self.driver = webdriver.Chrome(options=options)

    async def run(self):
        self.bot.logger.info("Starting the driver.")
        self.running = True
        await self.create_driver()
        await self.login(Config.username, Config.password)
        await self.start_course()

        while self.running:
            await self.automate()
            await asyncio.sleep(1)

        self.bot.logger.info("Driver stopped.")

    async def stop(self):

        try:
            if self.running:
                self.running = False
                self.driver.quit()
                self.driver = None
            else:
                self.bot.logger.warning(
                    "Attempted to stop the driver when it was not running."
                )
        except Exception:
            self.logger.error("An error occurred while stopping the driver. Exiting.")
            self.bot.log_channel.send(
                "```❌ An error occurred while stopping the driver. Exiting.```"
            )
            sys.exit(1)
