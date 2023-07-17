from aiogram.types import Message
from telethon.tl.types import Channel

from create_bot import bot
from utils.consts import errors
from config.logging_config import logger
from database.models import Session, GeneralChannel, UserChannel, User, PersonalPost, PersonalChannel, UserCategory, \
    GeneralPost


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


async def create_user_channel(user_tg_id, username):
    session = Session()
    try:
        personal_channel = session.query(PersonalChannel).filter_by(username=username).first()
        session.flush()

        if not personal_channel:
            personal_channel = PersonalChannel(username=username)
            session.add(personal_channel)
            session.flush()

        channel_id = personal_channel.id
        session.add(UserChannel(user_id=user_tg_id, channel_id=channel_id))
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_general_channel_by_admin(user_tg_id, channel_tg_entity):
    session = Session()
    try:
        username = channel_tg_entity.username
        new_general_channel = GeneralChannel(username=username)
        session.add(new_general_channel)
        session.flush()
        # channel_id = new_general_channel.id
        # session.add(GeneralChannel(user_id=user_tg_id, channel_id=channel_id))
        # session.flush()
        # channel_id = new_general_channel.id
        # session.add(UserChannel(user_id=user_tg_id, channel_id=channel_id))

        channel_id = new_general_channel.id
        session.add(UserChannel(user_id=user_tg_id, channel_id=channel_id))
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении общего канала: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_personal_post(data):
    session = Session()
    try:
        status_message_id = data[0]['status_message_id']
        chat_id = data[0]['chat_id']
        channel_name = data[0]['channel_name']
        for info in data:
            personal_post = PersonalPost(text=info['text'], image_path=info['media_id'], entities='hsbefhjbsef', channel_id=info['channel_id'])
            session.add(personal_post)
            print(info)
            session.flush()
        session.commit()
        await bot.edit_message_text(f'Посты с канала @{channel_name} получены 👍', chat_id, status_message_id)

        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении пользовательского поста: {err}')
        return False
    finally:
        session.close()

async def create_general_post(data):
    session = Session()
    try:
        for info in data:
            general_post = GeneralPost(text=info['text'], image_path=info['media_id'], likes=1, dislikes=1,
                                       general_channel_id=info['channel_id'])
            session.add(general_post)
            session.flush()
        session.commit()
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при добавлении общего поста: {err}')
    finally:
        session.close()


async def create_user_category(user_tg_id, category_id: int):
    session = Session()
    try:
        new_user_category = UserCategory(user_id=user_tg_id, category_id=category_id)
        session.add(new_user_category)
        session.commit()
        return True
    except Exception as err:
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        logger.error(f'Ошибка при добавлении категории пользователю: {err}')
        return False
    finally:
        session.close()
