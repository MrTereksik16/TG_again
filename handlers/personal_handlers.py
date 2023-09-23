import time
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from create_bot import bot_client
from utils.consts import answers, errors, callbacks
from parse import parse
from database.queries.create_queries import create_personal_posts
from database.queries.delete_queries import delete_user_channel
from database.queries.get_queries import get_user_channels_usernames
from keyboards import personal_inline_keyboards
from keyboards import personal_reply_keyboards
from store.states import PersonalStates
from utils.helpers import add_channels, reset_and_switch_state
from keyboards import personal_reply_buttons_texts, general_reply_buttons_texts, general_reply_keyboards
from utils.custom_types import ChannelPostTypes


async def on_personal_feed_message(message: Message, state: FSMContext):
    await reset_and_switch_state(state, PersonalStates.PERSONAL_FEED)
    user_tg_id = message.from_user.id
    user_channels = await get_user_channels_usernames(user_tg_id)

    if user_channels:
        keyboard = personal_reply_keyboards.personal_start_control_keyboard
        await message.answer(answers.PERSONAL_FEED_MESSAGE_TEXT, reply_markup=keyboard)
    else:
        await on_add_personal_channels_message(message, state)


async def on_add_personal_channels_message(message: Message, state: FSMContext):
    await message.answer(answers.ADD_CHANNELS_MESSAGE_TEXT, reply_markup=general_reply_keyboards.general_cancel_keyboard)
    await state.set_state(PersonalStates.GET_USER_CHANNELS)


async def on_add_channels_button_click(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    await bot_client.send_message(chat_id, answers.ADD_CHANNELS_MESSAGE_TEXT, reply_markup=general_reply_keyboards.general_cancel_keyboard)
    await state.set_state(PersonalStates.GET_USER_CHANNELS)
    await callback.answer()


async def on_personal_channels_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, PersonalStates.PERSONAL_FEED)
        return await message.answer(answers.PERSONAL_FEED_MESSAGE_TEXT, reply_markup=personal_reply_keyboards.personal_start_control_keyboard)

    keyboard = personal_reply_keyboards.personal_start_control_keyboard
    chat_id = message.chat.id
    user_tg_id = message.from_user.id
    channel_type = ChannelPostTypes.PERSONAL
    channels = message.text
    result = await add_channels(channels, channel_type=channel_type, user_tg_id=user_tg_id)

    answer = result.answer
    to_parse = result.to_parse

    await reset_and_switch_state(state, PersonalStates.PERSONAL_FEED)

    if not to_parse:
        return await message.answer(answer, reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardRemove()
        await message.answer(answer, reply_markup=keyboard)

    to_parse_len = len(to_parse)
    for i, channel_username in enumerate(to_parse, start=1):
        posts = await parse(channel_username, chat_id=chat_id, channel_type=channel_type)

        if posts == errors.NO_POSTS:
            await bot_client.send_message(chat_id, 'Канал пуст', reply_markup=personal_reply_keyboards.personal_start_control_keyboard)
        else:
            if i == to_parse_len:
                keyboard = personal_reply_keyboards.personal_start_control_keyboard

            result = await create_personal_posts(posts)
            if result:

                await bot_client.send_message(chat_id, f'Посты с канала @{channel_username} получены 👍', reply_markup=keyboard)
            else:
                await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}', reply_markup=keyboard)
        time.sleep(0.8)


async def on_list_channels_message(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_channels_usernames(user_tg_id)
    channels_usernames = []
    if not channels:
        await message.answer('Список ваших каналов пуст.',
                             reply_markup=personal_inline_keyboards.add_user_channels_keyboard)
    else:
        for channel in channels:
            channels_usernames.append(f'@{channel}')
        await message.answer(f'Список ваших каналов:\n{", ".join(channels_usernames)}',
                             reply_markup=personal_reply_keyboards.personal_start_control_keyboard)


async def on_delete_user_channel_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    channels_usernames = await get_user_channels_usernames(user_tg_id)

    if not channels_usernames:
        return await message.answer('Список ваших каналов пуст',
                                    reply_markup=personal_inline_keyboards.add_user_channels_keyboard)
    buttons = []
    for channel_username in channels_usernames:
        callback_data = f'{callbacks.DELETE_USER_CHANNEL}:{channel_username}'
        buttons.append([InlineKeyboardButton(channel_username, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(buttons)
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE_TEXT, reply_markup=keyboard)
    await state.update_data(user_channels_usernames=channels_usernames, delete_user_channels_message=msg)


async def on_delete_user_channel_button_click(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    channel_username = callback.data.split(':')[1]
    context_data = await state.get_data()
    channels_usernames = context_data['user_channels_usernames']
    msg = context_data['delete_user_channels_message']
    result = await delete_user_channel(user_tg_id, channel_username)

    if result:
        channels_usernames.remove(channel_username)
        await state.update_data(user_channels_usernames=channels_usernames)
        buttons = []
        for channel_username in channels_usernames:
            callback_data = f'{callbacks.DELETE_USER_CHANNEL}:{channel_username}'
            buttons.append([InlineKeyboardButton(channel_username, callback_data=callback_data)])
        keyboard = InlineKeyboardMarkup(buttons)

        if not buttons:
            await msg.edit_text('Список ваших каналов пуст', reply_markup=personal_inline_keyboards.add_user_channels_keyboard)
        else:
            await msg.edit_reply_markup(reply_markup=keyboard)
        await callback.answer('Канал успешно удалён из списка')
    else:
        await callback.answer('Не удалось удалить канал')


def register_personal_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_personal_feed_message,
        Text(equals=general_reply_buttons_texts.TO_PERSONAL_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_add_personal_channels_message,
        Text(equals=personal_reply_buttons_texts.ADD_USER_CHANNELS_BUTTON_TEXT),
        state=[PersonalStates.PERSONAL_FEED, PersonalStates.SCROLL]
    )

    dp.register_message_handler(
        on_personal_channels_message,
        content_types=types.ContentType.TEXT,
        state=PersonalStates.GET_USER_CHANNELS
    )

    dp.register_callback_query_handler(
        on_add_channels_button_click,
        Text(equals=callbacks.ADD_USER_CHANNELS),
        state=[PersonalStates.PERSONAL_FEED, PersonalStates.SCROLL]
    )

    dp.register_message_handler(
        on_list_channels_message,
        Text(equals=personal_reply_buttons_texts.LIST_USER_CHANNELS_BUTTON_TEXT),
        state=[PersonalStates.PERSONAL_FEED, PersonalStates.SCROLL]
    )

    dp.register_message_handler(
        on_delete_user_channel_message,
        Text(equals=personal_reply_buttons_texts.DELETE_USER_CHANNELS_BUTTON_TEXT),
        state=[PersonalStates.PERSONAL_FEED, PersonalStates.SCROLL]
    )

    dp.register_callback_query_handler(
        on_delete_user_channel_button_click,
        Text(startswith=callbacks.DELETE_USER_CHANNEL),
        state=[PersonalStates.PERSONAL_FEED, PersonalStates.SCROLL]
    )
