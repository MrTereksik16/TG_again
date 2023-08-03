from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, ReplyKeyboardRemove, Message
from pyrogram.types import ReplyKeyboardMarkup

from database.queries.delete_queries import delete_general_channel
from database.queries.get_queries import get_categories
from database.queries.create_queries import *
from parse import parse
from store.states import AdminPanelStates
from utils.helpers import add_channels_from_message, create_categories_buttons
from keyboards import admin_reply_buttons_texts, admin_reply_keyboards
from utils.consts.answers import *
from utils.types import Modes


async def on_add_general_channels_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.GET_GENERAL_CHANNELS)
    await message.answer(text=ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())


async def on_general_channels_message(message: Message, state: FSMContext):
    mode = Modes.RECOMMENDATIONS
    data = await add_channels_from_message(message, mode=mode)
    answer = data['answer']
    added = data['added']

    if added:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    else:
        await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard,
                             parse_mode=ParseMode.HTML)

    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    for channel_username in added:
        data = await parse(message, channel_username, mode=mode)

        result = await create_recommendation_post(data)
        if not result:
            await delete_general_channel(channel_username)


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
    mode = Modes.CATEGORIES
    context = await state.get_data()
    category = context['category']
    data = await add_channels_from_message(message, category=category, mode=mode)
    answer = data['answer']
    added = data['added']
    if added:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    else:
        await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard,
                             parse_mode=ParseMode.HTML)
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    for channel_username in added:
        data = await parse(message, channel_username, mode=mode)

        result = await create_category_post(data)
        if not result:
            await delete_general_channel(channel_username)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_add_general_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_GENERAL_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_general_channels_message,
        state=AdminPanelStates.GET_GENERAL_CHANNELS
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
