import logging

from aiogram import types
from aiogram import executor
from aiogram.types import Message
from database.models import Base, engine
from handlers.handlers import *
from logging_config import logger

logging.basicConfig(level=logging.INFO)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Посмотреть посты"),
        types.BotCommand("add_channels", "Добавить канал"),
        types.BotCommand("list", "Список добавленных каналов"),
        # types.BotCommand("deletechannels", "Удалить каналы из списка"),
    ])


@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    await on_start_command(message=message)


@dp.message_handler(commands=['add_channels'])
async def add_channels_command(message: Message):
    await on_add_channels_command(message)
    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def add_channels(message: Message):
        await on_add_channels_message(message)

@dp.message_handler(text = "🌟Перейти в ленту️ категорий")
async def go_to_categories_lent(message: Message):
    await go_to_categories_lenta(message=message)
    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def get_categories(message: Message):
        await get_categories_from_user(message=message)


@dp.message_handler(commands=['list'])
async def list_command(message: Message):
    await on_list_command(message)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    logger.warning("Starting the bot...")
    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)
