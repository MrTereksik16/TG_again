from config import config


class Modes:
    SINGLE_MODE: dict = {'id': 0, 'name': 'Одиночный'}
    MULTI_MODE: dict = {'id': 1, 'name': 'Мульти'}

    def __new__(cls, value: int):
        if value == cls.MULTI_MODE['id']:
            return cls.MULTI_MODE['id']
        elif value == cls.SINGLE_MODE['id']:
            return cls.SINGLE_MODE['id']

    @classmethod
    def get_mods(cls) -> list[dict]:
        return [cls.SINGLE_MODE, cls.MULTI_MODE]


class Feeds:
    RECOMMENDATIONS = 'Рекомендации'
    PERSONAL = 'Личная'
    CATEGORIES = 'Категории'

    def __new__(cls, value: str):
        if value == cls.RECOMMENDATIONS:
            return cls.RECOMMENDATIONS
        elif value == cls.PERSONAL:
            return cls.PERSONAL
        elif value == cls.CATEGORIES:
            return cls.CATEGORIES


class ChannelPostTypes:
    PREMIUM = 'Прем'
    PERSONAL = 'Лич'
    CATEGORY = 'Кат'

    def __new__(cls, value: str):
        if value == cls.PREMIUM:
            return cls.PREMIUM
        elif value == cls.PERSONAL:
            return cls.PERSONAL
        elif value == cls.CATEGORY:
            return cls.CATEGORY


class MarkTypes:
    LIKE = 1
    DISLIKE = 2
    NEUTRAL = 3
    REPORT = 4


class UserEventsTypes:
    REGISTRATION = 1
    USED = 2


class AddChannelsResult:
    answer = None
    to_parse = None

    def __init__(self, answer: str, to_parse: list):
        self.answer = answer
        self.to_parse = to_parse


class Post:
    channel_id = None
    message_text = None
    message_entities = None
    message_media_path = None
    channel_username = None

    def __init__(
            self,
            channel_id: int,
            channel_username: str,
            message_text: str | None,
            message_entities: bytes | None,
            message_media_path: str | None,
    ):
        self.channel_id = channel_id
        self.message_text = message_text
        self.message_entities = message_entities
        self.message_media_path = message_media_path
        self.channel_username = channel_username


class Statistic:
    total_users = 0
    daily_users = 0
    daily_likes = 0
    daily_dislikes = 0
    user_growth = 0
    daily_views = 0

    def __init__(self, total_users: int, daily_users: int, daily_likes: int, daily_dislikes: int, user_growth: int, daily_views: int):
        self.total_users = total_users
        self.daily_users = daily_users
        self.daily_likes = daily_likes
        self.daily_dislikes = daily_dislikes
        self.user_growth = user_growth
        self.daily_views = daily_views

    def __str__(self, user_is_admin: bool = False):
        return f'<i>Всего пользователей</i>: {self.total_users}\n<i>Новых пользователей</i>: {self.user_growth} 🆕\n<i>Пользовались сегодня</i>: {self.daily_users} 🔥\n<i>Лайков за сегодня</i>: {self.daily_likes} ❤\n<i>Дизлайков за сегодня</i>: {self.daily_dislikes} 👎\n<i>Просмотры за сегодня</i>: {self.daily_views} 👁\n<i>Подробнее</i>: {config.PUBLIC_STATISTIC_URL}'
