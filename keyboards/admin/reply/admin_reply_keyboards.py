from aiogram.types import ReplyKeyboardMarkup
from .admin_reply_buttons import *

control_buttons = [
    [add_general_channels_button, add_general_category_button],
    [delete_general_channels_button, delete_general_category_button],
    [list_general_channels_button, list_categories_button],
    [to_recommendations_button, to_categories_button],
]
waiting_buttons = [
    [delete_general_channels_button, delete_general_category_button],
    [list_general_channels_button, list_categories_button],
    [to_recommendations_button, to_categories_button],
]
admin_panel_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
admin_panel_wait_for_parse_general_channels_keyboard = ReplyKeyboardMarkup(waiting_buttons, resize_keyboard=True)
