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
from utils.helpers import add_channels


async def reset_stats():
    await update_users_views_per_day(reset=True)
    await create_daily_statistic()


async def scheduler_jobs():
    await create_daily_statistic()
    scheduler.add_job(reset_stats, trigger='cron', hour=0, minute=0, second=0)


async def add_base_channels():
    initial_channels_str = 'animal_planeta | Животные 🐶,animals_N1 | Животные 🐶,national_geograph1c | Животные 🐶,Cutecats08 | Животные 🐶,zoo_4lapy | Животные 🐶,Dota2 | Игры 🎮,newcsgo | Игры 🎮,NewGameProject | Игры 🎮,PROgame_news | Игры 🎮,indiegamergate | Игры 🎮,AK47pfl | Инвестиции 📈,tinkoff_invest_official | Инвестиции 📈,omyinvestments | Инвестиции 📈,MoscowExchangeOfficial | Инвестиции 📈,if_stocks | Инвестиции 📈,Match_TV | Спорт ⚽,rflive | Спорт ⚽,️sportosnews | Спорт ⚽,️fiztransform | Спорт ⚽,️top_anime_news | Спорт ⚽,️yoga_hudeem | Спорт ⚽,sci_one_tv | Наука 🔬,nsmag | Наука 🔬,mustreads | Наука 🔬,namochimanturu | Наука 🔬,antropogenez_ru | Наука 🔬,russiandriftseries | Машины 🚗,imehanik | Машины 🚗,porscheenthusiast | Машины 🚗,prodayavtorf | Машины 🚗,vse_o_electro | Машины 🚗,bugfeature | IT 👨‍💻,Alexey070315 | IT 👨‍💻,pythonist24 | IT 👨‍💻,it_teech | IT 👨‍💻,wind_community | IT 👨‍💻,rozetked | Техника ⚙,elonmusk_ru | Техника ⚙,️exploitex | Техника ⚙,️chatgpt1337tg | Техника ⚙,concertzaal | Техника ⚙,forbesrussia | Финансы 💸,bankser | Финансы 💸,business_theory | Финансы 💸,bankoffo | Финансы 💸,sob_f | Финансы 💸,mikearoundtheworld | Путешествия 🌎,ranarod | Путешествия 🌎,from_japan | Путешествия 🌎,dmitry_lukyanchuk | Путешествия 🌎,travelnow24 | Путешествия 🌎,bestmemes | Мемы 😂,thedankestmemes | Мемы 😂,evopublikk | Мемы 😂,vidoskb | Мемы 😂,memachh | Мемы 😂,Coin_Post | Криптовалюта 💎,ru_holder | Криптовалюта 💎,blockchaingerman | Криптовалюта 💎,cryptogram_ton | Криптовалюта 💎,cripto_vestnik | Криптовалюта 💎,kinotik| Фильмы 🎬,kinosom | Фильмы 🎬,kinogaba | Фильмы 🎬,filmy_knigy_for_mood | Фильмы 🎬,kinoremix | Фильмы 🎬,aniztop | Аниме 🉐,anizanime | Аниме 🉐,kingofamv | Аниме 🉐,animeartworldone | Аниме 🉐'
    channels_and_categories = initial_channels_str.split(',')
    channels = {}
    for elem in channels_and_categories:
        elem = elem.split(' ')
        channel_name = elem[0]
        category_name = elem[2]
        channels.setdefault(category_name, [])
        channels[category_name].append(channel_name)

    add_channels_result = []
    for category_name, channels in channels.items():
        channels = ', '.join(channels)
        result = await add_channels(channels, channel_type=ChannelPostTypes.CATEGORY, category_name=category_name)
        add_channels_result.append(result)
        time.sleep(1)

    to_parse = []
    for record in add_channels_result:
        to_parse.extend(record.to_parse)

    print(to_parse)

    for channel_username in to_parse:
        posts = await parse(channel_username, ChannelPostTypes.CATEGORY)
        await create_category_posts(posts)
        time.sleep(1)
    await add_channels_in_handler()


async def add_channels_in_handler():
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
    await add_channels_in_handler()
    # await add_base_channels()
    # await parse_and_create_added_channels_posts()
