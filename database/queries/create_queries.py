from database.create_db import Session
from utils.consts import errors
from config.logging_config import logger
from database.models import UserChannel, User, PersonalPost, PersonalChannel, UserCategory, \
    PremiumPost, CategoryChannel, PremiumChannel, CategoryPost, UserViewedPremiumPost, \
    UserViewedCategoryPost, UserViewedPersonalPost, Category
from utils.custom_types import Post


async def create_user(user_tg_id: int) -> bool:
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


async def create_personal_channel(channel_tg_id: int, channel_username: str) -> int | str | None:
    session = Session()
    try:
        personal_channel = PersonalChannel(id=channel_tg_id, username=channel_username)
        session.add(personal_channel)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении пользовательского канала: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_user_channel(user_tg_id: int, channel_tg_id: int) -> bool:
    session = Session()
    try:
        session.add(UserChannel(user_id=user_tg_id, channel_id=channel_tg_id))
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при связывании канала с пользователем: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_category_channel(channel_tg_id: int, channel_username: str, category_id: int) -> bool:
    session = Session()
    try:
        new_category_channel = CategoryChannel(id=channel_tg_id, category_id=category_id, username=channel_username)
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


async def create_personal_posts(posts: list[Post]):
    session = Session()
    try:
        for post in posts:
            entities = post.message_entities
            text = post.message_text
            image_path = post.message_media_path
            channel_id = post.channel_id

            new_personal_post = PersonalPost(text=text, image_path=image_path, personal_channel_id=channel_id, entities=entities)
            session.add(new_personal_post)
            session.flush()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении пользовательского поста: {err}')
        return False
    finally:
        session.close()


async def create_category_posts(posts: list[Post]):
    session = Session()

    try:
        for post in posts:
            entities = post.message_entities
            text = post.message_text
            image_path = post.message_media_path
            channel_id = post.channel_id

            new_category_post = CategoryPost(text=text, image_path=image_path, likes=0, dislikes=0, category_channel_id=channel_id, entities=entities)
            session.add(new_category_post)
            session.flush()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении общего поста: {err}')
        return False
    finally:
        session.close()


async def create_premium_posts(posts: list[Post]):
    session = Session()
    try:
        for post in posts:
            entities = post.message_entities
            text = post.message_text
            image_path = post.message_media_path
            channel_id = post.channel_id

            new_premium_post = PremiumPost(text=text, image_path=image_path, likes=0, dislikes=0, premium_channel_id=channel_id, entities=entities)
            session.add(new_premium_post)
            session.flush()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении постов из премиального канала: {err}')
        return False
    finally:
        session.close()


async def create_premium_post(post: Post) -> bool:
    session = Session()
    entities = post.message_entities
    text = post.message_text
    image_path = post.message_media_path
    channel_id = post.channel_id

    try:
        new_premium_post = PremiumPost(text=text, image_path=image_path, likes=0, dislikes=0, premium_channel_id=channel_id, entities=entities)
        session.add(new_premium_post)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении премиального поста: {err}')
        return False
    finally:
        session.close()


async def create_category_post(post: Post) -> bool:
    session = Session()
    entities = post.message_entities
    text = post.message_text
    image_path = post.message_media_path
    channel_id = post.channel_id
    try:
        new_category_post = CategoryPost(text=text, image_path=image_path, likes=0, dislikes=0, category_channel_id=channel_id, entities=entities)
        session.add(new_category_post)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении поста в категории: {err}')
        return False
    finally:
        session.close()


async def create_personal_post(post) -> bool:
    session = Session()
    entities = post.message_entities
    text = post.message_text
    image_path = post.message_media_path
    channel_id = post.channel_id
    try:
        new_personal_post = PersonalPost(text=text, image_path=image_path, likes=0, dislikes=0, personal_channel_id=channel_id, entities=entities)
        session.add(new_personal_post)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении персонального поста: {err}')
        return False
    finally:
        session.close()


async def create_category(category_name: str, category_emoji: str) -> bool | str:
    session = Session()
    try:
        new_category = Category(name=category_name, emoji=category_emoji)
        session.add(new_category)
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при добавлении общего поста: {err}')
        if 'Duplicate entry' in str(err):
            return errors.DUPLICATE_ENTRY_ERROR
        return False
    finally:
        session.close()


async def create_user_category(user_tg_id: int, category_id: int) -> bool:
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


async def create_recommendation_channel(channel_tg_id: int, channel_username: str) -> bool:
    session = Session()
    try:
        new_recommendation_channel = PremiumChannel(id=channel_tg_id, username=channel_username)
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


async def create_user_viewed_premium_post(user_tg_id, post_id) -> bool:
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


async def create_user_viewed_category_post(user_tg_id, post_id) -> bool:
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


async def create_user_viewed_personal_post(user_tg_id, post_id) -> bool:
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
