from config.logging_config import logger
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery, Message
from create_bot import bot_client
from utils.consts import answers, errors
from parse import parse
from callbacks import callbacks
from database.queries.create_queries import create_personal_posts
from database.queries.delete_queries import delete_personal_channel
from database.queries.get_queries import get_user_channels
from keyboards import personal_inline_keyboards
from keyboards import personal_reply_keyboards
from store.states import PersonalStates
from utils.helpers import add_channels_from_message, get_next_post, send_next_post, send_end_message
from keyboards import personal_reply_buttons_texts, general_reply_buttons_texts
from utils.types import Modes


async def on_personal_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_channels = await get_user_channels(user_tg_id)
    await state.set_state(PersonalStates.PERSONAL_FEED)

    if user_channels:
        await message.answer('<b>Личная лента</b>')
        await on_list_channels_message(message)
    else:
        await on_add_personal_channels_message(message, state)


async def on_add_personal_channels_message(message: Message, state: FSMContext):
    await message.answer(answers.ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(PersonalStates.GET_USER_CHANNELS)


async def on_add_channels_inline_button_click(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    await bot_client.send_message(chat_id, answers.ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(PersonalStates.GET_USER_CHANNELS)
    await callback.answer()


async def on_personal_channels_message(message: Message, state: FSMContext):
    chat_id = message.chat.id
    mode = Modes.PERSONAL
    result = await add_channels_from_message(message, mode=mode)

    answer = result.answer
    to_parse = result.to_parse
    added_channels = result.added_channels

    if added_channels:
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(answer, reply_markup=personal_reply_keyboards.personal_start_control_keyboard)

    await state.set_state(PersonalStates.PERSONAL_FEED)

    for channel_username in to_parse:
        data = await parse(channel_username, chat_id, mode=mode)
        await create_personal_posts(data, bot_client)


async def on_list_channels_message(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_channels(user_tg_id)
    usernames = []
    if not channels:
        await message.answer(answers.NO_USER_CHANNELS_MESSAGE,
                             reply_markup=personal_inline_keyboards.add_user_channels_inline_keyboard)
    else:
        for channel in channels:
            usernames.append(f'@{channel}')
        await message.answer(answers.ADDED_CHANNELS_MESSAGE + ', '.join(usernames),
                             reply_markup=personal_reply_keyboards.personal_start_control_keyboard)


async def on_delete_user_channel_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    usernames = await get_user_channels(user_tg_id)

    if not usernames:
        return await message.answer(answers.NO_USER_CHANNELS_MESSAGE,
                                    reply_markup=personal_inline_keyboards.add_user_channels_inline_keyboard)

    keyboard = InlineKeyboardMarkup()

    for username in usernames:
        keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE, reply_markup=keyboard)
    await state.update_data(user_channels_usernames=usernames)
    await state.update_data(delete_user_channels_message=msg)


async def on_delete_user_channel_inline_click(callback: CallbackQuery, state: FSMContext):
    channel_username = callback.data.split(':')[1]
    context_data = await state.get_data()
    user_tg_id = callback.from_user.id
    usernames = context_data.get('user_channels_usernames')
    result = await delete_personal_channel(user_tg_id, channel_username)
    msg = context_data.get('delete_user_channels_message')

    if result:
        usernames.remove(channel_username)
        await state.update_data(user_channels_usernames=usernames)
        edited_keyboard = InlineKeyboardMarkup()

        for username in usernames:
            edited_keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
        if not edited_keyboard['inline_keyboard']:
            await msg.edit_text(answers.NO_USER_CHANNELS_MESSAGE)
        else:
            await msg.edit_reply_markup(reply_markup=edited_keyboard)
        await callback.answer('Канал успешно удалён из списка')
    else:
        await callback.answer('Не удалось удалить канал')


async def on_start_message(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id

    next_post = await get_next_post(user_tg_id, Modes.PERSONAL)
    keyboard = personal_reply_keyboards.personal_control_keyboard

    if next_post:
        await message.answer(answers.PRE_START_MESSAGE, reply_markup=keyboard)
        await send_next_post(user_tg_id, chat_id, Modes.PERSONAL, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, Modes.PERSONAL)


async def on_skip_message(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    err = await send_next_post(user_tg_id, chat_id, Modes.PERSONAL)

    if err == errors.NO_POST:
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
        Text(general_reply_buttons_texts.START_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED,
    )

    dp.register_message_handler(
        on_skip_message,
        Text(general_reply_buttons_texts.SKIP_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )
