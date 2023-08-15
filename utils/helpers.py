import os
import pickle
import random
import shutil
from re import match, sub
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from pyrogram import Client
from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message
from pyrogram.enums import ChatAction
from config.config import ADMINS
from create_bot import bot_client
from database.queries.create_queries import *
from database.queries.get_queries import *
from database.queries.update_queries import *
from keyboards.general.helpers import build_reactions_inline_keyboard, build_delete_post_keyboard
from keyboards.general.inline.general_inline_buttons_texts import LIKE_BUTTON_TEXT, DISLIKE_BUTTON_TEXT, REPORT_BUTTON_TEXT
from utils.consts import answers, errors
from keyboards import personal_reply_keyboards, recommendations_reply_keyboards, categories_reply_keyboards
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
        posts = await get_not_viewed_categories_posts(user_tg_id)
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
        print(next_post)
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


async def send_next_post(user_tg_id: int, chat_id: int, mode: Modes, post=None):
    if not post:
        post = await get_next_post(user_tg_id, mode)
        if not post:
            return errors.NO_POST

    entities = pickle.loads(post.entities)
    media_path = post.media_path
    likes = post.likes
    dislikes = post.dislikes
    post_id = post.id
    message_text = post.text

    if mode == Modes.CATEGORIES:
        category = post.name + post.emoji
        message_text += f'\nКатегория: `{category}`'

    keyboard = ReplyKeyboardRemove()

    if mode == Modes.RECOMMENDATIONS:
        if hasattr(post, 'premium_channel_id'):
            result = await create_user_viewed_premium_post(user_tg_id, post_id)
            if result == errors.DUPLICATE_ERROR_TEXT:
                await update_user_viewed_premium_post_counter(user_tg_id, post_id)

            keyboard = build_reactions_inline_keyboard(likes, dislikes, PostTypes.PREMIUM, post_id)
        elif hasattr(post, 'category_channel_id'):
            result = await create_user_viewed_category_post(user_tg_id, post_id)
            if result == errors.DUPLICATE_ERROR_TEXT:
                await update_user_viewed_category_post_counter(user_tg_id, post_id)

            keyboard = build_reactions_inline_keyboard(likes, dislikes, PostTypes.CATEGORY, post_id)

    elif mode == Modes.CATEGORIES:
        await create_user_viewed_category_post(user_tg_id, post_id)
        keyboard = build_reactions_inline_keyboard(likes, dislikes, PostTypes.CATEGORY, post_id)

    elif mode == Modes.PERSONAL:
        await create_user_viewed_personal_post(user_tg_id, post_id)
        keyboard = build_reactions_inline_keyboard(likes, dislikes, PostTypes.PERSONAL, post_id)

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


async def send_post_to_support(chat_id: str | int, post):
    entities = pickle.loads(post.entities)
    post_text = post.text
    media_path = post.media_path
    reports = post.reports
    post_id = post.id
    report_message_id = post.report_message_id
    likes = format_number(post.likes)
    dislikes = format_number(post.dislikes)

    post_type = PostTypes.PERSONAL
    if hasattr(post, 'premium_channel_id'):
        post_type = PostTypes.PREMIUM
    elif hasattr(post, 'category_channel_id'):
        post_type = PostTypes.CATEGORY

    strings = [post_text, f'{LIKE_BUTTON_TEXT}: {likes}  {DISLIKE_BUTTON_TEXT}: {dislikes}  {REPORT_BUTTON_TEXT}: {reports}',
               f'Источник: `{post_type}`']
    result_post_text = join_with_newline(strings, 2)
    keyboard = build_delete_post_keyboard(post, post_type)
    report_message = None
    try:
        if report_message_id:
            return await bot_client.edit_message_text(chat_id, report_message_id, result_post_text, reply_markup=keyboard)

        if not media_path:
            report_message = await bot_client.send_message(chat_id, result_post_text, entities=entities, reply_markup=keyboard)
        else:
            if media_path.endswith('.jpg'):
                report_message = await bot_client.send_photo(chat_id, media_path, caption=result_post_text, caption_entities=entities,
                                                             reply_markup=keyboard)
            elif media_path.endswith('.mp4'):
                report_message = await bot_client.send_video(chat_id, media_path, caption=result_post_text, caption_entities=entities,
                                                             reply_markup=keyboard)
            elif os.path.isdir(media_path):
                media_group = []
                files = os.listdir(media_path)
                for file in files:
                    if file.endswith('.jpg'):
                        path = os.path.join(media_path, file)
                        media_group.append(InputMediaPhoto(path))
                    elif file.endswith('.mp4'):
                        path = os.path.join(media_path, file)
                        media_group.append(InputMediaVideo(path))
                media_group_message = await bot_client.send_media_group(chat_id, media_group)
                report_message = await bot_client.send_message(chat_id, result_post_text, entities=entities, reply_markup=keyboard,
                                                               reply_to_message_id=media_group_message[0].id)
        report_message_id = report_message.id

        if post_type == PostTypes.PREMIUM:
            await update_category_channel_post_report_message_id(post_id, report_message_id)
        elif post_type == PostTypes.CATEGORY:
            await update_category_channel_post_report_message_id(post_id, report_message_id)
        elif post_type == PostTypes.PERSONAL:
            await update_personal_channel_post_report_message_id(post_id, report_message_id)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, 'Упс. Не получилось получить содержимое этого поста 😬', reply_markup=keyboard)
        logger.error(f'Ошибка при отправлении поста в поддержку: {err}')
        return False


def join_with_newline(strings: list, new_lines_amount: int = 1) -> str:
    new_line = '\n'
    return f'{new_line * new_lines_amount}'.join(strings)


def format_number(num):
    if num >= 1000000:
        num_str = str(num)
        num_str = num_str[:-6] + 'm' + num_str[-6 + 1:]
        return num_str
    elif num >= 1000:
        num_str = str(num)
        num_str = num_str[:-3] + 'тыс.' + num_str[-3 + 1:]
        return num_str
    else:
        return str(num)
