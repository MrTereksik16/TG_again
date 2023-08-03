from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from config.config import ADMINS
from create_bot import bot
from database.queries.create_queries import *
from database.queries.get_queries import *
from keyboards import recommendations_reply_keyboards
from store.states import RecommendationsStates
from utils.consts import answers
from keyboards import general_reply_buttons_texts
from utils.helpers import get_next_post, send_next_post, send_end_message
from utils.types import Modes


async def on_start_command(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user = await get_user(user_tg_id)
    keyboard = recommendations_reply_keyboards.recommendations_control_keyboard
    user_is_admin = user_tg_id in ADMINS

    await state.set_state(RecommendationsStates.RECOMMENDATIONS_FEED)

    if user_is_admin:
        keyboard = recommendations_reply_keyboards.recommendations_admin_start_control_keyboard

    if not user:
        await create_user(user_tg_id)
        bot_info = await bot.get_me()
        bot_username = bot_info.first_name
        await message.answer(answers.START_MESSAGE_FOR_NEW.format(bot_username=bot_username), reply_markup=keyboard)
    else:
        await message.answer('<b>Лента рекомендаций</b>', reply_markup=keyboard)


async def on_recommendations_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    keyboard = recommendations_reply_keyboards.recommendations_admin_start_control_keyboard if user_is_admin else recommendations_reply_keyboards.recommendations_start_control_keyboard

    await state.set_state(RecommendationsStates.RECOMMENDATIONS_FEED)
    await message.answer('<b>Лента рекомендаций</b>', reply_markup=keyboard)


async def on_start_message(message: Message):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    chat_id = message.chat.id

    next_post = await get_next_post(user_tg_id, Modes.RECOMMENDATIONS)
    keyboard = recommendations_reply_keyboards.recommendations_control_keyboard

    if user_is_admin:
        keyboard = recommendations_reply_keyboards.recommendations_admin_control_keyboard

    if next_post:
        await message.answer(answers.PRE_START_MESSAGE, reply_markup=keyboard)
        await send_next_post(user_tg_id, chat_id, Modes.RECOMMENDATIONS, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, Modes.RECOMMENDATIONS)


async def on_skip_message(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    err = await send_next_post(user_tg_id, chat_id, Modes.RECOMMENDATIONS)

    if err == errors.NO_POST:
        await send_end_message(user_tg_id, chat_id, Modes.PERSONAL)


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

    dp.register_message_handler(
        on_start_message,
        Text(general_reply_buttons_texts.START_BUTTON_TEXT),
        state=RecommendationsStates.RECOMMENDATIONS_FEED,
    )

    dp.register_message_handler(
        on_skip_message,
        Text(general_reply_buttons_texts.SKIP_BUTTON_TEXT),
        state=RecommendationsStates.RECOMMENDATIONS_FEED
    )
