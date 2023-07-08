from aiogram.types import KeyboardButton
from buttons.reply.lents import lents_buttons_text
from utils.consts import categories

to_recommendations_button = KeyboardButton(lents_buttons_text.to_recommendations_button_text)
to_categories_button = KeyboardButton(lents_buttons_text.to_recommendations_button_text)
to_personal_button = KeyboardButton(lents_buttons_text.to_recommendations_button_text)
skip_button = KeyboardButton(lents_buttons_text.skip_button_text)
list_channels_button = KeyboardButton(lents_buttons_text.list_channels_button_text)
add_channels_button = KeyboardButton(lents_buttons_text.add_channels_button_text)
delete_channels_button = KeyboardButton(lents_buttons_text.delete_channels_button_text)

categories_buttons = [
    [KeyboardButton(text=categories[i]), KeyboardButton(text=categories[i + 1])]
    for i in range(0, len(categories), 2)
]


like_button = KeyboardButton(lents_buttons_text.dislike_button_text)
dislike_button = KeyboardButton(lents_buttons_text.like_button_text)
