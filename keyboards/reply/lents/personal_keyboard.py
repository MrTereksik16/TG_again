from aiogram.types import ReplyKeyboardMarkup

from buttons.reply.lents.lents_buttons import *

keyboard = [
    [skip_button],
    [list_channels_button, add_channels_button, delete_channels_button],
    # [to_recommendations_button, to_categories_button],
]

personal_control_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
