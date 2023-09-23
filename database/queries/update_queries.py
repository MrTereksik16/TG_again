from config.logging_config import logger
from sqlalchemy import text, func
from database.create_db import Session
from database.models import CategoryPost, PremiumPost, PersonalPost, Category
from utils.custom_types import MarkTypes


async def update_viewed_personal_post_mark_type(user_tg_id: int, post_id: int, mark_type_id: MarkTypes):
    session = Session()
    try:
        query = f'update user_viewed_personal_post set mark_type_id = {mark_type_id} where user_id = {user_tg_id} and personal_post_id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на персональный пост: {err}')
    finally:
        session.close()


async def update_viewed_premium_post_mark_type(user_tg_id: int, post_id: int, mark_type_id: MarkTypes):
    session = Session()
    try:
        query = f'update user_viewed_premium_post set mark_type_id = {mark_type_id} where user_id = {user_tg_id} and premium_post_id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на премиальный пост: {err}')
    finally:
        session.close()


async def update_viewed_category_post_mark_type(user_tg_id: int, post_id: int, mark_type_id: MarkTypes):
    session = Session()
    try:
        query = f'update user_viewed_category_post set mark_type_id = {mark_type_id} where user_id = {user_tg_id} and category_post_id = {post_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_personal_post_likes(post_id: int, increment: bool = True):
    session = Session()
    try:
        post = session.query(PersonalPost).filter_by(id=post_id).one()
        if increment:
            post.likes += 1
        else:
            post.likes -= 1
        session.commit()
        return post.likes
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_premium_post_likes(post_id: int, increment: bool = True):
    session = Session()
    try:
        post = session.query(PremiumPost).filter_by(id=post_id).one()
        if increment:
            post.likes += 1
        else:
            post.likes -= 1
        session.commit()
        return post.likes
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_category_post_likes(post_id: int, increment: bool = True):
    session = Session()
    try:
        post = session.query(CategoryPost).filter_by(id=post_id).one()
        if increment:
            post.likes += 1
        else:
            post.likes -= 1
        session.commit()
        return post.likes
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_personal_post_dislikes(post_id: int, increment: bool = True):
    session = Session()
    try:
        post = session.query(PersonalPost).filter_by(id=post_id).one()
        if increment:
            post.dislikes += 1
        else:
            post.dislikes -= 1
        session.commit()
        return post.dislikes
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_premium_post_dislikes(post_id: int, increment: bool = True):
    session = Session()
    try:
        post = session.query(PremiumPost).filter_by(id=post_id).one()
        if increment:
            post.dislikes += 1
        else:
            post.dislikes -= 1
        session.commit()
        return post.dislikes
    except Exception as err:
        logger.error(f'Ошибка при обновлении типа реакции пользователя на пост из категорий: {err}')
    finally:
        session.close()


async def update_category_post_dislikes(post_id: int, increment: bool = True):
    session = Session()
    try:
        post = session.query(CategoryPost).filter_by(id=post_id).one()
        if increment:
            post.dislikes += 1
        else:
            post.dislikes -= 1
        session.commit()
        return post.dislikes
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


async def update_user_mode(user_tg_id: int, mode: int):
    session = Session()
    try:
        query = f'update user set mode = {mode} where id = {user_tg_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении мода пользователя с id={user_tg_id}: {err}')
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


async def update_last_visit_time(user_tg_id: int):
    session = Session()
    try:
        query = f'update user set visited_at = NOW() where id={user_tg_id}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении времени последнего посещения пользователя: {err}')
    finally:
        session.close()


async def update_users_views_per_day(user_tg_id: int = None, views_amount: int = 1, reset: bool = False):
    session = Session()
    try:
        query = f'update user set views_per_day = views_per_day + {views_amount} where id={user_tg_id}'
        if reset:
            query = f'update user set views_per_day = 0 where id'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении числа просмотренных пользователем за день постов: {err}')
    finally:
        session.close()


async def update_daily_new_users_amount():
    session = Session()
    try:
        query = f'update daily_statistic set new_users_amount = new_users_amount + 1 where date_today = {func.current_date()}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении числа новых пользователей за день: {err}')
    finally:
        session.close()


async def update_daily_likes(increment: bool = True):
    session = Session()
    try:
        query = f'update daily_statistic set likes = likes + 1 where date_today = {func.current_date()}'
        if not increment:
            query = f'update daily_statistic set likes = likes - 1 where date_today = {func.current_date()}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении числа лайков за день: {err}')
    finally:
        session.close()


async def update_daily_dislikes(increment: bool = True):
    session = Session()
    try:
        query = f'update daily_statistic set dislikes = dislikes + 1 where date_today = {func.current_date()}'
        if not increment:
            query = f'update daily_statistic set dislikes = dislikes - 1 where date_today = {func.current_date()}'

        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении числа дизалйков за день: {err}')
    finally:
        session.close()


async def update_daily_views(views_amount: int = 1):
    session = Session()
    try:
        query = f'update daily_statistic set views = views + {views_amount} where date_today = {func.current_date()}'
        session.execute(text(query))
        session.commit()
    except Exception as err:
        logger.error(f'Ошибка при обновлении числа просмотров за день: {err}')
    finally:
        session.close()


async def update_category(old_category_name: str, new_category_name: str, new_category_emoji: str = None) -> bool:
    session = Session()
    try:
        category = session.query(Category).filter(Category.name == old_category_name).one()
        category.name = new_category_name
        if new_category_emoji:
            category.emoji = new_category_emoji

        session.commit()
        return category.name == new_category_name
    except Exception as err:
        logger.error(f'Ошибка при обновлении имени категории: {err}')
        return False
    finally:
        session.close()
