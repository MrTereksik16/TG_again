from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from aiogram import Dispatcher

from config.config import ADMINS
from database.queries.create_queries import *
from database.queries.delete_queries import *
from database.queries.get_queries import *
from handlers.general_handlers import on_start_message
from keyboards.categories.reply.categories_reply_keyboards import categories_admin_control_keyboard, \
    categories_control_keyboard, categories_keyboard

from store.states import CategoriesStates
from utils.helpers import convert_categories_to_string
from keyboards import general_reply_buttons_texts, categories_reply_buttons_texts

async def on_categories_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_categories = await get_user_categories(user_tg_id)
    await state.update_data(user_categories=user_categories)
    await state.set_state(CategoriesStates.CATEGORIES_FEED)
    if user_categories:
        keyboard = categories_admin_control_keyboard if user_tg_id in ADMINS else categories_control_keyboard
        await message.answer('Лента категорий', reply_markup=keyboard)
    else:
        await on_add_or_delete_user_categories_message(message, state)


async def on_add_or_delete_user_categories_message(message: Message, state: FSMContext):
    categories = await get_categories()
    context = await state.get_data()
    if 'user_categories' in context:
        user_categories = context['user_categories']
    else:
        user_tg_id = message.from_user.id
        user_categories = await get_user_categories(user_tg_id)

    list_of_categories = '\n'.join(user_categories)
    keyboard = await categories_keyboard(categories)
    answer = '<b>Наш список категорий, но он обязательно будет обновляться:</b>\n\n'
    answer += await convert_categories_to_string(categories)
    answer += '\n‼<b>Чтобы удалить категорию нажмите на нее второй раз</b>‼'
    await message.answer(answer, reply_markup=keyboard)

    if user_categories:
        await message.answer(f'<b>Список ваших категорий:</b>\n{list_of_categories}')

    await state.set_state(CategoriesStates.GET_USER_CATEGORIES)


async def on_category_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    categories = await get_categories()

    if message.text == general_reply_buttons_texts.START_BUTTON_TEXT:
        user_categories = await get_user_categories(user_tg_id)
        if user_categories:
            return await on_start_message(message, state)
        else:
            return await message.answer('<b>Сперва добавьте хотя бы одну категорию</b>')
    elif message.text not in categories:
        return await message.answer('Такой категории у нас пока нет 😅')

    category_id = int(message.text[0])
    created = await create_user_category(user_tg_id, category_id)

    user_categories = await get_user_categories(user_tg_id)

    if created == errors.DUPLICATE_ENTRY_ERROR:
        deleted = await delete_user_category(user_tg_id, category_id)
        user_categories = await get_user_categories(user_tg_id)
        if deleted:
            await message.answer(
                f'Категория `<code>{message.text.split(". ", 1)[1]}</code>` <b>удалена</b> из списка ваших категорий')
        else:
            await message.answer(f'Не удалось удалить категорию `<code>{message.text[2:]}</code>`')

    elif created:
        await message.answer(
            f'Категория `<code>{message.text.split(". ", 1)[1]}</code>` <b>добавлена</b>  в список ваших категорий', )
    else:
        await message.answer('Упс. Что-то пошло не так')

    if user_categories:
        list_of_categories = '\n'.join(user_categories)
        await message.answer(f'<b>Список ваших категорий:</b>\n{list_of_categories}')
    else:
        await message.answer(f'<b>Список ваших категорий пуст</b>')


def register_categories_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_category_message,
        content_types=ContentType.TEXT,
        state=CategoriesStates.GET_USER_CATEGORIES
    )

    dp.register_message_handler(
        on_categories_feed_message,
        Text(equals=general_reply_buttons_texts.TO_CATEGORIES_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_add_or_delete_user_categories_message,
        Text(equals=categories_reply_buttons_texts.ADD_OR_DELETE_USER_CATEGORIES_BUTTON_TEXT),
        state=CategoriesStates.CATEGORIES_FEED
    )