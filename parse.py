import pandas as pd
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from PIL import Image
import os
from config.config import ADMINS
from config import config
from config.logging_config import logger
from database.queries.get_queries import get_personal_channel, get_general_channel


async def download_media(client, msg):
    if not os.path.isdir("media"):
        os.mkdir("media")

    if msg.media and isinstance(msg.media, MessageMediaPhoto):
        filename = f'media/media_image_{msg.chat_id}_{msg.photo.id}.jpg'
        await client.download_media(msg.media, file=filename)
        return filename
        compressed_filename = f'media/{msg.chat_id}_{msg.document.id}.mp4'
        os.remove(filename)  # Удаление исходного файла после сжатия
        return compressed_filename

    elif msg.media and isinstance(msg.media, MessageMediaDocument):
        attrs = msg.media.document.attributes
        if any([isinstance(attr, DocumentAttributeVideo) for attr in attrs]):
            filename = f'media/media_video_{msg.chat_id}_{msg.document.id}.mp4'
            await client.download_media(msg.media, file=filename)


def compress_image(filename):
    image = Image.open(filename)
    compressed_filename = f'{filename}'
    image.save(compressed_filename, optimize=True, quality=30)
    return compressed_filename


async def parse(user_tg_id, channel_name: str, limit=3) -> list[dict]:
    client = TelegramClient('user_session', config.API_ID, config.API_HASH).start(config.PHONE_NUMBER)
    channel = channel_name.replace('@', '')
    channel_name = channel

    try:
        channel = await client.get_entity(channel_name)
        messages = await client.get_messages(channel, limit=limit)
        if user_tg_id not in ADMINS:
            channel = await get_personal_channel(channel_name)
            channel_id = channel.id
        else:
            channel = await get_general_channel(channel_name)
            channel_id = channel.id

        data = []
        tasks = []

        async for msg in client.iter_messages(channel_name, limit=limit):
            task = asyncio.create_task(download_media(client, msg))
            tasks.append(task)

        media_data = await asyncio.gather(*tasks)

        for message, md in zip(messages, media_data):
            data.append({
                'id': message.id,
                'text': f"{message.text}".replace("'", ""),
                'media_id': md,
                'chat_id': message.chat_id,
                'channel_name': channel_name,
                'grouped_id': message.grouped_id if message.grouped_id is not None else -1,
                'channel_id': channel_id
            })
            print(message.text)

            df = pd.DataFrame(data)

        return data
    except Exception as err:
        logger.error(f'Ошибка при парсинге сообщений канала {channel_name}:{err}')
