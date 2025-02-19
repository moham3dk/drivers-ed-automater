import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False # if u change this to true u will get in depth logs
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    bot_token = os.getenv("BOT_TOKEN")
    course_url = os.getenv("COURSE_URL")

    if not username or not password or not bot_token:
        raise ValueError("Please provide all the necessary environment variables.")
