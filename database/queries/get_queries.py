from sqlalchemy import text, func, cast, Date
from config.logging_config import logger
from database.create_db import Session
from database.models import User, PersonalChannel, UserChannel, PremiumChannel, CategoryChannel, Category, UserCategory, PersonalPost, PremiumPost, \
    CategoryPost, Coefficient, DailyStatistic
from utils.custom_types import MarkTypes, Statistic


async def get_user(user_tg_id: int) -> User:
    session = Session()
    user = None
    try:
        user = session.get(User, user_tg_id)
    except Exception as err:
        logger.error(err)
    finally:
        session.close()
        return user


async def get_personal_channel(channel_username: str) -> PersonalChannel:
    session = Session()
    channel = None
    try:
        channel = session.query(PersonalChannel).filter(PersonalChannel.channel_username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()
        return channel


async def get_personal_channel_post(post_id: int) -> PersonalPost:
    session = Session()
    channel = None
    try:
        channel = session.query(PersonalPost).filter(PersonalPost.id == post_id).one()
    except Exception as err:
        logger.error(f'Ошибка при получении поста из персонального канала: {err}')
    finally:
        session.close()
        return channel


async def get_user_channels_usernames(user_tg_id: int) -> list[str]:
    session = Session()
    channels = []
    try:
        records = session.query(PersonalChannel).select_from(UserChannel).join(PersonalChannel).filter(UserChannel.user_id == user_tg_id)
        channels = []
        for channel in records:
            channels.append(channel.channel_username)

    except Exception as err:
        logger.error(f'Ошибка при получении списка каналов пользователя: {err}')
    finally:
        session.close()
        return channels


async def get_premium_channel(channel_username: str) -> PremiumChannel | None:
    session = Session()
    channel = None
    try:
        channel = session.query(PremiumChannel).filter(
            PremiumChannel.channel_username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении премиального канала канала: {err}')
    finally:
        session.close()
        return channel


async def get_premium_channel_post(post_id: int) -> PremiumPost | None:
    session = Session()
    channel = None
    try:
        channel = session.query(PremiumPost).filter(PremiumPost.id == post_id).one()
    except Exception as err:
        logger.error(f'Ошибка при получении поста из премиального канала: {err}')
    finally:
        session.close()
        return channel


async def get_category_channel(channel_username: str) -> CategoryChannel | None:
    session = Session()
    channel = None
    try:
        channel = session.query(CategoryChannel).filter(CategoryChannel.channel_username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении канала из категорий: {err}')
    finally:
        session.close()
        return channel


async def get_category_channel_post(post_id: int) -> CategoryPost:
    session = Session()
    channel = None
    try:
        channel = session.query(CategoryPost).filter(CategoryPost.id == post_id).one()
    except Exception as err:
        logger.error(f'Ошибка при получении канала из категорий: {err}')
    finally:
        session.close()
        return channel


async def get_user_personal_posts(user_tg_id: int) -> list:
    session = Session()
    personal_posts = []
    try:
        query = f'''
        select posts.*, channel_username, coefficient
        from user join user_channel on user_channel.user_id = user.id
        join personal_post posts on user_channel.channel_id = posts.personal_channel_id
        join personal_channel on personal_channel.id = user_channel.channel_id and user_channel.user_id = {user_tg_id}
        left join user_viewed_personal_post uvpp on posts.id = uvpp.personal_post_id and uvpp.user_id = {user_tg_id}
        where uvpp.user_id is NULL
        group by channel_id
        '''

        records = session.execute(text(query))
        for record in records:
            personal_posts.append(record)
    except Exception as err:
        logger.error(f'Ошибка при получении постов из пользовательских каналов: {err}')
    finally:
        session.close()
        return personal_posts


async def get_personal_channel_posts(channel_id: int):
    session = Session()
    posts = []
    try:
        records = session \
            .query(PersonalPost) \
            .join(PersonalChannel) \
            .filter(PersonalChannel.id == channel_id)

        for record in records:
            posts.append(record)
    except Exception as err:
        logger.error(f'Ошибка при получении постов из пользовательского канала: {err}')
    finally:
        session.close()
        return posts


async def get_all_premium_channel_posts(channel_id: int):
    session = Session()
    posts = []
    try:
        records = session \
            .query(PremiumPost) \
            .join(PremiumChannel) \
            .filter(PremiumChannel.id == channel_id)

        for record in records:
            posts.append(record)
    except Exception as err:
        logger.error(f'Ошибка при получении всех постов из премиального канала: {err}')
    finally:
        session.close()
        return posts


async def get_category_channel_posts(channel_id: int):
    session = Session()
    posts = []
    try:
        records = session \
            .query(CategoryPost) \
            .join(CategoryChannel) \
            .filter(CategoryChannel.id == channel_id)

        for record in records:
            posts.append(record)
    except Exception as err:
        logger.error(f'Ошибка при получении постов из канала в категориях: {err}')
    finally:
        session.close()
        return posts


async def get_premium_posts(user_tg_id) -> list:
    session = Session()
    posts = []
    try:
        query = f'''
        select * from (
                select posts.*, coefficient, channel_username, row_number() over (partition by premium_channel_id order by rand()) as row_num from premium_post posts
                join premium_channel rc on rc.id = posts.premium_channel_id
                left join user_viewed_premium_post uvpp on posts.id = uvpp.premium_post_id and uvpp.user_id = {user_tg_id}
                where (counter is null or counter = 0) and (mark_type_id is null or mark_type_id != {MarkTypes.REPORT})
                order by RAND()
            ) p where row_num = 1
            '''

        records = session.execute(text(query))

        for post in records:
            posts.append(post)

    except Exception as err:
        logger.error(f'Ошибка при получении общего поста: {err}')
    finally:
        session.close()
        return posts


async def get_not_viewed_categories_posts(user_tg_id) -> list:
    session = Session()
    posts = []
    try:
        query = f'''
            select *
            from (
                select posts.*, coefficient, channel_username, name, emoji, row_number() over (partition by category_channel_id order by likes desc ) as row_num
                from category_post posts
                join category_channel cc on posts.category_channel_id = cc.id
                join category c on cc.category_id = c.id
                join user_category uc on cc.category_id = uc.category_id and uc.user_id = {user_tg_id}
                left join user_viewed_category_post uvcp on posts.id = uvcp.category_post_id and uvcp.user_id = {user_tg_id}
                where uvcp.user_id is null
            ) subquery
            where row_num = 1
        '''

        records = session.execute(text(query))
        for post in records:
            posts.append(post)
    except Exception as err:
        logger.error(f'Ошибка при получении постов из каналов в пользовательских категорий: {err}')
    finally:
        session.close()
        return posts


async def get_best_categories_posts(user_tg_id) -> list:
    session = Session()
    posts = []
    try:
        query = f'''
        select *
        from (select posts.*, coefficient, counter, channel_username, name, emoji, row_number() over (partition by category_channel_id order by likes desc, dislikes) as row_num
            from category_post posts
            join category_channel cc on posts.category_channel_id = cc.id
            join category c on cc.category_id = c.id
            left join user_viewed_category_post uvcp on posts.id = uvcp.category_post_id and uvcp.user_id = {user_tg_id}
            where (counter is NULL or counter = 0) and (mark_type_id is null or mark_type_id != {MarkTypes.REPORT})
        ) subquery where likes >= dislikes and row_num = 1 order by rand()
        '''

        records = session.execute(text(query))
        for post in records:
            posts.append(post)
    except Exception as err:
        logger.error(f'Ошибка при получении постов из каналов в пользовательских категорий: {err}')
    finally:
        session.close()
        return posts


async def get_categories() -> list[str]:
    session = Session()
    categories = []
    try:
        records = session.query(Category).all()
        for category in records:
            categories.append(f'{category.name} {category.emoji}')
    except Exception as err:
        logger.error(f'Ошибка при получении категорий: {err}')
    finally:
        session.close()
        return categories


async def get_user_categories(user_tg_id: int) -> list[str]:
    session = Session()
    result = []
    try:
        records = session \
            .query(Category) \
            .select_from(User) \
            .join(UserCategory).join(Category) \
            .filter(User.id == user_tg_id)

        user_categories = [record for record in records]
        for category in user_categories:
            result.append(f'{category.name} {category.emoji}')
    except Exception as err:
        logger.error(f'Ошибка при получении пользовательских категорий: {err}')
    finally:
        session.close()
        return result


async def get_viewed_personal_post(user_tg_id: int, post_id: int):
    session = Session()
    personal_post = None
    try:
        query = f'''
                    select mark_type_id, posts.* from personal_post posts
                    join user_viewed_personal_post uvpp on posts.id = uvpp.personal_post_id
                    where user_id = {user_tg_id} and posts.id = {post_id}
                '''

        personal_post = session.execute(text(query)).one()
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на персональный пост пользователя: {err}')
    finally:
        session.close()
        return personal_post


async def get_viewed_premium_post(user_tg_id: int, post_id: int):
    session = Session()
    premium_post = None
    try:
        query = f'''
            select mark_type_id, posts.* from premium_post posts
            join user_viewed_premium_post uvpp on posts.id = uvpp.premium_post_id
            where user_id = {user_tg_id} and posts.id = {post_id}
        '''
        premium_post = session.execute(text(query)).one()
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на премиальный пост пользователя: {err}')
    finally:
        session.close()
        return premium_post


async def get_viewed_category_post(user_tg_id: int, post_id: int):
    session = Session()
    category_post = None
    try:
        query = f'''
                    select mark_type_id, posts.* from category_post posts
                    join user_viewed_category_post uvcp on posts.id = uvcp.category_post_id
                    where user_id = {user_tg_id} and posts.id = {post_id}
                '''

        category_post = session.execute(text(query)).one()
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на пост из категорий пользователя: {err}')
    finally:
        session.close()
        return category_post


async def get_all_premium_channels() -> list[PremiumChannel]:
    session = Session()
    channels = []
    try:
        records = session.query(PremiumChannel).all()
        for channel in records:
            channels.append(channel)
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на пост из категорий пользователя: {err}')
    finally:
        session.close()
        return channels


async def get_all_categories_channels() -> list:
    session = Session()
    categories_channels = []
    try:
        records = session.query(CategoryChannel.channel_username, Category.emoji, Category.name).join(Category,
                                                                                                      CategoryChannel.category_id == Category.id)
        for channel in records:
            categories_channels.append(channel)
    except Exception as err:
        logger.error(f'Ошибка при получении категорий: {err}')
    finally:
        session.close()
        return categories_channels


async def get_all_personal_channels() -> list[PersonalChannel]:
    session = Session()
    channels = []
    try:
        records = session.query(PersonalChannel).all()
        for channel in records:
            channels.append(channel)
    except Exception as err:
        logger.error(f'Ошибка при получении статистики: {err}')
    finally:
        session.close()
        return channels


async def get_category_id(category_name) -> int | None:
    session = Session()
    category_id = None
    try:
        category = session.query(Category).filter(Category.name == category_name).one()
        category_id = category.id
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на пост из категорий пользователя: {err}')
    finally:
        session.close()
        return category_id


async def get_all_channels() -> list:
    session = Session()
    channels = []
    try:
        query = '''
            select id, channel_username from premium_channel
            union select id, channel_username from category_channel
            union select id, channel_username from personal_channel
        '''
        records = session.execute(text(query))

        for channel in records:
            channels.append(channel)

    except Exception as err:
        logger.error(f'Ошибка при получении всех каналов: {err}')
    finally:
        session.close()
        return channels


async def get_coefficients() -> list:
    session = Session()
    coefficients = []
    try:
        records = session.query(Coefficient).filter(Coefficient.value > 1).all()

        for coefficient in records:
            coefficients.append(f'{coefficient.value}X')

    except Exception as err:
        logger.error(f'Ошибка при получении всех коэффициентов: {err}')
    finally:
        session.close()
        return coefficients


async def get_statistic() -> Statistic | None:
    session = Session()
    statistic = None
    try:
        daily_statistic: DailyStatistic = session.query(DailyStatistic).filter(DailyStatistic.date_today == func.current_date()).one()
        total_users = session.query(User.id).count()
        daily_users = session.query(User).filter(cast(User.visited_at, Date) == func.current_date()).count()
        statistic = Statistic(total_users, daily_users, daily_statistic.likes, daily_statistic.dislikes, daily_statistic.new_users_amount)
    except Exception as err:
        logger.error(f'Ошибка при получении статистики: {err}')
    finally:
        session.close()
        return statistic
