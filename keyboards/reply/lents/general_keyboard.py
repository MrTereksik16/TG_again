from aiogram.types import ReplyKeyboardMarkup

from buttons.reply.lents.lents_buttons import like, dislike, skip, categories, personal

keyboard = [
    [like, dislike, skip],
    [categories, personal]
]

general_control_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
