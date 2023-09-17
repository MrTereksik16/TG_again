from sqlalchemy import text
from config.logging_config import logger
from database.create_db import Session
from database.models import Category, MarkType, Coefficient, EventType
from parse import parse
from utils.consts.categories import CATEGORIES, CATEGORIES_EMOJI
from utils.custom_types import UserEventsTypes


def create_initial_data():
    session = Session()
    query = 'SET NAMES "utf8mb4" COLLATE "utf8mb4_unicode_ci"'
    session.execute(text(query))
    session.flush()
    query = '''
        SET sql_mode="STRICT_TRANS_TABLES,STRICT_ALL_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,TRADITIONAL,NO_ENGINE_SUBSTITUTION"
    '''
    session.execute(text(query))
    session.flush()

    session.execute(text(query))
    session.flush()
    for i in range(0, len(CATEGORIES)):
        try:
            new_category = Category(id=i + 1, name=CATEGORIES[i], emoji=f'{CATEGORIES_EMOJI[CATEGORIES[i]]}')
            session.add(new_category)
            session.flush()
        except Exception as err:
            session.rollback()
            logger.error(err)
    session.commit()
    session = Session()
    try:
        new_mark_type = MarkType(name='like')
        session.add(new_mark_type)
        new_mark_type = MarkType(name='dislike')
        session.add(new_mark_type)
        new_mark_type = MarkType(name='neutral')
        session.add(new_mark_type)
        new_mark_type = MarkType(name='report')
        session.add(new_mark_type)

        new_coefficient = Coefficient(value=1)
        session.add(new_coefficient)
        new_coefficient = Coefficient(value=2)
        session.add(new_coefficient)
        new_coefficient = Coefficient(value=3)
        session.add(new_coefficient)
        new_coefficient = Coefficient(value=4)
        session.add(new_coefficient)
        new_coefficient = Coefficient(value=5)
        session.add(new_coefficient)
        session.commit()
    except Exception as err:
        logger.error(err)
    session = Session()
    try:
        new_event_type = EventType(id=UserEventsTypes.REGISTRATION, name='Зарегистрировался')
        session.add(new_event_type)
        new_event_type = EventType(id=UserEventsTypes.USED, name='Воспользовался')
        session.add(new_event_type)
        session.commit()
    except Exception as err:
        logger.error(err)
