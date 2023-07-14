from aiogram.types import ReplyKeyboardMarkup

from buttons.reply.reply_buttons import *

control_buttons = [
    [like_button, dislike_button, skip_button],
    [to_categories_button, to_personal_button]
]
admin_control_buttons = [
    [skip_button],
    [to_admin_panel_button],
    [to_categories_button, to_personal_button]
]

recommendations_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
recommendations_admin_control_keyboard = ReplyKeyboardMarkup(admin_control_buttons, resize_keyboard=True)
