import time
from pyrogram import Client
from create_bot import scheduler
from database.queries.create_queries import create_daily_statistic, create_premium_posts, create_category_posts, create_personal_posts
from database.queries.get_queries import get_all_channels, get_all_premium_channels, get_all_categories_channels, get_all_personal_channels
from database.queries.update_queries import update_users_views_per_day
from aiogram import types
from config import config
from parse import parse
from utils.custom_types import ChannelPostTypes


async def reset_stats():
    await update_users_views_per_day(reset=True)
    await create_daily_statistic()


async def scheduler_jobs():
    await create_daily_statistic()
    scheduler.add_job(reset_stats, trigger='cron', hour=0, minute=0, second=0)


async def add_channels_to_message_handler():
    all_channels_usernames = [channel.channel_username for channel in (await get_all_channels())]
    async with Client('user_session', config.BOT_API_ID, config.BOT_API_HASH, phone_number=config.BOT_PHONE_NUMBER) as user_client:
        user_client: Client
        for channel_username in all_channels_usernames:
            await user_client.send_message('me', channel_username)


async def parse_and_create_added_channels_posts():
    premium_channels = await get_all_premium_channels()
    for channel in premium_channels:
        premium_posts = await parse(channel.channel_username, ChannelPostTypes.PREMIUM)
        if premium_posts:
            await create_premium_posts(premium_posts)
        time.sleep(1)

    category_channels = await get_all_categories_channels()
    for channel in category_channels:
        category_posts = await parse(channel.channel_username, ChannelPostTypes.CATEGORY)
        if category_posts:
            await create_category_posts(category_posts)
        time.sleep(1)

    personal_channels = await get_all_personal_channels()
    for channel in personal_channels:
        personal_posts = await parse(channel.channel_username, ChannelPostTypes.PERSONAL)
        if personal_posts:
            await create_personal_posts(personal_posts)
        time.sleep(1)


async def on_start_bot_tasks(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", 'Лента рекомендаций'),
    ])
    await scheduler_jobs()
    # await add_channels_to_message_handler()
    # await parse_and_create_added_channels_posts()
