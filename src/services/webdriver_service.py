import sys
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from config.config import Config


# TODO check mandatory break function, better debugging and error handling
# TODO refactor the code to make it more readable and overall better
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
        self.bot.logger.debug(f"Clicking element: {value}...")
        try:
            element = self.driver.find_element(by, value)
            element.click()
            return True
        except Exception as e:
            self.bot.logger.debug(f"Failed to click element: {e}")
            return False

    async def get_title(self):
        self.bot.logger.debug("Getting page title...")
        try:
            return self.driver.title
        except Exception as e:
            self.bot.logger.error(f"Failed to get page title: {e}")
            return None

    async def save_screenshot(self, path):
        self.bot.logger.debug("Taking a screenshot...")
        try:
            self.driver.save_screenshot(path)
        except Exception as e:
            self.bot.logger.error(f"Failed to take screenshot: {e}")

    #################################
    # BASE FUNCTIONS FOR AUTOMATION #
    #################################
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

        await self.check_chapter_button()

    async def check_locked_out(self):
        try:
            self.driver.find_element(By.ID, "myLockoutModal")
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
            return True
        except Exception:
            return False

    async def check_chapter_button(self):
        try:
            if self.driver.current_url == Config.course_url:
                resume_button = self.driver.find_element(
                    By.XPATH, '//span[contains(text(), "Resume Chapter")]'
                )
                actions = ActionChains(self.driver)
                actions.move_to_element(resume_button).perform()
                resume_button.click()
                return True
            return False
        except Exception as e:
            self.bot.logger.debug(f"Failed to resume chapter: {e}")

        try:
            if self.driver.current_url == Config.course_url:
                resume_button = self.driver.find_element(
                    By.XPATH, '//span[contains(text(), "Start Chapter")]'
                )
                # scroll to the element
                actions = ActionChains(self.driver)
                actions.move_to_element(resume_button).perform()
                resume_button.click()
                return True
            return False
        except Exception as e:
            self.bot.logger.debug(f"Failed to start chapter: {e}")
            return False

    async def check_title(self):
        if self.time_title_last_checked is None:
            self.time_title_last_checked = datetime.now()
            self.title_state = await self.get_title()
            return True

        time_now = datetime.now()
        time_diff = time_now - self.time_title_last_checked
        if time_diff > timedelta(minutes=3):
            new_title_state = await self.get_title()
            if new_title_state is None:
                self.bot.logger.error("Failed to retrieve page title. Skipping check.")
                return False

            if new_title_state != self.title_state:
                self.title_state = new_title_state
                self.time_title_last_checked = time_now
                return True
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

                return False
        return True

    async def check_still_here_button(self):
        return await self.click_element(
            By.XPATH, '//button[contains(text(), "I\'m Still Here")]'
        )

    async def check_alert(self):
        self.bot.logger.debug("Checking for alerts...")
        try:
            alert = self.driver.find_element(By.CLASS_NAME, "alert")
            self.bot.logger.debug("ALERT FOUND")
            self.bot.logger.debug(f"Current URL: {self.driver.current_url}")

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
                self.bot.logger.debug("ALERT FOUND BUT NO QUESTION DETECTED")
            return True
        except Exception as e:
            self.bot.logger.debug(f"No alert found: {e}")
            return False

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
            pass

    async def check_next_button(self):
        return await self.click_element(By.ID, "next-button")

    ##############################
    # BASE FUNCTIONS FOR THE BOT #
    ##############################
    async def automate(self):
        self.bot.logger.debug("Automating...")
        await self.check_alert()
        await self.check_locked_out()
        await self.check_quiz()
        await self.check_still_here_button()
        await self.check_next_button()
        await self.check_chapter_button()
        await self.check_title()

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
        except Exception as e:
            self.bot.logger.error(f"An error occurred while stopping the driver: {e}")
            await self.bot.log_channel.send(
                "```❌ An error occurred while stopping the driver. Exiting.```"
            )
            sys.exit(1)
