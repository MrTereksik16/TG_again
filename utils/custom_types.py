class Modes:
    RECOMMENDATIONS = 'Рекомендации'
    PERSONAL = 'Личная лента'
    CATEGORIES = 'Категории'


class PostTypes:
    PREMIUM = 'Премиальный'
    PERSONAL = 'Личный'
    CATEGORY = 'Из категорий'

    def __new__(cls, value: str):
        if value == cls.PREMIUM:
            return cls.PREMIUM
        if value == cls.PERSONAL:
            return cls.PERSONAL
        if value == cls.CATEGORY:
            return cls.CATEGORY


class MarkTypes:
    LIKE = 1
    DISLIKE = 2
    NEUTRAL = 3
    REPORT = 4


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
