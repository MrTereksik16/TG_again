import pandas as pd
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
import Config_pars
from PIL import Image

import os
api_id = Config_pars.api_id
api_hash = Config_pars.api_hash

async def download_media(client, msg):
    if msg.media and isinstance(msg.media, MessageMediaPhoto):
        filename = f'media/media_image_{msg.chat_id}_{msg.photo.id}.jpg'.format(msg.id)
        await client.download_media(msg.media, file=filename)
        return filename

    elif msg.media and isinstance(msg.media, MessageMediaDocument):
        attrs = msg.media.document.attributes
        if any([isinstance(attr, DocumentAttributeVideo) for attr in attrs]):
            filename = f'media/media_video_{msg.chat_id}_{msg.document.id}.mp4'.format(msg.id)
            await client.download_media(msg.media, file=filename)
            compressed_filename = f'media/compressed_video_{msg.chat_id}_{msg.document.id}.mp4'.format(msg.id)
            os.remove(filename)  # Удаление исходного файла после сжатия
            return compressed_filename



def compress_image(filename):
    image = Image.open(filename)
    compressed_filename = f'{filename}'
    image.save(compressed_filename, optimize=True, quality=30)
    return compressed_filename



async def parse(name_channel: str) -> dict:
    limit = 10
    phone_number = '+224 (625) 083-393'
    channel = name_channel.replace('@', '')
    channel_name = f'{channel}'

    client = TelegramClient('session_name', Config_pars.api_id, Config_pars.api_hash)
    await client.start()
    await client.sign_in(phone=phone_number)

    channel = await client.get_entity(channel_name)
    messages = await client.get_messages(channel, limit=limit)

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
            'name_channel': name_channel,
            'grouped_id': message.grouped_id if message.grouped_id is not None else -1
        })

    print(data)

    df = pd.DataFrame(data)

    client.disconnect()
    return data
