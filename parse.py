import asyncio
import pickle
from pyrogram import Client
from config import config
from create_bot import bot_client
from database.queries.get_queries import *
from utils.consts import errors
from utils.custom_types import Post, ChannelPostTypes
from utils.helpers import download_media_group, download_media


async def parse(channel_username: str, channel_type: ChannelPostTypes, chat_id: int = None, limit=config.POSTS_AMOUNT_LIMIT) -> list[Post] | None:
    channel_username = channel_username.replace('@', '')
    if channel_type == ChannelPostTypes.PREMIUM:
        general_channel = await get_premium_channel(channel_username)
        channel_id = general_channel.id
    elif channel_type == ChannelPostTypes.CATEGORY:
        category_channel = await get_category_channel(channel_username)
        channel_id = category_channel.id
    elif channel_type == ChannelPostTypes.PERSONAL:
        personal_channel = await get_personal_channel(channel_username)
        channel_id = personal_channel.id
    else:
        return None

    channel_username = f'@{channel_username}'
    if chat_id:
        await bot_client.send_message(chat_id, f'Получаем посты из канала {channel_username}...')
    data = []
    tasks = []
    messages = []

    async with Client('user_session', config.BOT_API_ID, config.BOT_API_HASH, phone_number=config.BOT_PHONE_NUMBER) as user_client:
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
                data.append(Post(channel_id, channel_username, message_text, message_entities, message_media_path))
        except Exception as err:
            logger.error(f'Ошибка при получении постов из канала {channel_username}: {err}')

        try:
            await user_client.send_message('me', channel_username, disable_notification=True)
        except Exception as err:
            logger.error(f'Ошибка при отправке {channel_username} канала на номер {config.BOT_PHONE_NUMBER} для обновления постов: {err}')
        if not data:
            return errors.NO_POSTS
        return data
