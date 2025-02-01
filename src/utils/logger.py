from colorama import Fore, Style
from datetime import datetime
from config.config import Config


class Logger:
    LOG_STYLES = {
        "INFO": (Fore.CYAN, "[+]"),
        "WARNING": (Fore.MAGENTA, "[!]"),
        "ERROR": (Fore.RED, "[X]"),
        "SUCCESS": (Fore.GREEN, "[✔]"),
        "DEBUG": (Fore.YELLOW, "[*]"),
    }

    def generate_timestamp(self):
        return f"{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}"

    def log(self, level, message):
        color, symbol = self.LOG_STYLES.get(level, (Fore.WHITE, "[?]"))
        print(
            f"{color}{symbol} {Fore.WHITE}{Style.RESET_ALL} {self.generate_timestamp()} → {message}"
        )

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)

    def success(self, message):
        self.log("SUCCESS", message)

    def debug(self, message):
        if Config.DEBUG:
            self.log("DEBUG", message)
