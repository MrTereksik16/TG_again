from sqlalchemy import select
from telethon.tl.types import Channel
import pandas as pd
from database.models import PersonalChannel, UserChannel, User, session, GeneralChannel, PersonalPost

from database.models import PersonalChannel, UserChannel, User, Session
from config.logging_config import logger

# df = pd.read_csv('data.csv')


async def create_user(user_tg_id, last_post_id):
    session = Session()
    try:
        user = User(user_tg_id=user_tg_id, last_post_id=last_post_id)
        session.add(user)
        session.commit()
        return True
    except Exception as err:
        logger.error(err)
        return False
    finally:
        session.close()


async def create_user_channel(user_tg_id, channel_tg_entity: Channel):
    session = Session()
    try:
        username = channel_tg_entity.username
        new_personal_channel = PersonalChannel(username=username)
        session.add(new_personal_channel)
        session.flush()
        channel_id = new_personal_channel.id
        session.add(UserChannel(user_id=user_tg_id, channel_id=channel_id))
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        if 'Duplicate entry' in str(err):
            return 'duplicate_entry'
        return False
    finally:
        session.close()

async def create_general_channel_by_admin(user_tg_id, channel_tg_entity: Channel):
    try:
        username = channel_tg_entity.username
        new_general_channel = GeneralChannel(username=username)
        session.add(new_general_channel)
        session.flush()
        channel_id = new_general_channel.id
        session.add(UserChannel(user_id=user_tg_id, channel_id=channel_id))
        session.flush()
        session.commit()
        return True
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        if 'Duplicate entry' in str(err):
            return 'duplicate_entry'
        return False

async def get_user(user_tg_id):
    session = Session()
    try:
        user = session.get(User, user_tg_id)
        return user
    except Exception as err:
        logger.error(err)
    finally:
        session.close()


async def get_user_personal_channels(user_tg_id):
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


async def delete_personal_channel(username):
    session = Session()
    try:
        personal_channel_id = session.execute(select(PersonalChannel.id).where(PersonalChannel.username == username)).fetchone()[0]
        session.query(UserChannel).filter(UserChannel.channel_id == personal_channel_id).delete()
        session.flush()
        session.query(PersonalChannel).filter(PersonalChannel.id == personal_channel_id).delete()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении канала из списка пользователя:{err}')
        return False

async def add_personal_post(data):
    try:

        for info in data:
            personal_post = PersonalPost(text=info['text'], image_path=info['media_id'], channel_id=info['channel_id'])
            session.add(personal_post)
            session.flush()
        session.commit()


    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')

async def send_post_for_user_lenta(user_id):
    try:
        user_channels = session.query(UserChannel).filter_by(user_id=user_id).all()
        personal_posts = []

        for user_channel in user_channels:
            channel = user_channel.personal_channel_connection
            personal_posts.extend(channel.personal_post_connection)

        return personal_posts

    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при отправлении пользовательского поста: {err}')



async def get_last_post_id(user_id):
    try:
        user = session.query(User).get(user_id)
        if user:
            last_post_id = user.last_post_id
            return last_post_id
        else:
            return None
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при получении пользовательского последнего ID поста: {err}')

async def update_last_post_id(user_id, post_id):
    try:
        user = session.query(User).get(user_id)
        if user:
            user.last_post_id = post_id
            session.commit()
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при обновление пользовательского последнего ID поста: {err}')

