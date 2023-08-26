from pyrogram.types import InlineKeyboardButton

import callbacks
from .admin_inline_buttons_texts import *

recent_button = InlineKeyboardButton(RECENT_BUTTON_TEXT, callback_data=callbacks.FORWARD)
