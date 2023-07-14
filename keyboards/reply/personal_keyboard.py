from aiogram.types import ReplyKeyboardMarkup

from buttons.reply.reply_buttons import *

control_buttons = [
    [skip_button],
    [list_channels_button, add_personal_channels_button, delete_channels_button],
    [to_recommendations_button, to_categories_button],
]

personal_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
