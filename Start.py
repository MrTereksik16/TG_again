import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import executor
from ORM import *
from Keyboards import start_button
from aiogram.types import ReplyKeyboardMarkup
from Parse_mode import show_res
logging.basicConfig(level=logging.INFO)

TOKEN = '6274697186:AAFvHLkDA19G_wPTriryAkYd1c29t3wUZtk'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def on_start(message: Message):
    # keyboard = ReplyKeyboardMarkup(keyboard=start_button, resize_keyboard=True)
    # result = session.execute(select(User.user_tg_id)).all()
    # user_tg_ids = [row[0] for row in result]
    # if message.from_user.id not in user_tg_ids:
    #     session.add(User(user_tg_id=message.from_user.id, last_post_id=123))
    #     session.commit()
    #     await message.reply("<b>Добро пожаловать дорогой, {message.from_user.first_name}!👨‍💻\n\nМы создали этого бота для твоего удобства, чтобы тебе было удобно пользоваться Телеграммом, источниками твоего вдохновения и отдыха 😇</b>",parse_mode="HTML",
    #         reply_markup=keyboard)
    # else:
    #     await message.reply(f"<b>Рады вас снова видеть ,{message.from_user.first_name}😃</b>", reply_markup=keyboard, parse_mode="HTML")
    await show_res(message=message)
