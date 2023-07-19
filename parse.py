import asyncio
import base64
import pickle
from pyrogram import Client
from pyrogram.types import Message
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from PIL import Image
from config import config
from config.logging_config import logger
from create_bot import bot
from database.queries.get_queries import get_personal_channel, get_general_channel
import os
from datetime import datetime


async def download_media(client, msg):
    if not os.path.isdir("media"):
        os.mkdir("media")

    if msg.media and isinstance(msg.media, MessageMediaPhoto):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f'media/media_image_{msg.chat_id}_{msg.photo.id}_{current_time}.jpg'
        await client.download_media(msg.media, file=filename)
        return filename
    elif msg.media and isinstance(msg.media, MessageMediaDocument):
        attrs = msg.media.document.attributes
        if any([isinstance(attr, DocumentAttributeVideo) for attr in attrs]):
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f'media/media_video_{msg.chat_id}_{msg.document.id}_{current_time}.mp4'
            await client.download_media(msg.media, file=filename)
            return filename

    return None


def compress_image(filename):
    image = Image.open(filename)
    compressed_filename = f'{filename}'
    image.save(compressed_filename, optimize=True, quality=30)
    return compressed_filename


async def parse(message: Message, channel_username: str, keyboard, admin_panel=False, limit=3) -> list[dict]:
    async with Client('user_session', config.API_ID, config.API_HASH, phone_number=config.PHONE_NUMBER) as client:
        try:
            channel_username = channel_username.replace('@', '')
            if admin_panel:
                general_channel = await get_general_channel(channel_username)
                channel_id = general_channel.id
            else:
                personal_channel = await get_personal_channel(channel_username)
                channel_id = personal_channel.id

            channel_username = f'@{channel_username}'
            chat_id = message.chat.id

            await bot.send_message(chat_id, f'Получаем посты из канала {channel_username}...', reply_markup=keyboard)

            data = []
            tasks = []

            messages = []
            async for message in client.get_chat_history(channel_username, limit=limit):
                messages.append(message)
            messages = list(reversed(messages))
            for message in messages:
                task = asyncio.create_task(download_media(client, message))
                tasks.append(task)

            media_data = await asyncio.gather(*tasks)
            for message, md in zip(messages, media_data):
                entities = base64.b64encode(pickle.dumps(message.entities or message.caption_entities, protocol=None))
                data.append({
                    'id': message.id,
                    'text': f"{message.text}".replace("'", ""),
                    'media_id': md,
                    'channel_name': channel_username,
                    'grouped_id': message.media_group_id if message.media_group_id is not None else -1,
                    'channel_id': channel_id,
                    'entities': entities,
                    'chat_id': chat_id
                })
            print(data)
            return data
        except Exception as err:
            logger.error(f'Ошибка при парсинге сообщений канала {channel_username}: {err}')
