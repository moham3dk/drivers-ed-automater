import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = True
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    bot_token = os.getenv("BOT_TOKEN")
    course_url = "https://school.toocooltrafficschool.com/student/course/31113911"  # TODO remove course_url and make it navigate to the course page instead

    if not username or not password or not bot_token:
        raise ValueError("Please provide all the necessary environment variables.")
