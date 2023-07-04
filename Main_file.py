import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import executor
from ORM import *
from Start import on_start


logging.basicConfig(level=logging.INFO)

TOKEN = '6274697186:AAFvHLkDA19G_wPTriryAkYd1c29t3wUZtk'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: Message):
    await on_start(message=message)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    executor.start_polling(dp, skip_updates=True)