from aiogram.types import ReplyKeyboardMarkup

from buttons.reply.lents import lents_buttons

keyboard = [
    [lents_buttons.skip_button],
    [lents_buttons.list_channels_button, lents_buttons.add_channels_button, lents_buttons.delete_channels],
    # [lents_buttons.recommendations_button, lents_buttons.categories_button],
]
personal_control_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
