from create_bot import scheduler
from database.queries.create_queries import create_daily_statistic
from database.queries.update_queries import update_users_views_per_day


async def reset_stats():
    print('work')
    await update_users_views_per_day(reset=True)
    await create_daily_statistic()


async def scheduler_jobs():
    await create_daily_statistic()
    scheduler.add_job(reset_stats, trigger='cron',  hour=0, minute=0, second=0)
