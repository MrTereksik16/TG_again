from config.logging_config import logger
from database.create_db import Session
from database.models import PersonalChannel, UserChannel, UserCategory, PersonalPost, PremiumChannel, Category, PremiumPost, CategoryPost, \
    CategoryChannel, Coefficient


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


async def delete_category_channel(channel_username: str) -> bool:
    session = Session()
    try:
        result = session \
            .query(CategoryChannel) \
            .filter(CategoryChannel.username == channel_username) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении канала из категорий: {err}')
        return False
    finally:
        session.close()


async def delete_first_premium_channel_post(channel_id: int) -> bool:
    session = Session()
    try:
        result = session \
            .query(PremiumPost) \
            .join(PremiumChannel, PremiumPost.premium_channel_id == PremiumChannel.id) \
            .filter(PersonalChannel.id == channel_id) \
            .limit(1) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении первого поста в премиальном канале: {err}')
        return False
    finally:
        session.close()


async def delete_first_personal_channel_post(channel_id: int) -> bool:
    session = Session()
    try:
        result = session \
            .query(PersonalPost) \
            .join(PersonalChannel, PersonalPost.personal_channel_id == PersonalChannel.id) \
            .filter(PersonalChannel.id == channel_id) \
            .limit(1) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении первого поста в персональном канале: {err}')
        return False
    finally:
        session.close()


async def delete_first_category_channel_post(channel_id: int) -> bool:
    session = Session()
    try:
        result = session \
            .query(CategoryPost) \
            .join(CategoryChannel, CategoryPost.category_channel_id == CategoryChannel.id) \
            .filter(CategoryChannel.id == channel_id) \
            .limit(1) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении первого поста из канала в категориях: {err}')
        return False
    finally:
        session.close()


async def delete_premium_channel_post(post_id: int) -> bool:
    session = Session()
    try:
        result = session \
            .query(PremiumPost) \
            .filter(PremiumPost.id == post_id) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении поста в премиальном канале: {err}')
        return False
    finally:
        session.close()


async def delete_category_channel_post(post_id: int) -> bool:
    session = Session()
    try:
        result = session \
            .query(CategoryPost) \
            .filter(CategoryPost.id == post_id) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении поста из канала в категориях: {err}')
        return False
    finally:
        session.close()


async def delete_personal_channel_post(post_id: int) -> bool:
    session = Session()
    try:
        result = session \
            .query(PersonalPost) \
            .filter(PersonalPost.id == post_id) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении поста в персональном канале: {err}')
        return False
    finally:
        session.close()


async def delete_coefficient(coefficient_value: int):
    session = Session()
    try:
        result = session \
            .query(Coefficient) \
            .filter(Coefficient.value == coefficient_value) \
            .delete()

        session.commit()
        if not result:
            return False

        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении коэффициента: {err}')
        return False
    finally:
        session.close()
