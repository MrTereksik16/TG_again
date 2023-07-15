from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    GET_USER_CHANNELS = State()
    GET_GENERAL_CHANNELS = State()
    GET_USER_CATEGORIES = State()

    PERSONAL_FEED = State()
    CATEGORIES_FEED = State()
    RECOMMENDATIONS_FEED = State()
