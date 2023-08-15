from config.logging_config import logger
from sqlalchemy import text
from database.create_db import Session
from utils.custom_types import MarkTypes


async def update_viewed_personal_post_mark_type(user_tg_id: int, post_id: int, mark_type: MarkTypes):
    session = Session()
    try:
        query = f'update user_viewed_personal_post set mark_type_id = {mark_type} where user_id = {user_tg_id} and personal_post_id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на персональный пост: {err}')
    finally:
        session.close()


async def update_viewed_premium_post_mark_type(user_tg_id: int, post_id: int, mark_type: MarkTypes):
    session = Session()
    try:
        query = f'update user_viewed_premium_post set mark_type_id = {mark_type} where user_id = {user_tg_id} and premium_post_id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на премиальный пост: {err}')
    finally:
        session.close()


async def update_viewed_category_post_mark_type(user_tg_id: int, post_id: int, mark_type: MarkTypes):
    session = Session()
    try:
        query = f'update user_viewed_category_post set mark_type_id = {mark_type} where user_id = {user_tg_id} and category_post_id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_personal_post_likes(post_id, increment: bool = True):
    session = Session()
    try:
        query = f'update personal_post set likes = likes + 1 where id = {post_id}'
        if not increment:
            query = f'update personal_post set likes = likes - 1 where id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_premium_post_likes(post_id, increment: bool = True):
    session = Session()
    try:
        query = f'update premium_post set likes = likes + 1 where id = {post_id}'
        if not increment:
            query = f'update premium_post set likes = likes - 1 where id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_category_post_likes(post_id, increment: bool = True):
    session = Session()
    try:
        query = f'update category_post set likes = likes + 1 where id = {post_id}'

        if not increment:
            query = f'update category_post set likes = likes - 1 where id = {post_id}'

        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_personal_post_dislikes(post_id, increment: bool = True):
    session = Session()
    try:
        query = f'update personal_post set dislikes = dislikes + 1 where id = {post_id}'

        if not increment:
            query = f'update personal_post set dislikes = dislikes - 1 where id = {post_id}'

        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_premium_post_dislikes(post_id, increment: bool = True):
    session = Session()
    try:
        query = f'update premium_post set dislikes = dislikes + 1 where id = {post_id}'

        if not increment:
            query = f'update premium_post set dislikes = dislikes - 1 where id = {post_id}'

        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_category_post_dislikes(post_id, increment: bool = True):
    session = Session()
    try:
        query = f'update category_post set dislikes = dislikes + 1 where id = {post_id}'

        if not increment:
            query = f'update category_post set dislikes = dislikes - 1 where id = {post_id}'

        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_user_viewed_premium_posts_counters(user_tg_id: int):
    session = Session()
    try:
        query = f'update user_viewed_premium_post set counter = if(counter > 0, counter - 1, 0) where user_id = {user_tg_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного премиального поста: {err}')
    finally:
        session.close()


async def update_user_viewed_category_posts_counters(user_tg_id: int):
    session = Session()
    try:
        query = f'update user_viewed_category_post set counter = if(counter > 0, counter - 1, 0) where user_id = {user_tg_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_user_viewed_premium_post_counter(user_tg_id: int, post_id: int, counter_value: int = 15):
    session = Session()
    try:
        query = f'update user_viewed_premium_post set counter = {counter_value} where user_id = {user_tg_id} and premium_post_id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_user_viewed_category_post_counter(user_tg_id: int, post_id: int, counter_value: int = 15):
    session = Session()
    try:
        query = f'update user_viewed_category_post set counter = {counter_value} where user_id = {user_tg_id} and category_post_id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_premium_channel_post_reports(post_id: int):
    session = Session()
    try:
        query = f'update premium_post set reports = reports + 1 where id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_category_channel_post_reports(post_id: int):
    session = Session()
    try:
        query = f'update category_post set reports = reports + 1 where id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_personal_channel_post_reports(post_id: int):
    session = Session()
    try:
        query = f'update personal_post set reports = reports + 1 where id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_premium_channel_post_report_message_id(post_id: int, report_message_id: int):
    session = Session()
    try:
        query = f'update premium_post set report_message_id = {report_message_id} where id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_category_channel_post_report_message_id(post_id: int, report_message_id: int):
    session = Session()
    try:
        query = f'update category_post set report_message_id = {report_message_id} where id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()


async def update_personal_channel_post_report_message_id(post_id: int, report_message_id: int):
    session = Session()
    try:
        query = f'update personal_post set report_message_id = {report_message_id} where id={post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении счётчика просмотренного поста из категорий: {err}')
    finally:
        session.close()
