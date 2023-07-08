from sqlalchemy import select
from telethon.tl.types import Channel

from database.models import PersonalChannel, UserChannel, User, Session
from config.logging_config import logger


async def create_user(user_tg_id):
    session = Session()
    try:
        user = User(user_tg_id=user_tg_id)
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
    finally:
        session.close()
