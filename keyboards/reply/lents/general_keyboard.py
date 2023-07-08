from aiogram.types import ReplyKeyboardMarkup

from buttons.reply.lents.lents_buttons import *

keyboard = [
    [like_button, dislike_button, skip_button],
    [to_categories_button, to_personal_button]
]

general_control_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
