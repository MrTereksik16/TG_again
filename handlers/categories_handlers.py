from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, Message
from aiogram import Dispatcher
from config.config import ADMINS
from database.queries.create_queries import create_user_category
from database.queries.delete_queries import delete_user_category
from database.queries.get_queries import get_user_categories, get_categories, get_category_id
from keyboards import categories_reply_keyboards, general_reply_buttons, general_reply_buttons_texts, \
    categories_reply_buttons_texts
from store.states import CategoriesStates
from utils.consts import answers, errors
from utils.helpers import convert_list_of_items_to_string, create_buttons, get_next_post, send_next_post, send_end_message, \
    create_menu, reset_and_switch_state
from utils.custom_types import Modes


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
    user_tg_id = message.from_user.id
    categories = await get_categories()
    user_categories = await get_user_categories(user_tg_id)

    cat_buttons = create_buttons(categories)
    keyboard = create_menu(cat_buttons, header_buttons=general_reply_buttons.close_button)

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
    print(categories)
    keyboard = categories_reply_keyboards.categories_start_control_keyboard
    if user_is_admin:
        keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard

    if message.text == general_reply_buttons_texts.CLOSE_BUTTON_TEXT:
        await reset_and_switch_state(state, CategoriesStates.CATEGORIES_FEED)
        return await message.answer(answers.CATEGORIES_FEED_MESSAGE_TEXT, reply_markup=keyboard)
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


async def on_start_message(message: Message):
    user_tg_id = message.from_user.id
    user_categories = await get_user_categories(user_tg_id)
    if not user_categories:
        return await message.answer('Сперва нужно добавить хотя бы одну категорию')

    user_is_admin = user_tg_id in ADMINS
    chat_id = message.chat.id

    next_post = await get_next_post(user_tg_id, Modes.CATEGORIES)
    keyboard = categories_reply_keyboards.categories_control_keyboard

    if user_is_admin:
        keyboard = categories_reply_keyboards.categories_admin_control_keyboard

    if next_post:
        await message.answer(answers.PRE_SCROLL_MESSAGE_TEXT, reply_markup=keyboard)
        await send_next_post(user_tg_id, chat_id, Modes.CATEGORIES, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, Modes.CATEGORIES)


async def on_skip_message(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    result = await send_next_post(user_tg_id, chat_id, Modes.CATEGORIES)

    if not result:
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
