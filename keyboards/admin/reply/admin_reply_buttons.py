from pyrogram.types import KeyboardButton
from .admin_reply_buttons_texts import *
from keyboards.general.reply.general_reply_buttons import TO_RECOMMENDATIONS_BUTTON_TEXT, TO_CATEGORIES_BUTTON_TEXT

to_recommendations_button = KeyboardButton(TO_RECOMMENDATIONS_BUTTON_TEXT)
to_categories_button = KeyboardButton(TO_CATEGORIES_BUTTON_TEXT)

list_categories_button = KeyboardButton(LIST_CATEGORIES_BUTTON_TEXT)
list_premium_channels_button = KeyboardButton(LIST_PREMIUM_CHANNELS_BUTTON_TEXT)
list_category_channels_button = KeyboardButton(LIST_CATEGORIES_CHANNELS_BUTTON_TEXT)
list_coefficients_button = KeyboardButton(LIST_COEFFICIENTS)

add_premium_channels_button = KeyboardButton(ADD_PREMIUM_CHANNELS_BUTTON_TEXT)
add_category_channels_button = KeyboardButton(ADD_CATEGORY_CHANNELS_BUTTON_TEXT)
add_category_button = KeyboardButton(ADD_CATEGORY_BUTTON_TEXT)
add_coefficients_button = KeyboardButton(ADD_COEFFICIENTS)

delete_premium_channels_button = KeyboardButton(DELETE_PREMIUM_CHANNELS_BUTTON_TEXT)
delete_category_channels_button = KeyboardButton(DELETE_CATEGORIES_CHANNELS_BUTTON_TEXT)
delete_general_category_button = KeyboardButton(DELETE_CATEGORY_BUTTON_TEXT)
delete_coefficients_button = KeyboardButton(DELETE_COEFFICIENTS)
