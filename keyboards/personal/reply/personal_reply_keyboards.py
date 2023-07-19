from aiogram.types import ReplyKeyboardMarkup
from pyrogram.types import ReplyKeyboardMarkup as ReplyKeyboardMarkup2
from .personal_reply_buttons import *

start_control_buttons = [
    [start_button],
    [list_user_channels_button, add_user_channels_button, delete_user_channels_button],
    [to_recommendations_button, to_categories_button],
]

wait_for_parse_keyboard = [
    [list_user_channels_button, add_user_channels_button, delete_user_channels_button],
    [to_recommendations_button, to_categories_button],
]

control_buttons = [
    [skip_button],
    [list_user_channels_button, add_user_channels_button, delete_user_channels_button],
    [to_recommendations_button, to_categories_button],
]


start_control_buttons2 = [
    [start_button2],
    [list_user_channels_button2, add_user_channels_button2, delete_user_channels_button2],
    [to_recommendations_button2, to_categories_button2],
]

wait_for_parse_keyboard2 = [
    [list_user_channels_button2, add_user_channels_button2, delete_user_channels_button2],
    [to_recommendations_button2, to_categories_button2],
]

control_buttons2 = [
    [skip_button2],
    [list_user_channels_button2, add_user_channels_button2, delete_user_channels_button2],
    [to_recommendations_button2, to_categories_button2],
]

personal_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
personal_start_control_keyboard = ReplyKeyboardMarkup(start_control_buttons, resize_keyboard=True)
personal_wait_for_parse_keyboard = ReplyKeyboardMarkup(wait_for_parse_keyboard, resize_keyboard=True)

personal_control_keyboard2 = ReplyKeyboardMarkup2(control_buttons2, resize_keyboard=True)
personal_start_control_keyboard2 = ReplyKeyboardMarkup2(start_control_buttons2, resize_keyboard=True)
personal_wait_for_parse_keyboard2 = ReplyKeyboardMarkup2(wait_for_parse_keyboard2, resize_keyboard=True)
