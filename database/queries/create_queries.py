from telethon.tl.types import Channel

from config.logging_config import logger
from database.models import Session, GeneralChannel, UserChannel, User, PersonalPost, PersonalChannel, GeneralPost


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
    session = Session()
    try:
        username = channel_tg_entity.username
        new_general_channel = GeneralChannel(username=username)
        session.add(new_general_channel)
        session.flush()
        # channel_id = new_general_channel.id
        # session.add(GeneralChannel(user_id=user_tg_id, channel_id=channel_id))
        # session.flush()
        session.commit()
        return True
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        if 'Duplicate entry' in str(err):
            return 'duplicate_entry'
        return False


async def create_personal_post(data):
    session = Session()
    try:
        for info in data:
            personal_post = PersonalPost(text=info['text'], image_path=info['media_id'], channel_id=info['channel_id'])
            session.add(personal_post)
            session.flush()
        session.commit()
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при добавлении пользовательского поста: {err}')


async def create_general_post(data):
    session = Session()
    try:
        for info in data:
            general_post = GeneralPost(text=info['text'], image_path=info['media_id'], likes=1, dislikes=1, general_channel_id=info['channel_id'])
            session.add(general_post)
            session.flush()
        session.commit()
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при добавлении общего поста: {err}')
