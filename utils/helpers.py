import os
import pickle
import random
import shutil
from re import match, sub
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from pyrogram import Client
from pyrogram.types import KeyboardButton, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Message
from pyrogram.enums import ChatAction
from config.config import ADMINS
from create_bot import bot_client
from database.queries.create_queries import *
from database.queries.get_queries import *
from database.queries.update_queries import update_user_viewed_premium_posts_counters, update_user_viewed_category_posts_counters, \
    update_user_viewed_premium_post_counter, update_user_viewed_category_post_counter
from utils.consts import answers, errors
from keyboards import personal_reply_keyboards, recommendations_reply_keyboards, categories_reply_keyboards, \
    general_inline_buttons_texts
import callbacks
from utils.custom_types import Modes, PostTypes, AddChannelsResult
from pyrogram.types import ReplyKeyboardRemove
from PIL import Image


def convert_list_of_items_to_string(items: list, code: bool = True) -> str:
    if code:
        return '\n' + ''.join([f'{i}.  <code>{value}\n</code>' for i, value in enumerate(items, start=1)])
    else:
        return '\n' + ''.join([f'{i}.  {value}\n' for i, value in enumerate(items, start=1)])


async def get_next_post(user_tg_id: int, mode: Modes):
    next_post = None

    if mode == Modes.PERSONAL:
        posts = await get_user_personal_posts(user_tg_id)
        next_post = choose_post(posts)
    elif mode == Modes.CATEGORIES:
        posts = await get_best_not_viewed_categories_posts(user_tg_id)
        next_post = choose_post(posts)
    elif mode == Modes.RECOMMENDATIONS:
        await update_user_viewed_premium_posts_counters(user_tg_id)
        await update_user_viewed_category_posts_counters(user_tg_id)

        posts = []
        premium_best_posts = await get_premium_posts(user_tg_id)
        categories_best_posts = await get_best_categories_posts(user_tg_id)

        for post in premium_best_posts:
            posts.append(post)

        for post in categories_best_posts:
            posts.append(post)
        next_post = choose_post(posts)

    return next_post


def choose_post(posts: list):
    if not posts:
        return None

    total_weight = sum(post.coefficient for post in posts)
    random_num = random.randint(0, total_weight)

    for post in posts:
        random_num -= post.coefficient
        if random_num <= 0:
            return post

    return posts[0]


async def send_next_post(user_tg_id: int, chat_id: int, mode: Modes, next_post=None):
    if not next_post:
        next_post = await get_next_post(user_tg_id, mode)
        if not next_post:
            return False

    entities = pickle.loads(next_post.entities)
    text = next_post.text
    media_path = next_post.media_path
    channel_username = next_post.username
    likes = next_post.likes
    dislikes = next_post.dislikes
    post_id = next_post.id
    message_text = f'{text}\n{answers.POST_FROM_CHANNEL_MESSAGE_TEXT.format(channel_username=channel_username)}'

    if mode == Modes.CATEGORIES:
        category = next_post.name + next_post.emoji
        message_text += f'\nКатегория: `{category}`'

    keyboard = ReplyKeyboardRemove()

    if mode == Modes.RECOMMENDATIONS:
        if hasattr(next_post, 'premium_channel_id'):
            result = await create_user_viewed_premium_post(user_tg_id, post_id)
            if result == errors.DUPLICATE_ERROR_TEXT:
                await update_user_viewed_premium_post_counter(user_tg_id, post_id)

            keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.PREMIUM, post_id)
        elif hasattr(next_post, 'category_channel_id'):
            result = await create_user_viewed_category_post(user_tg_id, post_id)
            if result == errors.DUPLICATE_ERROR_TEXT:
                await update_user_viewed_category_post_counter(user_tg_id, post_id)

            keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.CATEGORY, post_id)

    elif mode == Modes.CATEGORIES:
        await create_user_viewed_category_post(user_tg_id, post_id)
        keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.CATEGORY, post_id)

    elif mode == Modes.PERSONAL:
        await create_user_viewed_personal_post(user_tg_id, post_id)
        keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.PERSONAL, post_id)

    try:
        if not media_path:
            await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)
        else:
            if media_path.endswith('.jpg'):
                await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                await bot_client.send_photo(chat_id, media_path, caption=message_text, caption_entities=entities, reply_markup=keyboard)
            elif media_path.endswith('.mp4'):
                await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_VIDEO)
                await bot_client.send_video(chat_id, media_path, caption=message_text, caption_entities=entities, reply_markup=keyboard)
            elif os.path.isdir(media_path):
                media_group = []
                files = os.listdir(media_path)
                for file in files:
                    if file.endswith('.jpg'):
                        await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                        path = os.path.join(media_path, file)
                        media_group.append(InputMediaPhoto(path))
                    elif file.endswith('.mp4'):
                        await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                        path = os.path.join(media_path, file)
                        media_group.append(InputMediaVideo(path))
                msg = await bot_client.send_media_group(chat_id, media_group)
                await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard, reply_to_message_id=msg[0].id)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, 'Упс. Не получилось получить этот пост 😬', reply_markup=keyboard)
        logger.error(f'Ошибка при отправлении поста пользователю: {err}')
        return False


async def send_end_message(user_tg_id, chat_id, mode: Modes):
    no_post_keyboard = ReplyKeyboardRemove()
    user_is_admin = user_tg_id in ADMINS

    if mode == Modes.RECOMMENDATIONS:
        no_post_keyboard = recommendations_reply_keyboards.recommendations_start_control_keyboard
    elif mode == Modes.CATEGORIES:
        no_post_keyboard = categories_reply_keyboards.categories_start_control_keyboard
    elif mode == Modes.PERSONAL:
        no_post_keyboard = personal_reply_keyboards.personal_start_control_keyboard

    if user_is_admin:
        if mode == Modes.RECOMMENDATIONS:
            no_post_keyboard = recommendations_reply_keyboards.recommendations_admin_start_control_keyboard
        elif mode == Modes.CATEGORIES:
            no_post_keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard

    await bot_client.send_message(chat_id, answers.POSTS_OVER, reply_markup=no_post_keyboard)


async def add_channels(channels: str, user_tg_id: int, mode: Modes, category_name='', coefficient: int = 1) -> AddChannelsResult:
    links = [link.strip() for link in channels.split(',') if link.strip()]
    to_parse = []
    added = []
    not_added = []
    already_added = []
    for link in links:
        try:
            if not match(r'^@[a-zA-Z0-9_]+', link):
                tg_link = sub(r'https://t.me/(\w+)', r'\1', link)
                channel_entity = await bot_client.get_chat(tg_link)
            else:
                channel_entity = await bot_client.get_chat(link)

        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')
            not_added.append(link)
            continue

        channel_username = channel_entity.username
        channel_tg_id = clean_channel_id(channel_entity.id)

        result = None

        if mode == Modes.RECOMMENDATIONS:
            result = await create_premium_channel(channel_tg_id, channel_username, coefficient)
            if result:
                to_parse.append(channel_username)
        elif mode == Modes.CATEGORIES:
            category_id = await get_category_id(category_name)
            result = await create_category_channel(channel_tg_id, channel_username, category_id, coefficient)
            if result:
                to_parse.append(channel_username)
        elif mode == Modes.PERSONAL:
            r = await create_personal_channel(channel_tg_id, channel_username, coefficient)
            if r == errors.DUPLICATE_ERROR_TEXT:
                result = await create_user_channel(user_tg_id, channel_tg_id)
            elif r:
                result = await create_user_channel(user_tg_id, channel_tg_id)
                to_parse.append(channel_username)

        if result == errors.DUPLICATE_ERROR_TEXT:
            already_added.append(f'@{channel_username}')
        elif result:
            added.append(f'@{channel_username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    answer = ''

    if mode == Modes.CATEGORIES and added:
        answer += f'Были добавлены каналы с категорией `<code>{category_name}</code>`:\n{", ".join(added)}'
    elif (mode == Modes.PERSONAL or mode == Modes.RECOMMENDATIONS) and added:
        answer += f'Были добавлены каналы:\n{", ".join(added)}\n'

    if not_added:
        answer += f'Не удалось добавить каналы:\n{", ".join(not_added)}\n'
    if already_added:
        answer += f'Каналы уже были добавлены ранее:\n{", ".join(already_added)}\n'
    return AddChannelsResult(answer, to_parse)


def create_buttons(texts: list[str]):
    buttons = []
    for category in texts:
        buttons.append(KeyboardButton(text=category))
    return buttons


def create_menu(buttons: list[KeyboardButton], n_cols: int = 2, header_buttons: list[KeyboardButton] | KeyboardButton = None,
                footer_buttons: list = None) -> ReplyKeyboardMarkup:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        if not isinstance(header_buttons, list):
            header_buttons = [header_buttons]
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return ReplyKeyboardMarkup(menu, resize_keyboard=True)


def create_reactions_keyboard(likes: int, dislikes: int, post_type: PostTypes, post_id: int):
    if likes >= 1000000:
        likes = f'{likes // 1000000}M'
    elif likes >= 1000:
        likes = f'{likes // 1000}K'

    if dislikes >= 1000000:
        likes = f'{dislikes // 1000000}M'
    elif dislikes >= 1000:
        dislikes = f'{dislikes // 1000}K'

    like_button = InlineKeyboardButton(f'{general_inline_buttons_texts.LIKE_BUTTON_TEXT} {likes}',
                                       callback_data=f'{callbacks.LIKE}:{post_type}:{post_id}:{likes}:{dislikes}')

    dislike_button = InlineKeyboardButton(f'{general_inline_buttons_texts.DISLIKE_BUTTON_TEXT} {dislikes}',
                                          callback_data=f'{callbacks.DISLIKE}:{post_type}:{post_id}:{likes}:{dislikes}')

    keyboard = InlineKeyboardMarkup([[like_button, dislike_button]])

    return keyboard


def clean_channel_id(channel_id: int) -> int:
    channel_id = str(channel_id)
    if channel_id.startswith('-100'):
        return int(channel_id[4:])
    else:
        return int(channel_id)


async def reset_and_switch_state(state: FSMContext, switch_to: State()):
    await state.reset_state()
    await state.set_state(switch_to)


async def download_media(client: Client, message: Message) -> str | None:
    file_path = None
    channel_username = message.chat.username
    if message.photo:
        file_path = f'media/{channel_username}/media_image_{message.chat.id}_{message.photo.file_unique_id}.jpg'
        await client.download_media(message, file_path)
    elif message.video:
        file_path = f'media/{channel_username}/media_video_{message.chat.id}_{message.video.file_id}.mp4'
        await client.download_media(message, file_path)
    return file_path


async def download_media_group(client: Client, message: Message) -> str | None:
    if not message.media_group_id:
        return None

    channel_name = message.chat.username
    media_group_id = message.media_group_id
    media_group = await message.get_media_group()
    media_group_folder_path = f'media/{channel_name}/{media_group_id}'
    if os.path.exists(media_group_folder_path):
        return media_group_folder_path

    os.makedirs(media_group_folder_path, exist_ok=True)
    for media_message in media_group:
        if media_message.photo:
            file_id = media_message.photo.file_id
            file_path = f'{media_group_folder_path}/{file_id}.jpg'
            await client.download_media(media_message, file_name=file_path)
        elif media_message.video:
            file_id = media_message.video.file_id
            file_path = f'{media_group_folder_path}/{file_id}.mp4'
            await client.download_media(media_message, file_name=file_path)

    return media_group_folder_path


def compress_image(filename):
    image = Image.open(filename)
    compressed_filename = f'{filename}'
    image.save(compressed_filename, optimize=True, quality=30)
    return compressed_filename


def remove_file_or_folder(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        try:
            os.rmdir(path)
        except OSError:
            shutil.rmtree(path)
    else:
        print("Path not found")
