import sys
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from config.config import Config


class WebDriverService:
    def __init__(self, bot):
        self.bot = bot
        self.driver = None
        self.running = False
        self.time_title_last_checked = None
        self.title_state = None

    #################################
    # BASE FUNCTIONS FOR THE DRIVER #
    #################################
    async def click_element(self, by, value):
        """Attempts to click an element on the page."""
        self.bot.logger.debug(f"Attempting to click element: {value}...")
        try:
            element = self.driver.find_element(by, value)
            element.click()
            self.bot.logger.debug(f"Successfully clicked element: {value}")
        except Exception as e:
            self.bot.logger.debug(
                f"Failed to click element with {by}: {value}. Error: {e}"
            )

    async def get_title(self):
        """Retrieves the current page title."""
        self.bot.logger.debug("Retrieving page title...")
        try:
            title = self.driver.title
            self.bot.logger.debug(f"Page title retrieved: {title}")
            return title
        except Exception as e:
            self.bot.logger.error(f"Failed to retrieve page title: {e}")
            return None

    async def save_screenshot(self, path):
        """Takes a screenshot of the current page."""
        self.bot.logger.debug(f"Taking a screenshot and saving to {path}...")
        try:
            self.driver.save_screenshot(path)
            self.bot.logger.debug("Screenshot taken successfully.")
        except Exception as e:
            self.bot.logger.error(f"Failed to take screenshot: {e}")

    async def get_dom(self):
        """Retrieves the current DOM."""
        self.bot.logger.debug("Retrieving DOM...")
        try:
            dom = self.driver.page_source
            self.bot.logger.debug("DOM retrieved.")
            return dom
        except Exception as e:
            self.bot.logger.error(f"Failed to retrieve DOM: {e}")
            return None

    #################################
    # BASE FUNCTIONS FOR AUTOMATION #
    #################################
    async def login(self, username, password):
        """Logs into the website."""
        self.bot.logger.debug("Logging in...")
        self.driver.get("https://school.toocooltrafficschool.com/login")
        await asyncio.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "_submit").click()
        self.bot.logger.success("Login attempt completed.")

    async def start_course(self):
        """Starts the course by navigating to the course URL."""
        self.bot.logger.debug("Starting the course...")
        self.driver.get(Config.course_url)
        await asyncio.sleep(1)
        await self.check_chapter_button()
        self.bot.logger.success("Course started.")

    async def check_locked_out(self):
        """Checks if the user is locked out due to exceeding daily limits."""
        self.bot.logger.debug("Checking for lockout status...")
        try:
            self.driver.find_element(By.ID, "myLockoutModal")
            self.bot.logger.info("Locked out detected. Stopping the bot.")
            await self.bot.log_channel.send("@everyone")
            await self.bot.log_channel.send(
                "```✅ You have been locked out as you reached the maximum of 4 hours in a day.```"
            )
            await self.bot.log_channel.send(
                "```⚙️ The bot will stop now. Restart the bot tomorrow to continue.```"
            )
            await self.stop()
            await self.bot.close()
            sys.exit(0)
        except Exception:
            self.bot.logger.debug("No lockout detected.")
            pass

    async def check_chapter_button(self):
        """Checks for and clicks the 'Resume Chapter' or 'Start Chapter' button."""
        try:
            if self.driver.current_url == Config.course_url:
                resume_button = self.driver.find_element(
                    By.XPATH, '//span[contains(text(), "Resume Chapter")]'
                )
                actions = ActionChains(self.driver)
                actions.move_to_element(resume_button).perform()
                resume_button.click()
                self.bot.logger.debug("Resumed chapter successfully.")
        except Exception as e:
            self.bot.logger.debug(f"Failed to resume chapter: {e}")

        try:
            if self.driver.current_url == Config.course_url:
                start_button = self.driver.find_element(
                    By.XPATH, '//span[contains(text(), "Start Chapter")]'
                )
                actions = ActionChains(self.driver)
                actions.move_to_element(start_button).perform()
                start_button.click()
                self.bot.logger.debug("Started chapter successfully.")
        except Exception as e:
            self.bot.logger.debug(f"Failed to start chapter: {e}")

    async def check_title(self):
        """Checks if the page title has changed within the last 3 minutes."""
        self.bot.logger.debug("Checking page title...")
        if self.time_title_last_checked is None:
            self.time_title_last_checked = datetime.now()
            self.title_state = await self.get_title()

        time_now = datetime.now()
        time_diff = time_now - self.time_title_last_checked
        if time_diff > timedelta(minutes=3):
            new_title_state = await self.get_title()
            if new_title_state is None:
                self.bot.logger.error("Failed to retrieve page title. Skipping check.")
                return

            if new_title_state != self.title_state:
                self.title_state = new_title_state
                self.time_title_last_checked = time_now
            else:
                self.bot.logger.warning("Page title has not changed in 3 minutes.")
                await self.bot.log_channel.send("@everyone")
                await self.bot.log_channel.send(
                    "```🚨 Page title has not changed in 3 minutes.```"
                )
                await self.bot.log_channel.send(
                    "```⚙️ Use !screenshot to see the current state.```"
                )
                self.time_title_last_checked = time_now

    async def check_still_here_button(self):
        """Clicks the 'I'm Still Here' button if present."""
        return await self.click_element(
            By.XPATH, '//button[contains(text(), "I\'m Still Here")]'
        )

    async def check_alert(self):
        """Checks for and handles any alerts on the page."""
        self.bot.logger.debug("Checking for alerts...")
        try:
            alert = self.driver.find_element(By.CLASS_NAME, "alert")
            self.bot.logger.debug("Alert found.")
            question_element = self.driver.find_element(By.CLASS_NAME, "questionLabel")
            answers_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".answerLabel label.required"
            )

            if question_element and answers_elements:
                question = question_element.text
                answers = [answer.text for answer in answers_elements]

                await self.bot.log_channel.send("@everyone")
                await self.bot.log_channel.send("```🚨 Alert found.```")
                await self.bot.log_channel.send(
                    "```⏳ You have 5 minutes to answer before the bot is stopped.```"
                )
                await self.bot.log_channel.send(f"```❓ Question: {question}```")
                for i, answer in enumerate(answers, start=1):
                    await self.bot.log_channel.send(f"```{i}. {answer}```")
                await self.bot.log_channel.send(
                    "```⚙️ Please choose an answer by replying with the corresponding number.```"
                )

                def check_message(m):
                    return (
                        m.author != self.bot.user and m.channel == self.bot.log_channel
                    )

                try:
                    msg = await self.bot.wait_for(
                        "message", check=check_message, timeout=300
                    )  # 5 minutes timeout
                    choice = int(msg.content.strip())
                    if 1 <= choice <= len(answers):
                        answer = answers_elements[choice - 1]
                        answer.click()
                        await self.bot.log_channel.send(
                            f"```✅ Selected answer {choice}.```"
                        )
                        submit_button = self.driver.find_element(By.ID, "form_submit")
                        submit_button.click()
                        await self.bot.log_channel.send(
                            "```✅ Form submitted successfully.```"
                        )
                    else:
                        await self.bot.log_channel.send(
                            "```❌ Invalid choice. Please try again.```"
                        )
                except asyncio.TimeoutError:
                    await self.bot.log_channel.send(
                        "```❌ No response received. Stopping the bot.```"
                    )
                    await self.stop()
                except ValueError:
                    await self.bot.log_channel.send(
                        "```❌ Invalid input. Please enter a number.```"
                    )
            else:
                self.bot.logger.debug("Alert found but no question detected.")
        except Exception as e:
            self.bot.logger.debug(f"No alert found: {e}")

    async def check_quiz(self):
        """Checks for and handles any quizzes on the page."""
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
        except Exception as e:
            self.bot.logger.debug(f"No quiz found: {e}")

        try:
            quiz = self.driver.find_element(By.CLASS_NAME, "question-sign")
            if quiz:
                await self.bot.log_channel.send("@everyone")
                await self.bot.log_channel.send("```🚨 Question sign quiz found.```")
                question = self.driver.find_element(
                    By.CLASS_NAME, "question-prompt"
                ).text
                answers = self.driver.find_elements(
                    By.CSS_SELECTOR, ".question-answers label p"
                )

                await self.bot.log_channel.send(f"```❓ Question: {question}```")
                for i, answer in enumerate(answers, start=1):
                    await self.bot.log_channel.send(f"```{i}. {answer.text}```")

                await self.bot.log_channel.send(
                    "```⚙️ Please respond with the number of the correct answer.```"
                )

                def check_message(m):
                    return (
                        m.author != self.bot.user and m.channel == self.bot.log_channel
                    )

                try:
                    msg = await self.bot.wait_for(
                        "message", check=check_message, timeout=60
                    )
                    choice = int(msg.content.strip())
                    if 1 <= choice <= len(answers):
                        await self.click_element(
                            By.CSS_SELECTOR,
                            f".question-answers label:nth-child({choice}) input",
                        )
                        await self.bot.log_channel.send(
                            f"```✅ Selected answer {choice}.```"
                        )
                    else:
                        await self.bot.log_channel.send(
                            "```❌ Invalid choice. Please try again.```"
                        )
                except asyncio.TimeoutError:
                    await self.bot.log_channel.send(
                        "```❌ No response received. Please try again.```"
                    )
                except ValueError:
                    await self.bot.log_channel.send(
                        "```❌ Invalid input. Please enter a number.```"
                    )
        except Exception as e:
            self.bot.logger.debug(f"No question sign quiz found: {e}")

    async def check_next_button(self):
        """Clicks the 'Next' button if present."""
        return await self.click_element(By.ID, "next-button")

    ##############################
    # BASE FUNCTIONS FOR THE BOT #
    ##############################
    async def automate(self):
        """Runs the automation tasks."""
        self.bot.logger.debug("Running automation tasks...")
        await self.check_alert()
        await self.check_locked_out()
        await self.check_quiz()
        await self.check_still_here_button()
        await self.check_next_button()
        await self.check_chapter_button()
        await self.check_title()

        await asyncio.sleep(1)

    async def create_driver(self):
        """Initializes the WebDriver."""
        options = Options()
        options.add_argument("--mute-audio")
        self.driver = webdriver.Chrome(options=options)
        self.bot.logger.success("WebDriver initialized.")

    async def run(self):
        """Starts the WebDriver and begins the automation process."""
        try:
            if self.running:
                self.bot.logger.warning(
                    "Attempted to start the WebDriver when it was already running."
                )
                await self.bot.log_channel.send(
                    "```❌ WebDriver is already running.```"
                )
                return
            self.bot.logger.info("Starting the WebDriver...")
            self.running = True
            await self.create_driver()
            await self.bot.log_channel.send(
                "```✅ WebDriver started. Use !help for a list of commands and !stop to stop the WebDriver.```"
            )
            await self.login(Config.username, Config.password)
            await self.start_course()

            while self.running:
                await self.automate()
                await asyncio.sleep(1)

            self.bot.logger.info("WebDriver stopped.")
        except Exception as e:
            self.bot.logger.error(
                f"An error occurred while starting the WebDriver: {e}"
            )
            await self.bot.log_channel.send(
                "```❌ An error occurred while starting the WebDriver. Exiting.```"
            )
            sys.exit(1)

    async def stop(self):
        """Stops the WebDriver and cleans up resources."""
        try:
            if self.running:
                self.running = False
                self.driver.quit()
                self.driver = None
                await self.bot.log_channel.send("```🛑 WebDriver stopped.```")
            else:
                self.bot.logger.warning(
                    "Attempted to stop the WebDriver when it was not running."
                )
                await self.bot.log_channel.send("```❌ WebDriver is not running.```")
        except Exception as e:
            self.bot.logger.error(
                f"An error occurred while stopping the WebDriver: {e}"
            )
            await self.bot.log_channel.send(
                "```❌ An error occurred while stopping the WebDriver. Exiting.```"
            )
            sys.exit(1)
