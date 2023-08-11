import pickle
from config import config
from config.logging_config import logger
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from database.queries.delete_queries import delete_first_personal_channel_post, delete_first_premium_channel_post, delete_first_category_channel_post
from database.queries.get_queries import get_premium_channel, get_category_channel, get_personal_channel, get_personal_channel_posts, \
    get_premium_channel_posts, get_category_channel_posts
from database.queries.create_queries import create_premium_post, create_category_post, create_personal_post
from utils.custom_types import Post

app = Client('update_session', config.API_ID, config.API_HASH, phone_number=config.PHONE_NUMBER)

async def on_message(client: Client, message: Message):
    channel = await client.get_chat(message.text)
    try:
        await client.get_chat_member(channel.username, 'me')
    except Exception as err:
        await client.join_chat(channel.username)
        logger.error(err)
    if channel:
        client.add_handler(MessageHandler(update_post, filters.chat(message.text)))


async def update_post(client: Client, message: Message):
    from utils.helpers import download_media, download_media_group
    from utils.helpers import clean_channel_id

    channel_username = message.chat.username
    channel_id = clean_channel_id(message.chat.id)
    message_text = message.text
    message_entities = pickle.dumps(message.entities)
    message_media_path = ''

    if message.media_group_id:
        message_media_path = await download_media_group(client, message)
    elif message.media:
        message_media_path = await download_media(client, message)

    post = Post(channel_id, channel_username, message_text, message_entities, message_media_path)
    premium_channel = await get_premium_channel(channel_username)
    category_channel = None

    if not premium_channel:
        category_channel = await get_category_channel(channel_username)

    personal_channel = await get_personal_channel(channel_username)

    if premium_channel:
        posts = await get_premium_channel_posts(channel_id)
        if len(posts) >= config.POSTS_AMOUNT_LIMIT:
            await delete_first_premium_channel_post(channel_id)
        await create_premium_post(post)
    elif category_channel:
        posts = await get_category_channel_posts(channel_id)
        if len(posts) >= config.POSTS_AMOUNT_LIMIT:
            await delete_first_category_channel_post(channel_id)
        await create_category_post(post)

    if personal_channel:
        posts = await get_personal_channel_posts(channel_id)
        if len(posts) >= config.POSTS_AMOUNT_LIMIT:
            await delete_first_personal_channel_post(channel_id)
        await create_personal_post(post)


app.add_handler(MessageHandler(on_message, filters.chat('me')))

app.run()
