from sqlalchemy import text
from config.logging_config import logger
from database.create_db import Session
from database.models import User, PersonalChannel, UserChannel, PremiumChannel, CategoryChannel, UserViewedPremiumPost, Category, UserCategory, \
    UserViewedCategoryPost, UserViewedPersonalPost
from utils.types import MarkTypes


async def get_user(user_tg_id: int):
    session = Session()
    user = None
    try:
        user = session.get(User, user_tg_id)
    except Exception as err:
        logger.error(err)
    finally:
        session.close()
        return user


async def get_personal_channel(channel_username: str):
    session = Session()
    channel = None
    try:
        channel = session.query(PersonalChannel).filter(PersonalChannel.username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()
        return channel


async def get_user_channels(user_tg_id: int):
    session = Session()
    channels = []
    try:
        records = session.query(PersonalChannel.username).select_from(User).join(UserChannel).join(PersonalChannel).filter(User.id == user_tg_id)
        channels = []
        for record in records:
            channels.append(record.username)

    except Exception as err:
        logger.error(f'Ошибка при получении списка каналов пользователя: {err}')
    finally:
        session.close()
        return channels


async def get_premium_channel(channel_username: str):
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


async def get_category_channel(channel_username: str):
    session = Session()
    channel = None
    try:
        channel = session.query(CategoryChannel).filter(CategoryChannel.username == channel_username).one()
    except Exception as err:
        logger.error(f'Ошибка при получении канала из категорий: {err}')
    finally:
        session.close()
        return channel


async def get_personal_posts(user_tg_id: int):
    session = Session()
    personal_posts = []
    try:
        query = f'''
        select posts.*, username, coefficient
        from user join user_channel on user_channel.user_id = user.id
        join personal_post posts on user_channel.channel_id = posts.personal_channel_id and user.id = {user_tg_id}
        join personal_channel on personal_channel.id = user_channel.channel_id
        left join user_viewed_personal_post uvpp on posts.id = uvpp.personal_post_id
        where uvpp.user_id is NULL
        group by channel_id
        '''

        records = session.execute(text(query))
        personal_posts = []
        for record in records:
            personal_posts.append(record)
    except Exception as err:
        logger.error(f'Ошибка при получении постов из пользовательских каналов: {err}')
    finally:
        session.close()
        return personal_posts


async def get_best_not_viewed_premium_posts(user_tg_id):
    session = Session()
    posts = []
    try:
        query = f'''
                select posts.*, coefficient, username from premium_post posts
                join premium_channel rc on rc.id = posts.premium_channel_id
                left join user_viewed_premium_post uvrp on posts.id = uvrp.premium_post_id and uvrp.user_id = {user_tg_id}
                where user_id is NULL
                group by premium_channel_id
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
                       uc.user_id,
                       name,
                       emoji,
                       ROW_NUMBER() over (partition by category_channel_id order by likes desc ) as row_num
                from category_post posts
                join category_channel cc on posts.category_channel_id = cc.id
                join category c on cc.category_id = c.id
                join user_category uc on cc.category_id = uc.category_id and uc.user_id = 1659612474
                left join user_viewed_category_post uvcp on posts.id = uvcp.category_post_id
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


async def get_categories():
    session = Session()
    categories = []
    try:
        records = session.query(Category).all()
        categories = [f'{category.id}. {category.name}{category.emoji}' for category in records]
    except Exception as err:
        logger.error(f'Ошибка при получении категорий: {err}')
    finally:
        session.close()
        return categories


async def get_user_categories(user_tg_id: int):
    session = Session()
    result = []
    try:
        records = session \
            .query(Category) \
            .select_from(User) \
            .join(UserCategory).join(Category) \
            .filter(User.id == user_tg_id)

        user_categories = [record for record in records]
        result = [f'<code>{i + 1}. {user_categories[i].name}{user_categories[i].emoji}</code>' for i in
                  range(0, len(user_categories))]
    except Exception as err:
        logger.error(f'Ошибка при получении пользовательских категорий: {err}')
    finally:
        session.close()
        return result


async def get_categories_channels():
    session = Session()
    channels = []
    try:
        records = session.query(CategoryChannel).all()
        for channel in records:
            channels.append(channel)
    except Exception as err:
        logger.error(f'Ошибка при получении всех каналов из категорий: {err}')
    finally:
        session.close()
        return channels


async def get_viewed_personal_post_mark_type(post_id: int):
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


async def get_viewed_premium_post_mark_type(post_id: int):
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


async def get_viewed_category_post_mark_type(post_id: int):
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
