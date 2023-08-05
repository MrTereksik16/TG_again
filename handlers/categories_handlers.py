from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode, Message
from aiogram import Dispatcher
from config.config import ADMINS
from database.queries.create_queries import create_user_category
from database.queries.delete_queries import delete_user_category
from database.queries.get_queries import get_user_categories, get_categories
from keyboards import categories_reply_keyboards, general_reply_buttons, general_reply_buttons_texts, \
    categories_reply_buttons_texts
from store.states import CategoriesStates
from utils.consts import answers, errors
from utils.helpers import convert_categories_to_string, create_categories_buttons, get_next_post, send_next_post, send_end_message, \
    build_categories_menu
from utils.types import Modes


async def on_categories_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_categories = await get_user_categories(user_tg_id)
    await state.update_data(user_categories=user_categories)
    await state.set_state(CategoriesStates.CATEGORIES_FEED)

    if user_categories:
        keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard if user_tg_id in ADMINS else categories_reply_keyboards.categories_start_control_keyboard
        await message.answer('<b>Лента категорий</b>', reply_markup=keyboard)
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

    cat_buttons = await create_categories_buttons(categories)
    keyboard = build_categories_menu(cat_buttons, header_buttons=[general_reply_buttons.close_button])

    answer = 'Наш список категорий, но он обязательно будет обновляться:\n\n'
    answer += await convert_categories_to_string(categories)
    answer += '\n‼Чтобы удалить категорию нажмите на нее второй раз‼'
    await message.answer(answer, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    if user_categories:
        await message.answer(f'<b>Список ваших категорий:</b>\n{list_of_categories}', parse_mode=ParseMode.HTML)

    await state.set_state(CategoriesStates.GET_USER_CATEGORIES)


async def on_category_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    categories = await get_categories()
    user_is_admin = user_tg_id in ADMINS

    keyboard = categories_reply_keyboards.categories_start_control_keyboard
    if user_is_admin:
        keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard

    if message.text == general_reply_buttons_texts.CLOSE_BUTTON_TEXT:
        await state.set_state(CategoriesStates.CATEGORIES_FEED)
        return await message.answer('<b>Лента категорий</b>', reply_markup=keyboard)
    elif message.text not in categories:
        return await message.answer('Такой категории у нас пока нет 😅')

    category_id = int(message.text.split('.')[0])
    created = await create_user_category(user_tg_id, category_id)

    if created == errors.DUPLICATE_ENTRY_ERROR:
        deleted = await delete_user_category(user_tg_id, category_id)
        if deleted:
            await message.answer(
                f'Категория `<code>{message.text.split(". ", 1)[1]}</code>` <b>удалена</b> из списка ваших категорий', parse_mode=ParseMode.HTML)
        else:
            await message.answer(f'Не удалось удалить категорию `<code>{message.text[2:]}</code>`', parse_mode=ParseMode.HTML)

    elif created:
        await message.answer(
            f'Категория `<code>{message.text.split(". ", 1)[1]}</code>` <b>добавлена</b>  в список ваших категорий', parse_mode=ParseMode.HTML)
    else:
        await message.answer('Упс. Что-то пошло не так')

    user_categories = await get_user_categories(user_tg_id)
    if user_categories:
        list_of_categories = '\n'.join(user_categories)
        await message.answer(f'Список ваших категорий:\n{list_of_categories}', parse_mode=ParseMode.HTML)
    else:
        await message.answer(f'Список ваших категорий пуст')


async def on_start_message(message: Message):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    chat_id = message.chat.id

    next_post = await get_next_post(user_tg_id, Modes.CATEGORIES)
    keyboard = categories_reply_keyboards.categories_control_keyboard

    if user_is_admin:
        keyboard = categories_reply_keyboards.categories_admin_control_keyboard

    if next_post:
        await message.answer(answers.PRE_START_MESSAGE, reply_markup=keyboard)
        await send_next_post(user_tg_id, chat_id, Modes.CATEGORIES, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, Modes.CATEGORIES)


async def on_skip_message(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    err = await send_next_post(user_tg_id, chat_id, Modes.CATEGORIES)

    if err == errors.NO_POST:
        await send_end_message(user_tg_id, chat_id, Modes.CATEGORIES)


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

    dp.register_message_handler(
        on_start_message,
        Text(general_reply_buttons_texts.START_BUTTON_TEXT),
        state=CategoriesStates.CATEGORIES_FEED,
    )

    dp.register_message_handler(
        on_skip_message,
        Text(general_reply_buttons_texts.SKIP_BUTTON_TEXT),
        state=CategoriesStates.CATEGORIES_FEED
    )
