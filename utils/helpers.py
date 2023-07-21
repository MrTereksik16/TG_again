import base64
import glob
import os
import pickle
from re import match, sub

from pyrogram.types import KeyboardButton, InputMediaPhoto, InputMediaVideo
from pyrogram.enums import ChatAction
from config.config import ADMINS
from database.queries.create_queries import *
from database.queries.get_queries import *
from database.queries.update_queries import *
from keyboards.personal.inline.personal_inline_keyboards import add_user_channels_inline_keyboard
from parse import parse
from utils.consts import answers, errors
from keyboards import personal_reply_keyboards, recommendations_reply_keyboards, categories_reply_keyboards


async def convert_categories_to_string(categories) -> str:
    return ''.join([f'<code>{categories[i]}\n</code>' for i in range(0, len(categories))])


async def send_post_in_personal_feed(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    personal_posts = await get_personal_posts(user_tg_id)
    last_post_id = await get_user_last_personal_post_id(user_tg_id)
    user_channels = await get_user_channels(user_tg_id)

    keyboard = personal_reply_keyboards.personal_control_keyboard

    if personal_posts:
        for post in personal_posts:
            if post.id > last_post_id:
                next_post = post
                break
        else:
            return await message.answer(answers.POST_ARE_OVER,
                                        reply_markup=personal_reply_keyboards.personal_start_control_keyboard)
        entities = pickle.loads(post.entities)
        text = next_post.text if next_post.text is not None else ''
        media_path = next_post.image_path
        channel_username = next_post.username
        message_text = f"{text}\n{answers.POST_FROM_CHANNEL_MESSAGE.format(channel_username=channel_username)}"

        try:
            if media_path is None:
                await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)
            else:
                if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                    await bot_client.send_photo(chat_id, media_path, caption=message_text, caption_entities=entities,
                                                reply_markup=keyboard)
                elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                    await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_VIDEO)
                    await bot_client.send_video(chat_id, media_path, caption=message_text, caption_entities=entities,
                                                reply_markup=keyboard)
                elif os.path.isdir(media_path):
                    media_group = []
                    files = os.listdir(media_path)
                    for file in files:
                        if file.endswith('.jpg'):
                            await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                            path = os.path.join(media_path, file)
                            media_group.append(InputMediaPhoto(path))
                        elif file.endswith('.mp4'):
                            await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_VIDEO)
                            path = os.path.join(media_path, file)
                            media_group.append(InputMediaVideo(path))
                    await bot_client.send_media_group(chat_id, media_group)
                    await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)

        except Exception as err:
            await message.answer('Упс. Не получилось получить этот пост 😬', reply_markup=keyboard)
            logger.error(f'Ошибка при отправлении поста пользователю: {err}')
        await update_user_last_personal_post_id(user_tg_id, next_post.id)
    elif user_channels:
        for channel in user_channels:
            await parse(message, channel, keyboard)
    else:
        await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)


async def send_post_in_recommendations_feed(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    general_posts = await get_general_posts()
    user_is_admin = user_tg_id in ADMINS

    keyboard = recommendations_reply_keyboards.recommendations_control_keyboard
    no_post_keyboard = recommendations_reply_keyboards.recommendations_start_control_keyboard

    if user_is_admin:
        keyboard = recommendations_reply_keyboards.recommendations_admin_control_keyboard
        no_post_keyboard = recommendations_reply_keyboards.recommendations_admin_start_control_keyboard

    if general_posts:
        last_post_id = await get_user_last_general_post_id(user_tg_id)
        for post in general_posts:
            if post.id > last_post_id:
                next_post = post
                break
        else:
            return await message.answer(answers.POST_ARE_OVER, reply_markup=no_post_keyboard)

        entities = pickle.loads(next_post.entities)
        text = next_post.text if next_post.text is not None else ''
        media_path = next_post.image_path
        channel_username = next_post.general_channel_connection.username
        message_text = f"{text}\n{answers.POST_FROM_CHANNEL_MESSAGE.format(channel_username=channel_username)}"

        try:
            if media_path is None:
                await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)
            else:
                if media_path.endswith('.jpg'):
                    await bot_client.send_photo(chat_id, media_path, caption=message_text, caption_entities=entities,
                                                reply_markup=keyboard)
                elif media_path.endswith('.mp4'):
                    await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_VIDEO)
                    await bot_client.send_video(chat_id, media_path, caption=message_text, caption_entities=entities,
                                                reply_markup=keyboard)
                elif os.path.isdir(media_path):
                    media_group = []
                    files = os.listdir(media_path)
                    for file in files:
                        if file.endswith('.jpg'):
                            path = os.path.join(media_path, file)
                            await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                            media_group.append(InputMediaPhoto(path))
                        elif file.endswith('.mp4'):
                            path = os.path.join(media_path, file)
                            await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_VIDEO)
                            media_group.append(InputMediaVideo(path))
                    await bot_client.send_media_group(chat_id, media_group)
                    await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)

        except Exception as err:
            await bot_client.send_message(chat_id, 'Упс. Не получилось получить этот пост 😬', reply_markup=keyboard)
            logger.error(f'Ошибка при отправлении поста пользователю: {err}')

        await update_user_last_general_post_id(user_tg_id, next_post.id)
    else:
        await message.answer("Нет доступных постов", reply_markup=no_post_keyboard)


async def send_post_in_categories_feed(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    user_is_admin = user_tg_id in ADMINS
    categories_posts = await get_categories_posts(user_tg_id)

    keyboard = categories_reply_keyboards.categories_control_keyboard
    no_post_keyboard = categories_reply_keyboards.categories_start_control_keyboard

    if user_is_admin:
        keyboard = categories_reply_keyboards.categories_admin_control_keyboard
        no_post_keyboard = categories_reply_keyboards.categories_admin_start_control_keyboard

    if categories_posts:
        for post in categories_posts:
            last_post_id = await get_user_last_category_post_id(user_tg_id, post.category_id)
            if post.id > last_post_id:
                next_post = post
                break
        else:
            return await message.answer(answers.POST_ARE_OVER, no_post_keyboard)

        entities = pickle.loads(next_post.entities)
        text = next_post.text if next_post.text is not None else ''
        media_path = next_post.image_path
        channel_username = next_post.username

        message_text = f"{text}\n{answers.POST_FROM_CHANNEL_MESSAGE.format(channel_username=channel_username)}"

        try:
            if media_path is None:
                await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)
            else:
                if media_path.endswith('.jpg'):
                    await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)
                    await bot_client.send_photo(chat_id, media_path, caption=message_text, caption_entities=entities,
                                                reply_markup=keyboard)
                elif media_path.endswith('.mp4'):
                    await bot_client.send_chat_action(chat_id, action=ChatAction.UPLOAD_VIDEO)
                    await bot_client.send_video(chat_id, media_path, caption=message_text, caption_entities=entities,
                                                reply_markup=keyboard)
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
                    await bot_client.send_media_group(chat_id, media_group)
                    await bot_client.send_message(chat_id, message_text, entities=entities, reply_markup=keyboard)
        except Exception as err:
            await message.answer('Упс. Не получилось получить этот пост 😬', reply_markup=keyboard)
            logger.error(f'Ошибка при отправлении поста пользователю: {err}')

        await update_user_last_category_post_id(user_tg_id, next_post.category_id, next_post.id)
    else:
        await message.answer("Нет доступных постов ", reply_markup=no_post_keyboard)


async def add_channels_from_message(message: Message,
                                    category='',
                                    ) -> dict[str | list[str]]:
    links = [link.strip() for link in message.text.split(',') if link.strip()]
    user_tg_id = message.from_user.id
    added = []
    not_added = []
    already_added = []
    admin_panel_mode = user_tg_id in ADMINS and category
    for link in links:
        try:
            if not match(r'^@[a-zA-Z0-9_]+', link):
                link = sub(r"https://t.me/(\w+)", r"\1", link)

            channel_entity = await bot_client.get_chat(link)
        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')
            continue

        if not channel_entity.username:
            channel_entity.username = link

        channel_username = channel_entity.username
        if admin_panel_mode:
            category_id = int(category[0])
            result = await create_general_channel(channel_username, category_id)
        else:
            result = await create_user_channel(user_tg_id, channel_username)

        if result == errors.DUPLICATE_ENTRY_ERROR:
            already_added.append(f'@{channel_username}')
        elif result:
            added.append(f'@{channel_username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    answer = ''
    if admin_panel_mode:
        if added:
            answer += answers.CHANNELS_ADDED_WITH_CATEGORY_MESSAGE.format(
                category=category.split(". ", 1)[1]) + ', '.join(added)
    else:
        if added:
            answer += answers.CHANNELS_ADDED_MESSAGE + ', '.join(added)

    if not_added:
        answer += answers.CHANNELS_NOT_ADDED_MESSAGE + ', '.join(not_added)
    if already_added:
        answer += answers.CHANNELS_ALREADY_ADDED_MESSAGE + ', '.join(already_added)

    return {'answer': answer, 'added': added, 'already_added': already_added, 'not_added': not_added}


async def create_categories_buttons(categories):
    categories_buttons = []
    for category in categories:
        categories_buttons.append(KeyboardButton(text=category))
    return categories_buttons
