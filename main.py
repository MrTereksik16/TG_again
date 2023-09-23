import logging
from aiogram.utils import executor
from config.logging_config import logger
from create_bot import dp, scheduler
from handlers import register_personal_handlers, register_recommendations_handlers, register_categories_handlers, \
    register_generals_handlers, register_admin_handlers
from database.initial_data import create_initial_data
from on_start_bot_tasks import on_start_bot_tasks

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger.warning("Starting the bot...")

    # create_initial_data()

    register_generals_handlers(dp)
    register_recommendations_handlers(dp)
    register_categories_handlers(dp)
    register_personal_handlers(dp)
    register_admin_handlers(dp)

    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=[on_start_bot_tasks])
