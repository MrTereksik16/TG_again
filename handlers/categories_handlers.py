from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, Message
from aiogram import Dispatcher
from config.config import ADMINS
from database.queries.create_queries import create_user_category
from database.queries.delete_queries import delete_user_category
from database.queries.get_queries import get_user_categories, get_categories, get_category_id
from handlers.general_handlers import on_start_message
from keyboards import categories_reply_keyboards, general_reply_buttons, general_reply_buttons_texts, \
    categories_reply_buttons_texts
from keyboards.general.helpers import build_reply_buttons, build_reply_keyboard
from store.states import CategoriesStates
from utils.consts import answers, errors
from utils.custom_types import Modes
from utils.helpers import convert_list_of_items_to_string, reset_and_switch_state, send_next_post, send_end_message, get_next_post


async def on_categories_feed_message(message: Message, state: FSMContext):
    await state.set_state(CategoriesStates.CATEGORIES_FEED)
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    mode = Modes.CATEGORIES
    user_is_admin = user_tg_id in ADMINS
    user_categories = await get_user_categories(user_tg_id)
    await state.update_data(user_categories=user_categories)

    if user_categories:
        next_post = await get_next_post(user_tg_id, mode)

        if next_post:
            keyboard = categories_reply_keyboards.categories_control_keyboard
            if user_is_admin:
                keyboard = categories_reply_keyboards.categories_admin_control_keyboard
        else:
            keyboard = categories_reply_keyboards.categories_start_control_keyboard
            if user_is_admin:
                keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard
        await message.answer(answers.CATEGORIES_FEED_MESSAGE_TEXT, reply_markup=keyboard)

        if next_post:
            await send_next_post(user_tg_id, chat_id, mode, next_post)
        else:
            await send_end_message(user_tg_id, chat_id, mode)
    else:
        await on_add_or_delete_user_categories_message(message, state)


async def on_add_or_delete_user_categories_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    categories = await get_categories()
    user_categories = await get_user_categories(user_tg_id)

    cat_buttons = build_reply_buttons(categories)
    keyboard = build_reply_keyboard(cat_buttons, header_buttons=general_reply_buttons.start_button)

    answer = 'Наш список категорий, но он обязательно будет обновляться:'
    answer += convert_list_of_items_to_string(categories)
    answer += '‼Чтобы удалить категорию нажмите на нее второй раз‼'
    await message.answer(answer, reply_markup=keyboard)

    answer = '<b>Список ваших категорий:</b>'
    answer += convert_list_of_items_to_string(user_categories)
    if user_categories:
        await message.answer(answer)

    await state.set_state(CategoriesStates.GET_USER_CATEGORIES)


async def on_category_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    categories = await get_categories()
    user_is_admin = user_tg_id in ADMINS
    keyboard = categories_reply_keyboards.categories_start_control_keyboard
    if user_is_admin:
        keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard

    if message.text == general_reply_buttons_texts.CLOSE_BUTTON_TEXT:
        await reset_and_switch_state(state, CategoriesStates.CATEGORIES_FEED)
        return await message.answer(answers.CATEGORIES_FEED_MESSAGE_TEXT, reply_markup=keyboard)
    elif message.text == general_reply_buttons_texts.START_BUTTON_TEXT:
        await reset_and_switch_state(state, CategoriesStates.CATEGORIES_FEED)
        return await on_start_message(message, state)
    elif message.text not in categories:
        return await message.answer('Такой категории у нас пока нет 😅')

    category_name = message.text.split(' ')[0]
    category_id = await get_category_id(category_name)

    if not category_id:
        return await message.answer('Упс, мы не нашли такой категории 😅')

    created = await create_user_category(user_tg_id, category_id)

    if created == errors.DUPLICATE_ERROR_TEXT:
        deleted = await delete_user_category(user_tg_id, category_id)
        if deleted:
            await message.answer(
                f'Категория `<code>{message.text}</code>` <b>удалена</b> из списка ваших категорий')
        else:
            await message.answer(f'Не удалось удалить категорию <code>{message.text}</code>')

    elif created:
        await message.answer(
            f'Категория `<code>{message.text}</code>` <b>добавлена</b>  в список ваших категорий')
    else:
        await message.answer('Не удалось добавить категорию <code>{message.text}</code>')

    user_categories = await get_user_categories(user_tg_id)
    if user_categories:
        answer = 'Список ваших категорий: '
        answer += convert_list_of_items_to_string(user_categories)
        await message.answer(answer)
    else:
        await message.answer(f'Список ваших категорий пуст')


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
