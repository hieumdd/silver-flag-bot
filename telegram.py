import os

from telegram import Bot

telegram_bot = Bot(os.getenv("TELEGRAM_TOKEN"))
