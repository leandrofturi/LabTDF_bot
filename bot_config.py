import os
import telegram
from telegram.ext import Updater, CallbackQueryHandler
from dotenv import load_dotenv
load_dotenv()

# Credentials
token = os.getenv("LabTDF_bot_token")

# Config
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
bot = telegram.Bot(token)