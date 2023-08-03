import logging
from aiogram import types, Dispatcher
from aiogram.utils import executor
from config.logging_config import logger
from create_bot import dp
from handlers import register_personal_handlers, register_recommendations_handlers, register_categories_handlers, \
    register_generals_handlers, register_admin_handlers
from database.initial_data import create_initial_data

async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "К рекомендациям"),
    ])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    create_initial_data()
    logger.warning("Starting the bot...")

    register_generals_handlers(dp)
    register_recommendations_handlers(dp)
    register_categories_handlers(dp)
    register_personal_handlers(dp)
    register_admin_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)
