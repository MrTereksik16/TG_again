from pyrogram.types import ReplyKeyboardMarkup
from .general_reply_buttons import cancel_button

cancel_buttons = [
    [cancel_button]
]


general_cancel_keyboard = ReplyKeyboardMarkup(cancel_buttons, resize_keyboard=True)