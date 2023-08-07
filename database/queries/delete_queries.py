from sqlalchemy import select
from config.logging_config import logger
from database.create_db import Session
from database.models import PersonalChannel, UserChannel, UserCategory, PersonalPost, PremiumChannel, Category


async def delete_personal_channel(user_tg_id, channel_username) -> bool:
    session = Session()
    try:
        personal_channel = session.query(PersonalChannel).filter(PersonalChannel.username == channel_username).one()
        session.query(UserChannel).filter(UserChannel.user_id == user_tg_id, UserChannel.channel_id == personal_channel.id).delete()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении канала из списка пользователя:{err}')
        return False
    finally:
        session.close()


async def delete_user_category(user_tg_id, category_id) -> bool:
    session = Session()
    try:
        session.query(UserCategory).filter(UserCategory.user_id == user_tg_id, UserCategory.category_id == category_id).delete()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении категории пользователя: {err}')
        return False
    finally:
        session.close()


async def delete_premium_channel(channel_username: str) -> bool:
    session = Session()
    try:
        result = session.query(PremiumChannel).filter(PremiumChannel.username == channel_username).delete()
        session.commit()
        if result:
            return True
        else:
            return False
    except Exception as err:
        logger.error(f'Ошибка при удалении категории пользователя: {err}')
        return False
    finally:
        session.close()


async def delete_category(category_name: str) -> bool:
    session = Session()
    try:
        session.query(Category).filter(Category.name == category_name).delete()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении категории: {err}')
        return False
    finally:
        session.close()
