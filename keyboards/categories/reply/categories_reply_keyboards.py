from aiogram.types import ReplyKeyboardMarkup
from .categories_reply_buttons import *


async def categories_keyboard(categories):
    categories_buttons = [
        [start_button],
    ]
    for category in categories:
        categories_buttons.append([KeyboardButton(text=category)])
    keyboard = ReplyKeyboardMarkup(categories_buttons, resize_keyboard=True)
    return keyboard

start_control_buttons = [
    [start_button],
    [add_delete_user_categories_button],
    [to_recommendations_button, to_personal_button]
]

admin_start_control_buttons = [
    [start_button],
    [add_delete_user_categories_button],
    [to_recommendations_button, to_personal_button]
]

control_buttons = [
    [skip_button],
    [add_delete_user_categories_button, to_admin_panel_button],
    [to_recommendations_button, to_personal_button]
]

admin_control_buttons = [
    [skip_button],
    [add_delete_user_categories_button, to_admin_panel_button],
    [to_recommendations_button, to_personal_button]
]

categories_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
categories_admin_control_keyboard = ReplyKeyboardMarkup(admin_control_buttons, resize_keyboard=True)
categories_start_control_keyboard = ReplyKeyboardMarkup(start_control_buttons, resize_keyboard=True)
categories_admin_start_control_keyboard = ReplyKeyboardMarkup(admin_start_control_buttons, resize_keyboard=True)
