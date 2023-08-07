from aiogram.dispatcher.filters.state import StatesGroup, State


class PersonalStates(StatesGroup):
    PERSONAL_FEED = State()
    GET_USER_CHANNELS = State()


class CategoriesStates(StatesGroup):
    CATEGORIES_FEED = State()
    GET_USER_CATEGORIES = State()


class RecommendationsStates(StatesGroup):
    RECOMMENDATIONS_FEED = State()


class AdminPanelStates(StatesGroup):
    ADMIN_PANEL = State()

    GET_CHANNELS_CATEGORY = State()
    GET_CATEGORY_NAME = State()
    GET_CATEGORY_EMOJI = State()
    GET_CATEGORY_CHANNELS = State()

    DELETE_CATEGORIES = State()
    DELETE_CATEGORIS_CHANNELS = State()

    GET_PREMIUM_CHANNELS = State()

