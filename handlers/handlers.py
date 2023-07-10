from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, ChatActions, InputFile
from aiogram import Bot, Dispatcher, types
from telethon import TelegramClient
from telethon.tl.types import Channel
from config import config
from database.queries import create_user_channel, get_user, create_user, get_user_personal_channels, \
    delete_personal_channel, create_general_channel_by_admin, add_personal_post, send_post_for_user_lenta, get_last_post_id, update_last_post_id
from config.logging_config import logger
from keyboards.inline.inline_keyboards import add_user_channels_inline_keyboard
from keyboards.reply.lents.categories_keyboard import categories_control_keyboard
from keyboards.reply.lents.personal_keyboard import personal_control_keyboard
from utils.consts import *
from store.states import UserStates
from callbacks import callbacks
from parse import parse
from config.config import ADMINS


client = TelegramClient('bot_session', config.API_ID, config.API_HASH)
client.start(bot_token=config.TOKEN)
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_start_command(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    last_post_id = 1
    user = await get_user(user_tg_id)
    if not user:
        await create_user(user_tg_id, last_post_id)
        await message.answer(START_MESSAGE_FOR_NEW)
    else:
        msg = await message.answer(START_MESSAGE_FOR_OLD, reply_markup=personal_control_keyboard)
        await state.update_data(reply_keyboard_message_id=msg.message_id)


async def on_add_channels_command(message: Message, state: FSMContext):
    await message.answer(ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.GET_CHANNELS)
    # await add_personal_post()

async def on_add_channels_button_click(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    await bot.send_message(chat_id, ADD_CHANNELS_MESSAGE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.GET_CHANNELS)
    await callback.answer()


async def on_add_channels_message(message: Message, state: FSMContext):
    links = [link.strip() for link in message.text.split(',') if link.strip()]
    user_tg_id = message.from_user.id
    added = []
    not_added = []
    already_added = []
    for link in links:
        channel_tg_entity = Channel
        try:
            channel_tg_entity = await client.get_entity(link)
        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')
        if message.from_user.id not in ADMINS:
            result = await create_user_channel(user_tg_id, channel_tg_entity)
        else:
            result = await create_general_channel_by_admin(user_tg_id, channel_tg_entity)
        if result == 'duplicate_entry':
            already_added.append(f'@{channel_tg_entity.username}')
        elif result:
            added.append(f'@{channel_tg_entity.username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    message_text = ''
    if added:
        message_text += CHANNELS_ADDED_MESSAGE.format(channels_added=', '.join(added))
    if not_added:
        message_text += CHANNELS_NOT_ADDED_MESSAGE.format(channels_not_added=', '.join(not_added))
    if already_added:
        message_text += CHANNELS_ALREADY_ADDED_MESSAGE.format(channels_already_added=', '.join(already_added))

    await message.answer(message_text, reply_markup=personal_control_keyboard)
    await state.reset_state()

    for username in added:
        data = await parse(username)
        print(data)
        await add_personal_post(data=data)




async def on_list_command(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_personal_channels(user_tg_id)
    usernames = []
    if not channels:
        await message.answer(EMPTY_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)
    else:
        for channel in channels:
            usernames.append(f'@{channel}')
        await message.answer(ADDED_CHANNELS_MESSAGE.format(usernames=', '.join(usernames)))


async def on_delete_user_channel_command(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    usernames = await get_user_personal_channels(user_tg_id)

    if not usernames:
        return await message.answer(EMPTY_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)

    keyboard = InlineKeyboardMarkup()

    for username in usernames:
        keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
    msg = await message.answer(DELETE_CHANNEL_MESSAGE, reply_markup=keyboard)
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
        logger.error(usernames)
        usernames.remove(username)
        await state.update_data(user_channels_usernames=usernames)
        edited_keyboard = InlineKeyboardMarkup()

        for username in usernames:
            edited_keyboard.add(InlineKeyboardButton(username, callback_data=f'delete_user_channel:{username}'))
        if not edited_keyboard['inline_keyboard']:
            await msg.edit_text('Список каналов пуст')
            await msg.edit_reply_markup(reply_markup=add_user_channels_inline_keyboard)
        else:
            await msg.edit_reply_markup(reply_markup=edited_keyboard)
        await callback.answer('Канал успешно удалён из списка')
    else:
        await callback.answer('Не удалось удалить канал')


async def get_categories_from_user(message: Message):
    if message.text in CATEGORIES:
        await message.answer(f'Мы добавили {message.text} в список ваших категорий')
    else:
        await message.answer('И как так то?')


async def go_to_categories(message: Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=categories_control_keyboard)
    answer = '***Наш список категорий, но он обязательно будет обновляться🤩***\n\n'
    for i in range(0, len(CATEGORIES)):
        answer += f'{CATEGORIES[i]}\n'
    answer += '\n‼***Чтобы удалить категорию нажмите на нее второй раз***‼'
    await message.answer(answer, reply_markup=keyboard, parse_mode='Markdown')


async def send_post_for_user(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    personal_posts = await send_post_for_user_lenta(user_id)

    try:
        if personal_posts:
            last_post_id = await get_last_post_id(user_id=message.from_user.id)

            next_post = None
            for post in personal_posts:
                if post.id > last_post_id:
                    next_post = post
                    break

            if next_post:
                text = next_post.text
                media_path = next_post.image_path
                channel_name = next_post.personal_channel_connection.username

            if media_path is not None:
                if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    message_text = f"Text: {text}\nChannel Name: @{channel_name}"
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                    await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text)

                elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                    message_text = f"Text: {text}\nChannel Name: @{channel_name}"
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                    await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text)
            elif text is None or text == '':
                if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    message_text = f"Channel Name: @{channel_name}"
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                    await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text)

                elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                    message_text = f"Channel Name: @{channel_name}"
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                    await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text)
            await update_last_post_id(user_id, post.id)
    except:
        await message.answer('Посты закончились')




