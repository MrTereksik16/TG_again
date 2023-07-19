from sqlalchemy import text
from config.logging_config import logger
from database.models import PersonalChannel, Session, User, UserChannel, Category, UserCategory, GeneralChannel, \
    GeneralPost


async def get_user(user_tg_id: int):
    session = Session()
    try:
        user = session.get(User, user_tg_id)
        return user
    except Exception as err:
        logger.error(err)
    finally:
        session.close()


async def get_personal_channel(channel_username: str):
    session = Session()
    try:
        channel = session.query(PersonalChannel).filter(PersonalChannel.username == channel_username).first()
        return channel
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()


async def get_user_channels(user_tg_id: int):
    session = Session()
    try:
        records = session.query(PersonalChannel.username).select_from(User).join(UserChannel).join(
            PersonalChannel).filter(User.user_tg_id == user_tg_id)
        channels = []
        for record in records:
            channels.append(record.username)

        return channels
    except Exception as err:
        logger.error(f'Ошибка при получении списка каналов пользователя: {err}')
    finally:
        session.close()


async def get_general_channel(channel_username: str):
    session = Session()
    try:
        logger.error(channel_username)
        channel = session.query(GeneralChannel).filter(GeneralChannel.username == channel_username).first()
        logger.error(channel)
        return channel
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()


async def get_personal_posts(user_tg_id: int):
    session = Session()
    try:
        query = f'select personal_post.id, personal_channel.username, personal_post.text, personal_post.image_path, personal_post.entities from user join user_channel on user_channel.user_id = user.user_tg_id join personal_post on user_channel.channel_id = personal_post.channel_id join personal_channel on personal_channel.id = user_channel.channel_id where user.user_tg_id = {user_tg_id}'
        records = session.execute(text(query))
        personal_posts = []
        for record in records:
            personal_posts.append(record)
        return personal_posts
    except Exception as err:
        logger.error(f'Ошибка при получении постов из пользовательских каналов: {err}')
    finally:
        session.close()


async def get_general_posts():
    session = Session()
    try:
        posts = session.query(GeneralPost).all()
        all_posts = []
        for post in posts:
            all_posts.append(post)
            general_channel = post.general_channel_connection
            all_posts.extend(general_channel.general_post_connection)
        return all_posts
    except Exception as err:
        logger.error(f'Ошибка при получении общего поста: {err}')
    finally:
        session.close()


async def get_user_last_personal_post_id(user_tg_id: int):
    session = Session()
    try:
        user = session.query(User).get(user_tg_id)
        if user:
            last_post_id = user.last_personal_post_id
            return last_post_id
        else:
            return None
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при получении последнего ID поста пользователя: {err}')
    finally:
        session.close()


async def get_user_last_general_post_id(user_tg_id: int):
    session = Session()
    try:
        user = session.query(User).get(user_tg_id)
        if user:
            last_post_id = user.last_general_post_id
            return last_post_id
        else:
            return None
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при получении последнего ID поста пользователя: {err}')
    finally:
        session.close()


async def get_categories():
    session = Session()
    try:
        categories = session.query(Category).all()
        return [f'{category.id}. {category.name}{category.emoji}' for category in categories]
    except Exception as err:
        logger.error(f'Ошибка при получении категорий: {err}')
    finally:
        session.close()


async def get_user_categories(user_tg_id: int):
    session = Session()
    try:
        records = session.query(Category).select_from(User).join(UserCategory).join(Category).filter(
            User.user_tg_id == user_tg_id)
        user_categories = [record for record in records]
        return [f'<code>{i + 1}. {user_categories[i].name}{user_categories[i].emoji}</code>' for i in
                range(0, len(user_categories))]
    except Exception as err:
        logger.error(f'Ошибка при получении пользовательских категорий: {err}')
        return []
    finally:
        session.close()


async def get_categories_posts(user_tg_id) -> list:
    session = Session()
    try:
        records = session.query(
            GeneralPost.id, GeneralPost.image_path, GeneralPost.text, GeneralChannel.category_id,
            GeneralChannel.username).select_from(User).join(UserCategory, User.user_tg_id == UserCategory.user_id). \
            join(GeneralChannel, UserCategory.category_id == GeneralChannel.category_id). \
            join(GeneralPost, GeneralChannel.id == GeneralPost.general_channel_id).filter(
            User.user_tg_id == user_tg_id).all()
        result = []
        for record in records:
            result.append(record)
        return result
    except Exception as err:
        logger.error(f'Ошибка при получении пользовательских категорий: {err}')
        return []
    finally:
        session.close()


async def get_user_last_category_post_id(user_tg_id, category_id) -> int:
    session = Session()
    try:
        result = session.query(UserCategory.last_post_id).select_from(User).join(UserCategory).filter(
            User.user_tg_id == user_tg_id, UserCategory.category_id == category_id).first()
        return result.last_post_id
    except Exception as err:
        logger.error(f'Ошибка при получении пользовательских категорий: {err}')
        return 0
    finally:
        session.close()
