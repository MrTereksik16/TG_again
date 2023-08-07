class Modes:
    RECOMMENDATIONS = 'recommendations'
    PERSONAL = 'personal'
    CATEGORIES = 'categories'


class PostTypes:
    PREMIUM = 'premium'
    PERSONAL = 'personal'
    CATEGORY = 'category'

    premium = None
    personal = None
    category = None

    def __init__(self, value: str):
        if value == 'premium':
            self.premium = value
        if value == 'personal':
            self.personal = value
        if value == 'category':
            self.category = value


class MarkTypes:
    LIKE = 1
    DISLIKE = 2
    NEUTRAL = 3

    def __new__(cls, value: int) -> int:
        if value == 1:
            return cls.LIKE
        if value == 2:
            return cls.DISLIKE
        if value == 3:
            return cls.NEUTRAL


class AddChannelsResult:
    answer = None
    to_parse = None

    def __init__(self, answer: str, to_parse: list):
        self.answer = answer
        self.to_parse = to_parse


class ParseData:
    chat_id = None
    message_id = None
    message_text = None
    message_media_path = None
    message_entities = None
    channel_id = None
    channel_username = None

    def __init__(
            self,
            message_id: int,
            message_text: str,
            message_media_path: str,
            channel_username: str,
            channel_id: int,
            message_entities: bytes,
            chat_id: int
    ):
        self.message_id = message_id
        self.chat_id = chat_id
        self.message_text = message_text
        self.message_media_path = message_media_path
        self.message_entities = message_entities
        self.channel_id = channel_id
        self.channel_username = channel_username
