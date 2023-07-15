from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from buttons.reply import reply_buttons_text
from config.config import ADMINS
from database.queries.get_queries import *
from handlers.personal_handlers import on_add_channels_message, on_list_channels_message
from keyboards.reply.admin_keyboard import *
from keyboards.reply.categories_keyboard import *
from keyboards.reply.personal_keyboard import *
from keyboards.reply.recommendations_keyboard import *
from store.states import UserStates
from utils.helpers import convert_categories_to_string, send_post_for_user_in_personal_feed


async def on_personal_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_channels = await get_user_channels(user_tg_id)
    await state.set_state(UserStates.PERSONAL_FEED)

    if user_channels:
        await on_list_channels_message(message)
    else:
        await on_add_channels_message(message, state)


async def on_add_or_delete_user_categories_message(message: Message, state: FSMContext):
    context = await state.get_data()
    if 'categories' in context:
        categories = await get_categories()
    else:
        categories = context['categories']

    user_tg_id = message.from_user.id
    user_categories = await get_user_categories(user_tg_id)
    list_of_categories = '\n'.join(user_categories)
    keyboard = await categories_keyboard(categories)
    answer = '***Наш список категорий, но он обязательно будет обновляться:***\n\n'
    answer += await convert_categories_to_string(categories)
    answer += '\n‼***Чтобы удалить категорию нажмите на нее второй раз***‼'
    await message.answer(answer, reply_markup=keyboard, parse_mode='Markdown')

    if user_categories:
        await message.answer(f'Список выбранных категорий:\n{list_of_categories}')

    await state.set_state(UserStates.GET_USER_CATEGORIES)


async def on_categories_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    categories = await get_categories()
    user_categories = await get_user_categories(user_tg_id)
    await state.update_data(categories=categories)

    await state.set_state(UserStates.CATEGORIES_FEED)
    if user_categories:
        keyboard = categories_admin_control_keyboard if user_tg_id in ADMINS else categories_control_keyboard
        # Тут типо должна вызываться функция отправки постов, но пока стоит заглушка
        await message.answer('Лента категорий', reply_markup=keyboard)
    else:
        await on_add_or_delete_user_categories_message(message, state)


async def on_start_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    current_state = await state.get_state()
    user_is_admin = user_tg_id in ADMINS

    if current_state == 'UserStates:RECOMMENDATIONS_FEED':
        keyboard = recommendations_admin_control_keyboard if user_is_admin else recommendations_control_keyboard
        await message.answer('Посты из рекоммендаций', reply_markup=keyboard)
    elif current_state == 'UserStates:GET_USER_CATEGORIES':
        await state.reset_state()
        keyboard = categories_admin_control_keyboard if user_is_admin else categories_control_keyboard
        await message.answer('Посты из категорий', reply_markup=keyboard)
    elif current_state == 'UserStates:CATEGORIES_FEED':
        keyboard = categories_admin_control_keyboard if user_is_admin else categories_control_keyboard
        await message.answer('Посты из категорий', reply_markup=keyboard)
    elif current_state == 'UserStates:PERSONAL_FEED':
        keyboard = personal_control_keyboard
        await send_post_for_user_in_personal_feed(message, keyboard)


async def on_recommendations_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    keyboard = recommendations_admin_start_control_keyboard if user_is_admin else recommendations_start_control_keyboard
    answer = 'Лента рекомендаций'

    await state.set_state(UserStates.RECOMMENDATIONS_FEED)
    await message.answer(answer, reply_markup=keyboard)


async def on_admin_panel_message(message: Message, state: FSMContext):
    await state.reset_state()
    await message.answer('Админ панель', reply_markup=admin_panel_control_keyboard)


def register_generals_handlers(dp):
    dp.register_message_handler(
        on_personal_feed_message,
        Text(equals=reply_buttons_text.TO_PERSONAL_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_categories_feed_message,
        Text(equals=reply_buttons_text.TO_CATEGORIES_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_recommendations_feed_message,
        Text(equals=reply_buttons_text.TO_RECOMMENDATIONS_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_admin_panel_message,
        Text(equals=reply_buttons_text.TO_ADMIN_PANEL_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_add_or_delete_user_categories_message,
        Text(equals=ADD_OR_DELETE_USER_CATEGORIES_BUTTON_TEXT),
        state='*'
    )
    dp.register_message_handler(
        on_start_message,
        Text(START_BUTTON_TEXT),
        state='*'
    )
