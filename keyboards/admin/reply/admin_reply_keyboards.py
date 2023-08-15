from pyrogram.types import ReplyKeyboardMarkup
from .admin_reply_buttons import *

control_buttons = [
    [add_premium_channels_button],
    [add_category_channels_button],
    [add_category_button],
    [add_coefficients_button],
    [list_premium_channels_button],
    [list_category_channels_button],
    [list_categories_button],
    [list_coefficients_button],
    [delete_premium_channels_button],
    [delete_category_channels_button],
    [delete_general_category_button],
    [delete_coefficients_button],
    [to_recommendations_button, to_categories_button],
]

admin_panel_control_keyboard = ReplyKeyboardMarkup(control_buttons, resize_keyboard=True)
