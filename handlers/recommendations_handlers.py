from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from config.config import ADMINS
from create_bot import bot, bot_client
from database.queries.create_queries import create_user, create_user_event
from database.queries.get_queries import get_user
from database.queries.update_queries import update_last_visit_time, update_daily_new_users_amount
from keyboards import recommendations_reply_keyboards
from keyboards.general.helpers import build_start_inline_keyboards
from store.states import RecommendationsStates
from utils.consts import answers, errors, commands
from keyboards import general_reply_buttons_texts
from utils.custom_types import Modes, UserEventsTypes
from utils.helpers import send_next_posts, send_end_message, get_next_posts


async def on_start_command(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user = await get_user(user_tg_id)
    user_is_admin = user_tg_id in ADMINS
    await state.set_state(RecommendationsStates.RECOMMENDATIONS_FEED)

    keyboard = recommendations_reply_keyboards.recommendations_start_control_keyboard

    if user_is_admin:
        keyboard = recommendations_reply_keyboards.recommendations_admin_start_control_keyboard
    if not user:
        first_name = message.from_user.first_name or ''
        last_name = message.from_user.last_name
        username = message.from_user.username

        await create_user(user_tg_id, first_name, last_name, username)
        bot_info = await bot.get_me()
        bot_username = bot_info.first_name
        await message.answer(answers.NEW_START_MESSAGE_TEXT.format(bot_username=bot_username), reply_markup=keyboard)
        await update_daily_new_users_amount()
        await create_user_event(user_tg_id, UserEventsTypes.REGISTRATION)
    else:
        await create_user_event(user_tg_id, UserEventsTypes.USED)
        await update_last_visit_time(user_tg_id)
        await message.answer(answers.RECOMMENDATIONS_FEED_MESSAGE_TEXT, reply_markup=keyboard)


async def on_recommendations_feed_message(message: Message, state: FSMContext):
    await state.set_state(RecommendationsStates.RECOMMENDATIONS_FEED)
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    user_is_admin = user_tg_id in ADMINS
    mode = Modes.RECOMMENDATIONS
    next_post = await get_next_posts(user_tg_id, mode)

    if next_post:
        keyboard = recommendations_reply_keyboards.recommendations_control_keyboard
        if user_is_admin:
            keyboard = recommendations_reply_keyboards.recommendations_admin_control_keyboard
    else:
        keyboard = recommendations_reply_keyboards.recommendations_start_control_keyboard
        if user_is_admin:
            keyboard = recommendations_reply_keyboards.recommendations_admin_start_control_keyboard

    keyboard = build_start_inline_keyboards(mode)

    await bot_client.send_message(chat_id, answers.RECOMMENDATIONS_FEED_MESSAGE_TEXT, reply_markup=keyboard)

    if next_post:
        await send_next_posts(user_tg_id, chat_id, mode, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, mode)


def register_recommendations_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_recommendations_feed_message,
        Text(equals=general_reply_buttons_texts.TO_RECOMMENDATIONS_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_start_command,
        commands=commands.START,
        state='*'
    )
