from pyrogram.types import InlineKeyboardButton

from utils.consts import callbacks
from .admin_inline_buttons_texts import *

recent_button = InlineKeyboardButton(RECENT_BUTTON_TEXT, callback_data=callbacks.FORWARD)
