from pyrogram.types import MessageEntity


class Modes:
    RECOMMENDATIONS = 'recommendations'
    PERSONAL = 'personal'
    CATEGORIES = 'categories'


class PostTypes:
    PREMIUM = 'premium'
    PERSONAL = 'personal'
    CATEGORY = 'category'

    def __new__(cls, value: str) -> str:
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
    added_channels = None
    already_added = None
    not_added_channels = None

    def __init__(self, answer: str, to_parse: list, added_channels: list, already_added: list, not_added_channels: list):
        self.answer = answer
        self.to_parse = to_parse
        self.added_channels = added_channels
        self.already_added = already_added
        self.not_added_channels = not_added_channels


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
