from config.logging_config import logger
from database.models import Session, User, UserCategory


async def update_user_last_personal_post_id(user_tg_id, post_id):
    session = Session()
    try:
        user = session.query(User).get(user_tg_id)
        if user:
            user.last_personal_post_id = post_id
            session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновление ID персонального поста пользователя: {err}')
    finally:
        session.close()


async def update_user_last_general_post_id(user_tg_id, post_id):
    session = Session()
    try:
        user = session.query(User).get(user_tg_id)
        if user:
            user.last_general_post_id = post_id
            session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновление ID общего поста пользователя: {err}')
    finally:
        session.close()


async def update_user_last_category_post_id(user_tg_id, category_id, post_id):
    session = Session()
    try:
        session.query(UserCategory).filter(UserCategory.user_id == user_tg_id, UserCategory.category_id == category_id).update({'last_post_id': post_id})
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновление ID поста из категорий пользователя: {err}')
    finally:
        session.close()

