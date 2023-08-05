from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, Message
from pyrogram.types import ReplyKeyboardMarkup

from create_bot import bot_client
from database.queries.get_queries import get_categories
from database.queries.create_queries import create_premium_posts, create_category_posts
from utils.consts.answers import *
from parse import parse
from store.states import AdminPanelStates
from utils.helpers import add_channels_from_message, create_categories_buttons
from keyboards import admin_reply_buttons_texts, admin_reply_keyboards
from utils.types import Modes


async def on_add_premium_channels_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.GET_PREMIUM_CHANNELS)
    await message.answer(text=ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())


async def on_premium_channels_message(message: Message, state: FSMContext):
    chat_id = message.chat.id
    mode = Modes.RECOMMENDATIONS
    result = await add_channels_from_message(message, mode=mode)

    answer = result.answer
    to_parse = result.to_parse
    added_channels = result.added_channels

    if added_channels:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    await state.set_state(AdminPanelStates.ADMIN_PANEL)

    for channel_username in to_parse:
        data = await parse(channel_username, chat_id, mode=mode)
        await create_premium_posts(data, bot_client)


async def on_add_category_channels_message(message: Message, state: FSMContext):
    categories = await get_categories()
    answer = '<b>Выберите категорию</b>'
    buttons = await create_categories_buttons(categories)
    keyboard_for_answer = ReplyKeyboardMarkup([[button] for button in buttons])

    await message.answer(answer, reply_markup=keyboard_for_answer)
    await state.update_data(categories=categories)
    await state.set_state(AdminPanelStates.GET_CATEGORY)


async def on_category_message(message: Message, state: FSMContext):
    context = await state.get_data()
    categories = context['categories']
    if message.text not in categories:
        return await message.answer('Такой категории нет')
    category = message.text
    await state.update_data(category=category)
    await state.set_state(AdminPanelStates.GET_CATEGORY_CHANNELS)
    await message.answer(text=ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())


async def on_category_channels_message(message: Message, state: FSMContext):
    chat_id = message.chat.id
    mode = Modes.CATEGORIES
    context = await state.get_data()
    category = context['category']

    result = await add_channels_from_message(message, category=category, mode=mode)

    answer = result.answer
    to_parse = result.to_parse
    added_channels = result.added_channels

    if added_channels:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    for channel_username in to_parse:
        data = await parse(channel_username, chat_id, mode=mode)
        await create_category_posts(data, bot_client)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_add_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_GENERAL_CHANNELS_BUTTON_TEXT),
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
        state=AdminPanelStates.GET_CATEGORY
    )

    dp.register_message_handler(
        on_category_channels_message,
        state=AdminPanelStates.GET_CATEGORY_CHANNELS
    )
