import asyncio
import pickle

from pyrogram import Client
from PIL import Image
from config import config
from config.logging_config import logger
from pyrogram.types import Message
from pyrogram import filters
from create_bot import bot_client
from database.queries.get_queries import *
import os

from utils.types import Modes, ParseData

MEDIA_GROUP_PATH = 'media/{channel_name}/{media_group_id}'


async def parse(channel_username: str, chat_id: int, mode: Modes, limit=15) -> list[ParseData]:
    async with Client('user_session', config.API_ID, config.API_HASH, phone_number=config.PHONE_NUMBER) as user_client:
        channel_username = channel_username.replace('@', '')
        if mode == Modes.RECOMMENDATIONS:
            general_channel = await get_premium_channel(channel_username)
            channel_id = general_channel.id
        elif mode == Modes.CATEGORIES:
            category_channel = await get_category_channel(channel_username)
            channel_id = category_channel.id
        elif mode == Modes.PERSONAL:
            personal_channel = await get_personal_channel(channel_username)
            channel_id = personal_channel.id

        channel_username = f'@{channel_username}'
        await bot_client.send_message(chat_id, f'Получаем посты из канала {channel_username}...')
        data = []
        tasks = []
        messages = []
        try:
            processed_media_groups = set()
            async for message in user_client.get_chat_history(channel_username):
                if message.media_group_id:
                    if message.media_group_id in processed_media_groups:
                        continue
                    else:
                        processed_media_groups.add(message.media_group_id)
                        messages.append(message)
                elif message.photo or message.video:
                    messages.append(message)
                elif message.text:
                    messages.append(message)

                if len(messages) == limit:
                    break

            for message in messages:
                if message.media_group_id:
                    task = asyncio.create_task(
                        download_media_group(user_client, message, channel_username.replace('@', '')))
                    tasks.append(task)
                elif message.media:
                    task = asyncio.create_task(download_media(user_client, message, channel_username.replace('@', '')))
                    tasks.append(task)
                else:
                    task = asyncio.create_task(download_media(user_client, message, channel_username.replace('@', '')))
                    tasks.append(task)

            media_paths = await asyncio.gather(*tasks)
            for message, message_media_path in zip(messages, media_paths):
                message_entities = pickle.dumps(message.entities or message.caption_entities, protocol=None)
                message_text = message.caption or message.text
                if message.media_group_id:
                    media_group = await message.get_media_group()
                    message_text = media_group[0].caption
                data.append(ParseData(message.id, message_text, message_media_path, channel_username, channel_id, message_entities, chat_id))
            return data
        except Exception as err:
            logger.error(f'Ошибка при парсинге сообщений канала {channel_username}: {err}')


async def download_media(user_client, message: Message, channel_username: str) -> str | None:
    file_path = None
    if message.photo:
        file_path = f'media/{channel_username}/media_image_{message.chat.id}_{message.photo.file_unique_id}.jpg'
        await user_client.download_media(message, file_path)
    elif message.video:
        file_path = f'media/{channel_username}/media_video_{message.chat.id}_{message.video.file_id}.mp4'
        await user_client.download_media(message, file_path)
    return file_path


async def download_media_group(user_client, message: Message, channel_name: str) -> str | None:
    if not message.media_group_id:
        return None

    media_group_id = message.media_group_id
    media_group = await message.get_media_group()
    media_group_folder_path = MEDIA_GROUP_PATH.format(channel_name=channel_name, media_group_id=media_group_id)
    if os.path.exists(media_group_folder_path):
        return media_group_folder_path

    os.makedirs(media_group_folder_path, exist_ok=True)
    for media_message in media_group:
        if media_message.photo:
            file_id = media_message.photo.file_id
            file_path = f'{media_group_folder_path}/{file_id}.jpg'
            await user_client.download_media(media_message, file_name=file_path)
        elif media_message.video:
            file_id = media_message.video.file_id
            file_path = f'{media_group_folder_path}/{file_id}.mp4'
            await user_client.download_media(media_message, file_name=file_path)

    return media_group_folder_path


def compress_image(filename):
    image = Image.open(filename)
    compressed_filename = f'{filename}'
    image.save(compressed_filename, optimize=True, quality=30)
    return compressed_filename
