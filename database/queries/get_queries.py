from config.logging_config import logger
from database.models import PersonalChannel, Session, User, UserChannel, GeneralChannel, GeneralPost

async def get_user(user_tg_id):
    session = Session()
    try:
        user = session.get(User, user_tg_id)
        return user
    except Exception as err:
        logger.error(err)
    finally:
        session.close()


async def get_personal_channel(channel_name):
    session = Session()
    try:
        channel = session.query(PersonalChannel).filter(PersonalChannel.username == channel_name).first()

        return channel
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()


async def get_user_channels(user_tg_id):
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



async def get_general_channel(channel_name):
    session = Session()
    try:
        channel = session.query(GeneralChannel).filter(GeneralChannel.username == channel_name).first()

        return channel
    except Exception as err:
        logger.error(f'Ошибка при получении канала пользователя: {err}')
    finally:
        session.close()


# Надо допилить
async def get_personal_posts(user_id):
    session = Session()
    try:
        user_channels = session.query(UserChannel).filter_by(user_id=user_id).all()
        personal_posts = []

        for user_channel in user_channels:
            channel = user_channel.personal_channel_connection
            personal_posts.extend(channel.personal_post_connection)

        return personal_posts

    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при получении постов из пользовательских каналов: {err}')

async def get_general_post():
    session = Session()
    try:
        general_posts = session.query(GeneralPost).all()
        all_posts = []

        for post in general_posts:
            all_posts.append(post)

            general_channel = post.general_channel_connection
            all_posts.extend(general_channel.general_post_connection)

        return all_posts

    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при получении общего поста: {err}')





async def get_user_last_post_id(user_id):
    session = Session()
    try:
        user = session.query(User).get(user_id)
        if user:
            last_post_id = user.last_post_id
            return last_post_id
        else:
            return None
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при получении последнего ID поста пользователя: {err}')
