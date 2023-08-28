from pyrogram import Client
from create_bot import scheduler
from database.queries.create_queries import create_daily_statistic
from database.queries.get_queries import get_all_channels
from database.queries.update_queries import update_users_views_per_day
from aiogram import types
from config import config


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


async def on_start_bot_tasks(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "К рекомендациям"),
    ])
    await scheduler_jobs()
    await add_channels_to_message_handler()
