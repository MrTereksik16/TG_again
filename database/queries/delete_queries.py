from sqlalchemy import select

from config.logging_config import logger
from database.models import Session, PersonalChannel, UserChannel, UserCategory


async def delete_personal_channel(username):
    session = Session()
    try:
        personal_channel_id = \
            session.execute(select(PersonalChannel.id).where(PersonalChannel.username == username)).fetchone()[0]
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


async def delete_user_category(user_tg_id, category_id):
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
