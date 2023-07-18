from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database.queries.get_queries import get_categories
from database.queries.create_queries import *
from parse import parse
from store.states import AdminPanelStates
from utils.helpers import add_channels_from_message, convert_categories_to_string, create_categories_buttons
from keyboards import admin_reply_buttons_texts, admin_reply_keyboards
from utils.consts.answers import *


async def on_add_general_channels_message(message: Message, state: FSMContext):
    categories = await get_categories()
    answer = '*Выберите категорию*'
    buttons = await create_categories_buttons(categories)
    keyboard_for_answer = ReplyKeyboardMarkup([[button] for button in buttons])

    await message.answer(answer, reply_markup=keyboard_for_answer)
    await state.set_state(AdminPanelStates.GET_GENERAL_CHANNEL_CATEGORY)
    await state.update_data(categories=categories)


async def on_category_message(message: Message, state: FSMContext):
    context = await state.get_data()
    categories = context['categories']
    if message.text not in categories:
        return await message.answer('Такой категории нет')
    category = message.text
    await state.update_data(category=category)
    await state.set_state(AdminPanelStates.GET_GENERAL_CHANNEL)
    await message.answer(text=ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())


async def on_channels_message(message: Message, state: FSMContext):
    context = await state.get_data()
    category = context['category']
    data = await add_channels_from_message(message, category)
    answer = data['answer']
    added = data['added']
    await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    for channel_username in added:
        data = await parse(message, channel_username, admin_panel=True)
        await create_general_post(data)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_add_general_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_GENERAL_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_category_message,
        state=AdminPanelStates.GET_GENERAL_CHANNEL_CATEGORY
    )

    dp.register_message_handler(
        on_channels_message,
        state=AdminPanelStates.GET_GENERAL_CHANNEL
    )
