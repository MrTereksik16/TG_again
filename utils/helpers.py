import os
import pickle
import random
from re import match, sub
from aiogram.types import Message
from pyrogram.types import KeyboardButton, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from pyrogram.enums import ChatAction
from config.config import ADMINS
from create_bot import bot_client
from database.queries.create_queries import *
from config.logging_config import logger
from database.queries.get_queries import *
from utils.consts import answers, errors
from keyboards import personal_reply_keyboards, recommendations_reply_keyboards, categories_reply_keyboards, \
    general_inline_buttons_texts
from callbacks import callbacks
from utils.types import Modes, PostTypes, AddChannelsResult
from pyrogram.types import ReplyKeyboardRemove


async def convert_categories_to_string(categories) -> str:
    return ''.join([f'<code>{categories[i]}\n</code>' for i in range(0, len(categories))])


async def send_next_post(user_tg_id: int, chat_id: int, mode: Modes, post=None):
    if not post:
        post = await get_next_post(user_tg_id, mode)
        if not post:
            return errors.NO_POST

    entities = pickle.loads(post.entities)
    text = post.text if post.text is not None else ''
    media_path = post.image_path
    channel_username = post.username
    likes = post.likes
    dislikes = post.dislikes

    message_text = f"{text}\n{answers.POST_FROM_CHANNEL_MESSAGE.format(channel_username=channel_username)}"

    if mode == Modes.CATEGORIES:
        category = post.name + post.emoji
        message_text += f'\nКатегория: `{category}`'

    keyboard = ReplyKeyboardRemove()

    if mode == Modes.RECOMMENDATIONS:
        if hasattr(post, 'premium_channel_id'):
            await create_user_viewed_premium_post(user_tg_id, post.id)
            keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.PREMIUM, post.id)
        elif hasattr(post, 'category_channel_id'):
            await create_user_viewed_category_post(user_tg_id, post.id)
            keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.CATEGORY, post.id)

    elif mode == Modes.CATEGORIES:
        await create_user_viewed_category_post(user_tg_id, post.id)
        keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.CATEGORY, post.id)

    elif mode == Modes.PERSONAL:
        await create_user_viewed_personal_post(user_tg_id, post.id)
        keyboard = create_reactions_keyboard(likes, dislikes, PostTypes.PERSONAL, post.id)

    try:
        if media_path is None:
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
    except Exception as err:
        await bot_client.send_message(chat_id, 'Упс. Не получилось получить этот пост 😬', reply_markup=keyboard)
        logger.error(f'Ошибка при отправлении поста пользователю: {err}')


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

    await bot_client.send_message(chat_id, answers.POST_ARE_OVER, reply_markup=no_post_keyboard)


async def get_next_post(user_tg_id: int, mode: Modes):
    next_post = None

    if mode == Modes.PERSONAL:
        posts = await get_personal_posts(user_tg_id)
        next_post = choose_post(posts)
    elif mode == Modes.CATEGORIES:
        posts = await get_best_not_viewed_categories_posts(user_tg_id)
        next_post = choose_post(posts)
    elif mode == Modes.RECOMMENDATIONS:
        posts = []
        premium_best_posts = await get_best_not_viewed_premium_posts(user_tg_id)
        categories_best_posts = await get_best_not_viewed_categories_posts(user_tg_id)

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
    random_num = random.uniform(0, total_weight)

    for post in posts:
        random_num -= post.coefficient
        if random_num <= 0:
            return post

    return posts[0]


async def add_channels_from_message(message: Message, mode: Modes, category='', ) -> AddChannelsResult:
    links = [link.strip() for link in message.text.split(',') if link.strip()]
    user_tg_id = message.from_user.id
    to_parse = []
    added = []
    not_added = []
    already_added = []
    for link in links:
        try:
            if not match(r'^@[a-zA-Z0-9_]+', link):
                link = sub(r"https://t.me/(\w+)", r"\1", link)
            channel_entity = await bot_client.get_chat(link)
        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')
            continue

        channel_username = channel_entity.username
        channel_tg_id = clean_channel_id(channel_entity.id)

        result = None

        if mode == Modes.RECOMMENDATIONS:
            result = await create_recommendation_channel(channel_tg_id, channel_username)
            if result:
                to_parse.append(channel_username)
        elif mode == Modes.CATEGORIES:
            category_id = int(category.split('.')[0])
            result = await create_category_channel(channel_tg_id, channel_username, category_id)

            if result:
                to_parse.append(channel_username)
        elif mode == Modes.PERSONAL:
            result = await create_personal_channel(channel_tg_id, channel_username)
            if result == errors.DUPLICATE_ENTRY_ERROR:
                result = await create_user_channel(user_tg_id, channel_tg_id)
            elif result:
                result = await create_user_channel(user_tg_id, channel_tg_id)
                to_parse.append(channel_username)

        if result == errors.DUPLICATE_ENTRY_ERROR:
            already_added.append(f'@{channel_username}')
        elif result:
            added.append(f'@{channel_username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    answer = ''

    if mode == Modes.CATEGORIES and added:
        answer += answers.CHANNELS_ADDED_WITH_CATEGORY_MESSAGE.format(category=category.split(". ", 1)[1]) + ', '.join(added)
    elif (mode == Modes.PERSONAL or mode == Modes.RECOMMENDATIONS) and added:
        answer += answers.CHANNELS_ADDED_MESSAGE + ', '.join(added)

    if not_added:
        answer += answers.CHANNELS_NOT_ADDED_MESSAGE + ', '.join(not_added)
    if already_added:
        answer += answers.CHANNELS_ALREADY_ADDED_MESSAGE + ', '.join(already_added)

    return AddChannelsResult(answer, to_parse, added, already_added, not_added)


async def create_categories_buttons(categories):
    categories_buttons = []
    for category in categories:
        categories_buttons.append(KeyboardButton(text=category))
    return categories_buttons


def build_categories_menu(buttons, n_cols: int = 2, header_buttons: list = None, footer_buttons: list = None) -> ReplyKeyboardMarkup:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return ReplyKeyboardMarkup(menu)


def create_reactions_keyboard(likes: int, dislikes: int, post_type: PostTypes, post_id: int):
    if likes >= 1000:
        likes = f"{likes // 1000}K"

    if dislikes >= 1000:
        dislikes = f"{dislikes // 1000}K"

    like_button = InlineKeyboardButton(f"{general_inline_buttons_texts.LIKE_BUTTON_TEXT} {likes}",
                                       callback_data=f'{callbacks.LIKE}:{post_type}:{post_id}:{likes}:{dislikes}')

    dislike_button = InlineKeyboardButton(f"{general_inline_buttons_texts.DISLIKE_BUTTON_TEXT} {dislikes}",
                                          callback_data=f'{callbacks.DISLIKE}:{post_type}:{post_id}:{likes}:{dislikes}')

    keyboard = InlineKeyboardMarkup([[like_button, dislike_button]])

    return keyboard


def clean_channel_id(channel_id: int) -> int:
    channel_id = str(channel_id)
    if channel_id.startswith('-100'):
        return int(channel_id[4:])
    else:
        return int(channel_id)
