import asyncio
import pickle
from pyrogram import Client
from config import config
from pyrogram.types import Message

from create_bot import bot_client
from database.queries.get_queries import *
from utils.custom_types import Modes, Post
from utils.helpers import download_media_group, download_media


async def parse(channel_username: str, chat_id: int, mode: Modes, limit=config.POSTS_AMOUNT_LIMIT) -> list[Post]:
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
                        download_media_group(user_client, message))
                    tasks.append(task)
                else:
                    task = asyncio.create_task(download_media(user_client, message))
                    tasks.append(task)

            media_paths = await asyncio.gather(*tasks)
            for message, message_media_path in zip(messages, media_paths):
                message_entities = pickle.dumps(message.entities or message.caption_entities, protocol=None)

                if message.media_group_id:
                    media_group = await message.get_media_group()
                    message_text = media_group[0].caption
                else:
                    message_text = message.caption or message.text or ''

                result_message_text = f'{message_text}\n\nПост с канала {channel_username}'
                data.append(Post(channel_id, channel_username, result_message_text, message_entities, message_media_path))

            await user_client.send_message('me', channel_username)
            return data
        except Exception as err:
            logger.error(f'Ошибка при парсинге сообщений канала {channel_username}: {err}')
