from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from config import config
from pyrogram import Client
from pyrogram import enums

client = Client('bot_session', config.API_ID, config.API_HASH, bot_token=config.TOKEN, parse_mode=enums.ParseMode.DISABLED)
client.start()
bot = Bot(token=config.TOKEN)
bot.parse_mode = ParseMode.MARKDOWN
bot.disable_web_page_preview = True
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
