from .admin_inline_buttons import *
from pyrogram.types import InlineKeyboardMarkup

buttons = [
    [recent_button]
]

admin_recent_keyboard = InlineKeyboardMarkup(buttons)