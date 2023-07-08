from aiogram.types import InlineKeyboardButton

from buttons.inline.inline_buttons_text import *
from callbacks import callbacks

add_user_channels_button = InlineKeyboardButton(add_user_channels_button_text, callback_data=callbacks.ADD_USER_CHANNELS)
