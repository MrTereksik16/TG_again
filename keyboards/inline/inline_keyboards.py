from aiogram.types import InlineKeyboardMarkup
from buttons.inline.inline_buttons import add_user_channels_button

add_user_channels_inline_keyboard = InlineKeyboardMarkup().add(add_user_channels_button)
