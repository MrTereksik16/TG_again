from sqlalchemy.exc import NoResultFound

from create_bot import bot_client
from utils.consts import errors
from config.logging_config import logger
from database.models import Session, UserChannel, User, PersonalPost, PersonalChannel, UserCategory, \
    PremiumPost, CategoryChannel, PremiumChannel, CategoryPost, UserViewedPremiumPost, \
    UserViewedCategoryPost, UserViewedPersonalPost
from keyboards import personal_reply_keyboards, admin_reply_keyboards


async def create_user(user_tg_id: int):
    session = Session()
    try:
        user = User(id=user_tg_id)
        session.add(user)
        session.commit()
        return True
    except Exception as err:
        logger.error(err)
        return False
    finally:
        session.close()


async def create_personal_channel(user_tg_id: int, channel_tg_id: int, channel_username: str):
    session = Session()
    try:
        personal_channel = session.query(PersonalChannel).filter(PersonalChannel.username == channel_username).one()
    except NoResultFound:
        personal_channel = PersonalChannel(username=channel_username, tg_id=channel_tg_id)
        session.add(personal_channel)
        session.flush()
    except Exception as err:
        session.close()
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        return False

    try:
        channel_id = personal_channel.id
        session.add(UserChannel(user_id=user_tg_id, channel_id=channel_id))
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при связывании канала с пользователем: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_category_channel(channel_tg_id: int, channel_username: str, category_id: int):
    session = Session()
    try:
        new_category_channel = CategoryChannel(username=channel_username, tg_id=channel_tg_id, category_id=category_id)
        session.add(new_category_channel)
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
            personal_post = PersonalPost(text=text, image_path=image_path, personal_channel_id=channel_id, entities=entities)
            session.add(personal_post)
            session.flush()
        session.commit()
        await bot_client.send_message(chat_id, f'Посты с канала {channel_username} получены 👍', reply_markup=keyboard)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}', reply_markup=keyboard)
        logger.error(f'Ошибка при добавлении пользовательского поста: {err}')
        return False
    finally:
        session.close()


async def create_recommendation_post(data: list[dict]):
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

            recommendation_post = PremiumPost(text=text, image_path=image_path, likes=0, dislikes=0, premium_channel_id=channel_id, entities=entities)
            session.add(recommendation_post)
            session.flush()
        session.commit()
        await bot_client.send_message(chat_id, f'Посты с канала {channel_username} получены 👍', reply_markup=keyboard)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}', reply_markup=keyboard)
        logger.error(f'Ошибка при добавлении общего поста: {err}')
        return False
    finally:
        session.close()


async def create_category_post(data: list[dict]):
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

            category_post = CategoryPost(text=text, image_path=image_path, likes=0, dislikes=0, category_channel_id=channel_id, entities=entities)
            session.add(category_post)
            session.flush()
        session.commit()
        await bot_client.send_message(chat_id, f'Посты с канала {channel_username} получены 👍', reply_markup=keyboard)
        return True
    except Exception as err:
        await bot_client.send_message(chat_id, f'Не удалось получить посты с канала {channel_username}', reply_markup=keyboard)
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


async def create_recommendation_channel(channel_tg_id: int, channel_username: str):
    session = Session()
    try:
        new_recommendation_channel = PremiumChannel(username=channel_username, tg_id=channel_tg_id)
        session.add(new_recommendation_channel)
        session.commit()
        return True
    except Exception as err:
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        logger.error(f'Ошибка при добавлении канала в рекомендации: {err}')
        return False
    finally:
        session.close()


async def create_user_viewed_premium_post(user_tg_id, post_id):
    session = Session()
    try:
        new_user_premium_post = UserViewedPremiumPost(user_id=user_tg_id, premium_post_id=post_id)
        session.add(new_user_premium_post)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении канала в просмотренные: {err}')
        return False
    finally:
        session.close()


async def create_user_viewed_category_post(user_tg_id, post_id):
    session = Session()
    try:
        new_user_category_post = UserViewedCategoryPost(user_id=user_tg_id, category_post_id=post_id)
        session.add(new_user_category_post)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении канала в просмотренные: {err}')
        return False
    finally:
        session.close()


async def create_user_viewed_personal_post(user_tg_id, post_id):
    session = Session()
    try:
        new_user_personal_post = UserViewedPersonalPost(user_id=user_tg_id, personal_post_id=post_id)
        session.add(new_user_personal_post)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении канала в просмотренные: {err}')
        return False
    finally:
        session.close()
