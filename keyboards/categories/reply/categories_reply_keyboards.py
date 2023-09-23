from pyrogram.types import ReplyKeyboardMarkup
from .categories_reply_buttons import *

start_control_buttons = [
    [start_button],
    [add_delete_user_categories_button],
    [to_recommendations_button, to_personal_button]
]

admin_start_control_buttons = [
    [start_button],
    [add_delete_user_categories_button, to_admin_panel_button],
    [to_recommendations_button, to_personal_button]
]

control_buttons = [
    [add_delete_user_categories_button],
    [to_recommendations_button, to_personal_button]
]

admin_control_buttons = [
    [add_delete_user_categories_button, to_admin_panel_button],
    [to_recommendations_button, to_personal_button]
]

categories_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
categories_admin_control_keyboard = ReplyKeyboardMarkup(admin_control_buttons, resize_keyboard=True)
categories_start_control_keyboard = ReplyKeyboardMarkup(start_control_buttons, resize_keyboard=True)
categories_admin_start_control_keyboard = ReplyKeyboardMarkup(admin_start_control_buttons, resize_keyboard=True)
