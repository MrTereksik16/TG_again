from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from config.config import ADMINS
from database.queries.create_queries import *
from database.queries.get_queries import *
from keyboards.reply.recommendations_keyboard import recommendations_control_keyboard, recommendations_admin_control_keyboard
from store.states import UserStates
from utils.consts import answers


async def on_start_command(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    last_post_id = 1
    user = await get_user(user_tg_id)
    keyboard = recommendations_control_keyboard
    user_is_admin = user_tg_id in ADMINS

    await state.set_state(UserStates.RECOMMENDATIONS_FEED)

    if user_is_admin:
        keyboard = recommendations_admin_control_keyboard
    if not user:
        await create_user(user_tg_id, last_post_id)
        await message.answer(answers.START_MESSAGE_FOR_NEW, reply_markup=keyboard)
    else:
        await message.answer(answers.START_MESSAGE_FOR_OLD, reply_markup=keyboard)


def register_recommendations_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_start_command,
        commands='start',
        state='*'
    )
