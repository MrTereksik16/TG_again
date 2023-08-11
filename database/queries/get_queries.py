from sqlalchemy import text
from config.logging_config import logger
from database.create_db import Session
from database.models import User, PersonalChannel, UserChannel, PremiumChannel, CategoryChannel, UserViewedPremiumPost, Category, UserCategory, \
    UserViewedCategoryPost, UserViewedPersonalPost, PersonalPost, PremiumPost, CategoryPost, Coefficient
from utils.custom_types import MarkTypes


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
        channel = session.query(PersonalChannel).filter(PersonalChannel.username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()
        return channel


async def get_user_channels_usernames(user_tg_id: int) -> list[str]:
    session = Session()
    channels = []
    try:
        records = session.query(PersonalChannel).select_from(User).join(UserChannel).join(PersonalChannel).filter(User.id == user_tg_id)
        channels = []
        for channel in records:
            channels.append(channel.username)

    except Exception as err:
        logger.error(f'Ошибка при получении списка каналов пользователя: {err}')
    finally:
        session.close()
        return channels


async def get_premium_channel(channel_username: str) -> PremiumChannel:
    session = Session()
    channel = None
    try:
        channel = session.query(PremiumChannel).filter(
            PremiumChannel.username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении общего канала канала: {err}')
    finally:
        session.close()
        return channel


async def get_category_channel(channel_username: str) -> CategoryChannel:
    session = Session()
    channel = None
    try:
        channel = session.query(CategoryChannel).filter(CategoryChannel.username == channel_username).one()
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
        select posts.*, username, coefficient
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


async def get_premium_channel_posts(channel_id: int):
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
        logger.error(f'Ошибка при получении постов из премиального канала: {err}')
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
                select posts.*, coefficient, username, row_number() over (partition by premium_channel_id order by rand()) as row_num from premium_post posts
                join premium_channel rc on rc.id = posts.premium_channel_id
            ) as p where row_num = 1
            '''

        records = session.execute(text(query))

        for post in records:
            posts.append(post)

    except Exception as err:
        logger.error(f'Ошибка при получении общего поста: {err}')
    finally:
        session.close()
        return posts


async def get_best_not_viewed_categories_posts(user_tg_id) -> list:
    session = Session()
    posts = []
    try:
        query = f'''
            select *
            from (
                select posts.*,
                       coefficient,
                       username,
                       name,
                       emoji,
                       row_number() over (partition by category_channel_id order by likes desc ) as row_num
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
            from (
                select posts.*,
                       coefficient,
                       username,
                       name,
                       emoji,
                       row_number() over (partition by category_channel_id order by likes desc ) as row_num
                from category_post posts
                join category_channel cc on posts.category_channel_id = cc.id
                join category c on cc.category_id = c.id
                join user_category uc on cc.category_id = uc.category_id and uc.user_id = {user_tg_id}
                left join user_viewed_category_post uvcp on posts.id = uvcp.category_post_id
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


async def get_viewed_personal_post_mark_type(post_id: int) -> MarkTypes | None:
    session = Session()
    mark_type = None
    try:
        post = session.query(UserViewedPersonalPost).filter(UserViewedPersonalPost.personal_post_id == post_id).one()
        mark_type = MarkTypes(post.mark_type_id)
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на персональный пост пользователя: {err}')
    finally:
        session.close()
        return mark_type


async def get_viewed_premium_post_mark_type(post_id: int) -> MarkTypes | None:
    session = Session()
    mark_type = None
    try:
        post = session.query(UserViewedPremiumPost.mark_type_id).filter(UserViewedPremiumPost.premium_post_id == post_id).one()
        mark_type = MarkTypes(post.mark_type_id)
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на премиальный пост пользователя: {err}')
    finally:
        session.close()
        return mark_type


async def get_viewed_category_post_mark_type(post_id: int) -> MarkTypes | None:
    session = Session()
    mark_type = None
    try:
        post = session.query(UserViewedCategoryPost.mark_type_id).filter(UserViewedCategoryPost.category_post_id == post_id).one()
        mark_type = MarkTypes(post.mark_type_id)
    except Exception as err:
        logger.error(f'Ошибка при получении реакции на пост из категорий пользователя: {err}')
    finally:
        session.close()
        return mark_type


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
        records = session.query(CategoryChannel.username, Category.emoji, Category.name).join(Category, CategoryChannel.category_id == Category.id)
        for channel in records:
            categories_channels.append(channel)
    except Exception as err:
        logger.error(f'Ошибка при получении категорий: {err}')
    finally:
        session.close()
        return categories_channels


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


async def get_all_channels_ids() -> list:
    session = Session()
    channels_ids = []
    try:
        query = '''
            select id from premium_channel
            union select id from category_channel
            union select id from personal_channel
        '''
        channels = session.execute(text(query))

        for channel_id in channels:
            channels_ids.append(channel_id.id)

    except Exception as err:
        logger.error(f'Ошибка при получении id всех каналов: {err}')
    finally:
        session.close()
        return channels_ids


async def get_coefficients() -> list:
    session = Session()
    coefficients = []
    try:
        records = session.query(Coefficient).filter(Coefficient.value > 1).all()

        for coefficient in records:
            coefficients.append(coefficient.value)

    except Exception as err:
        logger.error(f'Ошибка при получении всех коэффициентов: {err}')
    finally:
        session.close()
        return coefficients
