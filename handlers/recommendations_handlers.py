from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config.config import ADMINS
from database.queries.create_queries import *
from database.queries.get_queries import *
from keyboards.recommendations.reply.recommendations_reply_keyboards import *
from store.states import RecommendationsStates
from utils.consts import answers
from keyboards import general_reply_buttons_texts

async def on_recommendations_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    keyboard = recommendations_admin_start_control_keyboard if user_is_admin else recommendations_start_control_keyboard
    answer = 'Лента рекомендаций'

    await state.set_state(RecommendationsStates.RECOMMENDATIONS_FEED)
    await message.answer(answer, reply_markup=keyboard)


async def on_start_command(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    last_post_id = 1
    user = await get_user(user_tg_id)
    keyboard = recommendations_control_keyboard
    user_is_admin = user_tg_id in ADMINS

    await state.set_state(RecommendationsStates.RECOMMENDATIONS_FEED)

    if user_is_admin:
        keyboard = recommendations_admin_control_keyboard
    if not user:
        await create_user(user_tg_id, last_post_id)
        await message.answer(answers.START_MESSAGE_FOR_NEW, reply_markup=keyboard)
    else:
        await message.answer(answers.START_MESSAGE_FOR_OLD, reply_markup=keyboard)


def register_recommendations_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_recommendations_feed_message,
        Text(equals=general_reply_buttons_texts.TO_RECOMMENDATIONS_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_start_command,
        commands='start',
        state='*'
    )

