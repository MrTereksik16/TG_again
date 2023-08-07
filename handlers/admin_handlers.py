from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType
from aiogram.types import ReplyKeyboardRemove
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
import callbacks
from create_bot import bot_client
from database.queries.delete_queries import delete_category, delete_premium_channel
from database.queries.get_queries import get_categories, get_premium_channels, get_categories_channels
from database.queries.create_queries import create_premium_posts, create_category_posts, create_category
from utils.consts import answers, errors
from utils.consts.answers import *
from parse import parse
from store.states import AdminPanelStates
from utils.helpers import add_channels_from_message, create_categories_buttons, convert_list_of_items_to_string, build_menu, \
    reset_and_switch_state
from keyboards import admin_reply_buttons_texts, admin_reply_keyboards, general_reply_keyboards, general_reply_buttons_texts, general_reply_buttons
from utils.custom_types import Modes


async def on_add_premium_channels_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.GET_PREMIUM_CHANNELS)
    await message.answer(text=ADD_CHANNELS_MESSAGE, reply_markup=general_reply_keyboards.general_cancel_keyboard)


async def on_premium_channels_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    chat_id = message.chat.id
    mode = Modes.RECOMMENDATIONS
    result = await add_channels_from_message(message, mode=mode)

    answer = result.answer
    to_parse = result.to_parse

    if to_parse:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    await state.set_state(AdminPanelStates.ADMIN_PANEL)

    for channel_username in to_parse:
        data = await parse(channel_username, chat_id, mode=mode)
        await create_premium_posts(data, bot_client)


async def on_add_category_channels_message(message: Message, state: FSMContext):
    categories = await get_categories()
    if not categories:
        return await message.answer('Список категорий пуст', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    answer = '<b>Выберите категорию</b>'
    buttons = create_categories_buttons(categories)
    keyboard = build_menu(buttons, header_buttons=[general_reply_buttons.cancel_button])

    await message.answer(answer, reply_markup=keyboard)
    await state.update_data(categories=categories)
    await state.set_state(AdminPanelStates.GET_CHANNELS_CATEGORY)


async def on_category_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    context = await state.get_data()
    categories = context['categories']
    if message.text not in categories:
        return await message.answer('Такой категории нет')
    category = message.text[:-1]
    await state.update_data(category=category)
    await state.set_state(AdminPanelStates.GET_CATEGORY_CHANNELS)
    await message.answer(text=ADD_CHANNELS_MESSAGE, reply_markup=general_reply_keyboards.general_cancel_keyboard)


async def on_category_channels_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    chat_id = message.chat.id
    mode = Modes.CATEGORIES
    context = await state.get_data()
    category = context['category']

    result = await add_channels_from_message(message, category_name=category, mode=mode)

    answer = result.answer
    to_parse = result.to_parse

    if to_parse:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    for channel_username in to_parse:
        data = await parse(channel_username, chat_id, mode=mode)
        await create_category_posts(data, bot_client)


async def on_list_premium_channels_message(message: Message):
    channels = await get_premium_channels()
    channels = [f'@{channel.username} | <b>{channel.coefficient}</b>' for channel in channels]
    answer = 'Список премиальных каналов:'
    answer += convert_list_of_items_to_string(channels, code=False)

    if not channels:
        answer = 'Список премиальных каналов пуст'

    await message.answer(answer)


async def on_list_categories_message(message: Message):
    categories = await get_categories()
    answer = 'Список категорий:'
    answer += convert_list_of_items_to_string(categories)

    if not categories:
        answer = 'Список категорий пуст'

    await message.answer(answer)


async def on_list_categories_channels_message(message: Message):
    categories_channels = await get_categories_channels()
    if not categories_channels:
        return await message.answer('Список каналов в категориях пуст')
    else:

        categories_channels = [f'@{channel.username} | <code>{channel.name}{channel.emoji}</code>' for channel in categories_channels]
        answer = 'Список каналов из категорий:'
        answer += convert_list_of_items_to_string(categories_channels, code=False)
        await message.answer(answer)


async def on_add_category_message(message: Message, state: FSMContext):
    keyboard = general_reply_keyboards.general_cancel_keyboard
    await message.answer('<b>Введите название категории</b>', reply_markup=keyboard)
    await state.set_state(AdminPanelStates.GET_CATEGORY_NAME)


async def on_add_category_name_message(message: Message, state: FSMContext):
    keyboard = general_reply_keyboards.general_cancel_keyboard
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    await state.update_data(category_name=message.text)
    await message.answer('<b>Введите эмодзи</b>', reply_markup=keyboard)
    await state.set_state(AdminPanelStates.GET_CATEGORY_EMOJI)


async def on_add_category_emoji_message(message: Message, state: FSMContext):
    keyboard = admin_reply_keyboards.admin_panel_control_keyboard

    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL, reply_markup=keyboard)

    category_name = (await state.get_data())['category_name']
    category_emoji = message.text
    result = await create_category(category_name, category_emoji)

    if result == errors.DUPLICATE_ENTRY_ERROR:
        await message.answer('Категория с таким названием уже есть', reply_markup=keyboard)
    elif result:
        await message.answer('Категория успешно добавлена!', reply_markup=keyboard)
    else:
        await message.answer('Не удалось добавить категорию', reply_markup=keyboard)

    await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)


async def on_delete_category_message(message: Message, state: FSMContext):
    categories = await get_categories()
    if not categories:
        return await message.answer(answers.NO_USER_CHANNELS_MESSAGE)

    buttons = create_categories_buttons(categories)
    keyboard = build_menu(buttons)
    await message.answer(answers.DELETE_CATEGORY_MESSAGE, reply_markup=keyboard)
    await state.update_data(categories=categories)
    await state.set_state(AdminPanelStates.DELETE_CATEGORIES)


async def on_delete_category_name_message(message: Message, state: FSMContext):
    categories: list = (await state.get_data())['categories']
    if message.text not in categories:
        return await message.answer('Такой категории нет')
    category = message.text
    category_name = message.text[:-1]
    result = await delete_category(category_name)

    if result:
        categories.remove(category)
        buttons = create_categories_buttons(categories)
        keyboard = build_menu(buttons)
        await message.answer('Категория успешно удалена', reply_markup=keyboard)
    else:
        await message.answer('Не удалось удалить категорию')


async def on_delete_premium_channels_message(message: Message, state: FSMContext):
    premium_channels = await get_premium_channels()
    channels = [f'{channel.username}:{channel.coefficient}' for channel in premium_channels]

    if not channels:
        return await message.answer(answers.NO_USER_CHANNELS_MESSAGE)
    buttons = []
    for channel in channels:
        callback_data = f'{callbacks.DELETE_PREMIUM_CHANNEL}:{channel}'
        buttons.append([InlineKeyboardButton(channel.replace(':', ' | '), callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(buttons)
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE, reply_markup=keyboard)
    await state.update_data(premium_channels=channels, delete_premium_channels_message=msg)


async def on_delete_premium_channel_inline_click(callback: CallbackQuery, state: FSMContext):
    channel_data = callback.data.split(':')[1:]
    channel_username = channel_data[0]
    channel = ':'.join(channel_data)
    context_data = await state.get_data()
    premium_channels = context_data['premium_channels']
    msg = context_data['delete_premium_channels_message']
    result = await delete_premium_channel(channel_username)
    if result:
        premium_channels.remove(channel)
        await state.update_data(premium_channels=premium_channels)
        buttons = []
        for channel in premium_channels:
            callback_data = f'{callbacks.DELETE_PREMIUM_CHANNEL}:{channel}'
            buttons.append([InlineKeyboardButton(channel.replace(':', ' | '), callback_data=callback_data)])
        keyboard = InlineKeyboardMarkup(buttons)

        if not buttons:
            await msg.edit_text(answers.NO_USER_CHANNELS_MESSAGE)
        else:
            await msg.edit_reply_markup(reply_markup=keyboard)
        await callback.answer('Канал успешно удалён')
    else:
        await callback.answer('Не удалось удалить канал')


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_add_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_PREMIUM_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_premium_channels_message,
        state=AdminPanelStates.GET_PREMIUM_CHANNELS
    )

    dp.register_message_handler(
        on_add_category_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_CATEGORY_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_category_message,
        state=AdminPanelStates.GET_CHANNELS_CATEGORY
    )

    dp.register_message_handler(
        on_category_channels_message,
        state=AdminPanelStates.GET_CATEGORY_CHANNELS
    )

    dp.register_message_handler(
        on_list_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.LIST_PREMIUM_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_list_categories_message,
        Text(equals=admin_reply_buttons_texts.LIST_CATEGORIES_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_list_categories_channels_message,
        Text(equals=admin_reply_buttons_texts.LIST_CATEGORIES_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_add_category_message,
        Text(admin_reply_buttons_texts.ADD_CATEGORY_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_add_category_name_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.GET_CATEGORY_NAME
    )

    dp.register_message_handler(
        on_add_category_emoji_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.GET_CATEGORY_EMOJI
    )

    dp.register_message_handler(
        on_delete_category_message,
        Text(equals=admin_reply_buttons_texts.DELETE_CATEGORY_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_delete_category_name_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.DELETE_CATEGORIES
    )

    dp.register_message_handler(
        on_delete_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.DELETE_PREMIUM_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_callback_query_handler(
        on_delete_premium_channel_inline_click,
        Text(startswith=callbacks.DELETE_PREMIUM_CHANNEL),
        state=AdminPanelStates.ADMIN_PANEL
    )
