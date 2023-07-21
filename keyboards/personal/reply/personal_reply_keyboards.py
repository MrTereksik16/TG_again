from pyrogram.types import ReplyKeyboardMarkup
from .personal_reply_buttons import *

start_control_buttons = [
    [start_button],
    [list_user_channels_button, add_user_channels_button, delete_user_channels_button],
    [to_recommendations_button, to_categories_button],
]

control_buttons = [
    [skip_button],
    [list_user_channels_button, add_user_channels_button, delete_user_channels_button],
    [to_recommendations_button, to_categories_button],
]

personal_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
personal_start_control_keyboard = ReplyKeyboardMarkup(start_control_buttons, resize_keyboard=True)
