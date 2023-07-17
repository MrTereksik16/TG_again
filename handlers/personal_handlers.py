from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardRemove, CallbackQuery

from buttons.reply import reply_buttons_text
from utils.consts import answers
from parse import parse
from callbacks import callbacks
from create_bot import dp, client, bot
from database.queries.create_queries import *
from database.queries.delete_queries import delete_personal_channel
from database.queries.get_queries import get_user_channels
from keyboards.inline.inline_keyboards import add_user_channels_inline_keyboard
from keyboards.reply.personal_keyboard import personal_control_keyboard
from store.states import UserStates
from config.config import ADMINS



async def on_add_channels_message(message: Message, state: FSMContext):
    await message.answer(answers.ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.GET_USER_CHANNELS)

    dp.register_message_handler(
        on_channels_message,
        content_types=types.ContentType.TEXT,
        state=UserStates.GET_USER_CHANNELS
    )


async def on_add_channels_inline_click(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    await bot.send_message(chat_id, answers.ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.GET_USER_CHANNELS)
    await callback.answer()


async def on_channels_message(message: Message, state: FSMContext):
    links = [link.strip() for link in message.text.split(',') if link.strip()]
    user_tg_id = message.from_user.id
    added = []
    not_added = []
    already_added = []
    for link in links:
        try:
            channel_tg_entity = await client.get_entity(link)
        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')
            continue

        username = channel_tg_entity.username
        result = await create_user_channel(user_tg_id, username)
        if result == errors.DUPLICATE_ENTRY_ERROR:
            already_added.append(f'@{channel_tg_entity.username}')
        elif result:
            added.append(f'@{channel_tg_entity.username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    message_text = ''
    if added:
        message_text += answers.CHANNELS_ADDED_MESSAGE.format(channels_added=', '.join(added))
    if not_added:
        message_text += answers.CHANNELS_NOT_ADDED_MESSAGE.format(channels_not_added=', '.join(not_added))
    if already_added:
        message_text += answers.CHANNELS_ALREADY_ADDED_MESSAGE.format(channels_already_added=', '.join(already_added))

    await message.answer(message_text, reply_markup=personal_control_keyboard)
    await state.reset_state()

    for username in added:
        data = await parse(user_tg_id=message.from_user.id, channel_name=username)
        print(data)
        if message.from_user.id in ADMINS:
            await create_general_post(data=data)
        else:
            await create_personal_post(data=data)


async def on_list_channels_message(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_channels(user_tg_id)
    usernames = []
    if not channels:
        await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)
    else:
        for channel in channels:
            usernames.append(f'@{channel}')
        await message.answer(answers.ADDED_CHANNELS_MESSAGE.format(usernames=', '.join(usernames)))


async def on_delete_user_channel_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    usernames = await get_user_channels(user_tg_id)

    if not usernames:
        return await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)

    keyboard = InlineKeyboardMarkup()

    for username in usernames:
        keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE, reply_markup=keyboard)
    await state.update_data(user_channels_usernames=usernames)
    await state.update_data(delete_user_channels_message=msg)
    dp.register_callback_query_handler(on_delete_user_channel_button_click,
                                       Text(startswith=callbacks.DELETE_USER_CHANNEL))


async def on_delete_user_channel_button_click(callback: CallbackQuery, state: FSMContext):
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
            await msg.edit_reply_markup(reply_markup=add_user_channels_inline_keyboard)
        else:
            await msg.edit_reply_markup(reply_markup=edited_keyboard)
        await callback.answer('Канал успешно удалён из списка')
    else:
        await callback.answer('Не удалось удалить канал')


def register_personal_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_add_channels_message,
        Text(equals=reply_buttons_text.ADD_PERSONAL_CHANNELS_BUTTON_TEXT),
    )

    dp.register_callback_query_handler(
        on_add_channels_inline_click,
        Text(callbacks.ADD_USER_CHANNELS),
    )

    dp.register_message_handler(
        on_list_channels_message,
        Text(equals=reply_buttons_text.LIST_CHANNELS_BUTTON_TEXT),
    )

    dp.register_message_handler(
        on_delete_user_channel_message,
        Text(equals=reply_buttons_text.DELETE_CHANNELS_BUTTON_TEXT),
    )
