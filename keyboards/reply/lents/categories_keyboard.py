from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from buttons.reply.lents.lents_buttons import like, dislike, skip, recommendations, personal

choose_keyboard = [
    [KeyboardButton(text="🔥Продолжить")],
    [KeyboardButton(text="🦁Животные"), KeyboardButton(text="🎮Игры")],
    [KeyboardButton(text="📈Инвестиции"), KeyboardButton(text="⚽️Спорт")],
    [KeyboardButton(text="🔬Наука"), KeyboardButton(text="🚗Машины")],
    [KeyboardButton(text="👨‍💻IT"), KeyboardButton(text="🕹Техника")],
    [KeyboardButton(text="💸Финансы"), KeyboardButton(text="🌎Путешествия")],
    [KeyboardButton(text="😂Мемы"), KeyboardButton(text="🪙Криптовалюты")],
    [KeyboardButton(text="🎬Фильмы"), KeyboardButton(text="📸Аниме")]
]
categories_choose_keyboard = ReplyKeyboardMarkup(choose_keyboard, resize_keyboard=True)

control_keyboard = [
    [like, dislike, skip],
    [recommendations, personal]
]

categories_control_keyboard = ReplyKeyboardMarkup(control_keyboard, resize_keyboard=True)
