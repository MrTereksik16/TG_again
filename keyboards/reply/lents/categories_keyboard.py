from aiogram.types import ReplyKeyboardMarkup
from buttons.reply.lents.lents_buttons import *

categories_keyboard = ReplyKeyboardMarkup(categories_buttons, resize_keyboard=True)

control_keyboard = [
    [like_button, dislike_button, skip_button],
    [to_recommendations_button, to_personal_button]
]

categories_control_keyboard = ReplyKeyboardMarkup(control_keyboard, resize_keyboard=True)
