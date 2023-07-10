import logging
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from config.startup_config import set_default_commands
from database.models import Base, engine
from config.logging_config import logger
from handlers.handlers import dp, on_add_channels_command, on_list_command, on_start_command, on_add_channels_message, \
    on_delete_user_channel_command, on_add_channels_button_click
from store.states import UserStates
from callbacks import callbacks
from buttons.reply.lents import lents_buttons_text

dp.register_message_handler(
    on_start_command,
    commands='start',
)

dp.register_message_handler(
    on_add_channels_command,
    commands='add_channels'
)

dp.register_message_handler(
    on_add_channels_command,
    Text(equals=lents_buttons_text.add_channels_button_text),
)

dp.register_callback_query_handler(on_add_channels_button_click, Text(callbacks.ADD_USER_CHANNELS))

dp.register_message_handler(
    on_add_channels_message,
    state=UserStates.GET_CHANNELS,
    content_types=types.ContentType.TEXT,
)

dp.register_message_handler(
    on_list_command,
    commands='list',
)

dp.register_message_handler(
    on_list_command,
    Text(equals=lents_buttons_text.list_channels_button_text),
)

dp.register_message_handler(
    on_delete_user_channel_command,
    commands='delete_channels'
)
dp.register_message_handler(
    on_delete_user_channel_command,
    Text(equals=lents_buttons_text.delete_channels_button_text),
)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger.warning("Starting the bot...")

    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)
