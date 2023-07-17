from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon import TelegramClient

from config import config

client = TelegramClient('bot_session', config.API_ID, config.API_HASH)
client.start(bot_token=config.TOKEN)
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
