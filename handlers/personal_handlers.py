from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from create_bot import bot_client
from utils.consts import answers
from parse import parse
import callbacks
from database.queries.create_queries import create_personal_posts
from database.queries.delete_queries import delete_personal_channel
from database.queries.get_queries import get_user_channels_usernames
from keyboards import personal_inline_keyboards
from keyboards import personal_reply_keyboards
from store.states import PersonalStates
from utils.helpers import add_channels, get_next_post, send_next_post, send_end_message, reset_and_switch_state, remove_file_or_folder
from keyboards import personal_reply_buttons_texts, general_reply_buttons_texts, general_reply_keyboards
from utils.custom_types import Modes
from config.config import MEDIA_DIR


async def on_personal_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_channels = await get_user_channels_usernames(user_tg_id)
    await state.set_state(PersonalStates.PERSONAL_FEED)

    if user_channels:
        await message.answer(answers.PERSONAL_FEED_MESSAGE_TEXT)
        await on_list_channels_message(message)
    else:
        await on_add_personal_channels_message(message, state)


async def on_add_personal_channels_message(message: Message, state: FSMContext):
    await message.answer(answers.ADD_CHANNELS_MESSAGE_TEXT, reply_markup=general_reply_keyboards.general_cancel_keyboard)
    await state.set_state(PersonalStates.GET_USER_CHANNELS)


async def on_add_channels_inline_button_click(callback: CallbackQuery, state: FSMContext):
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
    mode = Modes.PERSONAL
    channels = message.text
    result = await add_channels(channels, user_tg_id, mode=mode)

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
        posts = await parse(channel_username, chat_id, mode=mode)
        if not posts:
            await bot_client.send_message(chat_id, 'Канал пуст', reply_markup=personal_reply_keyboards.personal_start_control_keyboard)
        else:
            if i == to_parse_len:
                keyboard = personal_reply_keyboards.personal_start_control_keyboard

            result = await create_personal_posts(posts)
            if result:

                await bot_client.send_message(chat_id, f'Посты с канала @{channel_username} получены 👍', reply_markup=keyboard)
            else:
                await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}', reply_markup=keyboard)


async def on_list_channels_message(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_channels_usernames(user_tg_id)
    channels_usernames = []
    if not channels:
        await message.answer('Список ваших каналов пуст.',
                             reply_markup=personal_inline_keyboards.add_user_channels_inline_keyboard)
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
                                    reply_markup=personal_inline_keyboards.add_user_channels_inline_keyboard)
    buttons = []
    for username in channels_usernames:
        callback_data = f'{callbacks.DELETE_USER_CHANNEL}:{username}'
        buttons.append([InlineKeyboardButton(username, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(buttons)
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE_TEXT, reply_markup=keyboard)
    await state.update_data(user_channels_usernames=channels_usernames, delete_user_channels_message=msg)


async def on_delete_user_channel_inline_click(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    channel_username = callback.data.split(':')[1]
    context_data = await state.get_data()
    channels_usernames = context_data['user_channels_usernames']
    msg = context_data['delete_user_channels_message']
    result = await delete_personal_channel(user_tg_id, channel_username)

    if result:
        remove_file_or_folder(MEDIA_DIR + channel_username)
        channels_usernames.remove(channel_username)
        await state.update_data(user_channels_usernames=channels_usernames)
        buttons = []
        for username in channels_usernames:
            callback_data = f'{callbacks.DELETE_USER_CHANNEL}:{username}'
            buttons.append([InlineKeyboardButton(username, callback_data=callback_data)])
        keyboard = InlineKeyboardMarkup(buttons)

        if not buttons:
            await msg.edit_text('Список ваших каналов пуст', reply_markup=personal_inline_keyboards.add_user_channels_inline_keyboard)
        else:
            await msg.edit_reply_markup(reply_markup=keyboard)
        await callback.answer('Канал успешно удалён из списка')
    else:
        await callback.answer('Не удалось удалить канал')


async def on_start_message(message: Message):
    user_tg_id = message.from_user.id
    user_channels = await get_user_channels_usernames(user_tg_id)
    if not user_channels:
        return await message.answer('Сперва нужно добавить хотя бы один канал')

    chat_id = message.chat.id
    next_post = await get_next_post(user_tg_id, Modes.PERSONAL)
    keyboard = personal_reply_keyboards.personal_control_keyboard

    if next_post:
        await message.answer(answers.PRE_SCROLL_MESSAGE_TEXT, reply_markup=keyboard)
        await send_next_post(user_tg_id, chat_id, Modes.PERSONAL, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, Modes.PERSONAL)


async def on_skip_message(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    result = await send_next_post(user_tg_id, chat_id, Modes.PERSONAL)

    if not result:
        await send_end_message(user_tg_id, chat_id, Modes.PERSONAL)


def register_personal_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_personal_feed_message,
        Text(equals=general_reply_buttons_texts.TO_PERSONAL_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_add_personal_channels_message,
        Text(equals=personal_reply_buttons_texts.ADD_USER_CHANNELS_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )

    dp.register_message_handler(
        on_personal_channels_message,
        content_types=types.ContentType.TEXT,
        state=PersonalStates.GET_USER_CHANNELS
    )

    dp.register_callback_query_handler(
        on_add_channels_inline_button_click,
        Text(equals=callbacks.ADD_USER_CHANNELS),
        state=PersonalStates.PERSONAL_FEED
    )

    dp.register_message_handler(
        on_list_channels_message,
        Text(equals=personal_reply_buttons_texts.LIST_USER_CHANNELS_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )

    dp.register_message_handler(
        on_delete_user_channel_message,
        Text(equals=personal_reply_buttons_texts.DELETE_USER_CHANNELS_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )

    dp.register_callback_query_handler(
        on_delete_user_channel_inline_click,
        Text(startswith=callbacks.DELETE_USER_CHANNEL),
        state=PersonalStates.PERSONAL_FEED
    )

    dp.register_message_handler(
        on_start_message,
        Text(equals=general_reply_buttons_texts.START_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED,
    )

    dp.register_message_handler(
        on_skip_message,
        Text(equals=general_reply_buttons_texts.SKIP_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )
