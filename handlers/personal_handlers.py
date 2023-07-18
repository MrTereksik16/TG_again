from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery, Message
from utils.consts import answers
from parse import parse
from callbacks import callbacks
from create_bot import dp
from database.queries.create_queries import *
from database.queries.delete_queries import delete_personal_channel
from database.queries.get_queries import get_user_channels
from keyboards import personal_inline_keyboards
from keyboards import personal_reply_keyboards
from store.states import PersonalStates
from utils.helpers import send_post_in_personal_feed, add_channels_from_message
from keyboards import personal_reply_buttons_texts, general_reply_buttons_texts


async def on_personal_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_channels = await get_user_channels(user_tg_id)
    await state.set_state(PersonalStates.PERSONAL_FEED)

    if user_channels:
        await message.answer('*Личная лента*')
        await on_list_channels_message(message)
    else:
        await on_add_channels_message(message, state)


async def on_add_channels_message(message: Message, state: FSMContext):
    await message.answer(answers.ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(PersonalStates.GET_USER_CHANNELS)

    dp.register_message_handler(
        on_channels_message,
        content_types=types.ContentType.TEXT,
        state=PersonalStates.GET_USER_CHANNELS
    )


async def on_add_channels_inline_click(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    await bot.send_message(chat_id, answers.ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(PersonalStates.GET_USER_CHANNELS)
    await callback.answer()


async def on_channels_message(message: Message, state: FSMContext):
    keyboard = personal_reply_keyboards.personal_wait_for_parse_keyboard
    data = await add_channels_from_message(message)
    answer = data['answer']
    added = data['added']
    if added:
        await message.answer(answer, reply_markup=personal_reply_keyboards.personal_wait_for_parse_keyboard)

    else:
        await message.answer(answer, reply_markup=personal_reply_keyboards.personal_start_control_keyboard)

    for username in added:
        data = await parse(message, username, keyboard, limit=10)
        await create_personal_post(data)
    await state.set_state(PersonalStates.PERSONAL_FEED)


async def on_list_channels_message(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_channels(user_tg_id)
    usernames = []
    if not channels:
        await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE,
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
        return await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE,
                                    reply_markup=personal_inline_keyboards.add_user_channels_inline_keyboard)

    keyboard = InlineKeyboardMarkup()

    for username in usernames:
        keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE, reply_markup=keyboard)
    await state.update_data(user_channels_usernames=usernames)
    await state.update_data(delete_user_channels_message=msg)

    dp.register_callback_query_handler(
        on_delete_user_channel_inline_click,
        Text(startswith=callbacks.DELETE_USER_CHANNEL),
        state=PersonalStates.PERSONAL_FEED
    )


async def on_delete_user_channel_inline_click(callback: CallbackQuery, state: FSMContext):
    username = callback.data.split(':')[1]
    logger.error(callback.data)
    context_data = await state.get_data()
    usernames = context_data.get('user_channels_usernames')
    result = await delete_personal_channel(username)
    msg = context_data.get('delete_user_channels_message')

    if result:
        usernames.remove(username)
        await state.update_data(user_channels_usernames=usernames)
        edited_keyboard = InlineKeyboardMarkup()

        for username in usernames:
            edited_keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
        if not edited_keyboard['inline_keyboard']:
            await msg.edit_text(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE)
        else:
            await msg.edit_reply_markup(reply_markup=edited_keyboard)
        await callback.answer('*Канал успешно удалён из списка*')
    else:
        await callback.answer('*Не удалось удалить канал*')


async def on_skip_message(message: Message):
    await send_post_in_personal_feed(message)


def register_personal_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_personal_feed_message,
        Text(equals=general_reply_buttons_texts.TO_PERSONAL_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_add_channels_message,
        Text(equals=personal_reply_buttons_texts.ADD_USER_CHANNELS_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )

    dp.register_callback_query_handler(
        on_add_channels_inline_click,
        Text(callbacks.ADD_USER_CHANNELS),
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

    dp.register_message_handler(
        on_skip_message,
        Text(personal_reply_buttons_texts.SKIP_BUTTON_TEXT),
        state=PersonalStates.PERSONAL_FEED
    )
