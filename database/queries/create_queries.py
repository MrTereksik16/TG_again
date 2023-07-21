from aiogram.types import Message

from create_bot import bot, bot_client
from utils.consts import errors
from config.logging_config import logger
from database.models import Session, GeneralChannel, UserChannel, User, PersonalPost, PersonalChannel, UserCategory, \
    GeneralPost
from keyboards import personal_reply_keyboards, admin_reply_keyboards


async def create_user(user_tg_id: int):
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


async def create_user_channel(user_tg_id: int, channel_username: str):
    session = Session()
    try:
        personal_channel = session.query(PersonalChannel).filter_by(username=channel_username).first()
        session.flush()

        if not personal_channel:
            personal_channel = PersonalChannel(username=channel_username)
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


async def create_general_channel(channel_username: str, category_id: int):
    session = Session()
    try:
        new_general_channel = GeneralChannel(username=channel_username, category_id=category_id)
        session.add(new_general_channel)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении общего канала: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_personal_post(data: list[dict]):
    session = Session()
    keyboard = personal_reply_keyboards.personal_start_control_keyboard

    channel_username = data[0]['channel_username']
    chat_id = data[0]['chat_id']

    try:

        for info in data:
            entities = info['entities']
            text = info['text']
            image_path = info['media_path']
            channel_id = info['channel_id']
            personal_post = PersonalPost(text=text, image_path=image_path, channel_id=channel_id, entities=entities)
            session.add(personal_post)
            session.flush()
        session.commit()
        await bot_client.send_message(chat_id, f'Посты с канала {channel_username} получены 👍',
                                      reply_markup=keyboard)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}',
                                      reply_markup=keyboard)
        logger.error(f'Ошибка при добавлении пользовательского поста: {err}')
        return False
    finally:
        session.close()


async def create_general_post(data: list[dict]):
    session = Session()
    keyboard = admin_reply_keyboards.admin_panel_control_keyboard

    channel_username = data[0]['channel_username']
    chat_id = data[0]['chat_id']

    try:
        for info in data:
            entities = info['entities']
            text = info['text']
            image_path = info['media_path']
            channel_id = info['channel_id']

            general_post = GeneralPost(text=text, image_path=image_path, likes=0, dislikes=0,
                                       general_channel_id=channel_id, entities=entities)
            session.add(general_post)
            session.flush()
        session.commit()
        await bot_client.send_message(chat_id, f'Посты с канала {channel_username} получены 👍',
                                      reply_markup=keyboard)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}',
                                      reply_markup=keyboard)
        logger.error(f'Ошибка при добавлении общего поста: {err}')
        return False
    finally:
        session.close()


async def create_user_category(user_tg_id: int, category_id: int):
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
