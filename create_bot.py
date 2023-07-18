from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from telethon import TelegramClient

from config import config

client = TelegramClient('bot_session', config.API_ID, config.API_HASH)
client.start(bot_token=config.TOKEN)
bot = Bot(token=config.TOKEN)
bot.parse_mode = ParseMode.MARKDOWN
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
