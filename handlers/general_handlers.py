from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from config.config import ADMINS

from database.queries.get_queries import get_categories_posts
from keyboards.categories.reply.categories_reply_keyboards import *
from keyboards.personal.reply.personal_reply_keyboards import *
from keyboards.recommendations.reply.recommendations_reply_keyboards import *
from utils.helpers import send_post_in_personal_feed, send_post_in_recommendations_feed, send_post_in_categories_feed
from store.states import *
from keyboards import admin_reply_keyboards
from keyboards import general_reply_buttons_texts


async def on_start_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    current_state = await state.get_state()
    user_is_admin = user_tg_id in ADMINS

    print(current_state)

    if current_state == 'RecommendationsStates:RECOMMENDATIONS_FEED':
        await send_post_in_recommendations_feed(message)
    elif current_state == 'CategoriesStates:CATEGORIES_FEED':
        await send_post_in_categories_feed(message)
    elif current_state == 'CategoriesStates:GET_USER_CATEGORIES':
        await state.set_state(CategoriesStates.CATEGORIES_FEED)
        await send_post_in_categories_feed(message)
    elif current_state == 'PersonalStates:PERSONAL_FEED':
        await send_post_in_personal_feed(message)


async def on_admin_panel_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    user_tg_id = message.from_user.id
    if user_tg_id in ADMINS:
        await message.answer('*Админ панель*', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)


def register_generals_handlers(dp):
    dp.register_message_handler(
        on_start_message,
        Text(START_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_admin_panel_message,
        Text(equals=general_reply_buttons_texts.TO_ADMIN_PANEL_BUTTON_TEXT),
        state='*'
    )
