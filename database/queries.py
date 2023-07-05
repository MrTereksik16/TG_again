from sqlalchemy import select
from telethon.tl.types import Channel

from database.models import Personal_Channels, session, User_Channels, User
from logging_config import logger


# Session = sessionmaker(bind=engine)
# session = Session()

async def create_user_channel(user_tg_id, channel_tg_entity: Channel):
    try:
        username = channel_tg_entity.username
        new_personal_channel = Personal_Channels(username=username)
        session.add(new_personal_channel)
        session.flush()
        channel_id = new_personal_channel.id
        session.add(User_Channels(user_id=user_tg_id, channel_id=channel_id))
        session.flush()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        if 'Duplicate entry' in str(err):
            return 'duplicate_entry'
        return False


async def get_user(user_tg_id):
    try:
        user = session.get(User, user_tg_id)
        return user
    except Exception as err:
        logger.error(err)


async def create_user(user_tg_id):
    try:
        user = User(user_tg_id=user_tg_id)
        session.add(user)
        session.flush()
        return user.user_tg_id
    except Exception as err:
        logger.error(err)


async def get_user_personal_channels(user_tg_id):
    try:
        records = session.query(Personal_Channels.username).select_from(User).join(User_Channels).join(Personal_Channels).filter(User.user_tg_id == user_tg_id)
        channels = []
        for record in records:
            channels.append(record.username)

        return channels
    except Exception as err:
        logger.error(f'Ошибка при получении списка каналов пользователя: {err}')
