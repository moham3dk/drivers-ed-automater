@echo off
setlocal enabledelayedexpansion

:prompt_input
set /p "input=%~1: "
exit /b

where python3 >nul 2>&1
if %errorlevel% neq 0 (
    echo Python3 is not installed. Please install Python3 and try again.
    exit /b 1
)

if not exist ".venv" (
    python3 -m venv .venv
    echo Virtual environment created.
    
    call .venv\Scripts\activate.bat
    
    if exist "requirements.txt" (
        pip install -r requirements.txt
        echo Requirements installed.
    ) else (
        echo requirements.txt not found. Please ensure it's in the same directory.
        deactivate
        exit /b 1
    )
) else (
    echo Virtual environment already exists. Skipping requirements installation.
    call .venv\Scripts\activate.bat
)

set "ENV_FILE=.env"

if exist "%ENV_FILE%" (
    set /p "overwrite=.env file already exists. Do you want to overwrite it? (y/n): "
    if /i not "!overwrite!"=="y" (
        echo Keeping existing .env file.
        goto :env_setup_done
    ) else (
        > %ENV_FILE%
    )
)

:env_setup
set /p "BOT_TOKEN=Enter your Discord bot token: "
set /p "DRIVERS_ED_USERNAME=Enter your Driver's Ed username: "
set /p "DRIVERS_ED_PASSWORD=Enter your Driver's Ed password: "
set /p "COURSE_URL=Enter the course page URL: "

(
    echo BOT_TOKEN=!BOT_TOKEN!
    echo USERNAME=!DRIVERS_ED_USERNAME!
    echo PASSWORD=!DRIVERS_ED_PASSWORD!
    echo COURSE_URL=!COURSE_URL!
) >> %ENV_FILE%
echo .env file created with provided details.

:env_setup_done

cls

python3 src\bot.py

deactivate

endlocal