from pyrogram.types import InlineKeyboardButton
import callbacks
from .personal_inline_buttons_texts import *

add_user_channels_button = InlineKeyboardButton(add_user_channels_button_text, callback_data=callbacks.ADD_USER_CHANNELS)
