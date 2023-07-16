from aiogram.types import ReplyKeyboardMarkup
from .recommendations_reply_buttons import *
from keyboards.general.reply.general_reply_buttons import *

start_control_buttons = [
    [start_button],
    [to_categories_button, to_personal_button],
]

admin_start_control_buttons = [
    [start_button],
    [to_admin_panel_button],
    [to_categories_button, to_personal_button]
]

control_buttons = [
    [skip_button],
    [to_categories_button, to_personal_button]
]

admin_control_buttons = [
    [skip_button],
    [to_admin_panel_button],
    [to_categories_button, to_personal_button]
]

recommendations_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
recommendations_admin_control_keyboard = ReplyKeyboardMarkup(admin_control_buttons, resize_keyboard=True)
recommendations_start_control_keyboard = ReplyKeyboardMarkup(start_control_buttons, resize_keyboard=True)
recommendations_admin_start_control_keyboard = ReplyKeyboardMarkup(admin_start_control_buttons, resize_keyboard=True)
