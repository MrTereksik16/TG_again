from aiogram.types import ReplyKeyboardMarkup
from buttons.reply.reply_buttons import *

control_buttons = [
    [add_general_channels_button, add_general_category_button],
    [delete_general_channels_button, delete_general_category_button],
    [to_recommendations_button],
    [to_personal_button],
    [to_categories_button]
]

admin_panel_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)