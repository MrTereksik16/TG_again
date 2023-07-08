from aiogram.types import InlineKeyboardButton

from callbacks import callbacks

add_user_channels_button = InlineKeyboardButton('Добавь каналы', callback_data=callbacks.ADD_USER_CHANNELS)
