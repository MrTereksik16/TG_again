from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import config
from pyrogram import Client
from pyrogram import enums

bot_client = Client('bot_session', config.BOT_API_ID, config.BOT_API_HASH, bot_token=config.TOKEN, parse_mode=enums.ParseMode.HTML).start()

bot = Bot(token=config.TOKEN, disable_web_page_preview=True, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()
