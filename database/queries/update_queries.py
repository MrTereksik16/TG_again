from config.logging_config import logger
from database.models import Session, User


async def update_user_last_post_id(user_id, post_id):
    session = Session()
    try:
        user = session.query(User).get(user_id)
        if user:
            user.last_post_id = post_id
            session.commit()
    except Exception as err:
        session.rollback()
        logger.error(f'Ошибка при обновление пользовательского последнего ID поста: {err}')
