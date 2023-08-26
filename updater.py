import pickle
from config import config
from config.logging_config import logger
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from database.queries.delete_queries import delete_first_personal_channel_post, delete_first_premium_channel_post, delete_first_category_channel_post
from database.queries.get_queries import get_premium_channel, get_category_channel, get_personal_channel, get_personal_channel_posts, \
    get_all_premium_channel_posts, get_category_channel_posts, get_all_channels_ids
from database.queries.create_queries import create_premium_post, create_category_post, create_personal_post
from utils.custom_types import Post

app = Client('update_session', config.BOT_API_ID, config.BOT_API_HASH, phone_number=config.BOT_PHONE_NUMBER)


async def on_message(client: Client, message: Message):
    from utils.helpers import clean_channel_id
    print('work')
    channel = await client.get_chat(message.text)
    all_channels_ids = await get_all_channels_ids()
    channel_id = clean_channel_id(channel.id)
    channel_username = channel.username

    if channel_id not in all_channels_ids:
        try:
            result = await client.get_chat_member(channel_username, 'me')
            if result:
                await client.leave_chat(channel.username)
        except Exception as err:
            logger.error(f'Ошибка при покидании канала: {err}')
        finally:
            return

    try:
        await client.get_chat_member(channel_username, 'me')
    except Exception:
        await client.join_chat(channel_username)

    client.add_handler(MessageHandler(update_post, filters.chat(message.text)))


async def update_post(client: Client, message: Message):
    from utils.helpers import download_media, download_media_group, clean_channel_id, remove_file_or_folder
    try:
        channel_username = message.chat.username

        premium_channel = await get_premium_channel(channel_username)
        category_channel = None

        if not premium_channel:
            category_channel = await get_category_channel(channel_username)

        personal_channel = await get_personal_channel(channel_username)

        if not (premium_channel or personal_channel or category_channel):
            return

        channel_id = clean_channel_id(message.chat.id)
        message_text = message.text
        message_entities = pickle.dumps(message.entities)
        message_media_path = ''

        if message.media_group_id:
            message_media_path = await download_media_group(client, message)
        elif message.media:
            message_media_path = await download_media(client, message)

        new_post = Post(channel_id, channel_username, message_text, message_entities, message_media_path)
        media_path = None

        if premium_channel:
            posts = await get_all_premium_channel_posts(channel_id)
            if len(posts) >= config.POSTS_AMOUNT_LIMIT:
                media_path = await delete_first_premium_channel_post(channel_id)
            await create_premium_post(new_post)
        elif category_channel:
            posts = await get_category_channel_posts(channel_id)
            if len(posts) >= config.POSTS_AMOUNT_LIMIT:
                media_path = await delete_first_category_channel_post(channel_id)
            await create_category_post(new_post)

        if personal_channel:
            posts = await get_personal_channel_posts(channel_id)
            if len(posts) >= config.POSTS_AMOUNT_LIMIT:
                media_path = await delete_first_personal_channel_post(channel_id)
            await create_personal_post(new_post)

        if media_path:
            remove_file_or_folder(media_path)
    except Exception as err:
        logger.error(f'Ошибка при обновлении постов: {err}')


app.add_handler(MessageHandler(on_message, filters.chat('me')))
app.run()
