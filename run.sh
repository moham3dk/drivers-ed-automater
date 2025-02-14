#!/bin/bash

prompt_input() {
    read -p "$1: " input
    echo "$input"
}

if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 and try again."
    exit 1
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
    
    source .venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "Requirements installed."
    else
        echo "requirements.txt not found. Please ensure it's in the same directory."
        deactivate
        exit 1
    fi
else
    echo "Virtual environment already exists. Skipping requirements installation."
    source .venv/bin/activate
fi

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    read -p ".env file already exists. Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Keeping existing .env file."
    else
        > $ENV_FILE
    fi
fi

if [ ! -f "$ENV_FILE" ] || [ "$overwrite" == "y" ]; then
    BOT_TOKEN=$(prompt_input "Enter your Discord bot token")
    DRIVERS_ED_USERNAME=$(prompt_input "Enter your Driver's Ed username")
    DRIVERS_ED_PASSWORD=$(prompt_input "Enter your Driver's Ed password")
    COURSE_URL=$(prompt_input "Enter the course page URL")

    echo "BOT_TOKEN=$BOT_TOKEN" >> $ENV_FILE
    echo "USERNAME=$DRIVERS_ED_USERNAME" >> $ENV_FILE
    echo "PASSWORD=$DRIVERS_ED_PASSWORD" >> $ENV_FILE
    echo "COURSE_URL=$COURSE_URL" >> $ENV_FILE
    echo ".env file created with provided details."
fi

clear

python3 src/bot.py

deactivate